#!/bin/bash

# ─────────────────────────────────────────────────────────────
#  SDXL Prompt Generator — Setup
#  Einmalig ausführen: bash setup.sh
# ─────────────────────────────────────────────────────────────

set -e  # Abbruch bei Fehler

BOLD=$(tput bold)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)
RESET=$(tput sgr0)

ok()   { echo "${GREEN}✓${RESET} $1"; }
warn() { echo "${YELLOW}!${RESET} $1"; }
err()  { echo "${RED}✗${RESET} $1"; exit 1; }
step() { echo ""; echo "${BOLD}$1${RESET}"; }

echo ""
echo "${BOLD}SDXL Prompt Generator — Setup${RESET}"
echo "─────────────────────────────────────────"

# ─── Python prüfen ────────────────────────────────────────────
step "1/5  Python prüfen"

if ! command -v python3 &>/dev/null; then
  err "Python 3 nicht gefunden. Bitte installieren: https://python.org"
fi

PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
  err "Python 3.11+ benötigt. Gefunden: $PY_VERSION"
fi

ok "Python $PY_VERSION"

# ─── Virtuelle Umgebung ───────────────────────────────────────
step "2/5  Virtuelle Umgebung"

if [ -d ".venv" ]; then
  warn ".venv existiert bereits — wird übersprungen"
else
  python3 -m venv .venv
  ok ".venv erstellt"
fi

source .venv/bin/activate
ok "Aktiviert (.venv)"

# ─── Abhängigkeiten ───────────────────────────────────────────
step "3/5  Abhängigkeiten installieren"

pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
ok "Pakete installiert"

# ─── .env anlegen ─────────────────────────────────────────────
step "4/5  Konfiguration"

if [ -f ".env" ]; then
  warn ".env existiert bereits — wird nicht überschrieben"
else
  cp .env.example .env
  ok ".env aus .env.example erstellt"
  echo ""
  echo "  ${YELLOW}Bitte jetzt .env öffnen und ANTHROPIC_API_KEY eintragen:${RESET}"
  echo "  ${BOLD}nano .env${RESET}  oder  ${BOLD}code .env${RESET}"
fi

# ─── Datenverzeichnisse anlegen ───────────────────────────────
step "5/5  Datenverzeichnisse"

mkdir -p data/images
ok "data/          (Characters & Prompt-Verlauf)"
ok "data/images/   (hochgeladene Referenzbilder)"

# ─── Fertig ───────────────────────────────────────────────────
echo ""
echo "─────────────────────────────────────────"
echo "${GREEN}${BOLD}Setup abgeschlossen.${RESET}"
echo ""
echo "Starten mit:  ${BOLD}bash start.sh${RESET}"
echo ""
