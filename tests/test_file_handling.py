from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys

from PySide6.QtCore import QUrl


def _make_window(main_module):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    return app, window


def test_confirm_discard_treats_closed_dialog_as_cancel(main_module, monkeypatch):
    _, window = _make_window(main_module)
    window.editor.setPlainText("modified")
    window.is_modified = True

    monkeypatch.setattr(main_module.QMessageBox, "exec", lambda self: None)
    monkeypatch.setattr(main_module.QMessageBox, "clickedButton", lambda self: None)

    assert window._confirm_discard() is False
    window.is_modified = False
    window.close()


def test_settings_store_ignores_unknown_json_fields(main_module, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    store = main_module.SettingsStore()
    payload = {
        "language": "en",
        "theme": "bright",
        "default_mode": "editor",
        "autosave_enabled": False,
        "autosave_interval": 42,
        "export_mode": "dedicated",
        "export_confirm": False,
        "output_dir": "C:/tmp",
        "file_toolbar_visible": True,
        "editor_toolbar_collapsed": True,
        "sync_scroll_positions": False,
        "window_width": 1111,
        "window_height": 777,
        "future_field": "ignore-me",
    }
    store.path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    settings = store.load()

    assert settings.language == "en"
    assert settings.theme == "bright"
    assert settings.default_mode == "editor"
    assert settings.autosave_enabled is False
    assert settings.autosave_interval == 42
    assert settings.export_mode == "dedicated"
    assert settings.export_confirm is False
    assert settings.output_dir == "C:/tmp"
    assert settings.file_toolbar_visible is True
    assert settings.editor_toolbar_collapsed is True
    assert settings.sync_scroll_positions is False
    assert settings.window_width == 1111
    assert settings.window_height == 777


def test_settings_persist_across_new_store_and_window_instances(main_module, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    expected = main_module.AppSettings(
        language="en",
        theme="bright",
        default_mode="editor",
        autosave_enabled=False,
        autosave_interval=47,
        export_mode="dedicated",
        export_confirm=False,
        output_dir="C:/Persist/Übergabe",
        file_toolbar_visible=True,
        editor_toolbar_collapsed=True,
        sync_scroll_positions=False,
        window_width=1111,
        window_height=777,
    )

    main_module.SettingsStore().save(expected)

    assert main_module.SettingsStore().load() == expected
    _, restarted_window = _make_window(main_module)
    assert restarted_window.settings == expected
    restarted_window.is_modified = False
    restarted_window.close()


def test_self_test_preserves_existing_user_settings_bytes_and_mtime(main_module, tmp_path, monkeypatch):
    appdata = tmp_path / "appdata"
    monkeypatch.setenv("APPDATA", str(appdata))
    expected = main_module.AppSettings(
        language="en",
        theme="bright",
        default_mode="editor",
        autosave_enabled=False,
        autosave_interval=47,
        export_mode="dedicated",
        export_confirm=False,
        output_dir="C:/Persist/Übergabe",
        file_toolbar_visible=True,
        editor_toolbar_collapsed=True,
        sync_scroll_positions=False,
        window_width=1111,
        window_height=777,
    )
    store = main_module.SettingsStore()
    store.save(expected)
    before_bytes = store.path.read_bytes()
    before_mtime_ns = store.path.stat().st_mtime_ns

    env = os.environ.copy()
    env["APPDATA"] = str(appdata)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["PYTHONPATH"] = os.pathsep.join(path for path in sys.path if path)
    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(Path(main_module.__file__)), "--self-test"],
        cwd=Path(main_module.__file__).parent,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert store.path.read_bytes() == before_bytes
    assert store.path.stat().st_mtime_ns == before_mtime_ns
    assert main_module.SettingsStore().load() == expected


def test_main_window_sanitizes_corrupt_settings_types(main_module, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    store = main_module.SettingsStore()
    payload = {
        "language": "de",
        "theme": "dark",
        "default_mode": "view",
        "autosave_enabled": "false",
        "autosave_interval": "12",
        "export_mode": "source",
        "export_confirm": "no",
        "output_dir": 123,
        "file_toolbar_visible": "true",
        "editor_toolbar_collapsed": "off",
        "sync_scroll_positions": "1",
        "window_width": "1440",
        "window_height": "960",
        "future_field": "ignore-me",
    }
    store.path.write_text(json.dumps(payload), encoding="utf-8")

    window = main_module.MainWindow()

    assert window.settings.autosave_enabled is False
    assert window.settings.autosave_interval == 12
    assert window.settings.export_confirm is False
    assert window.settings.output_dir == ""
    assert window.settings.file_toolbar_visible is True
    assert window.settings.editor_toolbar_collapsed is False
    assert window.settings.sync_scroll_positions is True
    assert window.settings.window_width == 1440
    assert window.settings.window_height == 960

    window.is_modified = False
    window.close()


def test_load_session_file_applies_markdown_and_settings(main_module, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    _, window = _make_window(main_module)
    session_path = tmp_path / "demo.cleanmarkdown-session-v1.json"
    payload = {
        "version": "cleanmarkdown-session-v1",
        "fileName": "unterwegs.md",
        "markdown": "# Unterwegs\n\näöü",
        "theme": "paper",
        "workspace": "split",
        "updatedAt": "2026-05-28T16:10:00",
        "settings": {
            "language": "en",
            "theme": "paper",
            "defaultMode": "editor",
            "autosaveEnabled": False,
            "autosaveIntervalSeconds": 33,
            "exportMode": "dedicated",
            "exportConfirm": False,
            "outputDir": str(tmp_path / "exports"),
            "fileToolbarVisible": True,
            "editorToolbarCollapsed": True,
            "syncScrollPositions": False,
        },
    }
    session_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    critical_calls = []
    monkeypatch.setattr(
        main_module.QMessageBox,
        "critical",
        lambda *args, **kwargs: critical_calls.append((args, kwargs)),
    )

    window.load_session_file(session_path)

    assert not critical_calls
    assert window.current_file is None
    assert window.session_display_name == "unterwegs.md"
    assert window.editor.toPlainText() == "# Unterwegs\n\näöü"
    assert window.settings.language == "en"
    assert window.settings.theme == "bright"
    assert window.settings.default_mode == "editor"
    assert window.settings.autosave_enabled is False
    assert window.settings.autosave_interval == 33
    assert window.settings.export_mode == "dedicated"
    assert window.settings.export_confirm is False
    assert window.settings.file_toolbar_visible is True
    assert window.settings.editor_toolbar_collapsed is True
    assert window.settings.sync_scroll_positions is False
    assert window.tabs.currentIndex() == 1

    window.is_modified = False
    window.close()


def test_load_session_file_uses_session_directory_for_relative_assets(main_module, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    _, window = _make_window(main_module)
    session_path = tmp_path / "assets-demo.cleanmarkdown-session-v1.json"
    asset_path = tmp_path / "diagram.png"
    asset_path.write_bytes(b"png")
    payload = {
        "version": "cleanmarkdown-session-v1",
        "fileName": "unterwegs.md",
        "markdown": "![Diagramm](diagram.png)",
        "theme": "paper",
        "workspace": "read",
        "updatedAt": "2026-06-01T12:00:00",
    }
    session_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args, **kwargs: None)

    window.load_session_file(session_path)

    resolved = window.viewer.document().baseUrl().resolved(QUrl("diagram.png")).toLocalFile()
    assert Path(resolved).resolve() == asset_path.resolve()

    window.is_modified = False
    window.close()


def test_load_session_file_keeps_current_theme_for_unknown_session_theme(main_module, tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    _, window = _make_window(main_module)
    session_path = tmp_path / "unknown-theme.cleanmarkdown-session-v1.json"
    payload = {
        "version": "cleanmarkdown-session-v1",
        "fileName": "theme.md",
        "markdown": "# Theme",
        "theme": "solarized",
        "workspace": "read",
    }
    session_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    window.settings.theme = "dark"

    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args, **kwargs: None)

    window.load_session_file(session_path)

    assert window.settings.theme == "dark"
    assert window.styleSheet() == main_module.THEMES["dark"]["app"]

    window.is_modified = False
    window.close()


def test_export_session_writes_compatible_payload(main_module, tmp_path, monkeypatch):
    _, window = _make_window(main_module)
    session_path = tmp_path / "session.cleanmarkdown-session-v1.json"
    window.session_display_name = "notiz.md"
    window.editor.setPlainText("# Hallo\n\n- [ ] Prüfen")
    window.settings.language = "de"
    window.settings.theme = "dark"
    window.settings.default_mode = "view"
    window.settings.autosave_enabled = True
    window.settings.autosave_interval = 15
    window.settings.export_mode = "source"
    window.settings.export_confirm = True
    window.settings.output_dir = ""
    window.settings.file_toolbar_visible = False
    window.settings.editor_toolbar_collapsed = False
    window.settings.sync_scroll_positions = True
    window.tabs.setCurrentIndex(0)

    monkeypatch.setattr(
        main_module.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(session_path), "CleanMarkdown Session (*.cleanmarkdown-session-v1.json)"),
    )
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args, **kwargs: None)

    window.export_session()

    payload = json.loads(session_path.read_text(encoding="utf-8"))
    assert payload["version"] == "cleanmarkdown-session-v1"
    assert payload["fileName"] == "notiz.md"
    assert payload["markdown"] == "# Hallo\n\n- [ ] Prüfen"
    assert payload["theme"] == "night"
    assert payload["workspace"] == "read"
    assert payload["settings"]["language"] == "de"
    assert payload["settings"]["theme"] == "night"
    assert payload["settings"]["defaultMode"] == "view"
    assert payload["settings"]["autosaveEnabled"] is True
    assert payload["settings"]["autosaveIntervalSeconds"] == 15
    assert payload["settings"]["exportMode"] == "source"
    assert payload["settings"]["syncScrollPositions"] is True

    window.is_modified = False
    window.close()


def test_save_file_as_restores_previous_file_on_write_failure(main_module, tmp_path, monkeypatch):
    _, window = _make_window(main_module)
    original = tmp_path / "orig.md"
    original.write_text("old", encoding="utf-8")
    window.current_file = original
    window.editor.setPlainText("updated")
    window.is_modified = True

    target = tmp_path / "missing" / "new.md"
    monkeypatch.setattr(
        main_module.QFileDialog,
        "getSaveFileName",
        lambda *args, **kwargs: (str(target), "Markdown Files (*.md)"),
    )
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args, **kwargs: None)

    assert window.save_file_as() is False
    assert window.current_file == original
    assert window.is_modified is True
    assert original.read_text(encoding="utf-8") == "old"
    window.is_modified = False
    window.close()


