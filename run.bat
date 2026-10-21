@echo off
title IVERI AI Assistant
cd /d "%~dp0"

echo ===================================================
echo               IVERI AI ASSISTANT
echo ===================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found on your PATH.
    echo Please install Python 3.8 or newer from https://www.python.org
    pause
    exit /b 1
)

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [INFO] Created .env configuration file from template.
    )
)

python main.py %*
if %errorlevel% neq 0 (
    echo.
    echo [INFO] Press any key to exit...
    pause >nul
)
