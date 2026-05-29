#!/bin/bash

# ─────────────────────────────────────────────────────────────
#  SDXL Prompt Generator — GitHub Init & Push
#  Einmalig ausführen um das Repo zu befüllen: bash github_init.sh
# ─────────────────────────────────────────────────────────────

set -e

BOLD=$(tput bold)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)
RESET=$(tput sgr0)

ok()   { echo "${GREEN}✓${RESET} $1"; }
warn() { echo "${YELLOW}!${RESET} $1"; }
err()  { echo "${RED}✗${RESET} $1"; exit 1; }
step() { echo ""; echo "${BOLD}$1${RESET}"; }

REPO_URL="https://github.com/konoichi/sdlx-promt-generator.git"

echo ""
echo "${BOLD}SDXL Prompt Generator — GitHub Init${RESET}"
echo "─────────────────────────────────────────"
echo "  Repo: $REPO_URL"
echo ""

# ─── Git prüfen ───────────────────────────────────────────────
step "1/4  Git prüfen"

if ! command -v git &>/dev/null; then
  err "Git nicht gefunden. Bitte installieren: https://git-scm.com"
fi
ok "Git $(git --version | awk '{print $3}')"

# ─── Git User prüfen ──────────────────────────────────────────
GIT_USER=$(git config --global user.name 2>/dev/null || echo "")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "")

if [ -z "$GIT_USER" ] || [ -z "$GIT_EMAIL" ]; then
  echo ""
  warn "Git-Identität nicht konfiguriert."
  read -p "  Dein Name für Git-Commits: " GIT_USER
  read -p "  Deine E-Mail für Git-Commits: " GIT_EMAIL
  git config --global user.name "$GIT_USER"
  git config --global user.email "$GIT_EMAIL"
  ok "Git-Identität gesetzt: $GIT_USER <$GIT_EMAIL>"
else
  ok "Git-Identität: $GIT_USER <$GIT_EMAIL>"
fi

# ─── .gitignore sicherstellen ─────────────────────────────────
step "2/4  .gitignore prüfen"

if [ ! -f ".gitignore" ]; then
  cat > .gitignore << 'EOF'
.venv/
venv/
__pycache__/
*.pyc
.env
data/
*.zip
.DS_Store
EOF
  ok ".gitignore erstellt"
else
  ok ".gitignore vorhanden"
fi

# .env niemals commiten — sicherheitshalber prüfen
if git ls-files --error-unmatch .env &>/dev/null 2>&1; then
  warn ".env ist bereits getrackt! Wird aus Git entfernt (Datei bleibt lokal)."
  git rm --cached .env
fi

# ─── Git Repo initialisieren ──────────────────────────────────
step "3/4  Git Repository"

if [ -d ".git" ]; then
  warn "Git-Repo existiert bereits — überspringe git init"
else
  git init
  ok "Git initialisiert"
fi

# Remote setzen (überschreiben falls schon vorhanden)
if git remote | grep -q "^origin$"; then
  git remote set-url origin "$REPO_URL"
  warn "Remote 'origin' aktualisiert"
else
  git remote add origin "$REPO_URL"
  ok "Remote 'origin' gesetzt"
fi

# ─── Commit & Push ────────────────────────────────────────────
step "4/4  Commit & Push"

git add .
git status --short

echo ""
read -p "${BOLD}Alles korrekt? Push zu GitHub? (j/N): ${RESET}" CONFIRM
if [[ ! "$CONFIRM" =~ ^[jJyY]$ ]]; then
  echo "Abgebrochen."
  exit 0
fi

# Branch auf main setzen
git checkout -b main 2>/dev/null || git checkout main

git commit -m "Initial commit: SDXL Prompt Generator

- Hexagonale Architektur (Ports & Adapters)
- Anthropic + Ollama Adapter
- Flask Web-UI mit Character-Verwaltung und Prompt-Verlauf
- JSON Storage
- setup.sh + start.sh"

echo ""
echo "Pushe zu GitHub..."
echo "(GitHub fragt ggf. nach Benutzername + Personal Access Token)"
echo ""

git push -u origin main

# ─── Fertig ───────────────────────────────────────────────────
echo ""
echo "─────────────────────────────────────────"
echo "${GREEN}${BOLD}Erfolgreich gepusht!${RESET}"
echo ""
echo "  ${BOLD}https://github.com/konoichi/sdlx-promt-generator${RESET}"
echo ""
echo "Nächste Pushes: ${BOLD}git add . && git commit -m '...' && git push${RESET}"
echo ""