def test_export_pdf_reports_invalid_output_directory(main_module, tmp_path, monkeypatch):
    _, window = _make_window(main_module)
    blocked = tmp_path / "blocked"
    blocked.write_text("conflict", encoding="utf-8")
    window.current_file = tmp_path / "doc.md"
    window.settings.export_confirm = False
    window.settings.export_mode = "dedicated"
    window.settings.output_dir = str(blocked)

    critical_calls = []
    monkeypatch.setattr(
        main_module.QMessageBox,
        "critical",
        lambda *args, **kwargs: critical_calls.append((args, kwargs)),
    )

    window.export_pdf()

    assert critical_calls, "Ungültige Exportpfade müssen eine Fehlermeldung auslösen"
    assert critical_calls[0][0][2] == window.t("cannot_export")
    window.is_modified = False
    window.close()


def test_export_pdf_always_uses_bright_theme_even_in_dark_mode(main_module):
    """U1: PDF-Export bleibt Print-Standard (hell), egal welches UI-Theme laeuft."""
    _, window = _make_window(main_module)
    window.settings.theme = "dark"
    window._apply_theme()
    window.editor.setPlainText("# Ueberschrift\n\nDunkles UI-Theme, PDF soll trotzdem hell sein.")

    export_html = window._build_export_document().toHtml()
    bright_body_bg = main_module.THEMES["bright"]["html"]
    dark_body_bg = main_module.THEMES["dark"]["html"]

    # Der Body-Hintergrund aus dem dunklen Theme ("#11161d") darf im
    # Export-HTML nicht auftauchen, der helle ("#ffffff") schon.
    assert dark_body_bg not in export_html
    assert bright_body_bg in export_html.lower() or "#ffffff" in export_html.lower() or "255,255,255" in export_html
    window.is_modified = False
    window.close()


