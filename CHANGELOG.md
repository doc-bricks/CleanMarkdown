# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Fixed
- **Bilder im Lesemodus wirkten wie Hintergrundelemente statt echter Bloecke
  im Dokumentfluss (T-20260728-01):** Qt's `QTextDocument`-HTML-Engine
  behandelt `<figure>` nicht als Block-Container und ignoriert
  `display: block` am `<img>`-Element selbst. Ein alleinstehendes Bild
  konnte dadurch im selben Textblock wie umgebender Text landen und wurde
  ueberlagert statt eigenstaendig dargestellt. Das Bild liegt in `<figure>`
  jetzt zusaetzlich in einem von Qt als eigener Block erkannten
  `<p class="image-block">`; nachfolgender Text beginnt nachweislich
  unterhalb des Bildes. Eine alleinstehende Bildzeile wird jetzt auch dann
  als eigener Block herausgeloest, wenn Markdown sie mangels Leerzeile mit
  benachbartem Text in EINEN Absatz gezogen hat -- ein Bild inmitten eines
  laufenden Satzes bleibt bewusst inline. Ueberbreite Bilder werden weiterhin
  seitenverhaeltnistreu auf die Lesebreite verkleinert, kleine Bilder nicht
  hochskaliert. Zusaetzlich behoben: Bereits HTML-escapte Alt-/Titeltexte
  wurden vor dem Bau der Bildunterschrift ein zweites Mal escaped
  (`&amp;` -> `&amp;amp;`); sie werden jetzt einmalig dekodiert und danach
  genau einmal escaped. Neue echte `QTextDocument`-/`QTextBrowser`-Geometrietests
  in `tests/test_image_block_layout.py` decken Block-Reihenfolge,
  Nicht-Ueberlappung, Skalierung, relative Pfade und beide Themes ab.

### Removed
- **Veraltete Web-Companion/PWA-Doku entfernt (T-20260821-242217156):** Die
  Web-Companion/PWA-Oberflaeche wurde bereits mit Commit `8cd31be` vollstaendig
  entfernt (`web_companion/` existiert nicht mehr im getrackten Baum). Ein
  spaeterer README-Umbau (`d39224a`) hatte "Web Companion (PWA)" versehentlich
  wieder als aktive Produktflaeche in die Vergleichstabelle und das
  Architektur-Diagramm von `README.md`/`README_DE.md` eingefuegt; die
  Tabellenspalte und der Diagramm-Verweis "PWA Handoff" sind jetzt entfernt
  (nur noch Desktop-App und Flutter-Mobile-Port als aktive Editionen). In
  `EXPORTFORMAT.md` sind die drei verbliebenen Web-Companion-Nennungen
  (Zweck-, Status- und Bundleformat-Bulletpoints) auf den tatsaechlichen
  Ist-Stand korrigiert, ohne die Oberflaeche als kuenftig geplant
  umzudeuten. Die Flutter-DE/EN-Paritaet war bereits gegeben und blieb
  unveraendert.

## [1.0.1] - 2026-08-23

### Fixed
- **Dateityp-Zuordnung im Store-Paket (`.md`) — Store-Version registrierte keinen Handler:**
  Das `AppxManifest.xml` deklarierte weder `uap:FileTypeAssociation` noch
  `uap3:AppExecutionAlias`. Nach einer Store-Installation existierte deshalb auf keinem
  System eine `.md`-Zuordnung, und CleanMarkdown erschien nicht im Dialog "Öffnen mit".
  Das Manifest deklariert jetzt `.md`, `.markdown`, `.mdown` und `.mkd` sowie den
  Ausführungsalias `cleanmarkdown.exe`.
- **`build_exe.bat` — Parserfehler im Exclude-Scanner-Zweig:** Ungeschützte Klammern in der
  `echo`-Zeile des `else`-Blocks zerrissen den `if`-Block beim Einlesen durch `cmd`, wodurch
  der komplette Build mit "baue kann syntaktisch an dieser Stelle nicht verarbeitet werden"
  abbrach — unabhängig davon, ob der Scanner gefunden wurde. Regression aus `914f6e0`.

### Changed
- **Store-Paket auf Verzeichnis-Build (onedir) umgestellt:** Das MSIX enthielt bisher eine
  PyInstaller-onefile-EXE, die bei jedem Start ins Temp-Verzeichnis entpackte (lange
  Startzeit). Das Paket enthält jetzt den onedir-Build; MSIX-Größe 73,6 MB -> 49,8 MB.
- Version auf 1.0.1 angehoben (`main.py`, `pyproject.toml`, `store_package.json`,
  `AppxManifest.xml`, `build_exe.bat`).

