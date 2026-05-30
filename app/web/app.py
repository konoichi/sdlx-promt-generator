"""
Flask Web App — nur Routing und HTTP.
Keine Business Logic hier. Alles geht durch den PromptGenerator.
"""

from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_file
import requests as req_lib
import json
import os
import markdown as md_lib
from app.config import (
    get_generator,
    get_image_backend,
    get_image_backends_status,
    get_providers_status,
    get_provider,
)
from app.core.character import Character
from app.core.ports import ImageGenerationRequest

_IMAGES_DIR = os.path.abspath(os.path.join(os.environ.get("DATA_DIR", "data"), "images"))
_GUIDE_PATH = os.path.abspath("docs/stable-diffusion-leitfaden-v3.md")
_ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp"}

app = Flask(__name__)


# ─── Status ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


@app.route("/guide")
def guide():
    import re
    text = open(_GUIDE_PATH, encoding="utf-8").read()
    version_match = re.search(r'\*\*Version\s+([\d.]+)\*\*.*?Stand:\s*([^\n]+)', text)
    version = version_match.group(1) if version_match else "–"
    stand   = version_match.group(2).strip() if version_match else ""
    converter = md_lib.Markdown(
        extensions=["toc", "tables", "fenced_code"],
        extension_configs={"toc": {"toc_depth": "2-3", "permalink": False}},
    )
    content = converter.convert(text)
    return render_template("guide.html", content=content, toc=converter.toc,
                           version=version, stand=stand)


@app.route("/api/providers")
def providers():
    return jsonify(get_providers_status())


@app.route("/api/providers/<provider_id>/models")
def provider_models(provider_id):
    adapter = get_provider(provider_id)
    return jsonify({"models": adapter.available_models})


@app.route("/api/image-backends")
def image_backends():
    return jsonify(get_image_backends_status())


@app.route("/api/image-backends/<backend_id>/host", methods=["POST"])
def set_image_backend_host(backend_id):
    backend = get_image_backend(backend_id)
    if not backend:
        return jsonify({"ok": False, "error": "Unbekanntes Image-Backend"}), 404
    host = request.json.get("host", backend.host)
    backend.set_host(host)
    status = backend.status()
    return jsonify({"ok": True, **status.__dict__})


# ─── Prompt generieren ─────────────────────────────────────────────────────

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    provider_name = data.pop("provider", "anthropic")
    model = data.pop("model", None)

    adapter = get_provider(provider_name)
    if model and hasattr(adapter, "set_model"):
        adapter.set_model(model)

    generator = get_generator(provider_name)

    try:
        character = Character.from_dict(data)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    def event_stream():
        for event in generator.generate_stream(character):
            yield f"data: {json.dumps(event)}\n\n"

    return Response(
        stream_with_context(event_stream()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─── Characters ───────────────────────────────────────────────────────────

@app.route("/api/characters", methods=["GET"])
def list_characters():
    generator = get_generator()
    return jsonify(generator.list_characters())


@app.route("/api/characters", methods=["POST"])
def save_character():
    data = request.json
    generator = get_generator()
    try:
        character = Character.from_dict(data)
        cid = generator.save_character(character)
        return jsonify({"ok": True, "id": cid})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/characters/<character_id>", methods=["GET"])
def load_character(character_id):
    generator = get_generator()
    character = generator.load_character(character_id)
    if character:
        return jsonify(character.to_dict())
    return jsonify({"error": "Nicht gefunden"}), 404


@app.route("/api/characters/<character_id>", methods=["DELETE"])
def delete_character(character_id):
    generator = get_generator()
    ok = generator.delete_character(character_id)
    return jsonify({"ok": ok})


# ─── Prompt History ────────────────────────────────────────────────────────

@app.route("/api/history")
def list_history():
    character_id = request.args.get("character_id")
    generator = get_generator()
    return jsonify(generator.list_prompt_history(character_id))


@app.route("/api/history/<entry_id>", methods=["DELETE"])
def delete_history(entry_id):
    generator = get_generator()
    ok = generator.delete_prompt_history(entry_id)
    return jsonify({"ok": ok})


# ─── History Images ───────────────────────────────────────────────────────

@app.route("/api/history/<entry_id>/image", methods=["POST"])
def upload_history_image(entry_id):
    if "image" not in request.files:
        return jsonify({"error": "Kein Bild"}), 400
    f = request.files["image"]
    ext = (f.filename or "").rsplit(".", 1)[-1].lower()
    if ext not in _ALLOWED_EXTS:
        return jsonify({"error": "Ungültiges Format (jpg/png/webp)"}), 400
    os.makedirs(_IMAGES_DIR, exist_ok=True)
    filename = f"{entry_id}.{ext}"
    f.save(os.path.join(_IMAGES_DIR, filename))
    generator = get_generator()
    generator.update_history_entry(entry_id, {"image_path": filename})
    return jsonify({"ok": True})


@app.route("/api/history/<entry_id>/image", methods=["GET"])
def serve_history_image(entry_id):
    for ext in _ALLOWED_EXTS:
        path = os.path.join(_IMAGES_DIR, f"{entry_id}.{ext}")
        if os.path.exists(path):
            return send_file(path)
    return jsonify({"error": "Nicht gefunden"}), 404


@app.route("/api/history/<entry_id>/generate-image", methods=["POST"])
def generate_history_image(entry_id):
    generator = get_generator()
    entry = generator.load_prompt_history(entry_id)
    if not entry:
        return jsonify({"ok": False, "error": "History-Eintrag nicht gefunden"}), 404
    if entry.get("status") != "success":
        return jsonify({"ok": False, "error": "Nur erfolgreiche Prompt-Einträge können gerendert werden"}), 400

    data = request.json or {}
    backend_id = data.get("backend", "comfyui")
    backend = get_image_backend(backend_id)
    if not backend:
        return jsonify({"ok": False, "error": "Unbekanntes Image-Backend"}), 404

    image_request = ImageGenerationRequest(
        positive_prompt=entry.get("positive_prompt", ""),
        negative_prompt=entry.get("negative_prompt", ""),
        model=data.get("model", ""),
        width=int(data.get("width", 1024)),
        height=int(data.get("height", 1024)),
        steps=int(data.get("steps", 25)),
        cfg_scale=float(data.get("cfg_scale", 7.0)),
        seed=int(data.get("seed", -1)),
    )

    try:
        result = backend.generate(image_request)
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502

    ext = result.extension.lower()
    if ext == "jpg":
        ext = "jpeg"
    if ext not in _ALLOWED_EXTS:
        ext = "png"

    os.makedirs(_IMAGES_DIR, exist_ok=True)
    filename = f"{entry_id}.{ext}"
    path = os.path.join(_IMAGES_DIR, filename)
    with open(path, "wb") as f:
        f.write(result.image_bytes)

    updates = {
        "image_path": filename,
        "image_backend": backend_id,
        "image_model": image_request.model,
        "image_generation": result.metadata,
    }
    generator.update_history_entry(entry_id, updates)
    return jsonify({"ok": True, "image_path": filename, "metadata": result.metadata})


# ─── Ollama Host setzen ────────────────────────────────────────────────────

@app.route("/api/ollama/<provider_id>/host", methods=["POST"])
def set_ollama_host(provider_id):
    adapter = get_provider(provider_id)
    if not hasattr(adapter, "set_host"):
        return jsonify({"ok": False, "error": "Provider unterstützt kein Host-Wechsel"}), 400
    host = request.json.get("host", "http://localhost:11434")
    adapter.set_host(host)
    available = adapter.is_available()
    models = adapter.available_models if available else []
    return jsonify({"ok": True, "available": available, "models": models})
