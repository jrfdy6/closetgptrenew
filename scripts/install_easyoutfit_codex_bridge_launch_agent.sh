#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
LABEL="com.neo.easyoutfit_codex_bridge"
PLIST_NAME="$LABEL.plist"
SOURCE_PLIST="$ROOT/automations/launchd/$PLIST_NAME"
LIVE_PLIST="$LAUNCH_AGENTS_DIR/$PLIST_NAME"

mkdir -p "$LAUNCH_AGENTS_DIR" "$ROOT/logs"

install -m 644 "$SOURCE_PLIST" "$LIVE_PLIST"

launchctl bootout "gui/$UID" "$LIVE_PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$UID" "$LIVE_PLIST"

echo "Installed $LABEL"
echo "  plist: $LIVE_PLIST"
echo "  log:   $ROOT/logs/easyoutfit_codex_bridge.log"
