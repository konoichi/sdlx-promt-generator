# SDXL Prompt Generator — Technische Dokumentation

**Für:** Externer Entwickler  
**Stand:** Aktueller Entwicklungsstand  
**Repo:** https://github.com/konoichi/sdlx-promt-generator  
**Zweck:** Lokale Flask-Webanwendung zur Generierung strukturierter SDXL-Prompts für Character-Design, mit Anbindung an verschiedene LLM-Anbieter.

---

## 1. Architektur-Überblick

Die Anwendung folgt einer **hexagonalen Architektur** (Ports & Adapters). Das bedeutet:

- Der **Core** (Business Logic) kennt keine Frameworks, keine Datenbanken, keine LLM-APIs — nur abstrakte Interfaces (Ports).
- **Adapter** implementieren diese Interfaces für konkrete Anbieter (Anthropic, Ollama) und Storage (JSON-Dateien).
- Die **Web-Schicht** (Flask) ist nur Routing — keine Business Logic.

Das Ziel dieser Trennung: Neuen LLM-Anbieter hinzufügen = eine neue Datei schreiben, eine Zeile in der Config ändern. Nichts anderes anfassen.

```
┌─────────────────────────────────────────────────────────────┐
│  Web (Flask)          app/web/app.py                        │
│  → nur HTTP-Routing, keine Logik                            │
├─────────────────────────────────────────────────────────────┤
│  Core                 app/core/                             │
│  → Business Logic, kennt nur Ports                          │
│  → ports.py, character.py, prompt_generator.py              │
├────────────────────┬────────────────────────────────────────┤
│  LLM-Adapter       │  Storage-Adapter                       │
│  app/adapters/llm/ │  app/adapters/storage/                 │
│  → anthropic       │  → json_storage                        │
│  → ollama          │                                        │
└────────────────────┴────────────────────────────────────────┘
```

---

## 2. Projektstruktur

```
sdxl_prompt_app/
├── run.py                          # Einstiegspunkt: python run.py
├── setup.sh                        # Einmaliges Setup (venv, pip, .env)
├── start.sh                        # App starten (venv aktivieren, checks, launch)
├── github_init.sh                  # Git init + push zum Repo
├── requirements.txt                # flask, anthropic, python-dotenv, requests
├── .env.example                    # Vorlage für Konfiguration
├── .gitignore                      # .venv/, data/, .env ausgeschlossen
├── README.md
└── app/
    ├── __init__.py
    ├── config.py                   # Dependency Injection, Provider-Registry
    ├── core/
    │   ├── ports.py                # Abstrakte Interfaces (LLMPort, StoragePort)
    │   ├── character.py            # Datenmodell + Checkpoint/Tool-Katalog
    │   └── prompt_generator.py     # Business Logic + System-Prompt
    ├── adapters/
    │   ├── llm/
    │   │   ├── anthropic_adapter.py
    │   │   └── ollama_adapter.py
    │   └── storage/
    │       └── json_storage.py
    └── web/
        ├── app.py                  # Flask Routes (REST API)
        └── templates/
            └── index.html          # Komplettes Single-Page UI (~990 Zeilen)
```

---

## 3. Dateien im Detail

### 3.1 `app/core/ports.py` — Interfaces

Zwei abstrakte Basisklassen:

**`LLMPort`** — muss von jedem LLM-Adapter implementiert werden:
```python
class LLMPort(ABC):
    def generate(self, system_prompt: str, user_message: str) -> LLMResponse
    def is_available(self) -> bool
    @property name(self) -> str
    @property available_models(self) -> list[str]
```

**`StoragePort`** — muss vom Storage-Adapter implementiert werden:
```python
class StoragePort(ABC):
    def save_character(self, character: dict) -> str          # gibt ID zurück
    def load_character(self, character_id: str) -> dict|None
    def list_characters(self) -> list[dict]
    def delete_character(self, character_id: str) -> bool
    def save_prompt_history(self, entry: dict) -> str
    def list_prompt_history(self, character_id: str|None) -> list[dict]
    def delete_prompt_history(self, entry_id: str) -> bool
```

