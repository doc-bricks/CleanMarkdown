# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Added
- Release-Vorbereitung mit `LICENSE`, `.gitignore`, `CHANGELOG`, `SECURITY`, `CONTRIBUTING` und `CODE_OF_CONDUCT`
- Bilinguale README für einen späteren GitHub-Start
- Vorbereiteter Screenshot-Pfad unter `README/screenshots/`
- Englisches Standard-README mit separater deutscher README
- Erster GUI-Screenshot für die GitHub-Repo-Seite

### Changed
- `requirements.txt` auf getestete Mindestversionen angehoben
- `start.bat` benutzerfreundlicher gemacht
- `AUFGABEN.txt` auf Release-Härtung und Validierung fokussiert

## [0.2.0] - 2026-04-23

### Added
- Desktop-App mit Tabs für `Lesen` und `Editor`
- Raw-Markdown-Editor mit Struktur-Buttons
- DE/EN UI, Light/Dark Theme und Einstellungsdialog
- Autosave, `Speichern`, `Speichern unter` und PDF-Export
- Editor-Syntaxhervorhebung für zentrale Markdown-Gruppen
- GUI-Selbsttest für Öffnen, Speichern unter, Task-Listen und PDF-Export

### Fixed
- Öffnen und `Speichern unter` repariert
- Task-Listen im Viewer korrekt gerendert
- Leere Dokumente erzeugen keine unnötigen Save-Warnungen mehr
- Viewer-Startzustand auf eine wirklich leere Ansicht reduziert
