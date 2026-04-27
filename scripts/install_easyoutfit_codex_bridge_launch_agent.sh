#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
LABEL="com.neo.easyoutfit_codex_bridge"
PLIST_NAME="$LABEL.plist"
SOURCE_PLIST="$ROOT/automations/launchd/$PLIST_NAME"
SOURCE_BRIDGE="$ROOT/scripts/local_codex_bridge_easyoutfit.py"
SOURCE_WRAPPER="$ROOT/scripts/run_local_codex_bridge_easyoutfit.sh"
SOURCE_ENV="$ROOT/.env.easyoutfit_codex_bridge"
TARGET_ROOT="$HOME/.easyoutfit-codex-bridge"
TARGET_SCRIPT_DIR="$TARGET_ROOT/scripts"
TARGET_LOG_DIR="$TARGET_ROOT/logs"
TARGET_ENV="$TARGET_ROOT/.env.easyoutfit_codex_bridge"
LIVE_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

mkdir -p "$LAUNCH_AGENTS_DIR" "$TARGET_SCRIPT_DIR" "$TARGET_LOG_DIR"

install -m 755 "$SOURCE_BRIDGE" "$TARGET_SCRIPT_DIR/local_codex_bridge_easyoutfit.py"
install -m 755 "$SOURCE_WRAPPER" "$TARGET_SCRIPT_DIR/run_local_codex_bridge_easyoutfit.sh"
if [ -f "$SOURCE_ENV" ]; then
  install -m 600 "$SOURCE_ENV" "$TARGET_ENV"
fi

install -m 644 "$SOURCE_PLIST" "$LIVE_PLIST"

launchctl bootout "gui/$UID" "$LIVE_PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$UID" "$LIVE_PLIST"

echo "Installed $LABEL"
echo "  plist: $LIVE_PLIST"
echo "  log:   $TARGET_LOG_DIR/easyoutfit_codex_bridge.log"
