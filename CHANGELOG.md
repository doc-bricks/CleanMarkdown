# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Fixed
- `_render_task_lists`: Gemischte Listen (normales Item als erstes, dann Task-Boxen) bekamen die CSS-Klasse `task-list` nicht auf `<ul>`, weil die vorherigen `str.replace()`-Aufrufe nur beim allerersten Item griffen. Fix: Task-Items werden zuerst per Regex markiert, dann wird `<ul>` per String-Split als `task-list` gesetzt, wenn mindestens ein `task-item` darin vorkommt. (6 Regressionstests ergänzt)
- `_render_strikethrough`: Vier oder mehr Tilden (`~~~~text~~~~`) erzeugten durch lazy Matching kaputtes HTML (`<del>~~text</del>~~`). Fix: Lookbehind/Lookahead `(?<!~)~~(?!~)` stellt sicher, dass nur genau zwei Tilden als Strikethrough-Marker akzeptiert werden. (Regressionstest ergänzt)

### Added
- `PRIVACY_POLICY.md` — DE+EN privacy policy documenting that CleanMarkdown makes no own network connections; link clicks delegate to the system browser (verified via code grep).
- `SUPPORT.md` — DE+EN support page with FAQ, contact details and system requirements.
- `WINDOWS_STORE_PREP.md` — pipeline-standard artefact status table replacing the older `STORE_READINESS.md`.
- `tests/test_store_materials.py` — 6 automated tests verifying store material completeness.
- `translator.py` and `locales/translations.json` — i18n system replacing the inline 96-key dict in `main.py`; 6 language slots (de, en, es, zh, ja, ru).
- `flutter_port/` — Flutter 3.44.0 mobile port (Android/iOS) with `flutter_markdown_plus`, file picker, DE/EN L10n via handwritten `AppLocalizations` + ARB reference files.
- `flutter_port/android/` — Android build configuration with `compileSdk 36`; `app-debug.apk` builds cleanly.
- `web_companion/tests/pwa.test.mjs` — 17 node:test PWA tests covering SVG icons, maskable PNG, manifest, and drag-leave null guard.
- `web_companion/public/` — `icon-maskable-192.png` and `icon-maskable-512.png` for PWA install.
- `flutter_port/test/bug_regression_test.dart` — 6 source-only regression tests; `widget_test.dart` extended with `_FakeFilePicker` + `_pickFile` happy-path test (11 tests total).
- `tests/source_platform_smoke.py` — P3 Source-Smoke for macOS/Linux: 6 checks (stdlib, PySide6, markdown-lib, offscreen QApplication + MainWindow smoke, SettingsStore roundtrip with Umlauts, Session-JSON roundtrip with validation logic).
- `.github/workflows/source-platform-smoke.yml` — CI workflow for ubuntu-latest and macos-latest; triggers on changes to `main.py`, `requirements.txt`, or `tests/source_platform_smoke.py`.
- pytest suite under `tests/` with 51 tests for the Markdown render pipeline (code protection, math inline/block, task lists, tables, lists, blockquotes, footnotes, links, images, strikethrough, Umlaut preservation).
- Real self-test roundtrip over public repo Markdown files (open, edit, save, reload) to validate the everyday workflow.
- GFM strikethrough support: `~~text~~` converts to `<del>text</del>`; code and pre blocks stay untouched.
- Windows Store base for CleanMarkdown: `store_package.json`, `STORE_LISTING.md`, store screenshot set under `README/screenshots/store/`, and generated `store_assets/`.
- `EXPORTFORMAT.md` documents `.md` as the primary format, `cleanmarkdown-session-v1.json` for local working state, and the reserved `cleanmarkdown-bundle-v1.zip` for future asset bundles.
- Desktop app can now export and import `cleanmarkdown-session-v1.json`; the exchange format remains compatible with the web companion.
- Additional Flutter widget tests now cover preview/edit/save state and Markdown-safe text input settings.

### Changed
- `store_package.json` now includes `logo` and `languages` fields; `privacy_url` and `support_url` point to GitHub policy files.

### Fixed
- The compact editor-toolbar toggle now keeps its symbol-only UI, but exposes a stable accessible name plus state-aware accessible descriptions in DE/EN so screenreaders can distinguish between collapsing and expanding the editor tools.
- Session import now ignores unknown theme values instead of silently switching the desktop UI to bright mode, and remaining PySide6 print/settings enums use the modern scoped names.
- Desktop release packaging now keeps the checked-in PyInstaller spec aligned with the project build script by disabling UPX there as well.
- Flutter mobile editor now disables autocorrect, suggestions, smart dashes, smart quotes, and auto-capitalization so Markdown syntax is not rewritten by the mobile keyboard.
- **Flutter `_pickFile`:** Three `if (!mounted) return;` guards after every `await` prevent `setState` calls on disposed widgets (`FlutterError`).
- **Flutter error logging:** `catch (_)` replaced by `catch (e, stackTrace)` + `debugPrint` for traceable file-read error diagnosis.
- **Flutter `pubspec.yaml`:** `path_provider` removed — never imported, unnecessary dependency.
- **Web companion `triggerDownload`:** Anchor appended to DOM before `.click()` and synchronously revoked via `revokeObjectURL`; fixes broken downloads in iOS Safari and Firefox (detached `<a>` element).
- **Web companion `readImportedFile`:** `JSON.parse` wrapped in try/catch; `SyntaxError` now throws `errorInvalidSession` instead of showing a raw engine message.
- **Web companion `package.json`:** Test script pointed at non-existent `i18n.test.mjs`; corrected to `pwa.test.mjs`.
- **Web companion `handleDragLeave`:** Explicit `null` check for `event.relatedTarget` prevents drag indicator flicker when crossing child elements.
- **Web companion `vite.config.ts`:** SVG/PNG hybrid, 4 icon entries (SVG any + PNG maskable), `lang: 'de'`; `index.html` adds `lang="de"`, `theme-color`, and `apple-touch-icon`.
- Strikethrough was not rendered because the `markdown` package does not cover GFM syntax without an extension.
- PDF export no longer crashes with an uncaught error on invalid target folders.
- `SettingsStore.load()` now ignores unknown JSON fields instead of discarding known settings when `settings.json` is extended.
- Corrupted `settings.json` types now fall back to safe defaults on load instead of crashing app start with a `TypeError`.
- Session imports now use the folder of the loaded session file for relative image preview even when no Markdown file is open.

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
