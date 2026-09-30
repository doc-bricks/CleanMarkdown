"""Malformed optional settings must not prevent loading valid session text."""
import json

import pytest


@pytest.mark.parametrize("field,value", [
    ("theme", []), ("theme", {}),
    ("defaultMode", []), ("defaultMode", {}),
    ("exportMode", []), ("exportMode", {}),
    ("autosaveIntervalSeconds", float("inf")),
    ("autosaveIntervalSeconds", 10**30),
    ("legacyTheme", []), ("legacyTheme", {}),
    ("legacyWorkspace", []), ("legacyWorkspace", {}),
])
def test_bad_optional_settings_load_text_with_safe_defaults(main_module, tmp_path, monkeypatch, field, value):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    window.settings.theme = "bright"
    window.settings.default_mode = "editor"
    window.settings.export_mode = "dedicated"
    window.settings.autosave_interval = 37
    payload = {"version": main_module.SESSION_VERSION, "markdown": "# Prüfung\n\nBücher."}
    if field.startswith("legacy"):
        payload["theme" if field == "legacyTheme" else "workspace"] = value
    else:
        payload["settings"] = {"language": "en", field: value}
    path = tmp_path / "session.json"
    # 1e309 is a valid JSON number which overflows Python's float range.
    path.write_text(json.dumps(payload, ensure_ascii=False).replace("Infinity", "1e309"), encoding="utf-8")
    errors = []
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: errors.append(args))
    try:
        window.load_session_file(path)
        assert not errors
        assert window.editor.toPlainText() == payload["markdown"]
        assert window.current_file is None
        assert not window.is_modified
        assert window.settings.theme == "bright"
        assert window.settings.default_mode == "editor"
        assert window.settings.export_mode == "dedicated"
        expected_interval = (2**31 - 1) // 1000 if value == 10**30 else 37
        assert window.settings.autosave_interval == expected_interval
        assert window.autosave_timer.interval() == expected_interval * 1000
        assert window.tabs.currentIndex() == 1
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()


@pytest.mark.parametrize("dirty", [False, True])
def test_theme_change_preserves_document_dirty_flag(main_module, dirty):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    try:
        window.editor.setPlainText("# Prüfung")
        window.is_modified = dirty
        window.settings.theme = "bright"
        window._apply_theme()
        assert window.is_modified is dirty
        assert window.editor.toPlainText() == "# Prüfung"
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()
