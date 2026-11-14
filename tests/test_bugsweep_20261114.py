"""Regressionstests — Bugsweep CleanMarkdown 2026-11-14."""
import pytest


def _window(main_module):
    application = main_module.QApplication.instance() or main_module.QApplication([])
    return application, main_module.MainWindow()


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_saving_keeps_the_files_line_endings(main_module, tmp_path, newline):
    """Laden normalisiert Zeilenenden, Speichern schrieb immer os.linesep: unter Windows wurde jede
    LF-Datei (z. B. README in einem Git-Repo) beim ersten Speichern komplett auf CRLF umgeschrieben —
    jede Zeile im Diff geändert."""
    path = tmp_path / "README.md"
    original = newline.join([b"# Titel", b"", b"Inhalt mit \xc3\xbcmlaut", b""])
    path.write_bytes(original)
    application, window = _window(main_module)
    try:
        window.load_file(path)
        window.is_modified = True
        assert window.save_file() is True
        assert path.read_bytes() == original
    finally:
        window.is_modified = False
        window.close()


def test_failing_autosave_does_not_stack_modal_error_dialogs(main_module, tmp_path, monkeypatch):
    """Autosave rief save_file(), das bei einem Fehler (Datei schreibgeschützt, Stick abgezogen) ein
    modales Fehlerfenster öffnet. Das modale Fenster lässt den wiederholenden Autosave-Timer weiterlaufen —
    alle paar Sekunden ein weiteres Fehlerfenster übereinander."""
    import time

    application, window = _window(main_module)
    window.current_file = tmp_path / "fehlt" / "doc.md"  # Ordner existiert nicht: Speichern scheitert
    window.editor.setPlainText("Text")
    window.is_modified = True
    window.settings.autosave_enabled = True
    window.autosave_timer.start(20)
    depth = {"now": 0, "max": 0}

    def modal(*_args, **_kwargs):  # verhält sich wie ein modales Fenster: eigene Ereignisschleife
        depth["now"] += 1
        depth["max"] = max(depth["max"], depth["now"])
        if depth["now"] < 4:
            end = time.monotonic() + 0.2
            while time.monotonic() < end:
                application.processEvents()
                time.sleep(0.01)
        depth["now"] -= 1

    monkeypatch.setattr(main_module.QMessageBox, "critical", modal)
    try:
        window._autosave_if_needed()
        assert depth["max"] <= 1, f"{depth['max']} Fehlerfenster übereinander"
        assert window.is_modified is True
    finally:
        window.autosave_timer.stop()
        window.is_modified = False
        window.close()
