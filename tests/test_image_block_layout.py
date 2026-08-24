"""Echte QTextDocument-/QTextBrowser-Layout- und Geometrietests fuer Bilder.

Regression T-20260728-01: Der bisherige Bildtest prueft nur, dass Markdown
ein ``<img>``-Element erzeugt (HTML-String-Ebene). Diese Suite geht darueber
hinaus und misst die tatsaechliche Qt-Blockgeometrie: Absatz davor, Bild,
Absatz danach duerfen sich nicht ueberlappen, das Bild belegt seine eigene
Layout-Hoehe, breite Bilder werden seitenverhaeltnistreu auf die Lesebreite
verkleinert, kleine Bilder werden nicht hochskaliert.

Baut fuer jeden Test eine echte ``MainWindow`` (Offscreen-Qt via
``conftest.isolated_appdata``), rendert Markdown mit lokalen PNG-Dateien und
liest die Blockgeometrie ueber ``QTextDocument``/``QAbstractTextDocumentLayout``
aus -- kein reiner HTML-String-Vergleich.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor, QImage, QTextDocument
from PySide6.QtWidgets import QApplication

IMAGE_OBJECT_REPLACEMENT_CHAR = "￼"


def _make_window(main_module):
    QApplication.instance() or QApplication([])
    window = main_module.MainWindow()
    # Verhindert den dokumentierten Test-Harness-Zwischenfall (2026-08-21):
    # Ein aktiver Autosave-Timer bzw. is_modified=True beim Schliessen loest
    # in _confirm_discard() einen modalen QMessageBox.exec() aus, der im
    # Offscreen-Modus (kein Nutzer zum Klicken) unendlich blockiert.
    window.autosave_timer.stop()
    return window


def _safe_close(window) -> None:
    window.autosave_timer.stop()
    window.is_modified = False
    window.close()


def _save_test_image(path: Path, width: int, height: int, color: str) -> None:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(color))
    assert image.save(str(path)), f"Testbild konnte nicht geschrieben werden: {path}"


def _render_and_lay_out(window, main_module, tmp_path: Path, markdown_text: str, text_width: int = 700):
    """Rendert Markdown in den Viewer und liefert (document, layout, blocks)."""

    window.current_file = tmp_path / "doc.md"
    window.viewer.document().setBaseUrl(QUrl.fromLocalFile(str(tmp_path) + "/"))
    window.editor.setPlainText(markdown_text)
    window._render_preview()

    document = window.viewer.document()
    document.setTextWidth(text_width)
    layout = document.documentLayout()

    blocks = []
    block = document.begin()
    while block.isValid():
        blocks.append(block)
        block = block.next()
    return document, layout, blocks


def _block_rect(layout, block):
    return layout.blockBoundingRect(block)


def _is_image_block(block) -> bool:
    return IMAGE_OBJECT_REPLACEMENT_CHAR in block.text()


def _image_fragment_format(block):
    it = block.begin()
    while not it.atEnd():
        fmt = it.fragment().charFormat()
        if fmt.isImageFormat():
            return fmt.toImageFormat()
        it += 1
    return None


# ---------------------------------------------------------------------------
# Block-im-Dokumentfluss: kein Ueberlappen von Vorher-/Bild-/Nachher-Block
# ---------------------------------------------------------------------------

def test_image_between_paragraphs_forms_own_non_overlapping_block(main_module, tmp_path):
    """Repro aus dem Ticket: Absatz davor. / Bild / Absatz danach., mit
    Leerzeilen. Kein Block darf den naechsten ueberlagern."""
    window = _make_window(main_module)
    try:
        _save_test_image(tmp_path / "grosses-bild.png", 1200, 600, "red")
        markdown_text = (
            "Absatz davor.\n\n![Beispiel](grosses-bild.png)\n\nAbsatz danach."
        )
        document, layout, blocks = _render_and_lay_out(window, main_module, tmp_path, markdown_text)

        image_blocks = [b for b in blocks if _is_image_block(b)]
        assert len(image_blocks) == 1, "Es muss genau ein Bild-Block existieren"
        image_block = image_blocks[0]
        image_rect = _block_rect(layout, image_block)
        assert image_rect.height() > 0, "Bild muss eigene Layout-Hoehe belegen"

        idx = blocks.index(image_block)
        before_block = blocks[idx - 1]
        before_rect = _block_rect(layout, before_block)
        assert "Absatz davor." in before_block.text()
        assert before_rect.bottom() <= image_rect.top() + 0.5, (
            "Vorheriger Absatz darf nicht vom Bild ueberlagert werden"
        )

        # Nachfolgender sichtbarer Text ("Absatz danach.") kann durch die
        # optionale Bildunterschrift von einem weiteren Block getrennt sein
        # (caption via alt-Text) -- entscheidend ist, dass ALLE folgenden
        # Bloecke unterhalb des Bildes beginnen (keine Ueberlagerung).
        after_blocks = blocks[idx + 1:]
        assert any("Absatz danach." in b.text() for b in after_blocks)
        for after_block in after_blocks:
            after_rect = _block_rect(layout, after_block)
            assert after_rect.top() >= image_rect.bottom() - 0.5, (
                "Nachfolgender Text darf nicht mit dem Bild ueberlappen"
            )
    finally:
        _safe_close(window)


def test_image_line_without_blank_lines_still_forms_own_block(main_module, tmp_path):
    """Ohne Leerzeilen zieht Markdown Text-Bild-Text in EINEN Absatz zusammen.
    Der Lesemodus darf dort trotzdem keine Ueberlagerung erzeugen -- die
    alleinstehende Bildzeile muss als eigener Block herausgeloest werden."""
    window = _make_window(main_module)
    try:
        _save_test_image(tmp_path / "bild.png", 400, 200, "purple")
        markdown_text = "Absatz davor.\n![Beispiel](bild.png)\nAbsatz danach."
        document, layout, blocks = _render_and_lay_out(window, main_module, tmp_path, markdown_text)

        image_blocks = [b for b in blocks if _is_image_block(b)]
        assert len(image_blocks) == 1
        image_block = image_blocks[0]
        image_rect = _block_rect(layout, image_block)
        idx = blocks.index(image_block)

        before_block = blocks[idx - 1]
        assert before_block.text().strip() == "Absatz davor.", (
            "Text vor dem Bild muss in einem EIGENEN Block stehen, nicht im selben "
            "Block wie das Bild"
        )
        assert _block_rect(layout, before_block).bottom() <= image_rect.top() + 0.5

        after_blocks = blocks[idx + 1:]
        assert any(b.text().strip() == "Absatz danach." for b in after_blocks)
        for after_block in after_blocks:
            assert _block_rect(layout, after_block).top() >= image_rect.bottom() - 0.5


    finally:
        _safe_close(window)


def test_inline_sentence_image_stays_inline_and_does_not_split_paragraph(main_module, tmp_path):
    """Ein Bild inmitten eines laufenden Satzes bleibt inline: Es entsteht
    KEIN eigener Block, der Satz bleibt EIN Textblock."""
    window = _make_window(main_module)
    try:
        _save_test_image(tmp_path / "icon.png", 32, 32, "orange")
        markdown_text = "Hier ein Icon ![Icon](icon.png) mitten im Satz."
        document, layout, blocks = _render_and_lay_out(window, main_module, tmp_path, markdown_text)

        text_blocks = [b for b in blocks if b.text().strip()]
        assert len(text_blocks) == 1, "Bild inmitten eines Satzes darf keinen Blockumbruch erzeugen"
        assert IMAGE_OBJECT_REPLACEMENT_CHAR in text_blocks[0].text()
        assert "Hier ein Icon" in text_blocks[0].text()
        assert "mitten im Satz." in text_blocks[0].text()
    finally:
        _safe_close(window)


# ---------------------------------------------------------------------------
# Skalierung: breite Bilder verkleinert (seitenverhaeltnistreu), kleine
# Bilder nicht hochskaliert
# ---------------------------------------------------------------------------

def test_oversized_image_is_scaled_down_to_reading_width(main_module, tmp_path):
    window = _make_window(main_module)
    try:
        _save_test_image(tmp_path / "grosses-bild.png", 1200, 600, "red")
        markdown_text = "Vorher.\n\n![Beispiel](grosses-bild.png)\n\nNachher."
        document, layout, blocks = _render_and_lay_out(window, main_module, tmp_path, markdown_text, text_width=700)

        image_block = next(b for b in blocks if _is_image_block(b))
        image_rect = _block_rect(layout, image_block)
        # Natuerliche Hoehe waere 600px; bei Skalierung auf ~700px Lesebreite
        # (abzueglich Rand/Body-Margin) und 2:1-Seitenverhaeltnis liegt die
        # tatsaechliche Blockhoehe deutlich darunter.
        assert 0 < image_rect.height() < 500, (
            f"Ueberbreites Bild muss auf die Lesebreite verkleinert werden, "
            f"Blockhoehe war {image_rect.height()}"
        )
    finally:
        _safe_close(window)


def test_small_image_is_not_upscaled(main_module, tmp_path):
    window = _make_window(main_module)
    try:
        _save_test_image(tmp_path / "klein.png", 40, 30, "blue")
        markdown_text = "Vorher.\n\n![klein](klein.png)\n\nNachher."
        document, layout, blocks = _render_and_lay_out(window, main_module, tmp_path, markdown_text, text_width=700)

        image_block = next(b for b in blocks if _is_image_block(b))
        image_rect = _block_rect(layout, image_block)
        # Natuerliche Hoehe ist 30px. `max-width: 100%` darf ein kleines Bild
        # NICHT auf die Lesebreite hochskalieren -- die Blockhoehe muss nah
        # an der natuerlichen Groesse bleiben, nicht Richtung Lesebreite (700)
        # tendieren.
        assert 20 <= image_rect.height() <= 60, (
            f"Kleines Bild darf nicht hochskaliert werden, Blockhoehe war {image_rect.height()}"
        )
    finally:
        _safe_close(window)


# ---------------------------------------------------------------------------
# Relative Pfade, Alt-Text, eigene Links
# ---------------------------------------------------------------------------

def test_relative_local_image_path_resolves_via_base_url(main_module, tmp_path):
    window = _make_window(main_module)
    try:
        (tmp_path / "assets").mkdir()
        _save_test_image(tmp_path / "assets" / "pic.png", 50, 25, "green")
        markdown_text = "![Mein Alt-Text](assets/pic.png)"
        document, layout, blocks = _render_and_lay_out(window, main_module, tmp_path, markdown_text)

        resource = document.resource(QTextDocument.ResourceType.ImageResource, QUrl("assets/pic.png"))
        assert resource is not None, "Relativer lokaler Bildpfad muss ueber die BaseUrl aufloesbar sein"

        image_block = next(b for b in blocks if _is_image_block(b))
        fmt = _image_fragment_format(image_block)
        assert fmt is not None
        assert fmt.name() == "assets/pic.png"
    finally:
        _safe_close(window)


def test_custom_link_target_preserved_over_image_source_in_document(main_module, tmp_path):
    """Regression: [![Alt](img.png)](https://example.com) darf den Autor-Link
    nicht durch den Bildpfad ueberschreiben -- echte Qt-Anchor-Metadaten."""
    window = _make_window(main_module)
    try:
        _save_test_image(tmp_path / "docs.png", 60, 40, "cyan")
        markdown_text = "[![Docs Diagramm](docs.png)](https://example.com/docs)"
        document, layout, blocks = _render_and_lay_out(window, main_module, tmp_path, markdown_text)

        image_block = next(b for b in blocks if _is_image_block(b))
        fmt = _image_fragment_format(image_block)
        assert fmt is not None
        assert fmt.isAnchor() is True
        assert fmt.anchorHref() == "https://example.com/docs"
    finally:
        _safe_close(window)


# ---------------------------------------------------------------------------
# Beide Themes + Export-Renderer (PDF)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("theme", ["dark", "bright"])
def test_image_block_renders_without_error_in_both_themes(main_module, tmp_path, theme):
    window = _make_window(main_module)
    try:
        _save_test_image(tmp_path / "bild.png", 300, 150, "magenta")
        window.settings.theme = theme
        window.current_file = tmp_path / "doc.md"
        window.viewer.document().setBaseUrl(QUrl.fromLocalFile(str(tmp_path) + "/"))
        window.editor.setPlainText("Vorher.\n\n![Beispiel](bild.png)\n\nNachher.")
        window._render_preview()

        document = window.viewer.document()
        document.setTextWidth(700)
        blocks = []
        block = document.begin()
        while block.isValid():
            blocks.append(block)
            block = block.next()
        assert any(_is_image_block(b) for b in blocks)
    finally:
        _safe_close(window)


def test_export_document_places_image_as_own_block(main_module, tmp_path):
    """Der PDF-Export nutzt immer das helle Theme und ein eigenstaendiges
    QTextDocument -- auch dort muss das Bild ein eigener Block bleiben."""
    window = _make_window(main_module)
    try:
        _save_test_image(tmp_path / "bild.png", 300, 150, "teal")
        window.current_file = tmp_path / "doc.md"
        window.viewer.document().setBaseUrl(QUrl.fromLocalFile(str(tmp_path) + "/"))
        window.editor.setPlainText("Vorher.\n\n![Beispiel](bild.png)\n\nNachher.")

        export_document = window._build_export_document()
        export_document.setTextWidth(700)

        blocks = []
        block = export_document.begin()
        while block.isValid():
            blocks.append(block)
            block = block.next()

        image_blocks = [b for b in blocks if _is_image_block(b)]
        assert len(image_blocks) == 1
    finally:
        _safe_close(window)
