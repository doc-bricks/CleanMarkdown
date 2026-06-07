@echo off
REM ============================================================================
REM  CleanMarkdown -- Build nach .SOFTWARE-Standardverfahren
REM  Siehe: C:\Users\User\OneDrive\.TOPICS\.SOFTWARE\BUILD-VERFAHREN.md
REM
REM  Pflicht:
REM   1) Lokal bauen: build/dist/spec unter C:\_Local_DEV\codex_build\...
REM   2) Auto-Excludes per _tools\build_exclude_scanner.py mit Build-Python
REM   3) Minimal-venv gegen ungewollte globale Imports
REM ============================================================================
cd /d "%~dp0"
setlocal

python --version >nul 2>&1
if errorlevel 1 ( echo [FEHLER] Python nicht gefunden! & pause & exit /b 1 )

set "PROJECT_ROOT=%CD%"
set "SOFTWARE_ROOT=C:\Users\User\OneDrive\.TOPICS\.SOFTWARE"
set "SCANNER=%SOFTWARE_ROOT%\_tools\build_exclude_scanner.py"
set "ICON_PATH=%PROJECT_ROOT%\assets\cleanmarkdown.ico"
set "VERSION=0.3.1"
set "APP_NAME=CleanMarkdown"
set "BUILD_ROOT=C:\_Local_DEV\codex_build\cleanmarkdown"
set "VENV_DIR=%BUILD_ROOT%\.venv"
set "BUILD_PY=%VENV_DIR%\Scripts\python.exe"
set "DIST_DIR=%BUILD_ROOT%\dist"
set "WORK_DIR=%BUILD_ROOT%\work"
set "SPEC_DIR=%BUILD_ROOT%\spec"
set "FAST_DIST_DIR=%BUILD_ROOT%\fastdist"
set "FAST_WORK_DIR=%BUILD_ROOT%\fastwork"
set "FAST_SPEC_DIR=%BUILD_ROOT%\fastspec"
set "EXCLUDES_FILE=%BUILD_ROOT%\pyinstaller-excludes.txt"
set "RELEASE_DIR=%PROJECT_ROOT%\releases\v%VERSION%"
set "RELEASE_EXE=%RELEASE_DIR%\%APP_NAME%-%VERSION%-win64.exe"
set "FAST_BUILD_DIR=%FAST_DIST_DIR%\%APP_NAME%"
set "FAST_RELEASE_DIR=%RELEASE_DIR%\%APP_NAME%-fast"
set "FAST_RELEASE_EXE=%FAST_RELEASE_DIR%\%APP_NAME%.exe"

set "PYTHONPATH="
set "PYTHONIOENCODING=utf-8"
set "QT_QPA_PLATFORM=offscreen"

if not exist "%BUILD_PY%" (
  echo [build] Erstelle lokales Minimal-venv: %VENV_DIR%
  python -m venv "%VENV_DIR%"
  if errorlevel 1 ( pause & exit /b 1 )
)

"%BUILD_PY%" -m pip install --disable-pip-version-check -q -r "%PROJECT_ROOT%\requirements-build.txt"
if errorlevel 1 ( pause & exit /b 1 )

"%BUILD_PY%" -m py_compile "%PROJECT_ROOT%\main.py"
if errorlevel 1 ( pause & exit /b 1 )

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"
set "EXCLUDES="
"%BUILD_PY%" "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller > "%EXCLUDES_FILE%"
if errorlevel 1 ( pause & exit /b 1 )
set /p EXCLUDES=<"%EXCLUDES_FILE%"
echo [build] Auto-Excludes: %EXCLUDES%

"%BUILD_PY%" -m PyInstaller --noconfirm --clean --windowed --onefile --noupx ^
  --name "%APP_NAME%" ^
  --icon "%ICON_PATH%" ^
  --add-data "%ICON_PATH%;assets" ^
  %EXCLUDES% ^
  --distpath "%DIST_DIR%" ^
  --workpath "%WORK_DIR%" ^
  --specpath "%SPEC_DIR%" ^
  "%PROJECT_ROOT%\main.py"

if errorlevel 1 ( pause & exit /b 1 )
if not exist "%RELEASE_DIR%" mkdir "%RELEASE_DIR%"
copy /y "%DIST_DIR%\%APP_NAME%.exe" "%RELEASE_EXE%" >nul
if errorlevel 1 ( pause & exit /b 1 )

"%BUILD_PY%" -m PyInstaller --noconfirm --clean --windowed --onedir --noupx ^
  --name "%APP_NAME%" ^
  --icon "%ICON_PATH%" ^
  --add-data "%ICON_PATH%;assets" ^
  %EXCLUDES% ^
  --distpath "%FAST_DIST_DIR%" ^
  --workpath "%FAST_WORK_DIR%" ^
  --specpath "%FAST_SPEC_DIR%" ^
  "%PROJECT_ROOT%\main.py"

if errorlevel 1 ( pause & exit /b 1 )
if exist "%FAST_RELEASE_DIR%" rmdir /s /q "%FAST_RELEASE_DIR%"
robocopy "%FAST_BUILD_DIR%" "%FAST_RELEASE_DIR%" /MIR /NFL /NDL /NJH /NJS /NP >nul
if %ERRORLEVEL% GEQ 8 ( pause & exit /b 1 )

powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-FileHash -Algorithm SHA256 -LiteralPath '%RELEASE_EXE%' | ForEach-Object { $_.Hash.ToLowerInvariant() + ' *' + (Split-Path -Leaf $_.Path) } | Set-Content -Encoding ASCII -LiteralPath '%RELEASE_DIR%\SHA256SUMS.txt'"
if errorlevel 1 ( pause & exit /b 1 )
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-FileHash -Algorithm SHA256 -LiteralPath '%FAST_RELEASE_EXE%' | ForEach-Object { $_.Hash.ToLowerInvariant() + ' *CleanMarkdown-fast\' + (Split-Path -Leaf $_.Path) } | Set-Content -Encoding ASCII -LiteralPath '%RELEASE_DIR%\SHA256SUMS-fast.txt'"
if errorlevel 1 ( pause & exit /b 1 )

echo.
echo [build] OK -- lokal gebaut: %DIST_DIR%\%APP_NAME%.exe
echo [build] Release-EXE: %RELEASE_EXE%
echo [build] Fast-Start: %FAST_RELEASE_EXE%
