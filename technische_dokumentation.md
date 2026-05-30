# SDXL Prompt Generator — Technische Dokumentation

**Zweck:** SaaS-ready Webanwendung zur Generierung strukturierter SDXL-Prompts mit Multi-User-Support, Addon-System und integrierter Bildverarbeitung.

---

## 1. Architektur-Überblick

Die Anwendung nutzt eine **hexagonale Architektur** (Ports & Adapters), erweitert um ein **SaaS-Layer** für Benutzerverwaltung und ein **Addon-System** für modulare Features.

### Schichtenmodell:
1.  **Web-Layer (Flask):** Authentifizierung, Session-Management, REST-API Routing.
2.  **Auth & Persistence (SQLAlchemy):** Benutzerverwaltung und Capability-Gating.
3.  **Core (Business Logic):** Prompt-Generierung, 4-Zonen-Modell, Charakter-Logik.
4.  **Adapters:** 
    *   `LLMPort`: Anthropic, Ollama.
    *   `StoragePort`: JSON-basiert mit User-Isolation.
    *   `ImageBackendPort`: Automatic1111, ComfyUI.
5.  **Addons:** Optionale Module (Civitai-Hub, NSFW-Expansion).

---

## 2. Projektstruktur

```
app/
├── core/
│   ├── ports.py             # Interfaces (StoragePort, LLMPort, etc.)
│   ├── character.py         # Datenmodell
│   ├── prompt_generator.py  # Generierungs-Logik
│   └── capabilities.py      # Feature-Gating (Admin/User)
├── adapters/
│   ├── llm/                 # Anthropic, Ollama
│   ├── image/               # A1111, ComfyUI
│   └── storage/             # JSON Storage mit User-ID Mapping
├── addons/
│   ├── __init__.py          # Plugin Registry
│   ├── model_hub/           # Civitai Integration
│   └── nsfw_expansion/      # NSFW Gating & Tags
├── web/
│   ├── app.py               # Flask REST API & Auth-Routes
│   └── templates/           # Jinja2 Templates (Index, Login, Register)
├── models.py                # Datenbank-Modelle (User)
├── extensions.py            # Flask Extensions (DB, LoginManager)
└── config.py                # Dependency Injection
```

---

## 3. Kern-Features (SaaS & Multi-User)

### 3.1 Authentifizierung & Sicherheit
- **Flask-Login:** Verwalten der Benutzersitzungen.
- **Werkzeug Security:** PBKDF2-Hashing für Passwörter.
- **Admin-System:** Der erste registrierte Nutzer erhält automatisch `is_admin=True` und damit Vollzugriff auf alle Features.

### 3.2 Data Isolation
Jeder Datensatz (Charakter, History) ist fest an eine `user_id` gebunden. Der `StoragePort` erzwingt die Übergabe der ID bei jeder Operation:
```python
def save_character(self, character: dict, user_id: str) -> str:
```

### 3.3 Addon & Capability System
Features können über **Feature-Keys** gesperrt oder freigeschaltet werden.
- **Registry:** Addons registrieren sich in `app/addons/__init__.py`.
- **Gating:** Das UI und das Backend prüfen `current_user.get_capabilities()`.
- **Unlock:** Nutzer können Keys (Mock-Keys: `NSFW-PASS`, `ULTIMATE`) eingeben, um Features permanent freizuschalten.

### 3.4 Profil-System & Ranking
- **Usernames:** Eindeutige Namen für Profile.
- **Member Ranking:** Dynamische Berechnung basierend auf Prompt-Anzahl:
    - 🥉 **Novice** (0-10)
    - 🥈 **Apprentice** (11-50)
    - 🥇 **Prompt Crafter** (51-200)
    - 💎 **Master** (200+)
- **Avatar-Processing:** Uploads werden via **Pillow** verarbeitet:
    - Center-Crop (1:1)
    - Resize auf 256x256 Pixel
    - Format-Konvertierung zu WebP (85% Qualität)

---

## 4. Datenfluss: Prompt-Generierung

1.  **Request:** Frontend sendet `POST /api/generate` inkl. User-Session.
2.  **Auth-Check:** Flask prüft Login und NSFW-Berechtigung (falls angefordert).
3.  **Core-Call:** `PromptGenerator.generate_stream(character, current_user.id)` wird aufgerufen.
4.  **LLM-Response:** Das LLM liefert JSON (4 Zonen).
5.  **Storage:** Das Ergebnis wird inkl. User-Snapshot und `user_id` im JSON-Storage gespeichert.
6.  **Response:** Frontend erhält SSE-Events mit Status, Thinking-Process und Ergebnis.

---

## 5. Konfiguration & Deployment

### Umgebungsvariablen (.env)
- `SECRET_KEY`: Für Flask Sessions.
- `DATA_DIR`: Pfad für SQLite DB, Avatars und JSON-Daten.
- `UNLOCKED_FEATURES`: Globaler Override für Entwickler (z.B. `all`).

### Container
Das Projekt ist vollständig dockerisiert. Persistente Daten liegen im Volume `/app/data`.

---

## 6. Abhängigkeiten

- **Backend:** `flask`, `flask-sqlalchemy`, `flask-login`, `gunicorn`, `requests`.
- **LLM:** `anthropic`, `ollama` (via API).
- **Processing:** `Pillow` (Bildverarbeitung).
- **Frontend:** Reines HTML/CSS/JS (Syne Font, FontAwesome Icons).
