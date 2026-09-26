"""Regressionstest fuer T-20260924-322340371 (traeges Tippen).

Root Cause (gemessen): ``_render_preview()`` parst das GESAMTE Dokument neu
(u. a. ``markdown.markdown()``) und ruft ``viewer.setHtml()`` auf -- bei einem
56 KB grossen Dokument mit einer 600-zeiligen Tabelle gemessen ~300ms/Aufruf.
Ohne Debounce lief das bei JEDEM Tastendruck synchron auf dem UI-Thread.

Dieser Test belegt, dass ``textChanged`` nicht mehr direkt rendert, sondern
ueber ``preview_debounce_timer`` gesammelt wird, und dass der Preview-Inhalt
nach Ablauf des Debounce trotzdem korrekt aktualisiert wird.
"""
from __future__ import annotations

import time


def _make_window(main_module):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    return app, window


def test_typing_does_not_render_synchronously(main_module):
    app, window = _make_window(main_module)

    window.editor.setPlainText("# Vorher")
    window.preview_debounce_timer.stop()
    window._render_preview()
    app.processEvents()
    assert "Vorher" in window.viewer.toPlainText()

    # Simuliert einen Tastendruck: setText loest textChanged aus, was den
    # Debounce-Timer NUR startet, nicht sofort rendert -- der Viewer muss
    # bis zum Timer-Ablauf den alten Inhalt behalten.
    window.editor.setPlainText("# Nachher")
    app.processEvents()
    assert window.preview_debounce_timer.isActive(), "textChanged muss den Debounce-Timer starten"
    assert "Vorher" in window.viewer.toPlainText(), "Viewer darf sich vor Timer-Ablauf nicht aendern"

    window.is_modified = False
    window.close()


def test_debounced_render_fires_after_interval(main_module):
    app, window = _make_window(main_module)

    window.editor.setPlainText("# Nachher")
    deadline = time.monotonic() + (window.PREVIEW_DEBOUNCE_MS + 500) / 1000
    while window.preview_debounce_timer.isActive() and time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.02)
    app.processEvents()

    assert not window.preview_debounce_timer.isActive()
    assert "Nachher" in window.viewer.toPlainText()

    window.is_modified = False
    window.close()


def test_repeated_typing_collapses_into_a_single_pending_render(main_module):
    """Mehrere schnelle 'Tastendruecke' duerfen nur EINEN Render anstossen."""
    app, window = _make_window(main_module)

    render_calls = []
    original = window._render_preview

    def counting_render():
        render_calls.append(1)
        return original()

    window._render_preview = counting_render
    window.preview_debounce_timer.timeout.disconnect()
    window.preview_debounce_timer.timeout.connect(window._render_preview)

    for ch in "abcde":
        window.editor.insertPlainText(ch)
        app.processEvents()  # Tippgeschwindigkeit: weit unter PREVIEW_DEBOUNCE_MS

    assert render_calls == [], "waehrend des Tippens darf noch nicht gerendert worden sein"
    assert window.preview_debounce_timer.isActive()

    window.is_modified = False
    window.close()
