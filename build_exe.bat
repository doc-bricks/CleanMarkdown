@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set "ICON_PATH=assets\cleanmarkdown.ico"
python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name CleanMarkdown ^
  --icon "%ICON_PATH%" ^
  --add-data "%ICON_PATH%;assets" ^
  main.py
