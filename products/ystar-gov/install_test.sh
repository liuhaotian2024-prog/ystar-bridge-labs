#!/bin/bash
# Y*gov Installation Verification
# Run this after: pip install ystar

set -e
echo "Checking Y*gov installation..."

# Check Python version
python3 -c "import sys; assert sys.version_info >= (3,11), f'Need Python 3.11+, got {sys.version}'"
echo "OK: Python version"

# Check import
python3 -c "from ystar import Policy; print('OK: ystar imports')"

# Check CLI
ystar version
echo "OK: CLI works"

# Check doctor
ystar doctor || echo "WARN: doctor reported issues"

echo ""
echo "Installation verified."
