"""Session exports replace files only after the entire JSON was written."""
import json
from pathlib import Path

import pytest
from PySide6.QtCore import QSaveFile


def make_window(main_module, tmp_path, monkeypatch, target):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    window.current_file = tmp_path / "source.md"
    window.session_display_name = "source.md"
    window.editor.setPlainText("# Bücher\n\nÄpfel, Öl und Übergabe.")
    window.is_modified = True
    window.statusBar().showMessage("previous status")
    monkeypatch.setattr(main_module.QFileDialog, "getSaveFileName", lambda *args: (str(target), ""))
    return app, window


@pytest.mark.parametrize("stage", ["open", "write", "commit"])
@pytest.mark.parametrize("existing", [False, True])
def test_failed_session_export_preserves_target_and_editor(main_module, tmp_path, monkeypatch, stage, existing):
    target = tmp_path / "session.json"
    original = b'{"old":"session"}\n'
    if existing:
        target.write_bytes(original)
    app, window = make_window(main_module, tmp_path, monkeypatch, target)
    original_write = Path.write_text

    def failing_write(path, content, *args, **kwargs):
        if path == target:
            path.write_bytes(b"partial")
            raise OSError("disk full")
        return original_write(path, content, *args, **kwargs)

    class FailingSave(QSaveFile):
        def open(self, mode):
            return False if stage == "open" else super().open(mode)

        def write(self, data):
            return super().write(data[:3]) if stage == "write" else super().write(data)

        def commit(self):
            return False if stage == "commit" else super().commit()

    errors = []
    monkeypatch.setattr(Path, "write_text", failing_write)
    monkeypatch.setattr(main_module, "QSaveFile", FailingSave)
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: errors.append(args))
    try:
        window.export_session()
        if existing:
            assert target.read_bytes() == original
        else:
            assert not target.exists()
        assert list(tmp_path.glob("session*")) == ([target] if existing else [])
        assert window.current_file == tmp_path / "source.md"
        assert window.session_display_name == "source.md"
        assert window.is_modified
        assert window.editor.toPlainText() == "# Bücher\n\nÄpfel, Öl und Übergabe."
        assert window.statusBar().currentMessage() == "previous status"
        assert len(errors) == 1
    finally:
        # The failure injector is scoped to the export. Restore the normal
        # writer before closeEvent saves the isolated test settings.
        monkeypatch.setattr(main_module, "QSaveFile", QSaveFile)
        window.is_modified = False
        window.close()
        app.processEvents()


def test_session_export_roundtrips_text_and_settings(main_module, tmp_path, monkeypatch):
    target = tmp_path / "session.json"
    target.write_bytes(b"old")
    app, window = make_window(main_module, tmp_path, monkeypatch, target)
    try:
        window.settings.output_dir = "Bücher/Übergabe"
        window.export_session()
        payload = json.loads(target.read_text(encoding="utf-8"))
        assert payload["version"] == main_module.SESSION_VERSION
        assert payload["markdown"] == window.editor.toPlainText()
        assert payload["settings"]["outputDir"] == "Bücher/Übergabe"
        assert window.is_modified
        assert window.current_file == tmp_path / "source.md"
        assert window.t("session_exported") in window.statusBar().currentMessage()
        assert list(tmp_path.glob("session*")) == [target]
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()


def test_cancel_session_export_creates_no_file(main_module, tmp_path, monkeypatch):
    target = tmp_path / "session.json"
    app, window = make_window(main_module, tmp_path, monkeypatch, target)
    monkeypatch.setattr(main_module.QFileDialog, "getSaveFileName", lambda *args: ("", ""))
    try:
        window.export_session()
        assert not target.exists()
        assert window.is_modified
        assert window.statusBar().currentMessage() == "previous status"
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()
