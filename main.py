from __future__ import annotations

import html
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import markdown
from PySide6.QtCore import QMarginsF, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QColor,
    QDesktopServices,
    QIcon,
    QKeySequence,
    QPageLayout,
    QSyntaxHighlighter,
    QTextCharFormat,
    QTextCursor,
)
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QStyle,
    QTabWidget,
    QTextBrowser,
    QToolBar,
    QVBoxLayout,
    QWidget,
)


APP_NAME = "CleanMarkdown"
APP_VERSION = "0.3.1"
ICON_RELATIVE_PATH = ("assets", "cleanmarkdown.ico")


def resource_path(*parts: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path.joinpath(*parts)


def load_app_icon() -> QIcon:
    icon_path = resource_path(*ICON_RELATIVE_PATH)
    return QIcon(str(icon_path)) if icon_path.exists() else QIcon()


def configure_application(app: QApplication) -> None:
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    icon = load_app_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)


TRANSLATIONS = {
    "de": {
        "app_title": "CleanMarkdown",
        "tab_view": "Lesen",
        "tab_editor": "Editor",
        "untitled": "Unbenannt",
        "file": "Datei",
        "edit": "Bearbeiten",
        "view": "Ansicht",
        "open": "Öffnen...",
        "save": "Speichern",
        "save_as": "Speichern unter...",
        "export_pdf": "PDF exportieren",
        "settings": "Einstellungen",
        "quit": "Beenden",
        "undo": "Rückgängig",
        "redo": "Wiederholen",
        "saved": "Gespeichert",
        "opened": "Datei geöffnet",
        "exported": "PDF exportiert",
        "autosave_saved": "Automatisch gespeichert",
        "autosave_skip": "Autosave übersprungen, Datei wurde noch nie gespeichert",
        "nothing_to_save": "Nichts zu speichern",
        "save_changes": "Änderungen speichern?",
        "save_changes_text": "Es gibt ungespeicherte Änderungen.",
        "viewer_empty": "",
        "open_title": "Markdown-Datei öffnen",
        "save_title": "Markdown speichern",
        "export_title": "PDF exportieren",
        "settings_title": "Einstellungen",
        "error": "Fehler",
        "cannot_open": "Datei konnte nicht geöffnet werden.",
        "cannot_save": "Datei konnte nicht gespeichert werden.",
        "cannot_export": "PDF konnte nicht erstellt werden.",
        "language": "Sprache",
        "theme": "Design",
        "default_mode": "Start-Tab",
        "autosave_enabled": "Autosave aktiv",
        "autosave_interval": "Autosave-Intervall (Sekunden)",
        "export_mode": "Export-Ziel",
        "export_confirm": "Beim PDF-Export Speicherfenster anzeigen",
        "output_dir": "Eigener Output-Ordner",
        "browse": "Auswählen...",
        "file_toolbar_visible": "Obere Aktionsleiste anzeigen",
        "editor_toolbar_default": "Editorleiste beim Start einklappen",
        "sync_scroll_positions": "Scroll-Position zwischen Lesen und Editor synchronisieren",
        "mode_view": "Lesen",
        "mode_editor": "Editor",
        "theme_dark": "Dark",
        "theme_bright": "Hell",
        "export_source": "Neben der Markdown-Datei",
        "export_dedicated": "Eigener Output-Ordner",
        "toolbar_file": "Datei",
        "toolbar_format": "Werkzeuge",
        "toolbar_history": "Verlauf",
        "select_output": "Output-Ordner wählen",
        "heading_1": "Überschrift 1",
        "heading_2": "Überschrift 2",
        "heading_3": "Überschrift 3",
        "bold": "Fett",
        "italic": "Kursiv",
        "bullet_list": "Aufzählung",
        "numbered_list": "Nummerierte Liste",
        "checklist": "Checkliste",
        "blockquote": "Zitat",
        "inline_code": "Inline-Code",
        "code_block": "Codeblock",
        "horizontal_rule": "Trennlinie",
        "table": "Tabelle",
        "link": "Link",
        "image": "Bild",
        "footnote": "Fußnote",
        "link_url": "Link-URL",
        "image_url": "Bildpfad oder URL",
        "image_alt": "Alt-Text",
        "footnote_id": "Fußnoten-ID",
        "status_ready": "Bereit",
        "open_tip": "Markdown-Datei öffnen",
        "save_tip": "Aktuelle Datei speichern",
        "save_as_tip": "Datei unter neuem Namen speichern",
        "export_tip": "Aktuelle Ansicht als PDF exportieren",
        "settings_tip": "Design, Sprache, Autosave und Export einstellen",
        "undo_tip": "Letzte Änderung rückgängig machen",
        "redo_tip": "Rückgängig gemachte Änderung wiederherstellen",
        "discard": "Verwerfen",
        "cancel": "Abbrechen",
        "read_mode_tip": "Zum Lesemodus wechseln",
        "edit_mode_tip": "Zum Editor wechseln",
        "collapse_toolbar_tip": "Editorleiste einklappen",
        "expand_toolbar_tip": "Editorleiste ausklappen",
        "format_only_editor": "Nur im Editor verfügbar",
    },
    "en": {
        "app_title": "CleanMarkdown",
        "tab_view": "Reading",
        "tab_editor": "Editor",
        "untitled": "Untitled",
        "file": "File",
        "edit": "Edit",
        "view": "View",
        "open": "Open...",
        "save": "Save",
        "save_as": "Save As...",
        "export_pdf": "Export PDF",
        "settings": "Settings",
        "quit": "Quit",
        "undo": "Undo",
        "redo": "Redo",
        "saved": "Saved",
        "opened": "File opened",
        "exported": "PDF exported",
        "autosave_saved": "Autosaved",
        "autosave_skip": "Autosave skipped, file has not been saved yet",
        "nothing_to_save": "Nothing to save",
        "save_changes": "Save changes?",
        "save_changes_text": "There are unsaved changes.",
        "viewer_empty": "",
        "open_title": "Open markdown file",
        "save_title": "Save markdown file",
        "export_title": "Export PDF",
        "settings_title": "Settings",
        "error": "Error",
        "cannot_open": "Could not open the file.",
        "cannot_save": "Could not save the file.",
        "cannot_export": "Could not create the PDF.",
        "language": "Language",
        "theme": "Theme",
        "default_mode": "Default tab",
        "autosave_enabled": "Enable autosave",
        "autosave_interval": "Autosave interval (seconds)",
        "export_mode": "Export target",
        "export_confirm": "Show save dialog on PDF export",
        "output_dir": "Dedicated output folder",
        "browse": "Browse...",
        "file_toolbar_visible": "Show top action bar",
        "editor_toolbar_default": "Collapse editor toolbar on startup",
        "sync_scroll_positions": "Sync scroll position between reading and editor",
        "mode_view": "Reading",
        "mode_editor": "Editor",
        "theme_dark": "Dark",
        "theme_bright": "Light",
        "export_source": "Next to the markdown file",
        "export_dedicated": "Dedicated output folder",
        "toolbar_file": "File",
        "toolbar_format": "Tools",
        "toolbar_history": "History",
        "select_output": "Choose output folder",
        "heading_1": "Heading 1",
        "heading_2": "Heading 2",
        "heading_3": "Heading 3",
        "bold": "Bold",
        "italic": "Italic",
        "bullet_list": "Bullets",
        "numbered_list": "Numbered list",
        "checklist": "Checklist",
        "blockquote": "Quote",
        "inline_code": "Inline code",
        "code_block": "Code block",
        "horizontal_rule": "Rule",
        "table": "Table",
        "link": "Link",
        "image": "Image",
        "footnote": "Footnote",
        "link_url": "Link URL",
        "image_url": "Image path or URL",
        "image_alt": "Alt text",
        "footnote_id": "Footnote ID",
        "status_ready": "Ready",
        "open_tip": "Open a markdown file",
        "save_tip": "Save the current file",
        "save_as_tip": "Save the file under a new name",
        "export_tip": "Export the current view as PDF",
        "settings_tip": "Adjust theme, language, autosave and export behavior",
        "undo_tip": "Undo the last change",
        "redo_tip": "Redo the last undone change",
        "discard": "Discard",
        "cancel": "Cancel",
        "read_mode_tip": "Switch to reading mode",
        "edit_mode_tip": "Switch to the editor",
        "collapse_toolbar_tip": "Collapse the editor toolbar",
        "expand_toolbar_tip": "Expand the editor toolbar",
        "format_only_editor": "Available in the editor only",
    },
}


