#!/bin/bash
echo "Installing python and ffmpeg..."
apt install -y python3.12 ffmpeg

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -e .

echo "Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "WARNING: FFmpeg not found. Please install it using your package manager."
fi

echo "Setup complete. Use 'source venv/bin/activate' to activate the environment." 