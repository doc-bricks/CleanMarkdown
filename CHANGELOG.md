# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Added
- **Android-Readiness:** `web_companion/scripts/android-doctor.mjs` prüft den
  Capacitor-Wrapper, Paket-Major, Node.js 20+, JDK 17+, Android SDK 35,
  Build-Tools und `adb`; JSON-/Allow-Blocker-Ausgabe und ein optionaler,
  auf 30 Sekunden begrenzter Gradle-Probe verhindern erneute Hänger.
- **Android-Readiness:** `tests/android-doctor.test.mjs` sichert Bericht,
  App-ID, SDK-Ziel und Package-Scripts auch ohne lokal installierte SDK-Toolchain.
- **Web-Companion:** Android-Capacitor-Wrapper unter `web_companion/android/`
  erzeugt; `npm run test:cap`/`cap:doctor` prüfen App-ID, Package-Scripts,
  Wrapper-Dateien und Android-Version `0.1.0`.
- **Web-Companion:** Statistik-Erweiterung — zwei neue StatCards `statLines` (Zeilen) und `statLinks` (Links) ergänzen die bestehenden Metriken Wörter, Zeichen und Lesezeit.
- **Web-Companion:** Kopier-Button (`btnCopy`) in der Toolbar — überträgt das aktuelle Markdown per Clipboard-API in die Zwischenablage; Status-Feedback `statusCopied` / `statusCopyFailed` im Header.
- **Web-Companion:** `src/lib/markdownStats.mjs` — pure-ESM-Modul mit `countLines()` und `countLinks()`; `markdownStats.d.mts` + `markdownStats.d.ts` als TypeScript-Deklarationen.
- **Web-Companion:** `tests/stats.test.mjs` — 31 Node:test-Tests (countLines, countLinks, i18n-Parität, App.tsx-Integration).
- **Web-Companion:** i18n-Keys `statLines`, `statLinks`, `btnCopy`, `statusCopied`, `statusCopyFailed` in `de.json` und `en.json` hinzugefügt (Parität gewahrt).

### Fixed
- **Web-Companion:** `apple-touch-icon.png` enthielt 6.324 vollständig transparente
  Randpixel und ließ den PWA-Test dauerhaft rot (Apple erlaubt dort keine Transparenz).
  Fix: Bild auf weißem Hintergrund geflattet und als opakes RGB gespeichert; `npm test`
  jetzt 66/66 grün statt 65/66.
- **Desktop:** Toolbar-Buttons exponieren jetzt echte `accessibleName`/
  `accessibleDescription` (aus dem Tooltip abgeleitet) statt nur Tooltip/StatusTip —
  Screenreader lesen Werkzeugname und Tastenkürzel getrennt vor.
- Der DragLeave-Regressionstest akzeptiert jetzt den bereits robusteren
  `event.relatedTarget instanceof Node`-Guard, statt eine schwächere
  Quelltextform festzuschreiben.
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
- **`CleanMarkdown.spec` / `build_exe.bat`:** PyInstaller `datas`/`--add-data` bundled only the app icon, not `locales/`; packaged EXE builds shipped with an empty translation catalog, so every UI string fell back to its raw lookup key regardless of the configured language (settings persistence itself was unaffected). Both the checked-in spec and the onefile/onedir build commands now include `locales`; verified that `locales/translations.json` is physically present under the built bundle's `_internal/` folder and that `TranslationSystem` resolves known keys (e.g. `language` -> `Sprache`) when pointed at that bundle path.
- Der 6-Sprachen-Pfad (`de/en/es/zh/ja/ru`) ist jetzt als echter Live-Vertrag abgesichert: `main.py` nutzt bereits `translator.py` + `locales/translations.json`, `tests/test_i18n.py` prüft die vollständige Sprachliste im Einstellungsdialog sowie reale Katalogwerte für zusätzliche Sprachen, und `TranslationSystem.t()` gibt bei absichtlich leeren Übersetzungen jetzt `""` statt des Key-Namens zurück.
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
- **Web companion `dompurify`:** Bumped `^3.2.6` → `^3.4.12` (moderate advisories for `<=3.4.11`, mostly `IN_PLACE`-mode-specific; this app calls `DOMPurify.sanitize(html)` in default string-return mode with no hooks/`setConfig()`, so reachable exposure was limited, but the upgrade removes it). `npm audit --omit=dev --audit-level=high` now reports 0 vulnerabilities.
- Strikethrough was not rendered because the `markdown` package does not cover GFM syntax without an extension.
- PDF export no longer crashes with an uncaught error on invalid target folders.
- `SettingsStore.load()` now ignores unknown JSON fields instead of discarding known settings when `settings.json` is extended.
- Corrupted `settings.json` types now fall back to safe defaults on load instead of crashing app start with a `TypeError`.
- Session imports now use the folder of the loaded session file for relative image preview even when no Markdown file is open.