THEMES = {
    "dark": {
        "editor_colors": {
            "accent_heading": "#84b8ff",
            "accent_code": "#73d4a6",
            "accent_meta": "#e79bd2",
            "accent_structure": "#aeb6d8",
        },
        "app": """
            QMainWindow, QWidget { background: #15181d; color: #f3f6fa; }
            QTabWidget::pane { border: 1px solid #2b313c; background: #111418; top: -1px; }
            QTabBar::tab { background: #18202b; color: #b8c6d8; padding: 8px 18px; border: 1px solid #2b313c; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-top: 7px; }
            QTabBar::tab:selected { background: #f3f7fc; color: #0f1722; margin-top: 0px; padding-top: 10px; border-bottom-color: #f3f7fc; }
            QToolBar { background: rgba(13, 25, 42, 0.92); border-bottom: 1px solid #243449; spacing: 6px; padding: 4px 6px; }
            QToolButton { background: rgba(20, 34, 54, 0.88); color: #f3f6fa; border: 1px solid #31435a; padding: 6px 8px; margin: 2px; border-radius: 8px; min-width: 30px; font-size: 15px; font-weight: 600; }
            QToolButton:hover { background: rgba(37, 63, 99, 0.95); border-color: #6d98c7; }
            QToolButton:pressed { background: #131922; }
            QToolButton#ExportPdfButton { background: #bf2f34; color: #ffffff; border: 1px solid #9b2328; min-width: 48px; padding: 6px 12px; }
            QToolButton#ExportPdfButton:hover { background: #cf4045; border-color: #b52c31; }
            QToolButton#ExportPdfButton:pressed { background: #9f2024; }
            QPlainTextEdit, QTextBrowser, QLineEdit, QComboBox, QSpinBox {
                background: #0f141b;
                color: #f2f5f8;
                border: 1px solid #2f3745;
                selection-background-color: #31527a;
                border-radius: 10px;
                padding: 8px 10px;
            }
            QMenuBar, QMenu, QStatusBar, QDialog { background: #15181d; color: #f3f6fa; }
            QPushButton { background: rgba(20, 34, 54, 0.88); color: #f3f6fa; border: 1px solid #31435a; padding: 6px 10px; border-radius: 8px; }
            QPushButton:hover { background: rgba(37, 63, 99, 0.95); }
            QCheckBox, QLabel { color: #f3f6fa; }
            QWidget#EditorToolbarHost { background: rgba(12, 21, 34, 0.72); border-bottom: 1px solid #243449; }
            QWidget#EditorToolbarHost QToolButton { background: rgba(23, 35, 53, 0.42); border: 1px solid rgba(68, 94, 124, 0.42); border-radius: 7px; }
            QWidget#EditorToolbarHost QToolButton:hover { background: rgba(34, 58, 92, 0.58); border-color: rgba(117, 154, 196, 0.72); }
        """,
        "html": """
            body { font-family: "Segoe UI", sans-serif; line-height: 1.65; color: #f4f7fb; background: #11161d; margin: 28px; }
            h1, h2, h3, h4, h5, h6 { color: #ffffff; margin-top: 1.35em; }
            a { color: #8ec8ff; }
            code { background: #1f2733; color: #f7b5c5; padding: 2px 6px; border-radius: 4px; }
            pre { background: #151c26; color: #f4f7fb; padding: 14px; border-radius: 8px; overflow-x: auto; }
            blockquote { border-left: 4px solid #4f7caf; margin: 1em 0; padding: 0.4em 1em; color: #d6deea; background: #16202c; }
            table { width: 100%; border-collapse: collapse; margin: 1em 0; }
            th, td { border: 1px solid #324052; padding: 8px 10px; }
            th { background: #1a2430; }
            hr { border: none; border-top: 1px solid #39475c; margin: 1.8em 0; }
            img { max-width: 100%; }
            ul.task-list { list-style: none; padding-left: 0.2em; }
            .task-box { display: inline-block; min-width: 1.5em; color: #9bc0e7; }
            .math-inline { font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif; background: rgba(46, 67, 93, 0.55); color: #f6fbff; border: 1px solid #496a8f; border-radius: 6px; padding: 0.08em 0.38em; white-space: pre-wrap; }
            .math-block { font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif; margin: 1.15em 0; padding: 0.85em 1em; border-left: 4px solid #6e98c2; background: #162332; color: #f4f8fc; border-radius: 8px; white-space: pre-wrap; overflow-x: auto; }
        """,
    },
    "bright": {
        "editor_colors": {
            "accent_heading": "#2f67a6",
            "accent_code": "#2f7f63",
            "accent_meta": "#a54884",
            "accent_structure": "#667099",
        },
        "app": """
            QMainWindow, QWidget { background: #f5f8fc; color: #121417; }
            QTabWidget::pane { border: 1px solid #d6deea; background: #ffffff; top: -1px; }
            QTabBar::tab { background: #dde6f2; color: #415770; padding: 8px 18px; border: 1px solid #d6deea; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-top: 7px; }
            QTabBar::tab:selected { background: #ffffff; color: #11243c; margin-top: 0px; padding-top: 10px; border-bottom-color: #ffffff; }
            QToolBar { background: rgba(226, 236, 248, 0.92); border-bottom: 1px solid #d2ddec; spacing: 6px; padding: 4px 6px; }
            QToolButton { background: rgba(255, 255, 255, 0.96); color: #17304f; border: 1px solid #c8d6e6; padding: 6px 8px; margin: 2px; border-radius: 8px; min-width: 30px; font-size: 15px; font-weight: 600; }
            QToolButton:hover { background: rgba(224, 236, 250, 0.98); border-color: #6f8fb8; }
            QToolButton:pressed { background: #d8e6f8; }
            QToolButton#ExportPdfButton { background: #c63a40; color: #ffffff; border: 1px solid #ab2f34; min-width: 48px; padding: 6px 12px; }
            QToolButton#ExportPdfButton:hover { background: #d84b51; border-color: #b6373c; }
            QToolButton#ExportPdfButton:pressed { background: #ab2f34; }
            QPlainTextEdit, QTextBrowser, QLineEdit, QComboBox, QSpinBox {
                background: #ffffff;
                color: #13161a;
                border: 1px solid #d1dae8;
                selection-background-color: #b7d8ff;
                border-radius: 10px;
                padding: 8px 10px;
            }
            QMenuBar, QMenu, QStatusBar, QDialog { background: #f5f8fc; color: #14171b; }
            QPushButton { background: rgba(255, 255, 255, 0.96); color: #17304f; border: 1px solid #c8d6e6; padding: 6px 10px; border-radius: 8px; }
            QPushButton:hover { background: rgba(224, 236, 250, 0.98); }
            QCheckBox, QLabel { color: #14171b; }
            QWidget#EditorToolbarHost { background: rgba(228, 236, 246, 0.72); border-bottom: 1px solid #d2ddec; }
            QWidget#EditorToolbarHost QToolButton { background: rgba(255, 255, 255, 0.72); border: 1px solid rgba(186, 202, 222, 0.88); border-radius: 7px; }
            QWidget#EditorToolbarHost QToolButton:hover { background: rgba(235, 243, 252, 0.96); border-color: rgba(102, 130, 168, 0.92); }
        """,
        "html": """
            body { font-family: "Georgia", "Segoe UI", serif; line-height: 1.72; color: #1b1e23; background: #ffffff; margin: 28px; }
            h1, h2, h3, h4, h5, h6 { color: #111317; margin-top: 1.35em; }
            a { color: #004e92; }
            code { background: #eef4fb; color: #21476f; padding: 2px 6px; border-radius: 4px; }
            pre { background: #f4f8fd; color: #1b1e23; padding: 14px; border-radius: 8px; overflow-x: auto; border: 1px solid #d6e0ec; }
            blockquote { border-left: 4px solid #7fa6cf; margin: 1em 0; padding: 0.4em 1em; color: #455667; background: #f6f9fd; }
            table { width: 100%; border-collapse: collapse; margin: 1em 0; }
            th, td { border: 1px solid #d3dcea; padding: 8px 10px; }
            th { background: #edf3fb; }
            hr { border: none; border-top: 1px solid #d3dcea; margin: 1.8em 0; }
            img { max-width: 100%; }
            ul.task-list { list-style: none; padding-left: 0.2em; }
            .task-box { display: inline-block; min-width: 1.5em; color: #4d6f95; }
            .math-inline { font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif; background: #eef4fb; color: #21476f; border: 1px solid #c7d8eb; border-radius: 6px; padding: 0.08em 0.38em; white-space: pre-wrap; }
            .math-block { font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif; margin: 1.15em 0; padding: 0.85em 1em; border-left: 4px solid #7fa6cf; background: #f5f8fc; color: #1b1e23; border-radius: 8px; white-space: pre-wrap; overflow-x: auto; }
        """,
    },
}


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, document, palette: dict[str, str]) -> None:
        super().__init__(document)
        self.formats: dict[str, QTextCharFormat] = {}
        self._set_palette(palette)

    def _make_format(self, color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        if bold:
            text_format.setFontWeight(700)
        if italic:
            text_format.setFontItalic(True)
        return text_format

    def _set_palette(self, palette: dict[str, str]) -> None:
        self.formats = {
            "heading": self._make_format(palette["accent_heading"], bold=True),
            "emphasis": self._make_format(palette["accent_heading"], bold=True),
            "code": self._make_format(palette["accent_code"]),
            "meta": self._make_format(palette["accent_meta"]),
            "structure": self._make_format(palette["accent_structure"]),
        }

    def update_palette(self, palette: dict[str, str]) -> None:
        self._set_palette(palette)
        self.rehighlight()

    def _apply_matches(self, pattern: str, text: str, text_format: QTextCharFormat) -> None:
        for match in re.finditer(pattern, text, re.MULTILINE):
            start, end = match.span()
            if end > start:
                self.setFormat(start, end - start, text_format)

    def highlightBlock(self, text: str) -> None:
        previous_state = self.previousBlockState()
        in_fenced_code = previous_state == 1

        if re.match(r"^\s*```", text):
            self.setFormat(0, len(text), self.formats["code"])
            self.setCurrentBlockState(0 if in_fenced_code else 1)
            return

        if in_fenced_code:
            self.setFormat(0, len(text), self.formats["code"])
            self.setCurrentBlockState(1)
            return

        self.setCurrentBlockState(0)

        if re.match(r"^\s{0,3}#{1,6}\s+.*$", text):
            self.setFormat(0, len(text), self.formats["heading"])

        self._apply_matches(r"(\*\*|__)(?=\S).+?(?<=\S)\1", text, self.formats["emphasis"])
        self._apply_matches(r"(?<!\*)\*(?=\S).+?(?<=\S)\*(?!\*)", text, self.formats["emphasis"])
        self._apply_matches(r"(?<!_)_(?=\S).+?(?<=\S)_(?!_)", text, self.formats["emphasis"])
        self._apply_matches(r"`[^`\n]+`", text, self.formats["code"])
        self._apply_matches(r"!\[[^\]]*\]\([^)]+\)", text, self.formats["meta"])
        self._apply_matches(r"\[[^\]]+\]\([^)]+\)", text, self.formats["meta"])
        self._apply_matches(r"\[\^[^\]]+\](?::.*)?", text, self.formats["meta"])
        self._apply_matches(r"^\s*(?:[-*+]\s|\d+\.\s)", text, self.formats["structure"])
        self._apply_matches(r"^\s*[-*+]\s\[[ xX]\]\s", text, self.formats["structure"])
        self._apply_matches(r"^\s*>\s?", text, self.formats["structure"])
        self._apply_matches(r"^\s*(?:---+|\*\*\*+|___+)\s*$", text, self.formats["structure"])

        if re.match(r"^\s*\|.*\|\s*$", text):
            self.setFormat(0, len(text), self.formats["structure"])
        else:
            self._apply_matches(r"\|", text, self.formats["structure"])


@dataclass
class AppSettings:
    language: str = "de"
    theme: str = "dark"
    default_mode: str = "view"
    autosave_enabled: bool = True
    autosave_interval: int = 12
    export_mode: str = "source"
    export_confirm: bool = True
    output_dir: str = ""
    file_toolbar_visible: bool = False
    editor_toolbar_collapsed: bool = False
    sync_scroll_positions: bool = True
    window_width: int = 1440
    window_height: int = 960


class SettingsStore:
    def __init__(self) -> None:
        base_dir = Path(os.environ.get("APPDATA", Path.home() / ".config")) / APP_NAME
        base_dir.mkdir(parents=True, exist_ok=True)
        self.path = base_dir / "settings.json"

    def load(self) -> AppSettings:
        if not self.path.exists():
            return AppSettings()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            defaults = asdict(AppSettings())
            defaults.update(data)
            return AppSettings(**defaults)
        except Exception:
            return AppSettings()

    def save(self, settings: AppSettings) -> None:
        self.path.write_text(json.dumps(asdict(settings), indent=2, ensure_ascii=False), encoding="utf-8")


class SettingsDialog(QDialog):
    def __init__(self, settings: AppSettings, translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.t = translator
        self.setWindowTitle(self.t("settings_title"))

        self.language_combo = QComboBox()
        self.language_combo.addItem("Deutsch", "de")
        self.language_combo.addItem("English", "en")
        self.language_combo.setCurrentIndex(0 if settings.language == "de" else 1)

        self.theme_combo = QComboBox()
        self.theme_combo.addItem(self.t("theme_dark"), "dark")
        self.theme_combo.addItem(self.t("theme_bright"), "bright")
        self.theme_combo.setCurrentIndex(0 if settings.theme == "dark" else 1)

        self.default_mode_combo = QComboBox()
        self.default_mode_combo.addItem(self.t("mode_view"), "view")
        self.default_mode_combo.addItem(self.t("mode_editor"), "editor")
        self.default_mode_combo.setCurrentIndex(0 if settings.default_mode == "view" else 1)

        self.autosave_enabled = QCheckBox(self.t("autosave_enabled"))
        self.autosave_enabled.setChecked(settings.autosave_enabled)

        self.autosave_interval = QSpinBox()
        self.autosave_interval.setRange(2, 3600)
        self.autosave_interval.setValue(settings.autosave_interval)

        self.export_mode_combo = QComboBox()
        self.export_mode_combo.addItem(self.t("export_source"), "source")
        self.export_mode_combo.addItem(self.t("export_dedicated"), "dedicated")
        self.export_mode_combo.setCurrentIndex(0 if settings.export_mode == "source" else 1)

        self.export_confirm = QCheckBox(self.t("export_confirm"))
        self.export_confirm.setChecked(settings.export_confirm)

        self.file_toolbar_visible = QCheckBox(self.t("file_toolbar_visible"))
        self.file_toolbar_visible.setChecked(settings.file_toolbar_visible)

        self.editor_toolbar_collapsed = QCheckBox(self.t("editor_toolbar_default"))
        self.editor_toolbar_collapsed.setChecked(settings.editor_toolbar_collapsed)

        self.sync_scroll_positions = QCheckBox(self.t("sync_scroll_positions"))
        self.sync_scroll_positions.setChecked(settings.sync_scroll_positions)

        self.output_dir_edit = QLineEdit(settings.output_dir)
        browse_button = QPushButton(self.t("browse"))
        browse_button.clicked.connect(self._choose_output_dir)
        output_layout = QHBoxLayout()
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(browse_button)

        form = QFormLayout()
        form.addRow(self.t("language"), self.language_combo)
        form.addRow(self.t("theme"), self.theme_combo)
        form.addRow(self.t("default_mode"), self.default_mode_combo)
        form.addRow(self.autosave_enabled)
        form.addRow(self.t("autosave_interval"), self.autosave_interval)
        form.addRow(self.t("export_mode"), self.export_mode_combo)
        form.addRow(self.export_confirm)
        form.addRow(self.file_toolbar_visible)
        form.addRow(self.editor_toolbar_collapsed)
        form.addRow(self.sync_scroll_positions)
        form.addRow(self.t("output_dir"), output_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addWidget(buttons)
        self.setLayout(layout)
        self.resize(560, 320)

    def _choose_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            self.t("select_output"),
            self.output_dir_edit.text() or str(Path.home()),
        )
        if directory:
            self.output_dir_edit.setText(directory)

    def values(self) -> AppSettings:
        return AppSettings(
            language=self.language_combo.currentData(),
            theme=self.theme_combo.currentData(),
            default_mode=self.default_mode_combo.currentData(),
            autosave_enabled=self.autosave_enabled.isChecked(),
            autosave_interval=self.autosave_interval.value(),
            export_mode=self.export_mode_combo.currentData(),
            export_confirm=self.export_confirm.isChecked(),
            output_dir=self.output_dir_edit.text().strip(),
            file_toolbar_visible=self.file_toolbar_visible.isChecked(),
            editor_toolbar_collapsed=self.editor_toolbar_collapsed.isChecked(),
            sync_scroll_positions=self.sync_scroll_positions.isChecked(),
        )


class MainWindow(QMainWindow):
    def __init__(self, initial_path: Path | None = None) -> None:
        super().__init__()
        icon = load_app_icon()
        if not icon.isNull():
            self.setWindowIcon(icon)
        self.store = SettingsStore()
        self.settings = self.store.load()
        self.current_file: Path | None = None
        self.is_modified = False
        self._autosave_notice_sent = False
        self._last_tab_index = 0

        self.tabs = QTabWidget()
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(True)
        self.viewer.setOpenLinks(False)
        self.viewer.anchorClicked.connect(self._open_anchor)

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("# Markdown")
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = self.editor.font()
        font.setPointSize(11)
        self.editor.setFont(font)
        self.editor_highlighter = MarkdownHighlighter(
            self.editor.document(),
            THEMES[self.settings.theme]["editor_colors"],
        )
        self.editor.textChanged.connect(self._on_text_changed)

        self.editor_page = QWidget()
        self.editor_page_layout = QVBoxLayout(self.editor_page)
        self.editor_page_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_page_layout.setSpacing(0)

        self.editor_toolbar_host = QWidget()
        self.editor_toolbar_host.setObjectName("EditorToolbarHost")
        self.editor_toolbar_layout = QHBoxLayout(self.editor_toolbar_host)
        self.editor_toolbar_layout.setContentsMargins(8, 6, 8, 6)
        self.editor_toolbar_layout.setSpacing(8)

        self.collapse_toolbar_button = QPushButton("▾")
        self.collapse_toolbar_button.setFixedWidth(44)
        self.collapse_toolbar_button.clicked.connect(self._toggle_editor_toolbar)

        self.editor_page_layout.addWidget(self.editor_toolbar_host)
        self.editor_page_layout.addWidget(self.editor)

        self.tabs.addTab(self.viewer, "")
        self.tabs.addTab(self.editor_page, "")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)
        self.setStatusBar(QStatusBar())

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self._autosave_if_needed)

        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._apply_theme()
        self._retranslate_ui()
        self._apply_settings()

        self.resize(self.settings.window_width, self.settings.window_height)

        if initial_path and initial_path.exists():
            self.load_file(initial_path)
        else:
            self._render_preview()
            self.tabs.setCurrentIndex(0 if self.settings.default_mode == "view" else 1)
        self._on_tab_changed(self.tabs.currentIndex())

    def t(self, key: str) -> str:
        language = self.settings.language if self.settings.language in TRANSLATIONS else "de"
        return TRANSLATIONS[language].get(key, key)

    def _format_tooltip(self, key: str, shortcut: str | None = None) -> str:
        text = self.t(key)
        return f"{text} ({shortcut})" if shortcut else text

    def _set_action_meta(self, action: QAction, text: str, tooltip_key: str, shortcut: str | None = None) -> None:
        action.setText(text)
        tooltip = self._format_tooltip(tooltip_key, shortcut)
        action.setToolTip(tooltip)
        action.setStatusTip(tooltip)

    def _create_actions(self) -> None:
        self.open_action = QAction(self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction(self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action = QAction(self)
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.save_as_action.triggered.connect(self.save_file_as)

        self.export_pdf_action = QAction(self)
        self.export_pdf_action.setShortcut("Ctrl+Shift+P")
        self.export_pdf_action.triggered.connect(self.export_pdf)

        self.settings_action = QAction(self)
        self.settings_action.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
        self.settings_action.triggered.connect(self.open_settings)

        self.quit_action = QAction(self)
        self.quit_action.setShortcut(QKeySequence.Quit)
        self.quit_action.triggered.connect(self.close)

        self.undo_action = QAction(self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowBack))
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction(self)
        self.redo_action.setShortcut(QKeySequence.Redo)
        self.redo_action.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.redo_action.triggered.connect(self.editor.redo)

        self.view_mode_action = QAction(self)
        self.view_mode_action.setShortcut("Ctrl+1")
        self.view_mode_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))

        self.editor_mode_action = QAction(self)
        self.editor_mode_action.setShortcut("Ctrl+2")
        self.editor_mode_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))

        self.heading1_action = QAction("H1", self)
        self.heading1_action.triggered.connect(lambda: self._apply_heading(1))
        self.heading2_action = QAction("H2", self)
        self.heading2_action.triggered.connect(lambda: self._apply_heading(2))
        self.heading3_action = QAction("H3", self)
        self.heading3_action.triggered.connect(lambda: self._apply_heading(3))

        self.bold_action = QAction(self)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(lambda: self._wrap_selection("**", "**", "bold"))

        self.italic_action = QAction(self)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(lambda: self._wrap_selection("*", "*", "italic"))

        self.inline_code_action = QAction(self)
        self.inline_code_action.setShortcut("Ctrl+`")
        self.inline_code_action.triggered.connect(lambda: self._wrap_selection("`", "`", "code"))

        self.code_block_action = QAction(self)
        self.code_block_action.triggered.connect(self._insert_code_block)

        self.bullet_action = QAction(self)
        self.bullet_action.triggered.connect(lambda: self._prefix_lines("- "))

        self.numbered_action = QAction(self)
        self.numbered_action.triggered.connect(self._insert_numbered_list)

        self.checklist_action = QAction(self)
        self.checklist_action.triggered.connect(lambda: self._prefix_lines("- [ ] "))

        self.blockquote_action = QAction(self)
        self.blockquote_action.triggered.connect(lambda: self._prefix_lines("> "))

        self.rule_action = QAction(self)
        self.rule_action.triggered.connect(lambda: self._insert_text("\n\n---\n\n"))

        self.table_action = QAction(self)
        self.table_action.triggered.connect(self._insert_table_template)

        self.link_action = QAction(self)
        self.link_action.triggered.connect(self._insert_link)

        self.image_action = QAction(self)
        self.image_action.triggered.connect(self._insert_image)

        self.footnote_action = QAction(self)
        self.footnote_action.triggered.connect(self._insert_footnote)

    def _create_menus(self) -> None:
        menu_bar = self.menuBar()

        self.file_menu = menu_bar.addMenu("")
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.export_pdf_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.quit_action)

        self.edit_menu = menu_bar.addMenu("")
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)

        self.view_menu = menu_bar.addMenu("")
        self.view_menu.addAction(self.view_mode_action)
        self.view_menu.addAction(self.editor_mode_action)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.settings_action)

    def _create_toolbars(self) -> None:
        self.file_toolbar = QToolBar()
        self.file_toolbar.setIconSize(QSize(18, 18))
        self.file_toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.file_toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.file_toolbar)
        self.file_toolbar.addAction(self.open_action)
        self.file_toolbar.addAction(self.save_action)
        self.file_toolbar.addAction(self.save_as_action)
        self.file_toolbar.addAction(self.export_pdf_action)
        self.file_toolbar.addSeparator()
        self.file_toolbar.addAction(self.undo_action)
        self.file_toolbar.addAction(self.redo_action)
        self.file_toolbar.addSeparator()
        self.file_toolbar.addAction(self.settings_action)
        export_button = self.file_toolbar.widgetForAction(self.export_pdf_action)
        if export_button is not None:
            export_button.setObjectName("ExportPdfButton")

        self.format_toolbar = QToolBar()
        self.format_toolbar.setMovable(False)
        self.format_toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.editor_toolbar_layout.addWidget(self.format_toolbar, 1)
        self.editor_toolbar_layout.addWidget(self.collapse_toolbar_button, 0, Qt.AlignRight)

        for action in [
            self.heading1_action,
            self.heading2_action,
            self.heading3_action,
            self.bold_action,
            self.italic_action,
            self.inline_code_action,
            self.code_block_action,
        ]:
            self.format_toolbar.addAction(action)
        self.format_toolbar.addSeparator()
        for action in [
            self.bullet_action,
            self.numbered_action,
            self.checklist_action,
            self.blockquote_action,
        ]:
            self.format_toolbar.addAction(action)
        self.format_toolbar.addSeparator()
        for action in [
            self.rule_action,
            self.table_action,
            self.link_action,
            self.image_action,
            self.footnote_action,
        ]:
            self.format_toolbar.addAction(action)

    def _retranslate_ui(self) -> None:
        self.setWindowTitle(self._window_title())
        self.tabs.setTabText(0, self.t("tab_view"))
        self.tabs.setTabText(1, self.t("tab_editor"))

        self.file_menu.setTitle(self.t("file"))
        self.edit_menu.setTitle(self.t("edit"))
        self.view_menu.setTitle(self.t("view"))

        self._set_action_meta(self.open_action, "", "open_tip", "Ctrl+O")
        self._set_action_meta(self.save_action, "S", "save_tip", "Ctrl+S")
        self._set_action_meta(self.save_as_action, "S+", "save_as_tip", "Ctrl+Shift+S")
        self._set_action_meta(self.export_pdf_action, "PDF", "export_tip", "Ctrl+Shift+P")
        self._set_action_meta(self.settings_action, self.t("settings"), "settings_tip")
        self.quit_action.setText(self.t("quit"))
        self._set_action_meta(self.undo_action, self.t("undo"), "undo_tip", "Ctrl+Z")
        self._set_action_meta(self.redo_action, self.t("redo"), "redo_tip", "Ctrl+Y")
        self._set_action_meta(self.view_mode_action, self.t("mode_view"), "read_mode_tip", "Ctrl+1")
        self._set_action_meta(self.editor_mode_action, self.t("mode_editor"), "edit_mode_tip", "Ctrl+2")

        self._set_action_meta(self.heading1_action, "H1", "heading_1")
        self._set_action_meta(self.heading2_action, "H2", "heading_2")
        self._set_action_meta(self.heading3_action, "H3", "heading_3")
        self._set_action_meta(self.bold_action, "B", "bold", "Ctrl+B")
        self._set_action_meta(self.italic_action, "I", "italic", "Ctrl+I")
        self._set_action_meta(self.inline_code_action, "</>", "inline_code", "Ctrl+`")
        self._set_action_meta(self.code_block_action, "{ }", "code_block")
        self._set_action_meta(self.bullet_action, "•", "bullet_list")
        self._set_action_meta(self.numbered_action, "1.", "numbered_list")
        self._set_action_meta(self.checklist_action, "chk", "checklist")
        self._set_action_meta(self.blockquote_action, "qt", "blockquote")
        self._set_action_meta(self.rule_action, "—", "horizontal_rule")
        self._set_action_meta(self.table_action, "tbl", "table")
        self._set_action_meta(self.link_action, "url", "link")
        self._set_action_meta(self.image_action, "img", "image")
        self._set_action_meta(self.footnote_action, "fn", "footnote")

        self.file_toolbar.setWindowTitle(self.t("toolbar_file"))
        self.format_toolbar.setWindowTitle(self.t("toolbar_format"))
        self._update_toolbar_button()
        self.statusBar().showMessage(self.t("status_ready"), 2000)
        self._render_preview()

    def _apply_theme(self) -> None:
        self.setStyleSheet(THEMES[self.settings.theme]["app"])
        self.editor_highlighter.update_palette(THEMES[self.settings.theme]["editor_colors"])
        self._render_preview()

    def _apply_settings(self) -> None:
        self.autosave_timer.setInterval(max(2, self.settings.autosave_interval) * 1000)
        if self.settings.autosave_enabled:
            self.autosave_timer.start()
        else:
            self.autosave_timer.stop()
        self.file_toolbar.setVisible(self.settings.file_toolbar_visible)
        self._set_editor_toolbar_collapsed(self.settings.editor_toolbar_collapsed)

    def _window_title(self) -> str:
        filename = self.current_file.name if self.current_file else self.t("untitled")
        marker = "*" if self.is_modified else ""
        return f"{marker}{filename} - {self.t('app_title')}"

    def _update_window_title(self) -> None:
        self.setWindowTitle(self._window_title())

    def _scrollbar_for_tab(self, index: int):
        widget = self.viewer if index == 0 else self.editor
        return widget.verticalScrollBar()

    def _scroll_ratio_for_tab(self, index: int) -> float:
        scrollbar = self._scrollbar_for_tab(index)
        maximum = scrollbar.maximum()
        if maximum <= 0:
            return 0.0
        return scrollbar.value() / maximum

    def _apply_scroll_ratio_to_tab(self, index: int, ratio: float) -> None:
        scrollbar = self._scrollbar_for_tab(index)
        maximum = scrollbar.maximum()
        clamped_ratio = max(0.0, min(1.0, ratio))
        scrollbar.setValue(0 if maximum <= 0 else round(clamped_ratio * maximum))

    def _sync_scroll_positions_between_tabs(self, source_index: int, target_index: int) -> None:
        ratio = self._scroll_ratio_for_tab(source_index)
        QTimer.singleShot(
            0,
            lambda ratio=ratio, target_index=target_index: self._apply_scroll_ratio_to_tab(target_index, ratio),
        )

    def _on_tab_changed(self, index: int) -> None:
        previous_index = self._last_tab_index
        self._last_tab_index = index
        self._update_window_title()
        if self.settings.sync_scroll_positions and previous_index != index:
            self._sync_scroll_positions_between_tabs(previous_index, index)
        if index == 1:
            self.editor.setFocus()

    def _is_blank_untitled_document(self) -> bool:
        return self.current_file is None and not self.editor.toPlainText().strip()

    def _update_toolbar_button(self) -> None:
        if self.settings.editor_toolbar_collapsed:
            self.collapse_toolbar_button.setText("▸")
            self.collapse_toolbar_button.setToolTip(self.t("expand_toolbar_tip"))
            self.collapse_toolbar_button.setStatusTip(self.t("expand_toolbar_tip"))
        else:
            self.collapse_toolbar_button.setText("▾")
            self.collapse_toolbar_button.setToolTip(self.t("collapse_toolbar_tip"))
            self.collapse_toolbar_button.setStatusTip(self.t("collapse_toolbar_tip"))
        self.collapse_toolbar_button.setStyleSheet("font-size: 18px; font-weight: 700;")

    def _set_editor_toolbar_collapsed(self, collapsed: bool) -> None:
        self.settings.editor_toolbar_collapsed = collapsed
        self.format_toolbar.setVisible(not collapsed)
        self._update_toolbar_button()

    def _toggle_editor_toolbar(self) -> None:
        self._set_editor_toolbar_collapsed(not self.settings.editor_toolbar_collapsed)

    def _open_anchor(self, url: QUrl) -> None:
        if url.isValid():
            QDesktopServices.openUrl(url)

    def _on_text_changed(self) -> None:
        self.is_modified = not self._is_blank_untitled_document()
        self._update_window_title()
        self._render_preview()

    def _render_task_lists(self, body: str) -> str:
        body = body.replace("<ul>\n<li>[ ]", '<ul class="task-list">\n<li class="task-item">[ ]')
        body = body.replace("<ul>\n<li>[x]", '<ul class="task-list">\n<li class="task-item">[x]')
        body = body.replace("<ul>\n<li>[X]", '<ul class="task-list">\n<li class="task-item">[X]')

        def repl(match: re.Match[str]) -> str:
            checked = match.group(1).lower() == "x"
            content = match.group(2)
            box = "☑" if checked else "☐"
            return f'<li class="task-item"><span class="task-box">{box}</span>{content}</li>'

        return re.sub(r"<li(?: class=\"task-item\")?>\[( |x|X)\]\s*(.*?)</li>", repl, body, flags=re.DOTALL)

    def _render_strikethrough(self, body: str) -> str:
        """Wandelt ``~~text~~`` zu ``<del>text</del>`` (GFM-Erweiterung).

        Code- und Pre-Bloecke werden ausgespart, damit Tilden im Code erhalten
        bleiben. Das Standard-Paket ``markdown`` unterstuetzt Strikethrough nicht
        ohne externe Extension; diese kleine Erweiterung schliesst die Luecke.
        """

        pattern = re.compile(r"(?s)<pre.*?</pre>|<code[^>]*>.*?</code>|~~(.+?)~~")

        def replace(match: re.Match[str]) -> str:
            inner = match.group(1)
            if inner is None:
                return match.group(0)
            return f"<del>{inner}</del>"

        return pattern.sub(replace, body)

    def _protect_code_regions(self, text: str) -> tuple[str, dict[str, str]]:
        protected: dict[str, str] = {}
        counter = 0

        def store(match: re.Match[str]) -> str:
            nonlocal counter
            token = f"@@CLEANMARKDOWN_CODE_{counter}@@"
            protected[token] = match.group(0)
            counter += 1
            return token

        fenced_pattern = re.compile(r"(?ms)(^```[^\n]*\n.*?^```[ \t]*$|^~~~[^\n]*\n.*?^~~~[ \t]*$)")
        text = fenced_pattern.sub(store, text)
        inline_code_pattern = re.compile(r"(?s)(`+)(.+?)\1")
        return inline_code_pattern.sub(store, text), protected

    def _restore_protected_regions(self, text: str, protected: dict[str, str]) -> str:
        for token, content in protected.items():
            text = text.replace(token, content)
        return text

    def _preview_base_url(self) -> QUrl:
        if self.current_file is None:
            return QUrl()
        return QUrl.fromLocalFile(str(self.current_file.parent.resolve()) + os.sep)

    def _inject_math_markup(self, text: str) -> str:
        """Preserve formulas as styled HTML without pulling in a full TeX runtime."""

        masked_text, protected = self._protect_code_regions(text)

        def render_block(content: str) -> str:
            cleaned = content.strip()
            if not cleaned:
                return content
            return f'<div class="math-block">{html.escape(cleaned)}</div>'

        masked_text = re.sub(
            r"(?ms)(^|\n)([ \t]*)\$\$\s*\n?(.*?)\n?[ \t]*\$\$(?=\n|$)",
            lambda match: f"{match.group(1)}{match.group(2)}{render_block(match.group(3))}",
            masked_text,
        )
        masked_text = re.sub(
            r"(?ms)(^|\n)([ \t]*)\\\[\s*\n?(.*?)\n?[ \t]*\\\](?=\n|$)",
            lambda match: f"{match.group(1)}{match.group(2)}{render_block(match.group(3))}",
            masked_text,
        )

        def render_inline(match: re.Match[str]) -> str:
            cleaned = match.group(1).strip()
            if not cleaned or re.fullmatch(r"[0-9][0-9.,\s]*", cleaned):
                return match.group(0)
            return f'<span class="math-inline">{html.escape(cleaned)}</span>'

        masked_text = re.sub(r"(?<!\\)\$(?!\$)(.+?)(?<!\\)\$(?!\$)", render_inline, masked_text)
        masked_text = re.sub(r"\\\((.+?)\\\)", render_inline, masked_text)
        return self._restore_protected_regions(masked_text, protected)

    def _render_preview(self) -> None:
        text = self.editor.toPlainText()
        self.viewer.document().setBaseUrl(self._preview_base_url())
        if not text.strip():
            self.viewer.setHtml(self.t("viewer_empty"))
            return
        text = self._inject_math_markup(text)
        body = markdown.markdown(text, extensions=["extra", "sane_lists", "footnotes"])
        body = self._render_task_lists(body)
        body = self._render_strikethrough(body)
        theme_css = THEMES[self.settings.theme]["html"]
        html_doc = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>{theme_css}</style>
