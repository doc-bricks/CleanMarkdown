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
