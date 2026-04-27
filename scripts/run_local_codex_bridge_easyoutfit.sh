#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${EASYOUTFIT_LOCAL_CODEX_BRIDGE_PYTHON:-$ROOT/backend/.venv311/bin/python}"
API_BASE_DEFAULT="https://closetgptrenew-production.up.railway.app/api/codex-jobs"
SECRET_ENV_FILE="${EASYOUTFIT_LOCAL_CODEX_BRIDGE_ENV_FILE:-$ROOT/.env.easyoutfit_codex_bridge}"

load_env_file() {
  local candidate="$1"
  if [ -f "$candidate" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$candidate"
    set +a
  fi
}

load_env_file "$ROOT/backend/.env"
load_env_file "$SECRET_ENV_FILE"

if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="$(command -v python3 || true)"
fi

if [ -z "$PYTHON_BIN" ] || [ ! -x "$PYTHON_BIN" ]; then
  echo "Python runtime not found for EasyOutfit Codex bridge." >&2
  exit 1
fi

if [ -z "${EASYOUTFIT_LOCAL_CODEX_TOKEN:-}" ]; then
  echo "EASYOUTFIT_LOCAL_CODEX_TOKEN must be set for the EasyOutfit Codex bridge." >&2
  exit 1
fi

export EASYOUTFIT_CODEX_API_BASE_URL="${EASYOUTFIT_CODEX_API_BASE_URL:-$API_BASE_DEFAULT}"
export EASYOUTFIT_LOCAL_CODEX_WORKSPACE_ROOT="${EASYOUTFIT_LOCAL_CODEX_WORKSPACE_ROOT:-$ROOT}"
export EASYOUTFIT_LOCAL_CODEX_WORKSPACE_SLUG="${EASYOUTFIT_LOCAL_CODEX_WORKSPACE_SLUG:-easyoutfitapp}"
export PATH="${PATH:-/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin}"

WORKER_SUFFIX="${EASYOUTFIT_LOCAL_CODEX_WORKER_SUFFIX:-easyoutfit-codex-bridge}"
WORKER_ID="${EASYOUTFIT_LOCAL_CODEX_WORKER_ID:-$(hostname -s)-$WORKER_SUFFIX}"

mkdir -p "$ROOT/logs"

exec "$PYTHON_BIN" "$ROOT/scripts/local_codex_bridge_easyoutfit.py" \
  --api-base "$EASYOUTFIT_CODEX_API_BASE_URL" \
  --workspace-root "$EASYOUTFIT_LOCAL_CODEX_WORKSPACE_ROOT" \
  --workspace-slug "$EASYOUTFIT_LOCAL_CODEX_WORKSPACE_SLUG" \
  --worker-id "$WORKER_ID"