**`LLMResponse`** — Dataclass für LLM-Antworten:
```python
@dataclass
class LLMResponse:
    content: str    # Rohtext der Antwort (erwartet: JSON-String)
    model: str      # verwendetes Modell
    provider: str   # "anthropic" | "ollama"
```

---

### 3.2 `app/core/character.py` — Datenmodell

**`Character`** — Python Dataclass mit allen Character-Attributen:

```python
@dataclass
class Character:
    # Pflichtfelder (ohne Default)
    name: str
    gender: str          # "woman" | "man" | "person"
    age: str             # "early 30s" etc.
    ethnicity: str       # "European features" etc.
    eyes: str
    nose: str
    jaw: str

    # Optionale Felder (mit Default "")
    face_special: str = ""
    hair_color: str = ""
    hair_length: str = ""
    hair_style: str = ""
    height: str = ""
    build: str = ""
    shoulders: str = ""
    skin: str = ""
    body_marks: list[str] = []    # Mehrfachauswahl

    # Kontext
    expression: str = "neutral expression, lips slightly parted"
    lighting: str = "soft studio lighting, light grey background"

    # Tool & Modell — NEU
    sd_tool: str = "ComfyUI"
    sd_checkpoint: str = "Juggernaut XL"
    sd_checkpoint_custom: str = ""   # wenn "custom" im Dropdown

    # Meta (auto-generiert)
    id: str = uuid4()
    created_at: str = datetime.now().isoformat()
    updated_at: str = datetime.now().isoformat()
    notes: str = ""
```

**Wichtige Methoden:**

- `to_dict()` — serialisiert zu dict (für Storage und API-Antworten)
- `from_dict(data)` — deserialisiert, filtert unbekannte Felder raus
- `effective_checkpoint` — Property: gibt `sd_checkpoint_custom` zurück wenn gesetzt, sonst `sd_checkpoint`
- `checkpoint_info` — Property: gibt Beschreibungstext aus `SDXL_CHECKPOINTS` dict zurück
- `tool_info` — Property: gibt Beschreibungstext aus `SD_TOOLS` dict zurück
- `to_prompt_context()` — formatiert den Character als lesbaren Text für die LLM User-Message

**Zwei Katalog-Dicts im Modul (kein ORM, kein DB):**

```python
SDXL_CHECKPOINTS = {
    "Juggernaut XL": "Sehr stabile Gesichter, photorealistisch, gute Hauttöne",
    "RealVisXL": "...",
    # 8 Einträge gesamt
}

SD_TOOLS = {
    "ComfyUI": "Gewichtung: (token:1.2), präzise Node-basierte Pipeline",
    "Automatic1111": "...",
    # 5 Einträge gesamt
}
```

---

### 3.3 `app/core/prompt_generator.py` — Business Logic

**Zwei Konstanten:**

```python
SYSTEM_PROMPT = """..."""   # ~5300 Zeichen, enthält:
                             # - Rolle des LLM als SDXL Prompt Engineer
                             # - CLIP-Tokenisierung Erklärung
                             # - Gewichtungsregeln (1.1–1.5)
                             # - Konsistenz-Anker Hierarchie (Augen > Knochen > Nase > ...)
                             # - Tool-spezifische Syntax (ComfyUI vs A1111 vs InvokeAI vs Fooocus)
                             # - Checkpoint-spezifische Token-Empfehlungen
                             # - Negativ-Prompt Best Practices
                             # - Ausgabeformat: JSON mit 4 Zonen + negative

USER_TEMPLATE = """Erstelle einen SDXL Portrait-Prompt für folgenden Character:
{context}
Wende dein SDXL-Fachwissen an: ..."""
```

**`PromptGenerator` Klasse** — erhält LLMPort und StoragePort per Dependency Injection:

```python
class PromptGenerator:
    def __init__(self, llm: LLMPort, storage: StoragePort)

    def generate(self, character: Character) -> dict:
        # 1. character.to_prompt_context() aufrufen
        # 2. USER_TEMPLATE befüllen
        # 3. llm.generate(SYSTEM_PROMPT, user_msg) aufrufen
        # 4. JSON aus Antwort parsen (Markdown-Backticks entfernen falls vorhanden)
        # 5. positive_prompt aus 4 Zonen zusammenbauen
        # 6. entry-Dict bauen mit id, character_id, provider, model, result, ...
        # 7. storage.save_prompt_history(entry) aufrufen
        # 8. entry zurückgeben
```

