#!/bin/bash
# IVERI AI - Bluetooth Audio Setup for Raspberry Pi
# Run with: chmod +x setup_bluetooth.sh && ./setup_bluetooth.sh

echo "=========================================="
echo "IVERI AI - Bluetooth Setup"
echo "=========================================="

# Start Bluetooth service
echo "[1/4] Starting Bluetooth..."
sudo systemctl start bluetooth
sudo systemctl enable bluetooth

# Start PulseAudio
echo "[2/4] Starting PulseAudio..."
pulseaudio --start

echo ""
echo "[3/4] Opening Bluetooth pairing..."
echo ""
echo "Instructions:"
echo "  1. Put your headset in pairing mode"
echo "  2. In bluetoothctl, type these commands:"
echo "     power on"
echo "     agent on"
echo "     scan on"
echo "     (wait for your device to appear)"
echo "     pair XX:XX:XX:XX:XX:XX"
echo "     connect XX:XX:XX:XX:XX:XX"
echo "     trust XX:XX:XX:XX:XX:XX"
echo "     exit"
echo ""
echo "Starting bluetoothctl..."
echo ""

bluetoothctl

echo ""
echo "[4/4] Testing audio..."
echo "If you hear sound, Bluetooth is working!"
speaker-test -t wav -c 2 -l 1

echo ""
echo "=========================================="
echo "Bluetooth Setup Complete!"
echo "=========================================="
echo ""
echo "To set Bluetooth as default audio:"
echo "  pactl list short sinks"
echo "  pactl set-default-sink <YOUR_BLUETOOTH_SINK>"
echo ""
echo "To auto-connect on boot, add to /etc/rc.local:"
echo "  bluetoothctl connect XX:XX:XX:XX:XX:XX"
echo ""
