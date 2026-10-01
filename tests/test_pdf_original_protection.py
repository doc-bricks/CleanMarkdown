import os
from pathlib import Path

import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import main

@pytest.mark.parametrize('alias', ['direct', 'relative', 'hardlink', 'late-hardlink', 'source-change', 'symlink'])
def test_pdf_export_preserves_active_markdown(tmp_path, monkeypatch, alias):
    monkeypatch.setenv('APPDATA', str(tmp_path / 'appdata'))
    app = main.QApplication.instance() or main.QApplication([])
    window = main.MainWindow()
    source = tmp_path / 'original.md'
    original = '# Bücher\n\nUnersetzbares Original.'.encode('utf-8')
    source.write_bytes(original)
    window.load_file(source)
    target = source if alias in ('direct', 'source-change') else tmp_path / 'chosen.pdf'
    if alias == 'relative':
        (tmp_path / 'sub').mkdir()
        target = tmp_path / 'sub' / '..' / source.name
    if alias == 'hardlink':
        os.link(source, target)
    if alias == 'symlink':
        try:
            target.symlink_to(source)
        except OSError as exc:
            if getattr(exc, 'winerror', None) != 1314:
                raise
            window.is_modified = False
            window.close()
            pytest.skip('Windows account lacks symbolic-link creation privilege')
    monkeypatch.setattr(main.QFileDialog, 'getSaveFileName', lambda *args: (str(target), ''))
    errors = []
    monkeypatch.setattr(main.QMessageBox, 'critical', lambda *args: errors.append(args))
    if alias == 'source-change':
        # Change GUI state during the save dialog: the original chosen at
        # export start must remain protected as well as the current file.
        replacement = tmp_path / 'replacement.md'
        replacement.write_text('# Replacement', encoding='utf-8')
        def choose(*args):
            window.current_file = replacement
            return str(target), ''
        monkeypatch.setattr(main.QFileDialog, 'getSaveFileName', choose)
    if alias == 'late-hardlink':
        real_build = window._build_export_document
        def build():
            document = real_build()
            class Document:
                def print_(self, printer):
                    document.print_(printer)
                    os.link(source, target)
            return Document()
        monkeypatch.setattr(window, '_build_export_document', build)
    window.settings.export_confirm = True
    try:
        window.export_pdf()
        assert source.read_bytes() == original
        assert target.read_bytes() == original
        assert len(errors) == 1
        assert window.statusBar().currentMessage() == window.t('cannot_export')
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()

@pytest.mark.parametrize('stat_error', [False, True])
def test_pdf_export_normal_target_and_stat_error(tmp_path, monkeypatch, stat_error):
    monkeypatch.setenv('APPDATA', str(tmp_path / 'appdata'))
    app = main.QApplication.instance() or main.QApplication([])
    window = main.MainWindow()
    source = tmp_path / 'source.md'
    original = '# Prüfung\n\nBücher bleiben erhalten.'.encode('utf-8')
    source.write_bytes(original)
    window.load_file(source)
    target = tmp_path / 'report.pdf'
    target.write_bytes(b'previous PDF')
    monkeypatch.setattr(main.QFileDialog, 'getSaveFileName', lambda *args: (str(target), ''))
    errors = []
    monkeypatch.setattr(main.QMessageBox, 'critical', lambda *args: errors.append(args))
    if stat_error:
        original_samefile = Path.samefile
        def samefile(path, other):
            if path == target:
                raise PermissionError('Cannot establish target identity')
            return original_samefile(path, other)
        monkeypatch.setattr(Path, 'samefile', samefile)
    window.settings.export_confirm = True
    try:
        window.export_pdf()
        assert source.read_bytes() == original
        if stat_error:
            assert errors
            assert target.read_bytes() == b'previous PDF'
            assert window.statusBar().currentMessage() == window.t('cannot_export')
        else:
            assert not errors
            assert target.read_bytes().startswith(b'%PDF-')
            assert window.t('exported') in window.statusBar().currentMessage()
        assert not list(tmp_path.glob('.cleanmarkdown-pdf-*'))
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()

