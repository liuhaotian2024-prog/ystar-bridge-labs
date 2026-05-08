#!/usr/bin/env bash
# Install the cieu_to_brain_streamer LaunchAgent.
# Run: bash scripts/launchagents/install_cieu_to_brain_streamer.sh
set -euo pipefail
PLIST_NAME="com.ystar.cieu_to_brain_streamer"
SOURCE="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs/scripts/launchagents/${PLIST_NAME}.plist"
TARGET="${HOME}/Library/LaunchAgents/${PLIST_NAME}.plist"

mkdir -p "${HOME}/Library/LaunchAgents"
mkdir -p "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs/scripts/.logs"

# Unload existing if present
launchctl unload "${TARGET}" 2>/dev/null || true

# Install
cp "${SOURCE}" "${TARGET}"
launchctl load -w "${TARGET}"

echo "Installed: ${PLIST_NAME}"
echo "Status:"
launchctl list | grep "${PLIST_NAME}" || true
echo "Log: /Users/haotianliu/.openclaw/workspace/ystar-bridge-labs/scripts/.logs/cieu_to_brain_streamer.log"
