#!/usr/bin/env bash
set -euo pipefail
PLIST_NAME="com.ystar.cieu_to_brain_streamer"
TARGET="${HOME}/Library/LaunchAgents/${PLIST_NAME}.plist"
launchctl unload "${TARGET}" 2>/dev/null || true
rm -f "${TARGET}"
echo "Uninstalled: ${PLIST_NAME}"
