#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Upgrading pip, setuptools, wheel and installing cmake..."
python -m pip install --upgrade pip setuptools wheel
pip install cmake

echo "Installing project requirements..."
pip install -r requirements.txt
