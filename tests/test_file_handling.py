from __future__ import annotations

import json


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
