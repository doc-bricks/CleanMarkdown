"""Regressionstests — Link-Härtung CleanMarkdown 2026-11-15."""
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6.QtCore import QUrl


def _window(main_module):
    application = main_module.QApplication.instance() or main_module.QApplication([])
    return application, main_module.MainWindow()


@pytest.mark.parametrize(
    ("target", "with_asset_dir"),
    [
        ("file://server/share/x.txt", True),
        (r"\\server\share\x.txt", True),
        ("//server/share/x.txt", True),
        ("file://localhost/share/x.txt", True),
        ("file://localhost/share/x.txt", False),
        ("   " + r"\\server\share\x.txt", True),
        ("   " + r"\\server\share\x.txt", False),
    ],
)
def test_unc_links_require_confirmation(main_module, tmp_path, monkeypatch, target, with_asset_dir):
    """Befund 1: UNC-/SMB-Ziele dürfen nie ohne Rückfrage geöffnet werden, auch nicht mit
    Positivlisten-Endung (.txt), mit file://localhost/<share> oder mit führenden Leerzeichen."""
    _app, window = _window(main_module)
    window._session_asset_dir = tmp_path if with_asset_dir else None
    opened, asked = [], []
    monkeypatch.setattr(main_module.QDesktopServices, "openUrl", lambda url: opened.append(url.toString()) or True)
    monkeypatch.setattr(
        main_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a) or main_module.QMessageBox.StandardButton.No,
    )
    try:
        window._open_anchor(QUrl(target))
        assert opened == [], f"{target} ohne Rückfrage geöffnet"
        assert len(asked) == 1
    finally:
        window.close()


@pytest.mark.parametrize(
    "target",
    [
        "file://server/share/bild.png",
        r"\\server\share\bild.png",
        "//server/share/bild.png",
        "file://localhost/share/bild.png",
    ],
)
def test_unc_image_links_require_confirmation_before_dialog(main_module, tmp_path, monkeypatch, target):
    """Befund 1: UNC-Bildlinks dürfen nicht ohne Rückfrage an ImagePreviewDialog übergeben werden."""
    _app, window = _window(main_module)
    window._session_asset_dir = tmp_path
    opened, asked, dialog_calls = [], [], []
    monkeypatch.setattr(main_module.QDesktopServices, "openUrl", lambda url: opened.append(url.toString()) or True)
    monkeypatch.setattr(
        main_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a) or main_module.QMessageBox.StandardButton.No,
    )
    monkeypatch.setattr(
        main_module,
        "ImagePreviewDialog",
        lambda *a, **k: dialog_calls.append((a, k)) or SimpleNamespace(exec=lambda: 0),
    )
    try:
        window._open_anchor(QUrl(target))
        assert dialog_calls == [], f"ImagePreviewDialog wurde für {target} ohne Ja erzeugt"
        assert opened == []
        assert len(asked) == 1
    finally:
        window.close()


@pytest.mark.parametrize(
    "target",
    [
        r"\\server\share\bild:stream.png",
        r"\\server:80\share\bild.png",
        "//./UNC/server/share/bild.png",
        "file://localhost/share/bild.png",
        "file://localhost/share/x.txt",
    ],
)
def test_is_network_target_detects_colon_device_unc_and_localhost_share(main_module, target):
    """Runde 2 (Befunde 1 & 2): UNC-Ziele mit Doppelpunkt, //./UNC/... und file://localhost/<share>
    werden direkt als Netzwerkziel erkannt."""
    assert main_module._is_network_target(target) is True


@pytest.mark.parametrize(
    "target",
    [
        "file://server/share/bild.png",
        r"\\server\share\bild.png",
        "//server/share/bild.png",
        "%5C%5Cserver%5Cshare%5Cbild.png",
        r"\\server\share\bild:stream.png",
        r"\\server:80\share\bild.png",
        "//./UNC/server/share/bild.png",
        "file://localhost/share/bild.png",
    ],
)
def test_load_pixmap_blocks_unc_without_network_access(main_module, tmp_path, monkeypatch, target):
    """Befund 1: ImagePreviewDialog._load_pixmap liefert für UNC-Ziele ein leeres QPixmap ohne
    Path.exists() oder QPixmap.load() aufzurufen."""
    _app = main_module.QApplication.instance() or main_module.QApplication([])
    exists_calls, load_calls = [], []

    def fake_exists(self):
        exists_calls.append(str(self))
        return False

    def fake_load(self, source, *_args, **_kwargs):
        load_calls.append(source)
        return False

    monkeypatch.setattr(Path, "exists", fake_exists)
    monkeypatch.setattr(main_module.QPixmap, "load", fake_load)

    pixmap = main_module.ImagePreviewDialog._load_pixmap(None, target, tmp_path)
    assert pixmap.isNull()
    assert exists_calls == [], f"Path.exists wurde auf UNC-Ziel aufgerufen: {exists_calls}"
    assert load_calls == [], f"QPixmap.load wurde auf UNC-Ziel aufgerufen: {load_calls}"


