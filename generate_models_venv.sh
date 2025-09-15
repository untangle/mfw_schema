#!/bin/bash
set -e

# Find a suitable Python interpreter
if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
else
  echo "Error: Python interpreter not found. Please install Python." >&2
  exit 1
fi

# Create a virtual environment if it doesn't already exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  $PYTHON_CMD -m venv .venv
fi

# Activate the virtual environment and install dependencies
source .venv/bin/activate
pip install -r requirements.txt

# Run the model generation script
./generate_models.sh
