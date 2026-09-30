"""Failed settings writes preserve the previous profile and usable window."""
from dataclasses import replace
from pathlib import Path

import pytest
from PySide6.QtCore import QSaveFile
from PySide6.QtGui import QCloseEvent


@pytest.mark.parametrize("stage", ["write", "commit"])
def test_failed_settings_save_preserves_profile(main_module, monkeypatch, stage):
    store = main_module.SettingsStore()
    original = main_module.AppSettings(language="en", output_dir="Bücher/Übergabe")
    store.save(original)
    original_bytes = store.path.read_bytes()
    original_write = Path.write_text

    def failing_write(target, content, *args, **kwargs):
        if target == store.path:
            target.write_bytes(b"partial")
            raise OSError("disk full")
        return original_write(target, content, *args, **kwargs)

    class FailingSave(QSaveFile):
        def write(self, data):
            if stage == "write":
                return super().write(data[:3])
            return super().write(data)

        def commit(self):
            return False if stage == "commit" else super().commit()

    monkeypatch.setattr(Path, "write_text", failing_write)
    monkeypatch.setattr(main_module, "QSaveFile", FailingSave)
    with pytest.raises(OSError):
        store.save(replace(original, language="de"))
    assert store.path.read_bytes() == original_bytes
    assert store.load() == original
    assert list(store.path.parent.iterdir()) == [store.path]


def test_settings_save_retains_utf8(main_module):
    store = main_module.SettingsStore()
    expected = main_module.AppSettings(output_dir="Bücher/Übergabe")
    store.save(expected)
    assert store.load() == expected
    assert "Bücher/Übergabe" in store.path.read_text(encoding="utf-8")
    assert list(store.path.parent.iterdir()) == [store.path]


def test_close_settings_failure_keeps_dirty_window(main_module, monkeypatch):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    window.editor.setPlainText("Ungespeicherte Prüfung")
    window.is_modified = True
    errors = []
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: errors.append(args))

    def failing_save(settings):
        raise OSError("disk full")

    with monkeypatch.context() as patch:
        patch.setattr(window.store, "save", failing_save)
        event = QCloseEvent()
        try:
            window.closeEvent(event)
            assert not event.isAccepted()
            assert window.is_modified
            assert window.editor.toPlainText() == "Ungespeicherte Prüfung"
            assert len(errors) == 1
        finally:
            window.is_modified = False
    window.close()
    app.processEvents()


def test_settings_dialog_failure_keeps_current_settings(main_module, monkeypatch):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    original = replace(window.settings)
    errors = []
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: errors.append(args))

    class AcceptedDialog:
        def __init__(self, *args):
            pass

        def exec(self):
            return main_module.QDialog.DialogCode.Accepted

        def values(self):
            return replace(original, language="en", theme="bright")

    def failing_save(settings):
        raise OSError("disk full")

    try:
        with monkeypatch.context() as patch:
            patch.setattr(main_module, "SettingsDialog", AcceptedDialog)
            patch.setattr(window.store, "save", failing_save)
            window.open_settings()
        assert window.settings == original
        assert len(errors) == 1
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()
