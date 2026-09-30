@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0" || exit /b 1
set "PYTHONIOENCODING=utf-8"
set "APP_PYTHON=python"
if exist "%~dp0.venv\Scripts\python.exe" set "APP_PYTHON=%~dp0.venv\Scripts\python.exe"
"%APP_PYTHON%" --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden. Bitte Python und requirements.txt installieren.
    pause
    exit /b 1
)
"%APP_PYTHON%" "%~dp0main.py" %*
set "APP_EXIT=%ERRORLEVEL%"
if not "%APP_EXIT%"=="0" pause
exit /b %APP_EXIT%
