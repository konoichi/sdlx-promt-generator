"""
PromptGenerator — core business logic.
Knows only ports, never concrete adapters.
"""

from .ports import LLMPort, StoragePort
from .character import Character
import json
import uuid
from datetime import datetime


def _categorize_error(exc: Exception) -> tuple[str, str]:
    """
    Returns (error_type, human_readable_message).

    error_type values:
      connection  — server not reachable
      timeout     — no response within timeout
      auth        — 401 / permission denied
      format      — model responded but not with valid JSON
      content     — model refused (content filter / safety)
      http        — other HTTP error
      unknown     — everything else
    """
    msg = str(exc)
    cls = type(exc).__name__

    if "401" in msg or "Unauthorized" in msg:
        return "auth", (
            "Zugriff verweigert (401 Unauthorized). "
            "API-Key fehlt oder ist ungültig — OLLAMA_LOCAL_API_KEY / OLLAMA_CLOUD_API_KEY prüfen."
        )

    if "nicht erreichbar" in msg or cls in ("ConnectionError", "ConnectionRefusedError"):
        return "connection", msg

    # requests.exceptions.ReadTimeout bubbles up as this message
    if "hat nicht innerhalb" in msg or "Read timed out" in msg or "ReadTimeout" in cls:
        return "timeout", msg

    if "Model returned no JSON" in msg:
        return "format", (
            "Das Modell hat kein JSON geliefert — es befolgt die Formatvorgabe nicht. "
            "Ursache: das Modell ist für diese Aufgabe nicht geeignet oder ignoriert den System-Prompt. "
            "Empfehlung: qwen2.5-coder:7b / qwen3-coder-next oder ein Cloud-Modell verwenden."
        )

    # Generic content refusal heuristic — model returns very short non-JSON response
    if "Response:" in msg and len(msg) < 200:
        return "content", (
            "Das Modell hat die Anfrage möglicherweise abgelehnt (Content-Filter). "
            f"Antwort: {msg}"
        )

    if any(code in msg for code in ("400", "403", "404", "429", "500", "502", "503")):
        return "http", msg

    return "unknown", msg


_ANCHORS = """## Consistency Anchors for Faces (strongest first)

1. Eye color + eye shape (strongest anchor by far)
2. Distinctive bone structure (cheekbones, jaw)
3. Nose shape
4. Hair color (unusual colors > common ones)
5. Special features (scars, freckles, dimples)"""

_WEIGHTING = """## Weighting Rules for Consistency

- Face structure tokens: (token:1.2–1.3) — eyes, bone structure, distinctive features
- Quality tokens: (token:1.1–1.4) — not too high or you get overemphasis
- General descriptions: no weight or max 1.1
- Never stack multiple high weights directly next to each other (>1.3) — they compete"""

_TOOL_SYNTAX = """## Tool-Specific Prompt Syntax

Adapt weighting syntax exactly to the tool in use:
- ComfyUI: (token:1.2) — standard, precise weighting
- Automatic1111: (token:1.2) for emphasis, [token] for de-emphasis, BREAK keyword between zones possible
- InvokeAI: (token)+ for light emphasis, (token)++ for stronger — no decimal numbers
- Fooocus: NO manual weights — Fooocus optimizes internally, brackets are ignored or disruptive
- ComfyUI + SDXL Turbo: weights max 1.2, no extremes — Turbo is more sensitive"""

_OUTPUT_FORMAT = """---

## Output Format

Reply ONLY with a JSON object. No markdown, no backticks, no text before or after.

{
  "zone1": {
    "prompt": "...",
    "tokens": [{"name": "TOKEN", "explanation": "Why this token matters for consistency, 1-2 sentences"}]
  },
  "zone2_face": {
    "prompt": "...",
    "tokens": [{"name": "TOKEN", "explanation": "..."}]
  },
  "zone3_body": {
    "prompt": "...",
    "tokens": [{"name": "TOKEN", "explanation": "..."}]
  },
  "zone4_context": {
    "prompt": "...",
    "tokens": [{"name": "TOKEN", "explanation": "..."}]
  },
  "negative": "..."
}"""