### Known Issues
- Die onefile-Release-EXE (`releases/v1.0.1/CleanMarkdown-1.0.1-win64.exe`) startet nicht
  zuverlässig und ist nicht ausgeliefert; das Store-Paket nutzt den geprüften onedir-Build.


### Added
- **Interactive Bilingual Mermaid Architecture & Lifecycle Diagrams (Mermaid-Diagramme):**
  - Integrated interactive `flowchart TD` architecture diagrams in `README.md` and `README_DE.md` visualizing UI Presentation, Markdown AST Core Pipeline, and Storage/Export Layer.
  - Integrated `sequenceDiagram` in English and German detailing document open, live AST transformation, interactive image inspection, vector PDF export, and local atomic autosave lifecycle.
- **Visual Showcase Gallery & Screenshots (Screenshot-Galerie):**
  - Added visual preview matrix with side-by-side Light and Dark reading mode, raw editor view, and full workspace overview across both READMEs.
- **Bilingual Quick Navigation & Sibling Tools Ecosystem Matrix (Schnellnavigation & Ökosystem):**
  - Added 12-section quick jump navigation to `README.md` and `README_DE.md`.
  - Added sibling tools matrix linking partner repositories across `doc-bricks`, `file-bricks`, `dev-bricks`, `ellmos-ai`, and `open-bricks`.
- **Automated Metadata & Contract Tests (Metadaten- & Paritätstests):**
  - Expanded `tests/test_metadata.py` with 5 new contract tests covering bilingual README parity, Mermaid syntax, sibling ecosystem links, version consistency (`1.0.0`), and local-first zero-egress invariants (10/10 contract tests, suite total 105 passed). [G 2026-08-23]

### Changed
- **Metadata, URLs & Badges Modernization (Metadaten & Badges):**
  - Synchronized Shields.io badges across `README.md` and `README_DE.md` (CI, 105 Tests, Python 3.10-3.13, Platforms, Zero-Egress, Local-First, MIT License, Ecosystem `doc-bricks`, Umbrella `open-bricks`, Version 1.0.0, LLM-Ready `llms.txt`).
  - Added PEP 621 URLs (`Documentation`, `Security`, `Umbrella`) in `pyproject.toml`.
  - Synchronized `store_package.json` version to `1.0.0.0`.
  - Updated `llms.txt` timestamp to `2026-08-23` and test count to 105. [G 2026-08-23]

### Fixed
- **Figure & Linked Image Rendering Preservation (Figure- & Hyperlink-Rendering):**
  - Fixed `_render_figures_and_captions` in `main.py` where standalone linked markdown images (`[![Alt](img.png)](https://example.com)`) were incorrectly wrapped with duplicate outer anchor tags (`<a href="img.png"><p><a href="https://example.com">...</a></p></a>`) that overrode user hyperlinks with local asset paths and generated invalid nested `<p>` inside anchor elements.
  - Properly un-nested `<p>` tags and preserved explicit anchor attributes and targets (`<figure><a href="..."><img></a><figcaption>...</figcaption></figure>`).
  - Added contract regression tests `test_render_figures_and_captions_preserves_custom_link`, `test_pipeline_linked_image_renders_figure_with_custom_link`, and paragraph un-nesting assertion.
  - Test suite expanded to 100 tests (100/100 passed, 100% green). [G 2026-08-21]

### Added
- **Automated Metadata Parity & CI Contract Testsuite (Metadaten- & CI-Vertrag):**
  - Created `tests/test_metadata.py` with 5 contract tests validating CI workflow action versions and matrices, PEP 621 classifiers, bilingual security policy invariants, documentation badges, and `llms.txt` currency.
  - Test suite expanded to 98 tests (98/98 passed, 100% green in 3.4s). [G 2026-08-21]

### Changed
- **CI/CD Modernization & Matrix Expansion (CI-Härtung):**
  - Updated GitHub Actions `.github/workflows/tests.yml` to official modern actions (`actions/checkout@v4`, `actions/setup-python@v5` with pip caching).
  - Expanded test matrix across Linux (`ubuntu-latest`) and Windows (`windows-latest`) for Python 3.10, 3.11, 3.12, and 3.13.
  - Integrated automated `ruff check .` gate and bytecode compilation check into CI pipeline. [G 2026-08-21]
- **Linter & Code Hygiene (Code-Hygiene):**
  - Fixed 11 ruff linter warnings across `main.py`, `manage_translations.py`, `translator.py`, `tests/source_platform_smoke.py`, `tests/test_file_handling.py`, and `tests/test_store_materials.py`.
  - Added `[tool.ruff]` and `[tool.ruff.lint]` configuration in `pyproject.toml`, plus standard PEP 621 classifiers (`OS Independent`, `Python 3.13`). [G 2026-08-21]
