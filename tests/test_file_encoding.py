"""Opening malformed UTF-8 must preserve the active document and source bytes."""
import pytest


@pytest.mark.parametrize("raw", [b"# Caf\xe9", b"# broken \xff", b"# truncated \xe2\x82"])
def test_invalid_utf8_preserves_unsaved_document(main_module, tmp_path, monkeypatch, raw):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    old_path = tmp_path / "active.md"
    old_path.write_text("# Original", encoding="utf-8")
    candidate = tmp_path / "invalid.md"
    candidate.write_bytes(raw)
    errors = []
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: errors.append(args))
    try:
        window.load_file(old_path)
        window.editor.setPlainText("# Ungespeicherte Änderung")
        window._render_preview()
        window.tabs.setCurrentIndex(1)
        before = (window.current_file, window._session_asset_dir,
                  window.session_display_name, window.editor.toPlainText(),
                  window.viewer.toPlainText(), window.is_modified,
                  window.tabs.currentIndex(), window.windowTitle())
        assert window.is_modified
        window.load_file(candidate)
        assert len(errors) == 1
        after = (window.current_file, window._session_asset_dir,
                 window.session_display_name, window.editor.toPlainText(),
                 window.viewer.toPlainText(), window.is_modified,
                 window.tabs.currentIndex(), window.windowTitle())
        assert after == before
        assert candidate.read_bytes() == raw
        # A subsequent ordinary save must still target the original document.
        assert window.save_file()
        assert old_path.read_text(encoding="utf-8") == "# Ungespeicherte Änderung"
        assert candidate.read_bytes() == raw
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()


@pytest.mark.parametrize("text", ["# Bücher, Grüße und Öl", "# Literal replacement character: \ufffd"])
def test_valid_utf8_still_opens_and_saves(main_module, tmp_path, monkeypatch, text):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    path = tmp_path / "valid.md"
    path.write_text(text, encoding="utf-8")
    errors = []
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: errors.append(args))
    try:
        window.load_file(path)
        assert not errors
        assert window.current_file == path
        assert window.editor.toPlainText() == text
        window.editor.appendPlainText("Weiter")
        assert window.save_file()
        assert path.read_text(encoding="utf-8") == text + "\nWeiter"
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()
