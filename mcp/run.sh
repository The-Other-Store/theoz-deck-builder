#!/usr/bin/env bash
# Lanceur du serveur MCP theoz-deck-builder.
#
# Objectif : demarrer le serveur meme sur un poste aux droits limites, sans sudo.
# Strategie en cascade (toute la sortie de setup va sur stderr : stdout est reserve
# au protocole MCP JSON-RPC de server.py) :
#   1. venv local au plugin deja pret (deps presentes)  -> demarre
#   2. construire le venv local + installer les deps (user-scoped, sans admin)
#   3. repli : python systeme s'il a deja mcp/pptx/PIL
#   4. echec -> message clair : pip install --user, ou mode distant (API AWS)
set -uo pipefail

ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
VENV="$ROOT/.venv"
REQ="$ROOT/engine/requirements.txt"
SERVER="$ROOT/mcp/server.py"
log() { echo "[theoz-mcp] $*" >&2; }

has_deps() { "$1" -c 'import mcp, pptx, PIL' >/dev/null 2>&1; }

pick_python() {
  for p in python3.12 python3.11 python3; do
    command -v "$p" >/dev/null 2>&1 || continue
    if "$p" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 11) else 1)' 2>/dev/null; then
      echo "$p"; return 0
    fi
  done
  return 1
}

# 1. venv deja operationnel
if [ -x "$VENV/bin/python" ] && has_deps "$VENV/bin/python"; then
  exec "$VENV/bin/python" "$SERVER"
fi

# 2. construire le venv local + installer les deps (aucun droit admin requis)
if PY="$(pick_python)"; then
  log "preparation du venv local ($PY) ..."
  if "$PY" -m venv "$VENV" >&2 2>&1 \
     && "$VENV/bin/python" -m pip install -q --upgrade pip >&2 2>&1 \
     && "$VENV/bin/python" -m pip install -q mcp -r "$REQ" >&2 2>&1 \
     && has_deps "$VENV/bin/python"; then
    log "venv pret."
    exec "$VENV/bin/python" "$SERVER"
  fi
  log "echec de la preparation du venv (droits limites ou PyPI injoignable ?)."
else
  log "aucun Python 3.11+ trouve."
fi

# 3. repli : python systeme qui aurait deja les deps
for p in python3.12 python3.11 python3; do
  command -v "$p" >/dev/null 2>&1 || continue
  if has_deps "$p"; then
    log "repli sur '$p' (deps systeme deja presentes)."
    exec "$p" "$SERVER"
  fi
done

# 4. echec : guider l'utilisateur
log "ERREUR : impossible de demarrer le serveur MCP local."
log "  Installer les deps (sans admin) dans le Python du client :"
log "    pip install --user mcp python-pptx Pillow"
log "  Prerequis : Python >= 3.11 et un acces reseau a PyPI au premier demarrage."
exit 1
