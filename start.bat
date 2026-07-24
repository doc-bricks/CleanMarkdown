@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "FAST_EXE=%CD%\releases\v0.3.2\CleanMarkdown-fast\CleanMarkdown.exe"
set "RELEASE_EXE=%CD%\releases\v0.3.2\CleanMarkdown-0.3.2-win64.exe"
if exist "%FAST_EXE%" (
    start "" "%FAST_EXE%"
    exit /b 0
)
if exist "%RELEASE_EXE%" (
    start "" "%RELEASE_EXE%"
    exit /b 0
)
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python wurde nicht gefunden und die Release-EXE fehlt.
    pause
    exit /b 1
)
echo [INFO] Release-EXE fehlt, starte Python-Fallback.
python main.py
if errorlevel 1 pause
