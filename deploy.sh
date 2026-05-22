#!/usr/bin/env bash
# ============================================================
#  InstantAttend God Mode — GitHub Deploy Script
#  Usage: bash deploy.sh <github_username> <github_token>
#  Or set GITHUB_USER and GITHUB_TOKEN as env vars.
# ============================================================
set -euo pipefail

REPO_NAME="InstantAttend"
GITHUB_USER="${1:-${GITHUB_USER:-BiplabaKrSamal}}"
GITHUB_TOKEN="${2:-${GITHUB_TOKEN:-}}"
BRANCH="godmode"

# ── Colours ──────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*"; exit 1; }

echo -e "${BOLD}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║   🎯 InstantAttend  God Mode Deploy   ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${RESET}"

# ── Prerequisites ─────────────────────────────────────────────
command -v git  >/dev/null || error "git not found. Install git first."
command -v curl >/dev/null || error "curl not found."

[[ -z "$GITHUB_TOKEN" ]] && error "GitHub token required.\n  Usage: bash deploy.sh <username> <token>\n  Or: export GITHUB_TOKEN=<token> && bash deploy.sh"

REMOTE_URL="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

# ── Step 1: Check / Create repo via API ───────────────────────
info "Checking if repo '${REPO_NAME}' exists on GitHub..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  "https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}")

if [[ "$HTTP_STATUS" == "404" ]]; then
  info "Repo not found — creating '${REPO_NAME}' on GitHub..."
  curl -s -X POST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"name\": \"${REPO_NAME}\",
      \"description\": \"🎯 Real-time face recognition attendance system — God Mode Edition\",
      \"homepage\": \"https://${GITHUB_USER}.github.io/${REPO_NAME}\",
      \"private\": false,
      \"has_issues\": true,
      \"has_projects\": false,
      \"has_wiki\": false,
      \"auto_init\": false
    }" \
    "https://api.github.com/user/repos" > /dev/null
  success "Repository created: https://github.com/${GITHUB_USER}/${REPO_NAME}"
  sleep 3
else
  success "Repository found: https://github.com/${GITHUB_USER}/${REPO_NAME}"
fi

# ── Step 2: Enable GitHub Pages (docs/ folder) ────────────────
info "Enabling GitHub Pages from docs/ ..."
curl -s -X POST \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"source": {"branch": "main", "path": "/docs"}}' \
  "https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/pages" > /dev/null 2>&1 || true

# ── Step 3: Git init & push ────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -d ".git" ]]; then
  info "Initialising git repository..."
  git init
  git branch -M main
fi

# Configure git identity if not set
git config user.email 2>/dev/null | grep -q '@' || git config user.email "instantattend@github.com"
git config user.name  2>/dev/null | grep -q '.'  || git config user.name  "InstantAttend Bot"

# Set remote
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE_URL"

info "Staging all files..."
git add -A

# Check if there's anything to commit
if git diff --cached --quiet; then
  warn "Nothing new to commit — repo is already up to date."
else
  git commit -m "🎯 God Mode v2.0 — SQLite + WebSocket + Docker + CI/CD + REST API

Changes:
- Replaced CSV storage with SQLite database
- Added real-time WebSocket updates via Flask-SocketIO
- Full REST API (/api/attendance/today, /api/stats, etc.)
- Export to CSV + Excel (.xlsx)
- Admin panel with user management & attendance history
- Weekly bar chart on dashboard
- Docker + docker-compose for one-command deployment
- GitHub Actions CI/CD (test → pages → docker build)
- GitHub Pages landing page in docs/
- pytest suite covering DB, helpers, and API routes
- Professional README with badges"
fi

info "Pushing to GitHub (branch: main)..."
git push -u origin main --force

success "✅ Pushed to https://github.com/${GITHUB_USER}/${REPO_NAME}"

# ── Step 4: Create 'godmode' branch ───────────────────────────
info "Creating branch '${BRANCH}'..."
git checkout -B "$BRANCH" 2>/dev/null || git checkout "$BRANCH"
git push -u origin "$BRANCH" --force 2>/dev/null || true
git checkout main

# ── Step 5: Add repo topics via API ───────────────────────────
info "Setting repository topics..."
curl -s -X PUT \
  -H "Authorization: token ${GITHUB_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"names": ["python","flask","opencv","face-recognition","attendance-system","machine-learning","sqlite","websocket","docker","github-actions"]}' \
  "https://api.github.com/repos/${GITHUB_USER}/${REPO_NAME}/topics" > /dev/null

success "Topics set."

# ── Summary ───────────────────────────────────────────────────
echo ""
echo -e "${BOLD}${GREEN}═══════════════════════════════════════════${RESET}"
echo -e "${BOLD}  🎯 InstantAttend God Mode is LIVE!${RESET}"
echo -e "${GREEN}═══════════════════════════════════════════${RESET}"
echo ""
echo -e "  📦 Repository  → ${CYAN}https://github.com/${GITHUB_USER}/${REPO_NAME}${RESET}"
echo -e "  🌐 Pages Site  → ${CYAN}https://${GITHUB_USER}.github.io/${REPO_NAME}${RESET}"
echo -e "  ⚙️  Actions     → ${CYAN}https://github.com/${GITHUB_USER}/${REPO_NAME}/actions${RESET}"
echo -e "  🐳 Docker run  → ${CYAN}docker compose up --build${RESET}"
echo ""
echo -e "  Run locally:"
echo -e "  ${YELLOW}pip install -r requirements.txt && python app.py${RESET}"
echo ""
