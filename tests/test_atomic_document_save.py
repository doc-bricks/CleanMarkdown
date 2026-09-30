"""Failed saves must retain both the previous document and unsaved editor state."""

from pathlib import Path

import pytest


def make_window(main_module, path):
    application = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    window.current_file = path
    window.editor.setPlainText("Neue Prüfung mit Bücherliste")
    window.is_modified = True
    return application, window


@pytest.mark.parametrize("stage", ["write", "commit"])
def test_failed_save_preserves_existing_document(main_module, tmp_path, monkeypatch, stage):
    path = tmp_path / "bericht.md"
    original = b"previous document"
    path.write_bytes(original)
    application, window = make_window(main_module, path)
    original_write = Path.write_text

    def failing_write(target, content, *args, **kwargs):
        if target == path:
            target.write_bytes(b"partial")
            raise OSError("disk full")
        return original_write(target, content, *args, **kwargs)

    from PySide6.QtCore import QSaveFile

    class FailingSave(QSaveFile):
        def write(self, data):
            if stage == "write":
                super().write(data[:3])
                return -1
            return super().write(data)

        def commit(self):
            if stage == "commit":
                return False
            return super().commit()

    monkeypatch.setattr(Path, "write_text", failing_write)
    monkeypatch.setattr(main_module, "QSaveFile", FailingSave, raising=False)
    errors = []
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: errors.append(args))
    try:
        assert window.save_file() is False
        assert path.read_bytes() == original
        assert window.is_modified is True
        assert window.current_file == path
        assert len(errors) == 1
        assert list(tmp_path.glob("bericht*")) == [path]
    finally:
        window.is_modified = False
        window.close()
        application.processEvents()


def test_successful_save_roundtrips_umlauts(main_module, tmp_path):
    path = tmp_path / "bericht.md"
    path.write_bytes(b"old document")
    application, window = make_window(main_module, path)
    try:
        assert window.save_file() is True
        assert path.read_text(encoding="utf-8") == "Neue Prüfung mit Bücherliste"
        assert window.is_modified is False
        assert list(tmp_path.glob("bericht*")) == [path]
    finally:
        window.is_modified = False
        window.close()
        application.processEvents()
