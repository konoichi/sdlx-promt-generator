# SDXL Prompt Generator

Flask-basierter lokaler Prompt-Generator für SDXL Character-Design.
Hexagonale Architektur — LLM-Anbieter einfach erweiterbar.

## Lokaler Start

```bash
# Setup einmalig ausführen
make setup

# App starten
make start
```

Browser öffnen: http://127.0.0.1:5000

Manuell geht es weiterhin so:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

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

---

## Modulare Architektur (Addons)

Die Anwendung verfolgt eine strikte Trennung zwischen Kernfunktionen und optionalen Erweiterungen (z.B. Civitai-Integration, NSFW-Content). Eine detaillierte Übersicht findest du in der [ADDONS.md](ADDONS.md).

---

## Container Deployment

```bash
# Konfiguration anlegen, falls noch nicht vorhanden
make env

# API-Keys und Provider in .env setzen

# Container bauen und starten
make dev
```

App öffnen: http://127.0.0.1:5000

Für Ollama muss `OLLAMA_LOCAL_HOST` in `.env` auf die aus dem Container
erreichbare Adresse zeigen. Beispiele:

```bash
# Ollama im Homelab
OLLAMA_LOCAL_HOST=http://192.168.13.113:11434

# Ollama im lokalen Hermes-Docker-Netzwerk
OLLAMA_LOCAL_HOST=http://hermes-ollama:11434

# Ollama auf demselben Docker-Host
OLLAMA_LOCAL_HOST=http://host.docker.internal:11434
```

Image-Backends können ebenfalls in `.env` konfiguriert werden:

```bash
# Automatic1111 mit --api
AUTOMATIC1111_HOST=http://host.docker.internal:7860

# ComfyUI
COMFYUI_HOST=http://host.docker.internal:8188
```

Automatic1111 muss mit aktivierter API laufen, z.B. mit `--api`. ComfyUI stellt
die benötigten Endpunkte standardmäßig bereit.

In der App:

1. Prompt generieren.
2. Unter `Bildausgabe` Backend, Checkpoint, Größe und Steps/CFG wählen.
3. `Bild generieren` klicken.
4. Das erzeugte Bild wird in `data/images/` gespeichert und am History-Eintrag
   referenziert.

Wenn ComfyUI `OutOfMemory` meldet: kleinere Größe wählen, ein kleineres Modell
nutzen oder andere GPU-Prozesse beenden.

### Make Targets

```bash
make help     # verfügbare Targets anzeigen
make check    # Syntax- und Compose-Check
make build    # Container-Image bauen
make up       # Container starten
make dev      # bauen und starten
make ps       # Status anzeigen
make logs     # Logs verfolgen
make shell    # Shell im Container
make health   # Healthcheck
make down     # stoppen
```

Direkte Docker-Compose-Befehle:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f app
docker compose down
```

Persistente Daten liegen weiterhin lokal in `data/` und werden nach `/app/data`
in den Container gemountet.

Optional einen anderen Host-Port verwenden:

```bash
APP_PORT=8080 docker compose up -d
```