## [0.3.2] - 2026-07-24

### Fixed
- **U1 (Welle-1-Usertest 2026-07-23):** PDF-Export übernahm bislang das aktuell
  aktive UI-Theme (Dark Mode -> schwarzer PDF-Hintergrund, weiße Schrift).
  Root-Cause: `export_pdf()` druckte einen Klon von `self.viewer.document()`,
  dessen HTML mit `THEMES[self.settings.theme]["html"]` gerendert wurde.
  Fix: neue Methode `_build_export_document()` baut ein eigenständiges
  `QTextDocument` immer mit dem `bright`-Theme-CSS, unabhängig vom
  UI-Theme -- PDF-Export ist jetzt durchgängig Print-Standard (heller
  Hintergrund, dunkle Schrift). `_render_preview()`/`export_pdf()` teilen
  sich dafür die neuen Bausteine `_render_markdown_body()` und
  `_wrap_html_document()`.
- **U2 (Welle-1-Usertest 2026-07-23):** PDF-Export eines noch nie
  gespeicherten Dokuments landete unauffindbar in `Path.home() / "Documents"`
  -- einem hartcodierten Pfad, der Windows-/OneDrive-Ordnerumleitungen
  ignoriert (auf diesem System ist der echte Dokumente-Ordner
  `OneDrive\Dokumente`, nicht `C:\Users\<user>\Documents`). Der Export
  "gelang" technisch, aber die Datei war für den Nutzer nicht auffindbar --
  daher der Eindruck eines stillen Fehlschlags. Fix:
  `_suggested_export_path()` nutzt jetzt `_documents_dir()`
  (`QStandardPaths.writableLocation(DocumentsLocation)`, Known-Folder-fest)
  statt eines hartcodierten Pfads. Zusätzlich speichert `export_pdf()` ein
  ungespeichertes, nicht-leeres Dokument jetzt automatisch als `.md` in
  diesen Ordner, bevor daraus exportiert wird (`_auto_save_for_export()`),
  und jeder Fehlerpfad (Auto-Save, Druckvorgang, leere/fehlende Ausgabedatei)
  zeigt jetzt garantiert einen Fehlerdialog plus Statusleisten-Meldung statt
  still zu scheitern. 4 neue Regressionstests in `tests/test_file_handling.py`.
- **U3 (Welle-1-Usertest 2026-07-23, Fix von Themen-Worker "thema-screenshots"):**
  Store-Screenshots S3.2–S3.4 (`editor-dark.png`, `reading-bright.png`,
  `reading-dark.png`) zeigten Tofu (Kästchen statt Text). Root-Cause:
  `QT_QPA_PLATFORM=offscreen` + `window.grab()` rendert unter Windows keine
  echten Glyphen -- jede wird als `.notdef`-Kästchen gerastert. Fix: neuer
  `generate_store_screenshots.py` nutzt die native Qt-Plattform mit
  `Qt.WA_DontShowOnScreen` statt `offscreen` (Fenster bleibt unsichtbar,
  echte Font-Engine rendert), zusätzlich ein Guard
  (`_assert_font_rendering()`), der Tofu vor dem Capture erkennt und mit
  klarem Fehler abbricht statt still ein defektes Set zu speichern.
  Screenshot-Set neu erzeugt und visuell verifiziert; 5 neue
  Regressionstests in `tests/test_store_materials.py` (Commit `bf5f226`).
- **U4 (Welle-1-Usertest 2026-07-23):** `CleanMarkdown.ico` im Projekt-Root
  war eine byte-identische, nie-getrackte Dopplung von
  `assets/cleanmarkdown.ico` (MD5 `ca353703b98b32383468491519da4c5f`,
  von keinem Code/Build-Skript referenziert) -- entfernt.
- **Testinfrastruktur:** Tests, die über `MainWindow()`/`SettingsStore()`
  laufen, teilten sich bislang die echte `%APPDATA%\CleanMarkdown\settings.json`
  des Nutzers (inkl. Schreibzugriff beim `closeEvent`). Ein Test mit
  testspezifischem `output_dir` hatte dadurch die reale Konfigurationsdatei
  kontaminiert und in der Folge einen produktiven Export in einen
  Pytest-Tempordner umgeleitet. Fix: neue `autouse`-Fixture
  `isolated_appdata` in `tests/conftest.py` isoliert `%APPDATA%` pro Test;
  die reale `settings.json` wurde manuell wiederhergestellt.

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
