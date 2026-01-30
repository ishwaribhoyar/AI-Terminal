#!/bin/bash
# IVERI AI Setup Script for Raspberry Pi
# Run with: chmod +x setup_pi.sh && ./setup_pi.sh

echo "=========================================="
echo "IVERI AI - Raspberry Pi Setup"
echo "=========================================="

# Update system
echo "[1/6] Updating system..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "[2/6] Installing system packages..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    libatlas-base-dev \
    flac \
    espeak \
    pulseaudio \
    pulseaudio-module-bluetooth \
    bluez \
    bluez-tools

# Install Python dependencies
echo "[3/6] Installing Python packages..."
pip3 install -r requirements.txt

# Install RPi.GPIO
echo "[4/6] Installing Raspberry Pi GPIO..."
pip3 install RPi.GPIO

# Create data directories
echo "[5/6] Creating directories..."
mkdir -p ~/iveri/data
mkdir -p ~/iveri/models
mkdir -p ~/Pictures

# Setup service for auto-start
echo "[6/6] Setting up auto-start service..."
sudo cp iveri.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iveri

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Test IVERI:"
echo "   python3 main.py"
echo ""
echo "3. For Bluetooth audio, run:"
echo "   ./setup_bluetooth.sh"
echo ""
echo "4. To start IVERI service:"
echo "   sudo systemctl start iveri"
echo ""