_ZONES_234 = """zone2_face — Face and Identity (consistency core)
Order: base (gender, age, ethnicity) → eyes (WITH weight!) → bone structure → nose → hair → expression → special features.
Eye color and distinctive facial features ALWAYS with appropriate weight.

zone3_body — Body and Clothing (adapt strictly to Shot Type from character data)
- portrait: one line max — shoulders and décolleté only; omit legs, hips, full figure; mention clothing if visible on shoulders (e.g., collar, straps)
- upper body shot: torso, chest, shoulders, upper arms; include breast_size, body_hair, and detailed CLOTHING tokens if provided
- full body shot: complete figure — build, posture, hips, legs; include breast_size, body_hair, and detailed CLOTHING tokens if provided

zone4_context — Scene, Composition and Light
Lighting → Scene/Environment Details (if provided) → framing token that matches the Shot Type → sharp focus on eyes.
Framing tokens per shot type:
- portrait: "close-up portrait, head and shoulders"
- upper body shot: "upper body shot, from waist up"
- full body shot: "full body shot, full length"
Always end with "sharp focus on eyes" as the last token. If scene/environment is specified, describe it vividly, ensuring it complements the character's lighting and style.
"""


_SYSTEM_SDXL = f"""You are an expert Stable Diffusion XL prompt engineer with deep knowledge of SDXL architecture, CLIP tokenization, and character consistency workflows.

Your task: Generate a production-ready SDXL portrait prompt from the given character data that enables maximum face and body consistency across multiple generations. Adapt syntax and tokens precisely to the specified tool and checkpoint.

## SDXL Prompt Processing

- SDXL uses two CLIP encoders (ViT-L and ViT-bigG) — early tokens are weighted more strongly
- Quality tokens must ALWAYS appear first
- Maximum effective token length: ~75 tokens per CLIP encoder
- Weights with (token:weight) — sensible range: 1.1–1.5, higher causes artifacts

## Proven SDXL Quality Token Combinations

- Photorealism: "RAW photo, (photorealistic:1.3), (hyperdetailed skin:1.2), dslr, analog style"
- Portrait sharpness: "sharp focus, (sharp facial features:1.2), subsurface scattering"
- Skin quality: "skin pores, detailed skin texture, natural skin imperfections"
- Professional: "studio photography, professional lighting, shot on Sony A7R"

{_ANCHORS}

## Negative Prompt Best Practices

- Face-specific: "asymmetric eyes, uneven eyes, lazy eye, crossed eyes, blurry face, out of focus eyes, bad eyes"
- Anatomy: "deformed, disfigured, bad anatomy, extra limbs, fused fingers, missing fingers"
- Quality: "lowres, worst quality, low quality, jpeg artifacts, noise, grain"
- Style exclusion: "painting, illustration, cartoon, anime, cgi, render, drawing, sketch"
- SDXL-specific: "oversaturated, overexposed, underexposed, plastic skin, waxy skin, airbrushed"

{_WEIGHTING}

{_TOOL_SYNTAX}

## Checkpoint-Specific Recommendations

- Juggernaut XL: Strong photorealism. "RAW photo, analog style" very effective. Extremely stable faces.
- RealVisXL: Natural rendering. "natural lighting, candid photo" rather than heavy studio tokens.
- ZavyChromaXL: Handles vivid descriptions well. "vibrant, detailed" work effectively.
- DreamShaper XL: Slightly stylized — "detailed portrait, artistic" fit, reduce hyperrealism tokens.
- Copax TimelessXL: "cinematic, film grain, 35mm" very effective for the cinematic look.
- Playground v2.5: Prefer "aesthetic, beautiful, high quality" over technical photo tokens.
- Animagine XL: Anime vocabulary: "1girl, masterpiece, best quality" instead of RAW photo.
- SDXL Base 1.0: Set all quality tokens explicitly, use maximum token width.

{_OUTPUT_FORMAT}

## Zone Rules

zone1 — Quality (always first, max 15 tokens)
Quality tokens with appropriate weights matching the checkpoint.
Order: photo type → realism → skin detail → resolution → camera.

{_ZONES_234}

negative
Complete SDXL-optimized negative prompt. Include face- and quality-specific tokens.
For Fooocus: keep negative prompt short as it is processed internally."""


