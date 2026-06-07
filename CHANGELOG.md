# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased] - 2026-06-06

### Added
- `tests/source_platform_smoke.py` — P3 Source-Smoke für macOS/Linux: 6 Checks
  (stdlib, PySide6, markdown-Lib, Offscreen-QApplication + MainWindow-Smoke,
  SettingsStore-Roundtrip mit Umlauten, Session-JSON-Roundtrip mit Validierungslogik).
- `.github/workflows/source-platform-smoke.yml` — CI-Workflow für ubuntu-latest und
  macos-latest; triggert bei Änderungen an `main.py`, `requirements.txt` oder
  `tests/source_platform_smoke.py`.

## [Unreleased] - 2026-05-03

### Added
- pytest-Suite unter `tests/` mit 40 Tests für die Markdown-Render-Pipeline
  (Code-Schutz, Mathe inline/block, Task-Lists, Tabellen, Listen, Blockquotes,
  Footnotes, Links, Bilder, Strikethrough, Umlaut-Erhalt).
- Realer Selbsttest-Roundtrip über öffentliche Repo-Markdown-Dateien
  (öffnen, bearbeiten, speichern, erneut laden) zur Absicherung des
  Alltags-Workflows.
- GFM-Strikethrough-Unterstützung: `~~text~~` wird in `<del>text</del>`
  konvertiert. Code- und Pre-Blöcke bleiben dabei unangetastet.
- Windows-Store-Basis für CleanMarkdown vorbereitet: `store_package.json`,
  `STORE_LISTING.md`, Store-Screenshot-Set unter `README/screenshots/store/`
  und generierte `store_assets/` aus dem Projekt-Icon.
- `EXPORTFORMAT.md` dokumentiert jetzt `.md` als Primärformat,
  `cleanmarkdown-session-v1.json` für lokale Arbeitsstände und das reservierte
  `cleanmarkdown-bundle-v1.zip` für spätere Asset-Bündel.
- Desktop-App kann `cleanmarkdown-session-v1.json` jetzt exportieren und
  wieder importieren; der Austausch bleibt zum Web-Companion kompatibel.

### Fixed
- Strikethrough wurde bisher gar nicht gerendert, weil das `markdown`-Paket
  diese GFM-Syntax ohne externe Extension nicht abdeckt.
- PDF-Export bricht bei ungültigen Zielordnern jetzt nicht mehr mit einem
  ungefangenen Fehler ab, sondern meldet den Fehler sauber im Dialog.
- `SettingsStore.load()` ignoriert unbekannte JSON-Felder jetzt, statt
  bekannte Einstellungen bei einer erweiterten `settings.json` zu verwerfen.
- Beschädigte `settings.json`-Typen fallen beim Laden jetzt auf sichere
  Standardwerte zurück, statt den App-Start mit einem `TypeError` zu beenden.
- Session-Importe nutzen für die Vorschau relativer Bilder jetzt den Ordner der
  geladenen Session-Datei, auch wenn keine echte Markdown-Datei geöffnet ist.

## [0.3.1] - 2026-05-01

### Fixed
- Relative Bild- und Asset-Links in der Vorschau werden jetzt gegen den Ordner der geöffneten Markdown-Datei aufgelöst.
- Nach `Speichern unter` wird die Vorschau neu gerendert, damit relative Assets sofort den neuen Dateispeicherort verwenden.

### Changed
- `--self-test` prüft zusätzlich die Basis-URL für relative Assets.
- `.gitignore` deckt lokale `.env`-Dateien, Logs, Datenbanken, Secret-Dateinamen und gängige Test-/Tool-Caches robuster ab.
- `build_exe.bat` legt PyInstaller-Work- und Spec-Dateien in einem temporären Ordner ab, damit nur die erwarteten Build-Artefakte im Projektordner entstehen.

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
