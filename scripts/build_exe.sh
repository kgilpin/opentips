#!/bin/bash

echo "Building OpenTips executable using cx_Freeze CLI..."

# Activate virtual environment if needed (uncomment and adjust path if you use a venv)
# source ../venv/bin/activate

# Install cx_Freeze if not already installed
pip install -U cx_Freeze

# Run cx_Freeze build using CLI options
cxfreeze opentips/cli/main.py \
  --target-name=opentips \
  --no-compress

echo "Build completed. Check the 'dist' directory for the executable."