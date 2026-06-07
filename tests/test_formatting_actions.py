from __future__ import annotations

from PySide6.QtGui import QTextCursor


def _make_window(main_module):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    return app, window


def test_clear_formatting_action_removes_common_markdown(main_module):
    _, window = _make_window(main_module)
    window.editor.setPlainText(
        "# Titel\n\n"
        "- [x] Erledigt\n"
        "> Zitat\n\n"
        "[Link](https://example.com) und ![Bild](bild.png)\n"
        "**fett** / *kursiv* / `code`\n\n"
        "$$\nE = mc^2\n$$\n"
    )

    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.Document)
    window.editor.setTextCursor(cursor)

    window.clear_formatting_action.trigger()

    assert window.editor.toPlainText() == (
        "Titel\n\n"
        "Erledigt\n"
        "Zitat\n\n"
        "Link und Bild\n"
        "fett / kursiv / code\n\n"
        "E = mc^2\n"
    )

    window.is_modified = False
    window.close()


def test_clear_formatting_action_works_without_selection(main_module):
    _, window = _make_window(main_module)
    window.editor.setPlainText("> Zitat")

    cursor = window.editor.textCursor()
    cursor.setPosition(2)
    window.editor.setTextCursor(cursor)

    window.clear_formatting_action.trigger()

    assert window.editor.toPlainText() == "Zitat"

    window.is_modified = False
    window.close()


def test_insert_code_block_selects_placeholder_not_backticks(main_module):
    """Bug #1: _insert_code_block() ohne Selektion waehlte nach dem Up-Move
    die oeffnenden Backticks aus (```), statt den Platzhalter 'code'."""
    _, window = _make_window(main_module)
    window.editor.setPlainText("")

    window._insert_code_block()

    cursor = window.editor.textCursor()
    selected = cursor.selectedText()
    assert selected == "code", (
        f"_insert_code_block() soll 'code' auswaehlen, nicht {selected!r} — Bug #1"
    )

    window.is_modified = False
    window.close()
