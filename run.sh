#!/usr/bin/env bash
# Launcher for IVERI AI Assistant on Linux and macOS

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "==================================================="
echo "              IVERI AI ASSISTANT"
echo "==================================================="

# Check for python3
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Python 3 was not found. Please install Python 3.8+."
    exit 1
fi

if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[INFO] Created .env configuration file from template."
fi

$PYTHON_CMD main.py "$@"
