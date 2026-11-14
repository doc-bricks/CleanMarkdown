---
name: cleanmarkdown
description: Local-first Markdown viewer and editor (PySide6 desktop app, Web PWA companion, Flutter mobile port) with reading mode, syntax highlighting, math preview, vector PDF export, and portable cleanmarkdown-session-v1.json handoff.
version: "1.0.5"
license: MIT
---

# CleanMarkdown Product Skill

Guide for humans and AI coding/desktop assistants operating **CleanMarkdown** (`v1.0.5`), a 100% offline, zero-egress Markdown reader and editor across Desktop (PySide6), Web Companion (`web_companion/`), and Flutter Mobile (`flutter_port/`).

## Supported Scope & Clear Boundaries

### What CleanMarkdown does
- **Render & Edit locally:** Dual-tab `Reading` (`QTextBrowser`) and raw `Editor` (`QPlainTextEdit`) workspace with optional scroll synchronization and a 4-group syntax highlighter.
- **Strict UTF-8 Opening:** Rejects files containing invalid UTF-8 before touching the active editor buffer; unsaved edits and original file bytes remain untouched.
- **Math & Figures:** Renders `$...$`, `$$...$$`, `\(...\)`, and `\[...\]` formulas without external TeX runtimes and wraps standalone images in `<figure>` / `<figcaption>` while preserving custom hyperlink targets.
- **Image Inspection:** Opens `ImagePreviewDialog` on image click with Zoom (`+` / `-` / `Fit` / `1:1`), clipboard copy, and image metadata.
- **Vector PDF Export:** Generates timestamped PDF files via `QPrinter` and refuses overwriting the active `.md` source file or its path aliases.
- **Portable Session Handoff:** Imports and exports `cleanmarkdown-session-v1.json` between Desktop, Web Companion PWA, and companion workflows (see [`EXPORTFORMAT.md`](EXPORTFORMAT.md)).
- **6-Language UI:** German (`de`), English (`en`), Spanish (`es`), Chinese (`zh`), Japanese (`ja`), and Russian (`ru`).

### What CleanMarkdown intentionally does NOT do
- **Zero-Egress / No Cloud:** Performs no network calls, no remote API fetches, no telemetry, and no cloud account login.
- **No Silent Encoding Guessing:** Non-UTF-8 files (e.g. Latin-1 / CP1252) must be converted to UTF-8 externally before opening.
- **No WYSIWYG Lock-in:** Edits remain standard UTF-8 Markdown; formatting removal strips Markdown markers explicitly on selection.
- **No Arbitrary Headless Document Conversion CLI Flag:** PDF export and interactive editing run inside the Qt workspace (`main.py`), while `--smoke-test` and `--self-test` provide deterministic headless verification. Planned or companion-only extensions are documented in `EXPORTFORMAT.md` (`cleanmarkdown-session-v1.json` active; `cleanmarkdown-bundle-v1.zip` reserved).

## Prerequisites & Safe Setup (No Credentials Required)

- **Python:** `3.10`, `3.11`, `3.12`, or `3.13`
- **Runtime packages:** `PySide6>=6.5.0,!=6.12.0`, `markdown>=3.4.0`
- **Install in an isolated virtual environment (recommended):**

```bash
git clone https://github.com/doc-bricks/CleanMarkdown.git
cd CleanMarkdown
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Entry Points, Commands & Exit Codes

All commands run in standard unprivileged user mode (`Non-Elevation`):

| Task | Command | Environment / Notes | Expected Exit Code |
| :--- | :--- | :--- | :--- |
| Launch desktop GUI | `python main.py` | Or `start.bat` on Windows (uses `.venv` if present) | `0` on clean exit |
| Open specific file on launch | `python main.py path/to/document.md` | Non-existing paths are ignored cleanly | `0` on clean exit |
| Headless Qt smoke test | `QT_QPA_PLATFORM=offscreen python main.py --smoke-test` | Initializes `MainWindow` and quits immediately | `0` on success |
| Full self-test suite | `QT_QPA_PLATFORM=offscreen PYTHONIOENCODING=utf-8 python main.py --self-test` | Isolated `APPDATA` temp dir; tests open/save/sync/PDF export and prints `<check>: ok` | `0` if all checks pass, `1` if any check fails |
| Translation parity check | `python manage_translations.py --check` | Validates all 143 i18n keys across 6 languages (`de/en/es/zh/ja/ru`) | `0` on 100% parity, `1` on gaps |
| Test suite & lint | `ruff check . && python -m pytest -ra -v` | Requires dev/test deps (`pytest>=9.1.1`, `ruff>=0.9.0`, `Pillow>=10.0`) | `0` on pass |
| Web renderer security tests | `node --test tests/test_web_renderer.cjs` | Node 22+ verifies fence escaping in `web_companion/` | `0` on 6/6 pass |

## Assisting a User: Common Workflows & Verification

1. **Pre-flight verify a checkout before editing documents:**
   ```bash
   QT_QPA_PLATFORM=offscreen PYTHONIOENCODING=utf-8 python main.py --self-test
   ```
   Confirm every printed line ends with `: ok` and exit status is `0`.
2. **Generate a portable `cleanmarkdown-session-v1.json` for Desktop or Web Companion handoff:**
   Required fields per [`EXPORTFORMAT.md`](EXPORTFORMAT.md):
   ```json
   {
     "version": "cleanmarkdown-session-v1",
     "fileName": "notes.md",
     "markdown": "# Notes\n\nReady for local review.",
     "theme": "paper",
     "workspace": "split",
     "updatedAt": "2026-11-14T06:00:00"
   }
   ```
   Valid values:
   - `version`: exactly `"cleanmarkdown-session-v1"`
   - `theme`: `"paper"` or `"night"`
   - `workspace`: `"read"`, `"write"`, or `"split"`
   - `updatedAt`: ISO-8601 timestamp string
   Verify with Python that UTF-8 JSON parses cleanly and contains all 6 required keys before handing the file to the user for `File -> Open...`.
3. **Validate localization edits safely:**
   After modifying `locales/translations.json`, always run `python manage_translations.py --check` and confirm exit code `0`.

## Further References

- Machine entry point: [`llms.txt`](llms.txt) (compatibility pointer: [`llm.txt`](llm.txt))
- Session & bundle contract: [`EXPORTFORMAT.md`](EXPORTFORMAT.md)
- CI & multi-platform test contract: [`docs/CI-CONTRACT.md`](docs/CI-CONTRACT.md)
- Security & zero-egress guarantees: [`SECURITY.md`](SECURITY.md)
- Multilingual user docs: [`README.md`](README.md), [`README_DE.md`](README_DE.md), [`README_es.md`](README_es.md)
