@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden.
    pause
    exit /b 1
)
python main.py
if errorlevel 1 pause