_SYSTEM_PONY_V6 = f"""You are an expert Pony Diffusion XL V6 prompt engineer with deep knowledge of Danbooru tag vocabulary, score chains, and character consistency workflows.

Your task: Generate a production-ready Pony V6 portrait prompt from the given character data that enables maximum face and body consistency across multiple generations. Pony V6 is SDXL-based and trained on Danbooru-tagged data.

## Pony V6 Prompt Processing

- SDXL-based with Danbooru tag vocabulary — use tag-style prompts, not natural language
- Score chain is MANDATORY at the very start of zone1 — never deviate from this
- Source tag follows the score chain (use the Pony Source Tag from the character data; omit entirely if none is specified)
- Safety rating MANDATORY for SFW: rating_safe
- CLIP Skip: 2
- Weights with (token:weight) — sensible range: 1.1–1.4

## Zone1 Score Chain (STRICT ORDER — never deviate)

MUST start with: score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up
Then (in order): source tag (if specified) → RATING TAG (rating_safe if NSFW is NO, rating_explicit if NSFW is YES) → style quality tokens.
NEVER place anything before the score chain. NEVER omit the score chain.

## Negative Prompt Rules (Pony V6)

MUST start with: score_3_up, score_2_up, score_1_up, rating_explicit, rating_questionable
Then add: bad anatomy, deformed hands, extra limbs, blurry face, out of focus eyes, asymmetric eyes, worst quality, low quality, watermark

{_ANCHORS}

{_WEIGHTING}

{_TOOL_SYNTAX}

{_OUTPUT_FORMAT}

## Zone Rules

zone1 — Score Chain + Quality (always first, max 20 tokens)
MUST start with: score_9, score_8_up, score_7_up, score_6_up, score_5_up, score_4_up
Then: source tag (if specified), rating_safe, then style quality tokens.

{_ZONES_234}

negative
MUST start with: score_3_up, score_2_up, score_1_up, rating_explicit, rating_questionable
Then anatomy, face, and quality negatives."""


_SYSTEM_ILLUSTRIOUS = f"""You are an expert Illustrious XL prompt engineer with deep knowledge of Danbooru tag vocabulary and character consistency workflows.

Your task: Generate a production-ready Illustrious XL portrait prompt from the given character data that enables maximum face and body consistency across multiple generations. Illustrious XL is SDXL-based, trained on Danbooru-tagged data, and natively knows Danbooru characters and artist styles.

## Illustrious XL Prompt Processing

- SDXL-based with Danbooru tag vocabulary — use Danbooru-style tags
- Quality prefix is MANDATORY at the start of zone1
- CLIP Skip: 2
- CFG Scale: 4.0–7.0
- Weights with (token:weight) — sensible range: 1.1–1.4
- Natively knows Danbooru characters and artist styles (no LoRA needed for known characters)

## Zone1 Quality Prefix (MANDATORY)

MUST start with: masterpiece, best quality, amazing quality, very aesthetic, absurdres
Then add style-appropriate quality tokens.

## Negative Prompt Rules (Illustrious XL)

Always include: lowres, bad anatomy, bad hands, extra digits, worst quality, jpeg artifacts, low quality, watermark, blurry
Plus face-specific: asymmetric eyes, uneven eyes, blurry face, out of focus eyes

{_ANCHORS}

{_WEIGHTING}

{_TOOL_SYNTAX}

{_OUTPUT_FORMAT}

## Zone Rules

zone1 — Quality (always first, max 15 tokens)
MUST start with: masterpiece, best quality, amazing quality, very aesthetic, absurdres
Then add style-appropriate quality tokens.

{_ZONES_234}

negative
Must include: lowres, bad anatomy, bad hands, extra digits, worst quality, jpeg artifacts, low quality, watermark, blurry
Then face- and anatomy-specific tokens."""


_SYSTEM_PROMPTS = {
    "sdxl": _SYSTEM_SDXL,
    "pony_v6": _SYSTEM_PONY_V6,
    "illustrious": _SYSTEM_ILLUSTRIOUS,
}


def _get_system_prompt(character: "Character") -> str:
    return _SYSTEM_PROMPTS.get(character.model_family, _SYSTEM_SDXL)


USER_TEMPLATE = """Generate a portrait prompt for the following character:

{context}

Important: Adapt prompt syntax, weights, and quality tokens precisely to the specified tool, checkpoint, and model family. Apply weights selectively to the strongest consistency anchors for this character.

NSFW Policy: If "NSFW/Explicit Content Allowed" is NO, strictly avoid any explicit, anatomical, or sexual terms. If YES, you are permitted to use descriptive anatomical terms and explicit tags as appropriate for the model family."""


