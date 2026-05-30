@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "ICON_PATH=%CD%\assets\cleanmarkdown.ico"
set "VERSION=0.3.1"
set "APP_NAME=CleanMarkdown"
set "PYI_TEMP=C:\_Local_DEV\codex_build\CleanMarkdown"
set "DIST_DIR=%PYI_TEMP%\dist"
set "RELEASE_DIR=%CD%\releases\v%VERSION%"
set "RELEASE_EXE=%RELEASE_DIR%\%APP_NAME%-%VERSION%-win64.exe"
if exist "%PYI_TEMP%" rmdir /s /q "%PYI_TEMP%"
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name "%APP_NAME%" ^
  --icon "%ICON_PATH%" ^
  --add-data "%ICON_PATH%;assets" ^
  --distpath "%DIST_DIR%" ^
  --workpath "%PYI_TEMP%\work" ^
  --specpath "%PYI_TEMP%\spec" ^
  main.py
if errorlevel 1 exit /b 1
copy /y "%DIST_DIR%\%APP_NAME%.exe" "%RELEASE_EXE%"
if errorlevel 1 exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-FileHash -Algorithm SHA256 -LiteralPath '%RELEASE_EXE%' | ForEach-Object { $_.Hash.ToLowerInvariant() + ' *' + (Split-Path -Leaf $_.Path) } | Set-Content -Encoding ASCII -LiteralPath '%RELEASE_DIR%\SHA256SUMS.txt'"
