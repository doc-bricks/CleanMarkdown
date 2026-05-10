from __future__ import annotations


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