</head>
<body>{body}</body>
</html>
"""
        self.viewer.setHtml(html_doc)

    def open_file(self) -> None:
        if not self._confirm_discard():
            return
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            self.t("open_title"),
            str(self.current_file.parent if self.current_file else Path.home()),
            "Markdown Files (*.md *.markdown *.txt);;All Files (*.*)",
        )
        if file_name:
            self.load_file(Path(file_name))

    def load_file(self, path: Path) -> None:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            QMessageBox.critical(self, self.t("error"), self.t("cannot_open"))
            return
        self.current_file = path
        self.editor.blockSignals(True)
        self.editor.setPlainText(content)
        self.editor.blockSignals(False)
        self.is_modified = False
        self._autosave_notice_sent = False
        self._render_preview()
        self.tabs.setCurrentIndex(0 if self.settings.default_mode == "view" else 1)
        self.statusBar().showMessage(f"{self.t('opened')}: {path.name}", 3000)
        self._update_window_title()

    def save_file(self) -> bool:
        if self._is_blank_untitled_document():
            self.is_modified = False
            self._update_window_title()
            self.statusBar().showMessage(self.t("nothing_to_save"), 2200)
            return False
        if self.current_file is None:
            return self.save_file_as()
        try:
            self.current_file.write_text(self.editor.toPlainText(), encoding="utf-8")
        except Exception:
            QMessageBox.critical(self, self.t("error"), self.t("cannot_save"))
            return False
        self.is_modified = False
        self._update_window_title()
        self._render_preview()
        self.statusBar().showMessage(self.t("saved"), 2500)
        return True

    def save_file_as(self) -> bool:
        suggested = self.current_file if self.current_file else Path.home() / "document.md"
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            self.t("save_title"),
            str(suggested),
            "Markdown Files (*.md *.markdown);;Text Files (*.txt);;All Files (*.*)",
        )
        if not file_name:
            return False
        self.current_file = Path(file_name)
        return self.save_file()

    def _autosave_if_needed(self) -> None:
        if not self.settings.autosave_enabled or not self.is_modified:
            return
        if self.current_file is None:
            if not self._autosave_notice_sent:
                self.statusBar().showMessage(self.t("autosave_skip"), 3500)
                self._autosave_notice_sent = True
            return
        if self.save_file():
            self.statusBar().showMessage(self.t("autosave_saved"), 1800)

    def export_pdf(self) -> None:
        target = self._suggested_export_path()
        if self.settings.export_confirm:
            file_name, _ = QFileDialog.getSaveFileName(self, self.t("export_title"), str(target), "PDF Files (*.pdf)")
            if not file_name:
                return
            target = Path(file_name)
        target.parent.mkdir(parents=True, exist_ok=True)

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(str(target))
        printer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Millimeter)

        document = self.viewer.document().clone()
        document.print_(printer)

        if not target.exists():
            QMessageBox.critical(self, self.t("error"), self.t("cannot_export"))
            return
        self.statusBar().showMessage(f"{self.t('exported')}: {target.name}", 3500)

    def _suggested_export_path(self) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = self.current_file.stem if self.current_file else "markdown"

        if self.settings.export_mode == "dedicated" and self.settings.output_dir:
            base_dir = Path(self.settings.output_dir)
        elif self.current_file:
            base_dir = self.current_file.parent
        else:
            base_dir = Path.home() / "Documents"

        return base_dir / f"{stem}_{timestamp}_pdf.pdf"

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.settings, self.t, self)
        if dialog.exec() != QDialog.Accepted:
            return
        updated = dialog.values()
        updated.window_width = self.width()
        updated.window_height = self.height()
        updated.editor_toolbar_collapsed = dialog.values().editor_toolbar_collapsed
        self.settings = updated
        self.store.save(self.settings)
        self._apply_settings()
        self._apply_theme()
        self._retranslate_ui()
        self.tabs.setCurrentIndex(0 if self.settings.default_mode == "view" else 1)

    def _confirm_discard(self) -> bool:
        if not self.is_modified or self._is_blank_untitled_document():
            return True
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle(self.t("save_changes"))
        box.setText(self.t("save_changes_text"))
        save_button = box.addButton(self.t("save"), QMessageBox.AcceptRole)
        discard_button = box.addButton(self.t("discard"), QMessageBox.DestructiveRole)
        cancel_button = box.addButton(self.t("cancel"), QMessageBox.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked == save_button:
            return self.save_file()
        if clicked == discard_button:
            return True
        return clicked != cancel_button

    def _insert_text(self, text: str) -> None:
        cursor = self.editor.textCursor()
        cursor.insertText(text)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _wrap_selection(self, prefix: str, suffix: str, placeholder: str) -> None:
        cursor = self.editor.textCursor()
        selected = cursor.selectedText().replace("\u2029", "\n")
        if selected:
            cursor.insertText(f"{prefix}{selected}{suffix}")
        else:
            cursor.insertText(f"{prefix}{placeholder}{suffix}")
            move_back = len(suffix) + len(placeholder)
            for _ in range(move_back):
                cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(placeholder))
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _selected_or_current_lines(self) -> tuple[QTextCursor, str]:
        cursor = self.editor.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.StartOfLine)
        cursor.setPosition(end, QTextCursor.KeepAnchor)
        if not cursor.atBlockEnd():
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        text = cursor.selectedText().replace("\u2029", "\n")
        return cursor, text

    def _prefix_lines(self, prefix: str) -> None:
        cursor, text = self._selected_or_current_lines()
        lines = text.splitlines() or [""]
        transformed = "\n".join(f"{prefix}{line}" if line.strip() else prefix.rstrip() for line in lines)
        cursor.insertText(transformed)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _apply_heading(self, level: int) -> None:
        prefix = "#" * level + " "
        cursor, text = self._selected_or_current_lines()
        lines = text.splitlines() or [""]
        transformed = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("#"):
                stripped = stripped.lstrip("#").lstrip()
            transformed.append(prefix + stripped if stripped else prefix.rstrip())
        cursor.insertText("\n".join(transformed))
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _insert_numbered_list(self) -> None:
        cursor, text = self._selected_or_current_lines()
        lines = text.splitlines() or [""]
        transformed = "\n".join(f"{index}. {line.strip()}" if line.strip() else f"{index}." for index, line in enumerate(lines, start=1))
        cursor.insertText(transformed)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _insert_code_block(self) -> None:
        cursor = self.editor.textCursor()
        selected = cursor.selectedText().replace("\u2029", "\n")
        if selected:
            cursor.insertText(f"```\n{selected}\n```")
        else:
            cursor.insertText("```\ncode\n```")
            cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Left)
            cursor.movePosition(QTextCursor.Up)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _insert_table_template(self) -> None:
        template = (
            "| Column 1 | Column 2 | Column 3 |\n"
            "| --- | --- | --- |\n"
            "| Value 1 | Value 2 | Value 3 |"
        )
        self._insert_text(template)

    def _insert_link(self) -> None:
        url, ok = QInputDialog.getText(self, self.t("link"), self.t("link_url"))
        if not ok or not url.strip():
            return
        cursor = self.editor.textCursor()
        selected = cursor.selectedText().replace("\u2029", "\n") or "link"
        cursor.insertText(f"[{selected}]({url.strip()})")
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def _insert_image(self) -> None:
        image_url, ok = QInputDialog.getText(self, self.t("image"), self.t("image_url"))
        if not ok or not image_url.strip():
            return
        alt_text, ok = QInputDialog.getText(self, self.t("image"), self.t("image_alt"))
        if not ok:
            return
        self._insert_text(f"![{alt_text.strip()}]({image_url.strip()})")

    def _insert_footnote(self) -> None:
        footnote_id, ok = QInputDialog.getText(self, self.t("footnote"), self.t("footnote_id"), text="1")
        if not ok or not footnote_id.strip():
            return
        cursor = self.editor.textCursor()
        selected = cursor.selectedText().replace("\u2029", "\n")
        token = f"[^{footnote_id.strip()}]"
        if selected:
            cursor.insertText(f"{selected}{token}")
        else:
            cursor.insertText(token)
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(f"\n\n{token}: ")
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.settings.window_width = self.width()
        self.settings.window_height = self.height()
        self.store.save(self.settings)
        if self._confirm_discard():
            event.accept()
        else:
            event.ignore()


def run_smoke_test() -> int:
    app = QApplication(sys.argv)
    configure_application(app)
    window = MainWindow()
    window.show()
    QTimer.singleShot(0, app.quit)
    return app.exec()


def run_self_test() -> int:
    app = QApplication(sys.argv)
    configure_application(app)
    results: list[tuple[str, bool]] = []
    original_open = QFileDialog.getOpenFileName
    original_save = QFileDialog.getSaveFileName
    sample_markdown = r"""# Titel

