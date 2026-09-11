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


def test_prefix_actions_on_empty_line_preserve_space(main_module):
    """Prueft, dass Listen-, Zitat- und Ueberschriften-Aktionen auf einer
    leeren Zeile den vollstaendigen Praefix inklusive Leerzeichen einfuegen,
    damit sofort getippter Text als gueltiges Markdown gerendert wird."""
    _, window = _make_window(main_module)

    # 1. Bullet list (- )
    window.editor.setPlainText("")
    window.bullet_action.trigger()
    assert window.editor.toPlainText() == "- ", (
        f"Auf leerer Zeile muss '- ' eingefuegt werden, nicht {window.editor.toPlainText()!r}"
    )

    # 2. Numbered list (1. )
    window.editor.setPlainText("")
    window.numbered_action.trigger()
    assert window.editor.toPlainText() == "1. ", (
        f"Auf leerer Zeile muss '1. ' eingefuegt werden, nicht {window.editor.toPlainText()!r}"
    )

    # 3. Checklist (- [ ] )
    window.editor.setPlainText("")
    window.checklist_action.trigger()
    assert window.editor.toPlainText() == "- [ ] ", (
        f"Auf leerer Zeile muss '- [ ] ' eingefuegt werden, nicht {window.editor.toPlainText()!r}"
    )

    # 4. Blockquote (> )
    window.editor.setPlainText("")
    window.blockquote_action.trigger()
    assert window.editor.toPlainText() == "> ", (
        f"Auf leerer Zeile muss '> ' eingefuegt werden, nicht {window.editor.toPlainText()!r}"
    )

    # 5. Headings (# , ## , ### )
    window.editor.setPlainText("")
    window.heading1_action.trigger()
    assert window.editor.toPlainText() == "# ", (
        f"Auf leerer Zeile muss '# ' eingefuegt werden, nicht {window.editor.toPlainText()!r}"
    )

    window.editor.setPlainText("")
    window.heading2_action.trigger()
    assert window.editor.toPlainText() == "## ", (
        f"Auf leerer Zeile muss '## ' eingefuegt werden, nicht {window.editor.toPlainText()!r}"
    )

    window.is_modified = False
    window.close()


def test_prefix_actions_multiline_preserve_blank_lines(main_module):
    """Prueft, dass bei Mehrzeilenselektion Leerzeilen zwischen Absaetzen
    nicht mit isolierten Satzzeichen wie '-', '2.' oder '#' korrumpiert werden."""
    _, window = _make_window(main_module)

    # Bullet list ueber Absaetze mit Leerzeile
    window.editor.setPlainText("Absatz 1\n\nAbsatz 2")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.Document)
    window.editor.setTextCursor(cursor)
    window.bullet_action.trigger()
    assert window.editor.toPlainText() == "- Absatz 1\n\n- Absatz 2"

    # Numbered list ueber Absaetze mit Leerzeile
    window.editor.setPlainText("Absatz 1\n\nAbsatz 2")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.Document)
    window.editor.setTextCursor(cursor)
    window.numbered_action.trigger()
    assert window.editor.toPlainText() == "1. Absatz 1\n\n2. Absatz 2"

    # Heading 1 ueber Absaetze mit Leerzeile
    window.editor.setPlainText("Absatz 1\n\nAbsatz 2")
    cursor = window.editor.textCursor()
    cursor.select(QTextCursor.Document)
    window.editor.setTextCursor(cursor)
    window.heading1_action.trigger()
    assert window.editor.toPlainText() == "# Absatz 1\n\n# Absatz 2"

    window.is_modified = False
    window.close()