**Erwartetes JSON vom LLM:**
```json
{
  "zone1": {
    "prompt": "RAW photo, (photorealistic:1.3), ...",
    "tokens": [
      {"name": "RAW photo", "explanation": "Erklärt warum auf Deutsch"}
    ]
  },
  "zone2_face": { "prompt": "...", "tokens": [...] },
  "zone3_body":  { "prompt": "...", "tokens": [...] },
  "zone4_context": { "prompt": "...", "tokens": [...] },
  "negative": "deformed, disfigured, ..."
}
```

---

### 3.4 `app/adapters/llm/anthropic_adapter.py`

Implementiert `LLMPort` für die Anthropic API.

- API Key aus Konstruktor oder `ANTHROPIC_API_KEY` Env-Variable
- Nutzt das offizielle `anthropic` Python SDK
- `available_models`: hardcodierte Liste (claude-sonnet-4, claude-opus-4, claude-haiku-4-5)
- `is_available()`: gibt `True` zurück wenn API Key gesetzt ist
- `set_model(model)`: wechselt das aktive Modell zur Laufzeit

```python
def generate(self, system_prompt, user_message) -> LLMResponse:
    client = anthropic.Anthropic(api_key=self._api_key)
    message = client.messages.create(
        model=self._model,
        max_tokens=1200,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return LLMResponse(content=message.content[0].text, model=..., provider="anthropic")
```

---

### 3.5 `app/adapters/llm/ollama_adapter.py`

Implementiert `LLMPort` für lokale Ollama-Instanzen.

- Host aus Konstruktor oder Default `http://localhost:11434`
- Kommuniziert über HTTP REST (kein SDK) — `requests` Bibliothek
- `available_models()`: fragt `GET /api/tags` am Ollama-Server ab — dynamisch
- `is_available()`: `GET /api/tags` mit 3s Timeout, gibt True bei Status 200
- `set_host(host)`: kann zur Laufzeit geändert werden (für Settings-Tab im UI)
- Temperature hardcodiert auf 0.3 für konsistente JSON-Ausgabe
- Timeout 120s (lokale Modelle können langsam sein)

```python
def generate(self, system_prompt, user_message) -> LLMResponse:
    payload = {
        "model": self._model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1200}
    }
    res = requests.post(f"{self._host}/api/chat", json=payload, timeout=120)
    return LLMResponse(content=res.json()["message"]["content"], ...)
```

---

### 3.6 `app/adapters/storage/json_storage.py`

Implementiert `StoragePort` mit zwei JSON-Dateien:

- `data/characters.json` — Liste aller Characters
- `data/prompt_history.json` — Liste aller generierten Prompts

Beide Dateien werden beim Start auto-erstellt wenn nicht vorhanden.

**Verhalten:**
- `save_character()`: Update wenn ID bereits existiert, Insert sonst. Setzt `updated_at`.
- `list_characters()`: Sortiert nach `updated_at` absteigend (neueste zuerst)
- `list_prompt_history(character_id=None)`: Optional nach Character filtern, sortiert nach `created_at` absteigend
- Kein Locking, kein Transaktions-Handling — Single-User-App, reicht aus

---

### 3.7 `app/config.py` — Dependency Injection

Zentrale Stelle wo alle Adapter instanziiert und zusammengesteckt werden.

```python
# Einmalig instanziiert
storage = JsonStorageAdapter(data_dir=DATA_DIR)
anthropic_adapter = AnthropicAdapter(api_key=..., model=...)
ollama_adapter = OllamaAdapter(host=..., model=...)

# Provider-Registry — hier neuen Anbieter eintragen
PROVIDERS = {
    "anthropic": anthropic_adapter,
    "ollama": ollama_adapter,
}

def get_generator(provider_name=None) -> PromptGenerator:
    provider = PROVIDERS.get(provider_name or DEFAULT_PROVIDER)
    return PromptGenerator(llm=provider, storage=storage)

def get_providers_status() -> list[dict]:
    # gibt id, name, available, models für alle Provider zurück
```

