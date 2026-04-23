#!/usr/bin/env bash
# Y* Bridge Labs Meeting Room — One-click start script
# Usage: bash scripts/meeting_room/start.sh
# Opens: http://localhost:8080

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "============================================"
echo "  Y* Bridge Labs — Meeting Room (Phase 0)"
echo "============================================"
echo ""

# Step 1: Ensure Python venv with dependencies
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/3] Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/3] Virtual environment exists."
fi

echo "[2/3] Installing dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet fastapi 'uvicorn[standard]' websockets

# Step 3: Launch the broker
echo "[3/3] Starting Meeting Room broker on http://localhost:8080"
echo ""
echo "  Open in browser:  http://localhost:8080"
echo "  Health check:     http://localhost:8080/health"
echo "  Stop:             Ctrl+C"
echo ""
echo "--------------------------------------------"

cd "$SCRIPT_DIR"
"$VENV_DIR/bin/python" -m uvicorn server:app --host 0.0.0.0 --port 8080 --log-level info
