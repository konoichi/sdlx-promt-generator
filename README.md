# SDXL Prompt Generator

Flask-basierter lokaler Prompt-Generator für SDXL Character-Design.
Hexagonale Architektur — LLM-Anbieter einfach erweiterbar.

## Setup

```bash
# 1. Virtuelle Umgebung erstellen und aktivieren
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
# .venv\Scripts\activate         # Windows

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Konfiguration anlegen
cp .env.example .env
# .env öffnen und ANTHROPIC_API_KEY eintragen

# 4. Starten
python run.py
```

Browser öffnen: http://127.0.0.1:5000

Venv verlassen: `deactivate`

> Die `.venv/`-Ordner nie ins ZIP oder Git packen — sie enthält nur installierte Pakete und ist immer neu generierbar mit `pip install -r requirements.txt`.

---

## Ollama (lokal, kostenlos)

```bash
# Ollama installieren (Mac)
brew install ollama

# Starten
ollama serve

# Modell laden (empfohlen für JSON-Output)
ollama pull llama3.1
# oder
ollama pull mistral

# In der App: Einstellungen → Ollama Host → Verbinden
```

---

## Neuen LLM-Anbieter hinzufügen

1. Neue Datei in `app/adapters/llm/` anlegen (z.B. `openai_adapter.py`)
2. `LLMPort` aus `app.core.ports` implementieren — drei Methoden: `generate()`, `is_available()`, `available_models`
3. In `app/config.py` unter `PROVIDERS` eintragen
4. App neu starten — der neue Anbieter erscheint automatisch in der UI

Beispiel-Vorlage: `app/adapters/llm/ollama_adapter.py`

---

## Projektstruktur

```
app/
├── core/                   # Business Logic — kennt keine Frameworks
│   ├── ports.py            # Interfaces (LLMPort, StoragePort)
│   ├── character.py        # Datenmodell
│   └── prompt_generator.py # Hauptlogik
├── adapters/
│   ├── llm/
│   │   ├── anthropic_adapter.py
│   │   └── ollama_adapter.py
│   └── storage/
│       └── json_storage.py
├── web/
│   ├── app.py              # Flask Routes
│   └── templates/
│       └── index.html
└── config.py               # Dependency Injection
data/                       # Characters & Verlauf (auto-erstellt)
run.py                      # Einstiegspunkt
```

---

## Daten

Characters und Prompt-Verlauf werden in `data/` als JSON gespeichert:
- `data/characters.json`
- `data/prompt_history.json`

Backup: den `data/`-Ordner kopieren.