def test_export_pdf_auto_saves_unsaved_document_before_export(main_module, tmp_path, monkeypatch):
    """U2: Export eines nie gespeicherten Dokuments speichert automatisch und
    exportiert daraus, statt im falschen/unauffindbaren Ordner zu landen."""
    monkeypatch.setattr(main_module, "_documents_dir", lambda: tmp_path)

    class _MockPrinter:
        PrinterMode = main_module.QPrinter.PrinterMode
        OutputFormat = main_module.QPrinter.OutputFormat

        def __init__(self, *args, **kwargs):
            self._file: Path | None = None

        def setOutputFormat(self, fmt):
            pass

        def setOutputFileName(self, fname):
            self._file = Path(fname)

        def setPageMargins(self, *args, **kwargs):
            pass

    monkeypatch.setattr(main_module, "QPrinter", _MockPrinter)
    orig_build = main_module.MainWindow._build_export_document

    def mock_build(self):
        doc = orig_build(self)
        doc.print_ = lambda printer: printer._file.write_bytes(b"%PDF-1.4 mock\n%%EOF\n") if getattr(printer, "_file", None) else None
        return doc

    monkeypatch.setattr(main_module.MainWindow, "_build_export_document", mock_build)

    _, window = _make_window(main_module)
    window.settings.export_confirm = False
    window.editor.setPlainText("# Nie gespeichert\n\nExport ohne vorheriges Speichern.")

    assert window.current_file is None
    window.export_pdf()

    assert window.current_file is not None, "Export muss das Dokument automatisch verankern (U2)"
    assert window.current_file.exists()
    assert window.current_file.parent == tmp_path
    assert "autosave" in window.current_file.name
    assert window.current_file.read_text(encoding="utf-8").startswith("# Nie gespeichert")

    pdfs = list(tmp_path.glob("*_pdf.pdf"))
    assert len(pdfs) == 1, "genau ein PDF muss im (korrekten) Documents-Ordner entstehen"
    assert pdfs[0].stat().st_size > 0
    window.is_modified = False
    window.close()