---

### 3.8 `app/web/app.py` — Flask REST API

Nur Routing. Keine Business Logic. Alle Endpoints delegieren sofort an `get_generator()`.

| Method | Endpoint | Beschreibung |
|---|---|---|
| GET | `/` | Liefert index.html |
| GET | `/api/providers` | Alle Provider mit Status und Modellen |
| GET | `/api/providers/<id>/models` | Modelle eines Providers |
| POST | `/api/generate` | Prompt generieren (Body: Character-Dict + provider + model) |
| GET | `/api/characters` | Alle gespeicherten Characters |
| POST | `/api/characters` | Character speichern/updaten |
| GET | `/api/characters/<id>` | Einzelnen Character laden |
| DELETE | `/api/characters/<id>` | Character löschen |
| GET | `/api/history` | Prompt-Verlauf (optional: ?character_id=...) |
| DELETE | `/api/history/<id>` | Verlauf-Eintrag löschen |
| POST | `/api/ollama/host` | Ollama Host zur Laufzeit ändern |

**`POST /api/generate` erwartet:**
```json
{
  "name": "Lyra",
  "gender": "woman",
  "age": "early 30s",
  "ethnicity": "Nordic features",
  "eyes": "ice blue eyes",
  "nose": "straight nose",
  "jaw": "defined cheekbones, sharp jawline",
  "hair_color": "platinum blonde hair",
  "hair_length": "long hair",
  "hair_style": "loose and natural",
  "height": "tall, long limbs",
  "build": "lean, athletic build",
  "shoulders": "",
  "skin": "fair skin",
  "body_marks": ["tattoo sleeve on left arm"],
  "expression": "neutral expression, lips slightly parted",
  "lighting": "soft studio lighting, light grey background",
  "sd_tool": "ComfyUI",
  "sd_checkpoint": "Juggernaut XL",
  "sd_checkpoint_custom": "",
  "notes": "",
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514"
}
```

`provider` und `model` werden vor der Character-Erstellung aus dem Dict entfernt (`data.pop()`).

---

### 3.9 `app/web/templates/index.html` — Frontend (~990 Zeilen)

Single-Page-Application. Kein Frontend-Framework, kein Build-Step — reines HTML/CSS/JS.

**Layout:** CSS Grid, zwei Spalten:
- Linke Sidebar (260px): Character-Liste, Neu-Button
- Rechts: Tab-Navigation mit drei Tabs

**Drei Tabs:**
1. **Generator** — das Hauptformular + Ergebnis-Anzeige
2. **Verlauf** — alle generierten Prompts, filterbar nach Character
3. **Einstellungen** — Ollama-Host konfigurieren, Hinweise zu API-Keys

**Formular-Abschnitte (in dieser Reihenfolge):**
1. LLM Provider-Bar (Anbieter + Modell, dynamisch geladen)
2. Character Name (Freitext)
3. **Stable Diffusion Setup** (NEU): Tool-Dropdown + Checkpoint-Dropdown + Custom-Feld + Hint-Text
4. Basis (Geschlecht, Alter)
5. Ethnizität (Tag-Auswahl, Single-Select)
6. Gesicht (4 Dropdowns: Augen, Nase, Kiefer, Besonderes)
7. Haare (3 Dropdowns: Farbe, Länge, Styling)
8. Körperbau (4 Dropdowns: Statur, Typ, Schultern, Hautton)
9. Körpermerkmale (Tag-Auswahl, Multi-Select)
10. Mimik (Tag-Auswahl, Single-Select)
11. Lighting (Tag-Auswahl, Single-Select)
12. Notizen (Freitext, nicht Teil des Prompts)

**Ergebnis-Anzeige (unterhalb des Formulars):**
- 4 Zone-Cards (Zone 1–4) mit Prompt-Text + Token-Erklärungen
- Negativ-Prompt Card
- 4 Copy-Buttons: Alles / Nur Positiv / Nur Negativ / Phase 1 (ohne Zone 3)

