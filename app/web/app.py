"""
Flask Web App — nur Routing und HTTP.
Keine Business Logic hier. Alles geht durch den PromptGenerator.
"""

from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_file, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
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
from app.core.capabilities import get_unlocked_features, verify_and_unlock
from app.addons import list_active_addons, list_all_installed_addons
from app.core.character import Character
from app.core.ports import ImageGenerationRequest
from app.extensions import db, login_manager
from app.models import User

_IMAGES_DIR = os.path.abspath(os.path.join(os.environ.get("DATA_DIR", "data"), "images"))
_GUIDE_PATH = os.path.abspath("docs/stable-diffusion-leitfaden-v3.md")
_ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp"}

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key-12345")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(os.environ.get('DATA_DIR', 'data'), 'app.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Auth Routes ───────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if User.query.filter_by(email=email).first():
            flash("Email bereits registriert.")
            return redirect(url_for("register"))
        
        # Erster User wird automatisch Admin
        is_first = User.query.count() == 0
        user = User(email=email, is_admin=is_first)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Ungültige Email oder Passwort.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ─── Status ────────────────────────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"ok": True})


@app.route("/guide")
@login_required
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
@login_required
def providers():
    return jsonify(get_providers_status())


@app.route("/api/providers/<provider_id>/models")
@login_required
def provider_models(provider_id):
    adapter = get_provider(provider_id)
    return jsonify({"models": adapter.available_models})


@app.route("/api/image-backends")
@login_required
def image_backends():
    return jsonify(get_image_backends_status())


@app.route("/api/image-backends/<backend_id>/host", methods=["POST"])
@login_required
def set_image_backend_host(backend_id):
    backend = get_image_backend(backend_id)
    if not backend:
        return jsonify({"ok": False, "error": "Unbekanntes Image-Backend"}), 404
    host = request.json.get("host", backend.host)
    backend.set_host(host)
    status = backend.status()
    return jsonify({"ok": True, **status.__dict__})


@app.route("/api/system/status")
@login_required
def system_status():
    user_caps = current_user.get_capabilities()
    return jsonify({
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "is_admin": current_user.is_admin
        },
        "capabilities": user_caps,
        "addons": list_all_installed_addons(user_caps, current_user.is_admin)
    })


@app.route("/api/system/unlock", methods=["POST"])
@login_required
def system_unlock():
    key = request.json.get("key")
    if not key:
        return jsonify({"ok": False, "error": "Lizenzschlüssel fehlt"}), 400
    
    success, message, new_features = verify_license_key(key)
    if success:
        for feature in new_features:
            current_user.add_capability(feature)
        db.session.commit()
        return jsonify({"ok": True, "message": message, "features": current_user.get_capabilities()})
    
    return jsonify({"ok": False, "error": message}), 403


@app.route("/api/addons/model-hub/info")
@login_required
def get_model_hub_info():
    model_name = request.args.get("name")
    model_type = request.args.get("type", "checkpoint")
    if not model_name:
        return jsonify({"ok": False, "error": "Name fehlt"}), 400
    
    from app.addons import get_active_addons_by_type
    from app.core.addon_ports import ModelMetadataProvider
    
    user_caps = current_user.get_capabilities()
    providers = get_active_addons_by_type(ModelMetadataProvider, user_caps, current_user.is_admin)
    if not providers:
        return jsonify({"ok": False, "error": "Model Hub Addon nicht aktiv oder nicht freigeschaltet"}), 403
    
    info = providers[0].get_model_info(model_name, model_type)
    if not info:
        return jsonify({"ok": False, "error": "Modell bei Civitai nicht gefunden"}), 404
        
    return jsonify({"ok": True, "data": info})


# ─── Prompt generieren ─────────────────────────────────────────────────────
@app.route("/api/generate", methods=["POST"])
@login_required
def generate():
    data = request.json
    provider_name = data.pop("provider", "anthropic")
    model = data.pop("model", None)

    # NSFW Gating Check
    if data.get("allow_nsfw"):
        user_caps = current_user.get_capabilities()
        if not is_feature_unlocked("nsfw_content", user_caps, current_user.is_admin):
            return jsonify({"ok": False, "error": "NSFW-Funktion ist für dieses Konto nicht freigeschaltet."}), 403

    generator = get_generator(provider_name)
    try:

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
@login_required
def list_characters():
    generator = get_generator()
    return jsonify(generator.list_characters(current_user.id))


@app.route("/api/characters", methods=["POST"])
@login_required
def save_character():
    data = request.json
    generator = get_generator()
    try:
        character = Character.from_dict(data)
        cid = generator.save_character(character, current_user.id)
        return jsonify({"ok": True, "id": cid})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/characters/<character_id>", methods=["GET"])
@login_required
def load_character(character_id):
    generator = get_generator()
    character = generator.load_character(character_id, current_user.id)
    if character:
        return jsonify(character.to_dict())
    return jsonify({"error": "Nicht gefunden"}), 404


@app.route("/api/characters/<character_id>", methods=["DELETE"])
@login_required
def delete_character(character_id):
    generator = get_generator()
    ok = generator.delete_character(character_id, current_user.id)
    return jsonify({"ok": ok})


# ─── Prompt History ────────────────────────────────────────────────────────

@app.route("/api/history")
@login_required
def list_history():
    character_id = request.args.get("character_id")
    generator = get_generator()
    return jsonify(generator.list_prompt_history(current_user.id, character_id))


@app.route("/api/history/<entry_id>", methods=["DELETE"])
@login_required
def delete_history(entry_id):
    generator = get_generator()
    ok = generator.delete_prompt_history(entry_id, current_user.id)
    return jsonify({"ok": ok})


# ─── History Images ───────────────────────────────────────────────────────

@app.route("/api/history/<entry_id>/image", methods=["POST"])
@login_required
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
    generator.update_history_entry(entry_id, current_user.id, {"image_path": filename})
    return jsonify({"ok": True})


@app.route("/api/history/<entry_id>/image", methods=["GET"])
@login_required
def serve_history_image(entry_id):
    # Verifizierung, dass der User Zugriff hat
    generator = get_generator()
    entry = generator.load_prompt_history(entry_id, current_user.id)
    if not entry:
        return jsonify({"error": "Nicht gefunden"}), 404
        
    for ext in _ALLOWED_EXTS:
        path = os.path.join(_IMAGES_DIR, f"{entry_id}.{ext}")
        if os.path.exists(path):
            return send_file(path)
    return jsonify({"error": "Bilddatei nicht gefunden"}), 404


@app.route("/api/history/<entry_id>/generate-image", methods=["POST"])
@login_required
def generate_history_image(entry_id):
    generator = get_generator()
    entry = generator.load_prompt_history(entry_id, current_user.id)
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
    generator.update_history_entry(entry_id, current_user.id, updates)
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