def test_export_pdf_reports_error_when_auto_save_fails(main_module, tmp_path, monkeypatch):
    """Grundregel U2: Export darf NIE still scheitern -- auch nicht, wenn das
    automatische Zwischenspeichern selbst fehlschlaegt."""
    blocked = tmp_path / "documents_is_a_file"
    blocked.write_text("kein Ordner", encoding="utf-8")
    monkeypatch.setattr(main_module, "_documents_dir", lambda: blocked)
    _, window = _make_window(main_module)
    window.settings.export_confirm = False
    window.editor.setPlainText("# Inhalt\n\nAuto-Save-Ziel ist blockiert.")

    critical_calls = []
    monkeypatch.setattr(
        main_module.QMessageBox,
        "critical",
        lambda *args, **kwargs: critical_calls.append((args, kwargs)),
    )

    window.export_pdf()

    assert critical_calls, "Fehlschlagendes Auto-Save vor Export muss eine Fehlermeldung zeigen"
    assert window.current_file is None
    window.is_modified = False
    window.close()


def test_suggested_export_path_falls_back_to_real_documents_dir(main_module, tmp_path, monkeypatch):
    """U2: Der Fallback-Zielordner fuer ungespeicherte Dokumente kommt aus
    QStandardPaths (Known-Folder-fest), nicht aus einem hartcodierten
    ``Path.home() / "Documents"``, das OneDrive-Umleitungen ignoriert."""
    monkeypatch.setattr(main_module, "_documents_dir", lambda: tmp_path / "Dokumente")
    _, window = _make_window(main_module)

    target = window._suggested_export_path()

    assert target.parent == tmp_path / "Dokumente"
    window.is_modified = False
    window.close()