**Wichtige JS-Funktionen:**
- `buildSingle(id, opts, getter, setter)` — rendert Single-Select Tag-Reihe
- `buildMulti(id, opts, set)` — rendert Multi-Select Tag-Reihe
- `getFormData()` — sammelt alle Formularwerte inkl. sd_tool, sd_checkpoint
- `fillForm(char)` — befüllt Formular aus Character-Dict (beim Laden)
- `generate()` — POST /api/generate, rendert Ergebnis
- `saveCharacter()` — POST /api/characters
- `loadCharacters()` — GET /api/characters, rendert Sidebar
- `loadHistory()` — GET /api/history, rendert Verlauf-Tab
- `onCheckpointChange()` — zeigt/versteckt Custom-Feld, aktualisiert Hint
- `updateCheckpointHint()` — liest `checkpointHints` Dict, zeigt Hinweis-Text

**State-Variablen (global in JS):**
```javascript
let selEthnicity = 'European features';   // Single-Select
let selExpression = '...';                // Single-Select
let selLighting = '...';                  // Single-Select
let selBodyMarks = new Set();             // Multi-Select
let lastResult = null;                    // letztes Generierungs-Ergebnis (für Copy)
let currentCharId = null;                 // aktuell geladener Character
```

---

## 4. Datenfluss: Prompt generieren

```
User klickt "Prompt generieren"
    ↓
getFormData() → JS-Dict mit allen Formularwerten
    ↓
POST /api/generate (JSON-Body)
    ↓
Flask: data.pop("provider"), data.pop("model")
Flask: Character.from_dict(data)
Flask: generator.generate(character)
    ↓
PromptGenerator.generate():
    character.to_prompt_context() → lesbarer Text
    USER_TEMPLATE.format(context=...) → User-Message
    llm.generate(SYSTEM_PROMPT, user_message) → LLMResponse
    json.loads(response.content) → result-Dict
    positive = zone1 + zone2_face + zone3_body + zone4_context
    storage.save_prompt_history(entry)
    return entry
    ↓
Flask: jsonify({"ok": True, "data": entry})
    ↓
JS: renderResult(data.data)
    → renderZone() für jede Zone
    → Token-Erklärungen einblenden
    → result-Section sichtbar machen
```

---

## 5. Datenfluss: Neuen LLM-Anbieter hinzufügen

Das ist die zentrale Erweiterbarkeit der hexagonalen Architektur:

1. Neue Datei: `app/adapters/llm/openai_adapter.py`
2. Klasse `OpenAIAdapter(LLMPort)` implementieren — drei Methoden: `generate()`, `is_available()`, `available_models`
3. In `app/config.py`:
   ```python
   from app.adapters.llm.openai_adapter import OpenAIAdapter
   openai_adapter = OpenAIAdapter(api_key=os.getenv("OPENAI_API_KEY"))
   PROVIDERS["openai"] = openai_adapter
   ```
4. In `.env.example`: `OPENAI_API_KEY=...` ergänzen
5. App neu starten — Provider erscheint automatisch im UI-Dropdown

Keine anderen Dateien anfassen.

---

## 6. Konfiguration (.env)

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1
DEFAULT_PROVIDER=anthropic
DATA_DIR=data
HOST=127.0.0.1
PORT=5000
DEBUG=false
```

---

## 7. Dependencies

```
flask>=3.0.0          # Web-Framework
anthropic>=0.40.0     # Anthropic SDK
python-dotenv>=1.0.0  # .env laden
requests>=2.31.0      # Ollama HTTP-Kommunikation
```

Python 3.11+ erforderlich (wegen `str | None` Union-Syntax ohne `from __future__`).

---

## 8. Was noch fehlt / nächste Schritte

- **Keine Authentifizierung** — reine Single-User-Lokal-App, kein Login
- **Kein SQLite** — JSON-Storage reicht für Single-User, bei Mehrbenutzerbetrieb ersetzen (StoragePort implementieren)
- **Kein Rate-Limiting** — API-Calls gehen direkt durch
- **Phase 2** (geplant): IPAdapter FaceID Workflow-Generator, ControlNet-Einstellungen, Ganzkörper-Prompt-Erweiterung
- **LoRA-Training** (geplant): Character-Set-Verwaltung, Export für Kohya/LoRA-Trainer
