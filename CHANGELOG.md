# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [0.3.1] - 2026-05-01

### Fixed
- Relative Bild- und Asset-Links in der Vorschau werden jetzt gegen den Ordner der geöffneten Markdown-Datei aufgelöst.
- Nach `Speichern unter` wird die Vorschau neu gerendert, damit relative Assets sofort den neuen Dateispeicherort verwenden.

### Changed
- `--self-test` prüft zusätzlich die Basis-URL für relative Assets.
- `.gitignore` deckt lokale `.env`-Dateien, Logs, Datenbanken, Secret-Dateinamen und gängige Test-/Tool-Caches robuster ab.

## [0.3.0] - 2026-04-30

### Added
- Release-Vorbereitung mit `LICENSE`, `.gitignore`, `CHANGELOG`, `SECURITY`, `CONTRIBUTING` und `CODE_OF_CONDUCT`
- Bilinguale README für die GitHub-Repo-Seite
- Vorbereiteter Screenshot-Pfad unter `README/screenshots/`
- Englisches Standard-README mit separater deutscher README
- Erster GUI-Screenshot für die GitHub-Repo-Seite
- Optionale Scroll-Synchronisierung zwischen `Lesen` und `Editor` beim Tab-Wechsel
- Leichtgewichtige Math-Vorschau für `$...$`, `$$...$$`, `\(...\)` und `\[...\]`

### Changed
- `requirements.txt` auf getestete Mindestversionen angehoben
- `start.bat` benutzerfreundlicher gemacht
- `AUFGABEN.txt` auf Release-Härtung und Validierung fokussiert
- `--self-test` prüft jetzt auch die Scroll-Synchronisierung und deren Deaktivierung
- `--self-test` prüft jetzt zusätzlich Math-Markup und den Schutz von Code-Bereichen

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
