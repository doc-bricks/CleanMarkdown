"""Regressionstests — bugfix-library-transfer 2026-06-21."""
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
MAIN = ROOT / "main.py"
MANAGE_TRANSLATIONS = ROOT / "manage_translations.py"


class TestD2NoDeprecatedEnums(unittest.TestCase):
    """BUG-D2: Deprecated Qt-Enums in main.py (PySide6 6.4+)."""

    def _src(self):
        return MAIN.read_text(encoding="utf-8")

    def test_no_qt_toolbutton_text_beside_icon(self):
        self.assertNotIn(
            "Qt.ToolButtonTextBesideIcon",
            self._src(),
            "Qt.ToolButtonTextBesideIcon (deprecated) in main.py — BUG-D2",
        )

    def test_no_qt_top_toolbar_area(self):
        self.assertNotIn(
            "Qt.TopToolBarArea",
            self._src(),
            "Qt.TopToolBarArea (deprecated) in main.py — BUG-D2",
        )

    def test_no_qt_toolbutton_text_only(self):
        self.assertNotIn(
            "Qt.ToolButtonTextOnly",
            self._src(),
            "Qt.ToolButtonTextOnly (deprecated) in main.py — BUG-D2",
        )

    def test_no_qt_align_right_bare(self):
        src = self._src()
        self.assertNotIn(
            "Qt.AlignRight",
            src,
            "Qt.AlignRight (deprecated) in main.py — BUG-D2",
        )

    def test_no_qmessagebox_warning_bare(self):
        src = self._src()
        self.assertNotIn(
            "QMessageBox.Warning",
            src,
            "QMessageBox.Warning (deprecated) in main.py — BUG-D2",
        )

    def test_no_qmessagebox_role_bare(self):
        src = self._src()
        for old in ("QMessageBox.AcceptRole", "QMessageBox.DestructiveRole", "QMessageBox.RejectRole"):
            self.assertNotIn(old, src, f"{old} (deprecated) in main.py — BUG-D2")

    def test_no_qdialogbuttonbox_bare(self):
        src = self._src()
        for old in ("QDialogButtonBox.Ok", "QDialogButtonBox.Cancel"):
            self.assertNotIn(
                old,
                src,
                f"{old} (deprecated bare form) in main.py — BUG-D2",
            )

    def test_no_remaining_dialog_or_print_bare_enums(self):
        src = self._src()
        for old in (
            "QDialog.Accepted",
            "QPrinter.HighResolution",
            "QPrinter.PdfFormat",
            "QPageLayout.Millimeter",
        ):
            self.assertNotIn(old, src, f"{old} (deprecated bare form) in main.py — BUG-D2")


class TestU2ManageTranslationsJsonLoad(unittest.TestCase):
    """BUG-U2: json.load in manage_translations.py ohne JSONDecodeError-Handler."""

    def test_has_json_error_handler(self):
        src = MANAGE_TRANSLATIONS.read_text(encoding="utf-8")
        idx = src.find("json.load(f)")
        self.assertGreater(idx, 0, "json.load(f) nicht in manage_translations.py gefunden")
        window = src[max(0, idx - 100):idx + 50]
        self.assertIn(
            "JSONDecodeError",
            window,
            "manage_translations: json.load ohne JSONDecodeError-Handler — BUG-U2",
        )


class TestPdfExportSafePrinterCreation(unittest.TestCase):
    """Regression: PDF-Export muss PDF-Druckertreiber bevorzugen, um Haenger an Offline-Netzwerkdruckern zu vermeiden."""

    def test_create_pdf_printer_uses_pdf_printer_when_available(self):
        from PySide6.QtWidgets import QApplication
        from PySide6.QtPrintSupport import QPrinter
        import main

        _app = QApplication.instance() or QApplication([])
        printer = main.MainWindow._create_pdf_printer()
        self.assertIsInstance(printer, QPrinter)

    def test_create_pdf_printer_prioritizes_pdf_names(self):
        from unittest.mock import patch, MagicMock
        import main

        mock_printer_info = MagicMock()
        mock_pdf_info = MagicMock()
        mock_pdf_info.isNull.return_value = False
        mock_printer_info.availablePrinterNames.return_value = ["Canon TS5300 series", "Microsoft Print to PDF"]
        mock_printer_info.printerInfo.side_effect = lambda name: mock_pdf_info if name == "Microsoft Print to PDF" else MagicMock(isNull=lambda: False)

        with patch("main.QPrinterInfo", mock_printer_info), patch("main.QPrinter") as mock_qprinter:
            main.MainWindow._create_pdf_printer()
            mock_printer_info.printerInfo.assert_called_with("Microsoft Print to PDF")
            mock_qprinter.assert_called_with(mock_pdf_info, mock_qprinter.PrinterMode.HighResolution)


if __name__ == "__main__":
    unittest.main()