- [ ] Offen
- [x] Fertig

![Asset](asset.png)

| Spalte | Wert |
| --- | --- |
| Alpha | Beta |

Inline-Mathe $a^2 + b^2 = c^2$ und `$roh$` im Code.

$$
\int_0^1 x^2 \\, dx
$$

```python
print("$code$")
```

Text mit Fußnote.[^1]

[^1]: Randnotiz
"""

    with TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source_path = tmp_path / "quelle.md"
        save_as_path = tmp_path / "kopie.md"
        export_path = tmp_path / "export.pdf"
        dedicated_dir = tmp_path / "exports"
        screenshot_path = Path(__file__).resolve().parent / "README" / "screenshots" / "main_view.png"
        (tmp_path / "asset.png").write_bytes(b"not a real png")
        source_path.write_text(sample_markdown, encoding="utf-8")

        def fake_open(*args, **kwargs):
            return (str(source_path), "Markdown Files (*.md)")

        def fake_save(*args, **kwargs):
            title = args[1] if len(args) > 1 else ""
            if "PDF" in str(title):
                return (str(export_path), "PDF Files (*.pdf)")
            return (str(save_as_path), "Markdown Files (*.md)")

        QFileDialog.getOpenFileName = fake_open
        QFileDialog.getSaveFileName = fake_save
        try:
            window = MainWindow()
            window.show()
            app.processEvents()

            results.append(("blank_viewer_clean", window.viewer.toPlainText().strip() == ""))
            results.append(("blank_save_skipped", window.save_file() is False and window.current_file is None))

            window.open_file()
            app.processEvents()
            results.append(("open_action", window.current_file == source_path))
            resolved_asset = Path(window.viewer.document().baseUrl().resolved(QUrl("asset.png")).toLocalFile())
            results.append(("relative_asset_base_url", resolved_asset.resolve() == (tmp_path / "asset.png").resolve()))

            viewer_text = window.viewer.toPlainText()
            normalized_viewer_text = " ".join(viewer_text.split())
            results.append(("task_list_rendering", "[ ]" not in viewer_text and "☐" in viewer_text and "☑" in viewer_text))
            results.append((
                "rich_markdown_rendering",
                all(token in viewer_text for token in ("Titel", "Alpha", "Beta", "Randnotiz", "$code$", "$roh$")),
            ))
            results.append((
                "math_rendering",
                "a^2 + b^2 = c^2" in normalized_viewer_text
                and r"\int_0^1 x^2" in normalized_viewer_text
                and "dx" in normalized_viewer_text,
            ))
            math_markup = window._inject_math_markup(sample_markdown)
            results.append(("math_markup_classes", 'class="math-inline"' in math_markup and 'class="math-block"' in math_markup))
            results.append(("math_code_protection", "$code$" in math_markup and "`$roh$`" in math_markup))

            results.append(("editor_toolbar_default_visible", window.tabs.widget(0) is window.viewer))
            results.append(("editor_highlighter_ready", window.editor_highlighter is not None))
            results.append(("readme_screenshot_present", screenshot_path.is_file() and screenshot_path.stat().st_size > 0))

            window.settings.language = "en"
            window._retranslate_ui()
            app.processEvents()
            results.append((
                "language_switch_en",
                window.file_menu.title() == window.t("file")
                and window.tabs.tabText(0) == window.t("tab_view")
                and window.settings_action.text() == window.t("settings"),
            ))

            window.settings.theme = "bright"
            window._apply_theme()
            app.processEvents()
            results.append(("theme_switch_bright", window.styleSheet() == THEMES["bright"]["app"]))

            window.settings.language = "de"
            window._retranslate_ui()
            window.settings.theme = "dark"
            window._apply_theme()
            app.processEvents()
            results.append((
                "language_theme_roundtrip_de_dark",
                window.file_menu.title() == window.t("file")
                and window.tabs.tabText(0) == window.t("tab_view")
                and window.styleSheet() == THEMES["dark"]["app"],
            ))

            long_markdown = "\n\n".join(
                f"## Abschnitt {index}\n\n" + "\n".join(f"- Punkt {index}-{item}" for item in range(1, 8))
                for index in range(1, 90)
            )
            window.editor.setPlainText(long_markdown)
            app.processEvents()

            editor_bar = window.editor.verticalScrollBar()
            viewer_bar = window.viewer.verticalScrollBar()

            window.settings.sync_scroll_positions = True
            window.tabs.setCurrentIndex(1)
            app.processEvents()
            editor_bar.setValue(round(editor_bar.maximum() * 0.58))
            app.processEvents()
            editor_ratio_before = window._scroll_ratio_for_tab(1)
            window.tabs.setCurrentIndex(0)
            app.processEvents()
            results.append((
                "scroll_sync_editor_to_view",
                viewer_bar.maximum() > 0 and abs(window._scroll_ratio_for_tab(0) - editor_ratio_before) <= 0.2,
            ))

            viewer_bar.setValue(round(viewer_bar.maximum() * 0.82))
            app.processEvents()
            viewer_ratio_before = window._scroll_ratio_for_tab(0)
            window.tabs.setCurrentIndex(1)
            app.processEvents()
            results.append((
                "scroll_sync_view_to_editor",
                editor_bar.maximum() > 0 and abs(window._scroll_ratio_for_tab(1) - viewer_ratio_before) <= 0.2,
            ))

            window.settings.sync_scroll_positions = False
            viewer_bar.setValue(0)
            window.tabs.setCurrentIndex(1)
            app.processEvents()
            editor_bar.setValue(editor_bar.maximum())
            app.processEvents()
            window.tabs.setCurrentIndex(0)
            app.processEvents()
            results.append(("scroll_sync_toggle_off", viewer_bar.value() == 0))

            window.editor.appendPlainText("\nMehr Text")
            app.processEvents()
            window.save_as_action.trigger()
            app.processEvents()
            results.append(("save_as_action", save_as_path.exists()))
            results.append(("save_as_content", "Mehr Text" in save_as_path.read_text(encoding="utf-8")))

            window.settings.export_confirm = True
            window.export_pdf_action.trigger()
            app.processEvents()
            results.append(("export_pdf_action", export_path.exists()))

            window.settings.export_confirm = False
            window.settings.export_mode = "dedicated"
            window.settings.output_dir = str(dedicated_dir)
            window.export_pdf_action.trigger()
            app.processEvents()
            results.append(("export_pdf_dedicated", len(list(dedicated_dir.glob("*_pdf.pdf"))) == 1))
            window.close()
        finally:
            QFileDialog.getOpenFileName = original_open
            QFileDialog.getSaveFileName = original_save

    failed = [name for name, ok in results if not ok]
    for name, ok in results:
        print(f"{name}: {'ok' if ok else 'failed'}")
    app.quit()
    return 0 if not failed else 1


def main() -> int:
    if "--smoke-test" in sys.argv:
        return run_smoke_test()
    if "--self-test" in sys.argv:
        return run_self_test()

    app = QApplication(sys.argv)
    configure_application(app)
    initial_path = None
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            continue
        path = Path(arg)
        if path.exists():
            initial_path = path
            break

    window = MainWindow(initial_path)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