class PromptGenerator:
    def __init__(self, llm: LLMPort, storage: StoragePort):
        self._llm = llm
        self._storage = storage

    # ── helpers ────────────────────────────────────────────────────────────

    def _parse_json_response(self, raw: str) -> dict:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError(f"Model returned no JSON. Response: {raw[:300]!r}")
        return json.loads(raw[start:end + 1].strip())

    def _build_history_entry(self, result: dict, character: Character,
                              provider: str, model: str, user_id: str) -> dict:
        positive = "\n\n".join([
            result["zone1"]["prompt"],
            result["zone2_face"]["prompt"],
            result["zone3_body"]["prompt"],
            result["zone4_context"]["prompt"],
        ])
        entry = {
            "id": str(uuid.uuid4()),
            "character_id": character.id,
            "character_name": character.name,
            "provider": provider,
            "model": model,
            "sd_tool": character.sd_tool,
            "sd_checkpoint": character.effective_checkpoint,
            "model_family": character.model_family,
            "character_snapshot": character.to_dict(),
            "status": "success",
            "result": result,
            "positive_prompt": positive,
            "negative_prompt": result["negative"],
            "created_at": datetime.now().isoformat(),
        }
        self._storage.save_prompt_history(entry, user_id)
        return entry

    # ── public API ─────────────────────────────────────────────────────────

    def generate(self, character: Character, user_id: str) -> dict:
        context = character.to_prompt_context()
        user_msg = USER_TEMPLATE.format(context=context)

        response = self._llm.generate(
            system_prompt=_get_system_prompt(character),
            user_message=user_msg,
        )

        result = self._parse_json_response(response.content)
        return self._build_history_entry(result, character, response.provider, response.model, user_id)

    def generate_stream(self, character: Character, user_id: str):
        """
        Yields SSE-ready event dicts for the /api/generate endpoint.
        Works with any adapter: streaming if available, sync fallback otherwise.

        Event types emitted:
          {"type": "status",   "msg": "connecting"|"loaded"|"thinking"|"generating"}
          {"type": "thinking", "delta": str}   — reasoning chunk
          {"type": "result",   "data": dict}   — final history entry on success
          {"type": "error",    "error": str}   — on failure (already saved to history)
        """
        context = character.to_prompt_context()
        user_msg = USER_TEMPLATE.format(context=context)

        yield {"type": "status", "msg": "connecting"}

        if not hasattr(self._llm, "generate_stream"):
            # Sync fallback for adapters that don't support streaming (e.g. Anthropic)
            try:
                result = self.generate(character, user_id)
                yield {"type": "result", "data": result}
            except Exception as e:
                error_type, friendly_msg = _categorize_error(e)
                yield {"type": "error", "error": friendly_msg, "error_type": error_type}
            return

        provider = "ollama"
        model = ""
        full_content = ""
        has_thinking = False

        try:
            for event in self._llm.generate_stream(_get_system_prompt(character), user_msg):
                etype = event["type"]

                if etype == "meta":
                    provider = event.get("provider", "ollama")
                    model = event.get("model", "")

                elif etype == "loaded":
                    yield {"type": "status", "msg": "loaded"}

                elif etype == "thinking":
                    if not has_thinking:
                        has_thinking = True
                        yield {"type": "status", "msg": "thinking"}
                    yield {"type": "thinking", "delta": event["delta"]}

                elif etype == "token":
                    if not full_content:
                        yield {"type": "status", "msg": "generating"}
                    full_content += event["delta"]

            result = self._parse_json_response(full_content)
            entry = self._build_history_entry(result, character, provider, model, user_id)
            yield {"type": "result", "data": entry}

        except Exception as e:
            error_type, friendly_msg = _categorize_error(e)
            try:
                self.save_error(
                    character_name=character.name,
                    provider=provider,
                    model=model,
                    error=friendly_msg,
                    user_id=user_id,
                    character_id=character.id,
                    error_type=error_type,
                )
            except Exception:
                pass
            yield {"type": "error", "error": friendly_msg, "error_type": error_type}

    def save_error(self, character_name: str, provider: str, model: str,
                   error: str, user_id: str, character_id: str | None = None,
                   error_type: str = "unknown") -> dict:
        entry = {
            "id": str(uuid.uuid4()),
            "character_id": character_id,
            "character_name": character_name,
            "provider": provider,
            "model": model,
            "status": "error",
            "error_type": error_type,
            "error": error,
            "created_at": datetime.now().isoformat(),
        }
        self._storage.save_prompt_history(entry, user_id)
        return entry

    def save_character(self, character: Character, user_id: str) -> str:
        return self._storage.save_character(character.to_dict(), user_id)

    def load_character(self, character_id: str, user_id: str) -> Character | None:
        data = self._storage.load_character(character_id, user_id)
        if data:
            return Character.from_dict(data)
        return None

    def list_characters(self, user_id: str) -> list[dict]:
        return self._storage.list_characters(user_id)

    def delete_character(self, character_id: str, user_id: str) -> bool:
        return self._storage.delete_character(character_id, user_id)

    def list_prompt_history(self, user_id: str, character_id: str | None = None) -> list[dict]:
        return self._storage.list_prompt_history(user_id, character_id)

    def load_prompt_history(self, entry_id: str, user_id: str) -> dict | None:
        return self._storage.load_prompt_history(entry_id, user_id)

    def delete_prompt_history(self, entry_id: str, user_id: str) -> bool:
        return self._storage.delete_prompt_history(entry_id, user_id)

    def update_history_entry(self, entry_id: str, user_id: str, updates: dict) -> bool:
        return self._storage.update_prompt_history(entry_id, user_id, updates)
