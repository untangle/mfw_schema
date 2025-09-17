#!/bin/bash
# This script sets up the virtual environment, installs dependencies, and runs the validation script.
# Used as a vs code target
set -e

# Check if the venv directory exists. If not, create it and install dependencies.
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
  echo "Installing dependencies..."
  ./venv/bin/pip install -r requirements.txt
fi

# Run the validation script using the virtual environment's python
echo "Running validation..."
./venv/bin/python validate.py
