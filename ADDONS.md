# SDXL Prompt App - Addon Roadmap

Dieses Dokument beschreibt die modulare Architektur der Anwendung. Das Ziel ist eine strikte Trennung zwischen der **Basis-Version** (stateless Prompt-Generator) und optionalen **Premium-Erweiterungen**.

## Basis-Version (Base)
Die Basis-Version ist für alle Nutzer kostenlos und bietet:
- Strukturierte Prompt-Generierung (4-Zonen-Modell)
- Unterstützung für SDXL, Pony V6 und Illustrious XL
- Tool-spezifische Gewichtungs-Syntax (ComfyUI, A1111, InvokeAI)
- Kleidungs- und Umgebungs-Beschreibungen (SFW)

## Erweiterungen (Addons)

### 1. Model Metadata Hub (`premium_model_hub`)
- **Status:** Implementiert ✅
- **Funktion:** Holt Triggerwords und empfohlene Einstellungen direkt von Civitai.
- **Freischaltung:** Erfordert Addon-Modul und gültigen Key.

### 2. NSFW Expansion (`nsfw_content`)
- **Status:** In Planung 🛠️
- **Funktion:** 
    - Schaltet anatomische Details frei (Oberweite, Schambehaarung).
    - Ermöglicht dem LLM die Nutzung von NSFW-Tags (`rating_explicit`).
    - Fügt "Nude" und "Lingerie" zu den Presets hinzu.

### 3. Character Vault (`char_management`)
- **Status:** In Planung 🛠️ (aktuell noch im Core)
- **Funktion:** 
    - Persistente Speicherung von Charakter-Profilen.
    - Vollständige History mit Snapshots der Einstellungen.
    - Charakter-Sheet-Ansicht.

### 4. Image Generation Integration (`image_generation`)
- **Status:** In Planung 🛠️ (aktuell noch im Core)
- **Funktion:** 
    - Direkte Anbindung an Automatic1111 und ComfyUI.
    - Bild-Vorschau in der History.
    - In-App Rendering-Kontrolle.

## Lizenz- & Freischalt-System (Mock-Server)
Die Freischaltung erfolgt über das "Addon & Erweiterungen"-Menü in den Einstellungen. Aktuell unterstützte Test-Keys:
- `BETA-TESTER`: Schaltet den Model Hub frei.
- `NSFW-PASS`: Schaltet die NSFW-Erweiterungen frei.
- `CREATOR-PRO`: Schaltet Charakter-Management und Bildgenerierung frei.
- `ULTIMATE`: Schaltet alle aktuellen und zukünftigen Funktionen frei.
