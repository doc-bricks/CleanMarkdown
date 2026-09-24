"""Typing must not re-render the whole preview on every keystroke (T-20260924-322340371)."""


def test_typing_debounces_and_tab_switch_flushes(main_module):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    try:
        window._render_preview()
        window.editor.setPlainText("# Titel")
        assert window.preview_timer.isActive()
        assert "Titel" not in window.viewer.toPlainText()

        window.tabs.setCurrentIndex(1 - window.tabs.currentIndex())
        window.tabs.setCurrentIndex(1 - window.tabs.currentIndex())
        assert not window.preview_timer.isActive()
        assert "Titel" in window.viewer.toPlainText()
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()