- **Security Policy & Zero-Egress Invariants (Sicherheitsrichtlinie):**
  - Hardened bilingual `SECURITY.md` with explicit Local-First and Zero-Egress guarantees, direct security contacts (`security@ellmos.ai`, `support@lukasgeiger.com`), and GitHub Security Advisories link. [G 2026-08-21]
- **Image Display Improvements (Bessere Bildanzeige):**
  - High-resolution interactive `ImagePreviewDialog` with Zoom (+/- / Fit / 1:1), Clipboard Copying, and image metadata.
  - Enhanced HTML rendering wrapping markdown images into `<figure>` elements with clickable `<a href="...">` links and `<figcaption>` text from `title`/`alt`.
  - Responsive image styling with rounded borders, dark/light theme elevation shadows, and adaptive scaling.
  - Enhanced `_insert_image` dialog supporting both local file browsing (`QFileDialog`) with relative path resolution and URL entry.
  - Added 7 new i18n keys (`image_preview`, `zoom_in`, `zoom_out`, `zoom_reset`, `zoom_fit`, `copy_image`, `select_image_file`) across all 6 supported languages (`de`, `en`, `es`, `zh`, `ja`, `ru`).

### Changed
- **Headless Test Suite Stabilization & Print Subsystem Isolation (Headless-Test-Stabilisierung):**
  - Isolated `QPrinter` and `document.print_` in `tests/test_file_handling.py` (`test_export_pdf_auto_saves_unsaved_document_before_export`) to prevent indefinite blocking caused by Windows Print Spooler / GDI printer queries in headless `QT_QPA_PLATFORM=offscreen` environments.
  - Test suite fully verified with 93 passing tests (93/93 passed, 100% green in 2.6s). [G 2026-08-20]
- **Privacy & Build Script Sanitization (Datenschutz & Build-Hygiene):**
  - Removed hardcoded `C:\Users\User` path in `build_exe.bat` in favor of `%USERPROFILE%` and dynamic `%SOFTWARE_ROOT%` resolution.
  - Verified 0 secrets, tokens, or hardcoded user paths across all 85 tracked repository files. [G 2026-08-20]
- **Docstring & Translation Normalization (Typografie & Strings):**
  - Standardized UTF-8 umlauts and comments across `main.py`, `manage_translations.py`, and `translator.py`. [G 2026-08-20]
- **Discoverability, Badges & Metadata Parity (Metadaten & Dokumentation):**
  - Synchronized `README.md` and `README_DE.md` version badges to `1.0.0` and added `Tests: 93 passed` badge.
  - Updated `llms.txt` timestamp to `2026-08-20` and synced test counts to 93. [G 2026-08-20]
- **Build Infrastructure & Preflight Guard (Build-Infrastruktur & Preflight-Absicherung):**
  - Hardened `build_exe.bat` with dynamic `SOFTWARE_ROOT` resolution and fail-safe guard for `build_exclude_scanner.py`.
  - Added automated preflight test `test_build_exe_bat_guarded_preflight` in `tests/test_store_materials.py` (92/92 passed, 100% green). [G 2026-08-14]
- **Discoverability, SEO & Maintenance (Sichtbarkeit & Pflege):**
  - Updated `llms.txt` `Last-checked` timestamp to 2026-08-03 and expanded 6-language UI context.
  - Added Ökosystem (`doc-bricks`) & Umbrella (`open-bricks`) Shields.io badges and GFM `llms.txt` discoverability callout in `README.md` and `README_DE.md`.
  - Updated version badges to `0.3.3` across documentation.
  - Verified pytest test suite (91/91 passed). [G 2026-08-03]

## [1.0.0] - 2026-08-11

### Released
- **Windows-Store-Release:** CleanMarkdown ist seit 2026-08-11 im Microsoft
  Store live (MSIX-Paket 1.0.0.0, gebaut 2026-08-10). Versionsangleichung in
  `main.py` (`APP_VERSION`), `pyproject.toml`, README/README_DE,
  PRIVACY_POLICY und SUPPORT auf `1.0.0`. Build-Ausgabeordner
  `store_package/` ist ab jetzt gitignored (141 MB Artefakte bleiben lokal).

## [0.3.3] - 2026-07-25

### Changed
- Standardized project metadata with new PEP 621 `pyproject.toml` including `[tool.pytest.ini_options]` (`pythonpath = "."`).
- Updated `llms.txt` `Last-checked` timestamp to 2026-07-25.
- Verified test suite execution with pytest (90 passed tests).



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
- **Desktop accessibility:** The reading view, Markdown editor, workspace tabs,
  and both toolbars now expose localized accessible names and descriptions.
  This preserves the compact visual design while giving screenreader users
  clear orientation within the main workspace.
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
