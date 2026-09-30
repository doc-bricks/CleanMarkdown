"""A failed PDF export preserves the previous PDF and never reports success."""
from pathlib import Path
from types import SimpleNamespace

import pytest


def make_window(main_module, tmp_path, monkeypatch, target):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    window.current_file = tmp_path / "source.md"
    window.editor.setPlainText("# Prüfung\n\nBücher und Übergabe.")
    window.is_modified = True
    window.settings.export_confirm = True
    monkeypatch.setattr(main_module.QFileDialog, "getSaveFileName", lambda *args: (str(target), ""))
    return app, window


@pytest.mark.parametrize("stage", ["partial", "empty", "missing", "truncated", "publish"])
@pytest.mark.parametrize("existing", [False, True])
def test_failed_pdf_export_preserves_target(main_module, tmp_path, monkeypatch, stage, existing):
    target = tmp_path / "exports" / "report.pdf"
    target.parent.mkdir()
    original = b"previous PDF bytes"
    if existing:
        target.write_bytes(original)
    app, window = make_window(main_module, tmp_path, monkeypatch, target)
    errors = []
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: errors.append(args))

    class Printer:
        def setOutputFormat(self, value):
            pass

        def setOutputFileName(self, name):
            self.path = Path(name)

        def setPageMargins(self, *args):
            pass

    def print_document(printer):
        if stage == "partial":
            printer.path.write_bytes(b"partial PDF")
            raise OSError("print failure")
        if stage == "empty":
            printer.path.write_bytes(b"")
        if stage == "truncated":
            printer.path.write_bytes(b"%PDF-1.4\nincomplete")
        if stage == "publish":
            printer.path.write_bytes(b"%PDF-1.4\n%%EOF\n")

    monkeypatch.setattr(window, "_create_pdf_printer", Printer)
    monkeypatch.setattr(window, "_build_export_document", lambda: SimpleNamespace(print_=print_document))
    original_replace = main_module.os.replace

    def failing_publish(source, destination):
        if Path(destination) == target:
            raise OSError("destination locked")
        return original_replace(source, destination)

    if stage == "publish":
        monkeypatch.setattr(main_module.os, "replace", failing_publish)
    try:
        window.export_pdf()
        assert len(errors) == 1
        assert window.statusBar().currentMessage() == window.t("cannot_export")
        assert target.read_bytes() == original if existing else not target.exists()
        assert set(target.parent.iterdir()) == ({target} if existing else set())
        assert window.is_modified
        assert window.current_file == tmp_path / "source.md"
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()


def test_real_pdf_export_replaces_previous_pdf(main_module, tmp_path, monkeypatch):
    target = tmp_path / "exports" / "report.pdf"
    target.parent.mkdir()
    target.write_bytes(b"old")
    app, window = make_window(main_module, tmp_path, monkeypatch, target)
    try:
        window.export_pdf()
        data = target.read_bytes()
        assert data.startswith(b"%PDF-")
        assert data.rstrip().endswith(b"%%EOF")
        assert len(data) > 100
        assert window.t("exported") in window.statusBar().currentMessage()
        assert set(target.parent.iterdir()) == {target}
        assert window.is_modified
    finally:
        window.is_modified = False
        window.close()
        app.processEvents()