def test_editor_toolbar_toggle_exposes_translated_accessible_context(main_module):
    _, window = _make_window(main_module)

    export_button = window.file_toolbar.widgetForAction(window.export_pdf_action)
    assert export_button is not None
    assert export_button.accessibleName() == "Aktuelle Ansicht als PDF exportieren"
    assert export_button.accessibleDescription() == "Aktuelle Ansicht als PDF exportieren (Ctrl+Shift+P)"

    bold_button = window.format_toolbar.widgetForAction(window.bold_action)
    assert bold_button is not None
    assert bold_button.accessibleName() == "Fett"
    assert bold_button.accessibleDescription() == "Fett (Ctrl+B)"

    assert window.collapse_toolbar_button.text() == "▾"
    assert window.collapse_toolbar_button.accessibleName() == "Editorwerkzeuge umschalten"
    assert window.collapse_toolbar_button.accessibleDescription() == "Blendet die Editorwerkzeuge aus."
    assert window.collapse_toolbar_button.toolTip() == "Editorleiste einklappen"

    window._set_editor_toolbar_collapsed(True)
    assert window.collapse_toolbar_button.text() == "▸"
    assert window.collapse_toolbar_button.accessibleDescription() == "Blendet die Editorwerkzeuge ein."
    assert window.collapse_toolbar_button.toolTip() == "Editorleiste ausklappen"

    window.settings.language = "en"
    window._retranslate_ui()
    assert export_button.accessibleName() == "Export the current view as PDF"
    assert export_button.accessibleDescription() == "Export the current view as PDF (Ctrl+Shift+P)"
    assert bold_button.accessibleName() == "Bold"
    assert bold_button.accessibleDescription() == "Bold (Ctrl+B)"
    assert window.collapse_toolbar_button.accessibleName() == "Toggle editor tools"
    assert window.collapse_toolbar_button.accessibleDescription() == "Shows the editor tools."
    assert window.collapse_toolbar_button.toolTip() == "Expand the editor toolbar"

    window.is_modified = False
    window.close()


def test_main_workspaces_expose_translated_accessible_context(main_module):
    _, window = _make_window(main_module)

    assert window.tabs.accessibleName() == "CleanMarkdown"
    assert window.tabs.accessibleDescription() == "Wechselt zwischen Leseansicht und Markdown-Editor."
    assert window.viewer.accessibleName() == "Lesen"
    assert window.viewer.accessibleDescription() == "Gerenderte Leseansicht des aktuellen Markdown-Dokuments."
    assert window.editor.accessibleName() == "Editor"
    assert window.editor.accessibleDescription() == "Editor für den Markdown-Quelltext des aktuellen Dokuments."
    assert window.file_toolbar.accessibleName() == "Datei"
    assert window.file_toolbar.accessibleDescription() == "Werkzeugleiste für Datei- und Exportaktionen."
    assert window.format_toolbar.accessibleName() == "Werkzeuge"
    assert window.format_toolbar.accessibleDescription() == "Werkzeugleiste zum Bearbeiten und Formatieren von Markdown."

    window.settings.language = "en"
    window._retranslate_ui()

    assert window.tabs.accessibleDescription() == "Switches between the reading view and the Markdown editor."
    assert window.viewer.accessibleName() == "Reading"
    assert window.editor.accessibleDescription() == "Editor for the Markdown source text of the current document."
    assert window.file_toolbar.accessibleDescription() == "Toolbar for file and export actions."
    assert window.format_toolbar.accessibleDescription() == "Toolbar for editing and formatting Markdown."

    window.is_modified = False
    window.close()