@pytest.mark.parametrize(
    ("target", "opens_without_asking"),
    [
        ("../geheim.txt", False),
        ("../../x.txt", False),
        ("/etc/hosts.txt", False),
        ("%2e%2e/geheim.txt", False),
        # Positivkontrolle (bereits vorher grün): Unterordner im Dokumentordner öffnet direkt
        ("unterordner/notiz.txt", True),
    ],
)
def test_relative_links_escaping_asset_dir_require_confirmation(
    main_module, tmp_path, monkeypatch, target, opens_without_asking
):
    """Befund 2: Relative/pfadabsolute Links außerhalb von _session_asset_dir erfordern Rückfrage;
    Unterordner innerhalb von _session_asset_dir öffnen weiter direkt."""
    _app, window = _window(main_module)
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    window._session_asset_dir = doc_dir
    opened, asked = [], []
    monkeypatch.setattr(main_module.QDesktopServices, "openUrl", lambda url: opened.append(url.toString()) or True)
    monkeypatch.setattr(
        main_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a) or main_module.QMessageBox.StandardButton.No,
    )
    try:
        window._open_anchor(QUrl(target))
        if opens_without_asking:
            assert len(opened) == 1 and not asked, (opened, asked)
        else:
            assert opened == [], f"{target} außerhalb des Dokumentordners ohne Rückfrage geöffnet"
            assert len(asked) == 1
    finally:
        window.close()


@pytest.mark.parametrize("target", ["seite.html", "seite.htm"])
def test_local_html_links_require_confirmation(main_module, tmp_path, monkeypatch, target):
    """Befund 3: Lokale .html- und .htm-Dateien sind aus SAFE_LOCAL_LINK_SUFFIXES entfernt und
    dürfen nur noch nach Rückfrage geöffnet werden."""
    _app, window = _window(main_module)
    window._session_asset_dir = tmp_path
    opened, asked = [], []
    monkeypatch.setattr(main_module.QDesktopServices, "openUrl", lambda url: opened.append(url.toString()) or True)
    monkeypatch.setattr(
        main_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a) or main_module.QMessageBox.StandardButton.No,
    )
    try:
        window._open_anchor(QUrl(target))
        assert opened == [], f"{target} ohne Rückfrage geöffnet"
        assert len(asked) == 1
    finally:
        window.close()


@pytest.mark.parametrize(
    ("target", "expected_fragment"),
    [
        ("#kapitel", "kapitel"),
        ("#fn:1", "fn:1"),
    ],
)
def test_pure_anchor_links_scroll_viewer_without_prompt_or_openurl(
    main_module, tmp_path, monkeypatch, target, expected_fragment
):
    """Befund 4: Reine Anker-Links (#kapitel, Fußnoten) rufen viewer.scrollToAnchor(fragment) auf,
    ohne openUrl oder QMessageBox.question auszulösen."""
    _app, window = _window(main_module)
    window._session_asset_dir = tmp_path
    scrolled, opened, asked = [], [], []
    monkeypatch.setattr(window.viewer, "scrollToAnchor", lambda name: scrolled.append(name))
    monkeypatch.setattr(main_module.QDesktopServices, "openUrl", lambda url: opened.append(url.toString()) or True)
    monkeypatch.setattr(
        main_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a) or main_module.QMessageBox.StandardButton.No,
    )
    try:
        window._open_anchor(QUrl(target))
        assert scrolled == [expected_fragment]
        assert opened == []
        assert asked == []
    finally:
        window.close()


@pytest.mark.parametrize(
    ("target", "with_asset_dir"),
    [
        # Positivkontrollen (bereits vorher grün): bleiben ohne Rückfrage
        ("https://example.org", True),
        ("notizen.txt", True),
        ("handbuch.pdf", True),
        ("notizen.txt", False),
        ("file://localhost/c:/notizen.txt", False),
    ],
)
def test_safe_links_positive_controls_open_without_confirmation(
    main_module, tmp_path, monkeypatch, target, with_asset_dir
):
    """Positivkontrollen (bereits vor dem Fix grün): Web-Links, sichere lokale Dokumente und
    file://localhost ohne Dokumentordner-Grenze öffnen weiterhin ohne Rückfrage."""
    _app, window = _window(main_module)
    window._session_asset_dir = tmp_path if with_asset_dir else None
    opened, asked = [], []
    monkeypatch.setattr(main_module.QDesktopServices, "openUrl", lambda url: opened.append(url.toString()) or True)
    monkeypatch.setattr(
        main_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a) or main_module.QMessageBox.StandardButton.No,
    )
    try:
        window._open_anchor(QUrl(target))
        assert len(opened) == 1 and not asked, (opened, asked)
    finally:
        window.close()


@pytest.mark.parametrize(
    ("target_filename", "opens_without_asking"),
    [
        ("werkzeug.bat", False),
        ("ziel.md", True),
    ],
)
def test_symlink_inside_asset_dir_checks_resolved_suffix(
    main_module, tmp_path, monkeypatch, target_filename, opens_without_asking
):
    """Runde 2 (Befund 4): Ein Symlink mit harmloser Endung (notiz.txt) auf eine gefährliche
    Endung (werkzeug.bat) im Dokumentordner erfordert Rückfrage; ein Symlink auf .md öffnet direkt."""
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    real_target = doc_dir / target_filename
    real_target.write_text("inhalt", encoding="utf-8")
    link_path = doc_dir / "notiz.txt"
    try:
        os.symlink(real_target, link_path)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"os.symlink auf diesem System nicht verfügbar: {exc}")

    _app, window = _window(main_module)
    window._session_asset_dir = doc_dir
    opened, asked = [], []
    monkeypatch.setattr(main_module.QDesktopServices, "openUrl", lambda url: opened.append(url.toString()) or True)
    monkeypatch.setattr(
        main_module.QMessageBox,
        "question",
        lambda *a, **k: asked.append(a) or main_module.QMessageBox.StandardButton.No,
    )
    try:
        window._open_anchor(QUrl("notiz.txt"))
        if opens_without_asking:
            assert len(opened) == 1 and not asked, (opened, asked)
        else:
            assert opened == [], f"Symlink auf {target_filename} ohne Rückfrage geöffnet"
            assert len(asked) == 1
    finally:
        window.close()
