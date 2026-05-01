# CleanMarkdown

Fast local Markdown viewer and editor with a clean reading mode, raw Markdown editing, PDF export, and DE/EN UI.

[Deutsche README](README_DE.md)

## Features

- Two clear tabs: `Reading` and `Editor`
- Raw Markdown editor with helper buttons instead of WYSIWYG complexity
- Clean rendered reading view
- PDF export with timestamp-based filenames
- Autosave with configurable interval
- German and English UI
- Light and dark theme
- Optional top action bar for a cleaner default layout
- Optional scroll sync when switching between reading and editor tabs
- Lightweight math preview for `$...$`, `$$...$$`, `\(...\)`, and `\[...\]` in reading view and PDF export
- Calm syntax highlighting for key Markdown groups
- Relative images and local asset links resolve from the opened Markdown file's folder

## Screenshot

![CleanMarkdown main window](README/screenshots/main_view.png)

## Installation

### Requirements

- Windows with Python 3.12+
- Packages from `requirements.txt`

### Steps

```powershell
python -m pip install -r requirements.txt
python main.py
```

Or start it directly on Windows:

```bat
start.bat
```

## Usage

1. Open a Markdown file from `File -> Open...` or start writing in the editor.
2. Switch between `Reading` and `Editor` with the two tabs.
3. Use the editor helper buttons to insert or format Markdown structures.
4. Export the current document via `File -> Export PDF`.
5. Adjust language, theme, autosave, export behavior, toolbar visibility, and scroll sync in `View -> Settings`.

Math is intentionally lightweight: formulas stay readable and styled locally without a separate TeX runtime.

Relative image links such as `![Diagram](diagram.png)` resolve against the current Markdown file location. After `Save as`, the preview refreshes so moved or newly created asset references use the new folder immediately.

## Local Privacy

CleanMarkdown opens and saves files locally. Normal editing, preview, and PDF export do not upload documents to a cloud service.

## Editor Highlighting

The raw editor uses a restrained four-group color system:

- Blue for headings and emphasis
- Green for inline code and fenced code blocks
- Pink/magenta for links, images, and footnotes
- Soft gray-violet for lists, quotes, tables, and structural markers

## Project Status

Current version: `0.3.1`

CleanMarkdown is already usable as a small public MVP. The current focus is practical polish around real-world rendering and PDF export, not feature bloat.

## Development

```powershell
python -m py_compile main.py
python main.py --self-test
python main.py
```

The self-test covers file opening, save/export flows, task lists, math markup, scroll sync, and relative asset resolution.

## License

This project is licensed under the [MIT License](LICENSE).
