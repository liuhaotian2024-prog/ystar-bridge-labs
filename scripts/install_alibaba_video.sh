#!/bin/bash
# Install ComfyUI + CogVideoX for local video generation (替代 HeyGen)
# Target: Mac M-series (24GB RAM, <20GB download budget)
# CTO: Ethan Wright | 2026-04-15

set -e

WORKSPACE_ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company"
INSTALL_DIR="$HOME/comfyui_video"
PYTHON_MIN_VERSION="3.10"

echo "=== Y* Bridge Labs — Local Video Generation Setup ==="
echo "Model: CogVideoX-2B (6GB VRAM, ~5GB download)"
echo "Install path: $INSTALL_DIR"
echo ""

# Step 1: Check Python version (require 3.11 or 3.10)
echo "[1/7] Checking Python version..."
PYTHON_CMD=$(which python3.11 2>/dev/null || which python3.10 2>/dev/null || echo "")
if [ -z "$PYTHON_CMD" ]; then
    echo "ERROR: python3.11 or python3.10 not found. Install via: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "Found: Python $PYTHON_VERSION at $PYTHON_CMD"

# Step 2: Create install directory
echo "[2/7] Creating install directory..."
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Step 3: Clone ComfyUI
echo "[3/7] Cloning ComfyUI..."
if [ ! -d "ComfyUI" ]; then
    git clone https://github.com/comfyanonymous/ComfyUI.git
else
    echo "ComfyUI already exists, skipping clone."
fi
cd ComfyUI

# Step 4: Install ComfyUI dependencies
echo "[4/7] Installing ComfyUI dependencies..."
$PYTHON_CMD -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install torch torchvision torchaudio  # Mac CPU/MPS support
pip install -r requirements.txt

# Step 5: Install CogVideoX wrapper
echo "[5/7] Installing CogVideoX custom nodes..."
cd custom_nodes
if [ ! -d "ComfyUI-CogVideoXWrapper" ]; then
    git clone https://github.com/kijai/ComfyUI-CogVideoXWrapper.git
else
    echo "CogVideoX wrapper already exists, skipping clone."
fi
cd ComfyUI-CogVideoXWrapper
pip install -r requirements.txt
cd ../..

# Step 6: Install ffmpeg (required for video output)
echo "[6/7] Checking ffmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing ffmpeg via pip..."
    pip install imageio-ffmpeg
else
    echo "ffmpeg found: $(which ffmpeg)"
fi

# Step 7: Install diffusers for headless testing
echo "[7/7] Installing diffusers + dependencies..."
pip install diffusers transformers accelerate moviepy

echo ""
echo "=== Installation Complete ==="
echo "Launch ComfyUI: cd $INSTALL_DIR/ComfyUI && source venv/bin/activate && python main.py"
echo "Web UI: http://127.0.0.1:8188"
echo ""
echo "Headless test: $WORKSPACE_ROOT/scripts/test_cogvideox_sanity.py"
echo ""
