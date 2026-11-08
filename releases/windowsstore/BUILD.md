# CleanMarkdown - Windows Store Build-Anleitung

## Voraussetzungen

1. Python 3.10+ mit PySide6 (`pip install -r requirements.txt`)
2. PyInstaller für den Desktop-Build (`pip install -r requirements-build.txt`)
3. Windows 10/11 SDK mit `makeappx.exe`, `signtool.exe` und `appcert.exe` (WACK)
4. Lokaler Schreibpfad außerhalb synchronisierter Ordner für MSIX-Artefakte

## Build-Schritte

1. PyInstaller Build ausführen:
   ```cmd
   build_exe.bat
   ```
   Erzeugt die Standalone-Executable `dist\CleanMarkdown\CleanMarkdown.exe`.

2. MSIX-Paket erstellen:
   ```powershell
   makeappx.exe pack /d store_package\CleanMarkdown /p releases\CleanMarkdown.msix
   ```

3. WACK-Zertifizierungstest ausführen:
   ```cmd
   appcert.exe test -appxpackagepath releases\CleanMarkdown.msix -reportoutputpath releases\windowsstore\test_reports\wack_report.xml
   ```

4. Preflight-Store-Audit verifizieren:
   ```powershell
   python -X utf8 scripts\check_store_readiness.py
   ```
