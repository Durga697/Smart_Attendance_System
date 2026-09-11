#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Upgrading build tools..."
pip install --upgrade pip setuptools wheel

echo "Installing cmake..."
pip install cmake

echo "Installing application dependencies..."
pip install -r requirements.txt
