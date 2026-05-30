"""
Character — das zentrale Datenmodell.
Reine Datenstruktur, keine Abhängigkeiten nach außen.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional
import uuid
from datetime import datetime


SDXL_CHECKPOINTS = {
    "Juggernaut XL":        "Sehr stabile Gesichter, photorealistisch, gute Hauttöne",
    "RealVisXL":            "Natürliche Hauttöne, exzellente Detailschärfe, authentisch",
    "ZavyChromaXL":         "Vielseitig, gute Gesichtsstruktur, lebendige Farben",
    "DreamShaper XL":       "Kreativ, leicht stilisiert, gute Gesichter",
    "Copax TimelessXL":     "Zeitloser Look, stabile Proportionen, cineastisch",
    "SDXL Base 1.0":        "Vanilla SDXL, maximale Kompatibilität",
    "Animagine XL":         "Anime/Semi-Anime Stil",
    "Playground v2.5":      "Ästhetisch, gute Komposition, leicht künstlerisch",
}

SD_TOOLS = {
    "ComfyUI":                  "Gewichtung: (token:1.2), präzise Node-basierte Pipeline",
    "Automatic1111":            "Gewichtung: (token:1.2) und [token] für Deemphasis, weit verbreitet",
    "InvokeAI":                 "Gewichtung: (token)+ oder (token)-, eigene Syntax",
    "Fooocus":                  "Vereinfacht, keine manuellen Gewichtungen, interne Optimierung",
    "ComfyUI + SDXL Turbo":     "Weniger Steps (4-8), CFG niedrig (1-2), Gewichtungen vorsichtig",
}


@dataclass
class Character:
    # Basis
    name: str
    gender: str
    age: str
    ethnicity: str

    # Gesicht
    eyes: str
    nose: str
    jaw: str
    face_special: str = ""

    # Haare
    hair_color: str = ""
    hair_length: str = ""
    hair_style: str = ""

    # Körper
    height: str = ""
    build: str = ""
    shoulders: str = ""
    skin: str = ""
    breast_size: str = ""                         # small/medium/large/huge breasts — nur bei Frau
    pubic_hair: str = ""                          # no pubic hair | pubic stubble | trimmed pubic hair | landing strip | pubic hair — nur bei Frau
    body_hair: list[str] = field(default_factory=list)   # chest hair | armpit hair | leg hair | hairy
    body_marks: list[str] = field(default_factory=list)

    # Kleidung & Szene
    clothing: str = ""
    clothing_standard: str = ""
    scene: str = ""
    scene_standard: str = ""

    # Kontext
    expression: str = "neutral expression, lips slightly parted"
    lighting: str = "soft studio lighting, light grey background"

    # Aufnahme
    shot_type: str = "portrait"   # portrait | upper body shot | full body shot

    # Modell-Familie
    model_family: str = "sdxl"    # sdxl | pony_v6 | illustrious
    pony_source: str = ""          # source_anime | source_cartoon | source_furry | source_pony | ""
    allow_nsfw: bool = False

    # Tool & Checkpoint
    sd_tool: str = "ComfyUI"
    sd_checkpoint: str = "Juggernaut XL"
    sd_checkpoint_custom: str = ""

    # Meta
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Character":
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    @property
    def effective_checkpoint(self) -> str:
        return self.sd_checkpoint_custom if self.sd_checkpoint_custom else self.sd_checkpoint

    @property
    def checkpoint_info(self) -> str:
        return SDXL_CHECKPOINTS.get(self.effective_checkpoint, "Kein spezifisches Profil bekannt")

    @property
    def tool_info(self) -> str:
        return SD_TOOLS.get(self.sd_tool, "Standard Prompt-Syntax")

    def to_prompt_context(self) -> str:
        """Formatiert den Character für den LLM-Prompt."""
        family_label = {
            "sdxl": "SDXL",
            "pony_v6": "Pony Diffusion XL V6",
            "illustrious": "Illustrious XL",
        }.get(self.model_family, self.model_family)

        ckpt_line = f"Checkpoint: {self.effective_checkpoint}"
        if self.model_family == "sdxl":
            ckpt_line += f" — {self.checkpoint_info}"

        parts = [
            f"Model Family: {family_label}",
            f"Tool: {self.sd_tool} — {self.tool_info}",
            ckpt_line,
        ]
        if self.model_family == "pony_v6":
            source = self.pony_source or "none (photorealistic checkpoint — omit source tag)"
            parts.append(f"Pony Source Tag: {source}")
        
        parts.append(f"NSFW/Explicit Content Allowed: {'YES' if self.allow_nsfw else 'NO'}")
        
        parts += [
            f"Shot Type: {self.shot_type}",
            "",
            f"Basis: {self.gender}, {self.age}, {self.ethnicity}",
            f"Gesicht: {self.eyes}, {self.nose}, {self.jaw}" +
            (f", {self.face_special}" if self.face_special else ""),
            f"Haare: {self.hair_color}, {self.hair_length}, {self.hair_style}",
            f"Körper: {self.height}, {self.build}" +
            (f", {self.shoulders}" if self.shoulders else "") +
            f", {self.skin}",
        ]
        if self.breast_size:
            parts.append(f"Breast Size: {self.breast_size}")
        if self.pubic_hair and self.shot_type == "full body shot":
            parts.append(f"Pubic Hair Style: {self.pubic_hair}")
        if self.body_hair:
            parts.append(f"Body Hair: {', '.join(self.body_hair)}")
        
        # Kleidung & Szene
        clothing_parts = []
        if self.clothing_standard: clothing_parts.append(self.clothing_standard)
        if self.clothing: clothing_parts.append(self.clothing)
        if clothing_parts:
            parts.append(f"Clothing: {', '.join(clothing_parts)}")

        scene_parts = []
        if self.scene_standard: scene_parts.append(self.scene_standard)
        if self.scene: scene_parts.append(self.scene)
        if scene_parts:
            parts.append(f"Scene/Environment: {', '.join(scene_parts)}")

        parts += [
            f"Körpermerkmale: {', '.join(self.body_marks) if self.body_marks else 'keine'}",
            f"Mimik: {self.expression}",
            f"Lighting: {self.lighting}",
        ]
        return "\n".join(parts)
