#!/bin/bash

# ─────────────────────────────────────────────────────────────
#  SDXL Prompt Generator — Start
#  Starten mit: bash start.sh
# ─────────────────────────────────────────────────────────────

BOLD=$(tput bold)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)
CYAN=$(tput setaf 6)
RESET=$(tput sgr0)

ok()   { echo "${GREEN}✓${RESET} $1"; }
warn() { echo "${YELLOW}!${RESET} $1"; }
err()  { echo "${RED}✗${RESET} $1"; exit 1; }

echo ""
echo "${BOLD}SDXL Prompt Generator${RESET}"
echo "─────────────────────────────────────────"

# ─── Setup-Check ──────────────────────────────────────────────
if [ ! -d ".venv" ]; then
  err ".venv nicht gefunden. Bitte zuerst setup.sh ausführen: bash setup.sh"
fi

if [ ! -f ".env" ]; then
  err ".env nicht gefunden. Bitte zuerst setup.sh ausführen: bash setup.sh"
fi

# ─── venv aktivieren ──────────────────────────────────────────
source .venv/bin/activate
ok "Virtuelle Umgebung aktiv"

# ─── .env laden und prüfen ────────────────────────────────────
set -a; source .env; set +a

if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "sk-ant-..." ]; then
  warn "ANTHROPIC_API_KEY nicht gesetzt — Anthropic nicht verfügbar"
  warn "Eintragen in .env oder Ollama als Anbieter nutzen"
else
  ok "Anthropic API Key gefunden"
fi

# ─── Ollama-Status (optional) ─────────────────────────────────
OLLAMA_HOST="${OLLAMA_LOCAL_HOST:-${OLLAMA_HOST:-http://localhost:11434}}"
if curl -s --max-time 2 "$OLLAMA_HOST/api/tags" &>/dev/null; then
  OLLAMA_MODELS=$(curl -s "$OLLAMA_HOST/api/tags" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); print(', '.join(m['name'] for m in d.get('models',[])))" 2>/dev/null)
  ok "Ollama erreichbar${OLLAMA_MODELS:+ · $OLLAMA_MODELS}"
else
  warn "Ollama nicht erreichbar (optional) · starten mit: ollama serve"
fi

# ─── data/ sicherstellen ──────────────────────────────────────
mkdir -p data/images

# ─── Konfiguration anzeigen ───────────────────────────────────
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-5000}"

echo ""
echo "─────────────────────────────────────────"
echo "  ${CYAN}${BOLD}http://${HOST}:${PORT}${RESET}"
echo "─────────────────────────────────────────"
echo "  Beenden: ${BOLD}Ctrl + C${RESET}"
echo ""

# ─── App starten ──────────────────────────────────────────────

# Browser automatisch öffnen (nach kurzer Verzögerung)
if command -v open &>/dev/null; then          # macOS
  (sleep 1.5 && open "http://${HOST}:${PORT}") &
elif command -v xdg-open &>/dev/null; then    # Linux
  (sleep 1.5 && xdg-open "http://${HOST}:${PORT}") &
fi

python run.py
