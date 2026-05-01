@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "ICON_PATH=%CD%\assets\cleanmarkdown.ico"
set "PYI_TEMP=%TEMP%\CleanMarkdown_pyinstaller"
if exist "%PYI_TEMP%" rmdir /s /q "%PYI_TEMP%"
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name CleanMarkdown ^
  --icon "%ICON_PATH%" ^
  --add-data "%ICON_PATH%;assets" ^
  --distpath "dist" ^
  --workpath "%PYI_TEMP%\work" ^
  --specpath "%PYI_TEMP%\spec" ^
  main.py
