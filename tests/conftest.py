"""Pytest fixtures fuer CleanMarkdown.

Stellt Qt im Offscreen-Modus bereit, damit Tests headless laufen koennen, und
liefert eine MainWindow-aehnliche Helfer-Instanz fuer die Markdown-Pipeline,
ohne den vollen GUI-Aufbau auszuloesen.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def main_module():
    import main as cleanmarkdown_main
    return cleanmarkdown_main


@pytest.fixture(autouse=True)
def isolated_appdata(tmp_path, monkeypatch):
    """Isoliert %APPDATA% fuer JEDEN Test, der eine MainWindow/SettingsStore
    aufbaut -- verhindert, dass Tests die echte
    ``%APPDATA%\\CleanMarkdown\\settings.json`` des Nutzers lesen oder
    ueberschreiben.

    Fund (2026-07-24, Welle-1-U1/U2-Regressionstests): Ohne diese Isolation
    teilen sich alle Tests, die ueber ``MainWindow()``/``SettingsStore()``
    laufen, die reale Settings-Datei -- inklusive Schreibzugriff beim
    regulaeren ``closeEvent``. Ein Test mit testspezifischen/kaputten Werten
    (z. B. ein absichtlich blockierter ``output_dir``) kontaminiert dadurch
    dauerhaft die echte Anwendungskonfiguration. Genau das ist hier passiert:
    ``test_export_pdf_reports_invalid_output_directory`` schrieb einen
    Pytest-Tempordner als ``output_dir`` in die echte settings.json; ein
    spaeterer Testlauf uebernahm diesen kaputten Pfad, wodurch
    ``target.parent.mkdir()`` in einem produktiven Szenario auf einen
    ``FileExistsError`` lief und der anschliessende ``QMessageBox.critical``
    im Offscreen-Modus unendlich blockierte (kein Nutzer da, der den
    Modal-Dialog schliesst).
    """
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))


@pytest.fixture()
def render_helpers(main_module):
    """Bindet die Render-Hilfsmethoden an ein leichtes Dummy-Objekt.

    Die Methoden ``_protect_code_regions``, ``_restore_protected_regions``,
    ``_render_task_lists`` und ``_inject_math_markup`` greifen nur ueber ``self``
    auf einander zu, ohne weitere Attribute zu nutzen. Daher reicht ein
    SimpleNamespace, um den Aufrufkontext nachzubilden, ohne ``MainWindow`` und
    damit eine vollstaendige Qt-Anwendung instanziieren zu muessen.
    """

    helpers = SimpleNamespace()
    main_window_cls = main_module.MainWindow
    helpers._protect_code_regions = main_window_cls._protect_code_regions.__get__(helpers)
    helpers._restore_protected_regions = main_window_cls._restore_protected_regions.__get__(helpers)
    helpers._render_task_lists = main_window_cls._render_task_lists.__get__(helpers)
    helpers._render_strikethrough = main_window_cls._render_strikethrough.__get__(helpers)
    helpers._inject_math_markup = main_window_cls._inject_math_markup.__get__(helpers)
    return helpers


def render_to_body(helpers, text: str) -> str:
    """Reproduziert die Render-Pipeline aus ``MainWindow._render_preview``.

    Damit lassen sich vollstaendige Markdown-zu-HTML-Pfade in Tests pruefen,
    ohne ein QTextBrowser-Widget aufzubauen.
    """

    import markdown

    text = helpers._inject_math_markup(text)
    body = markdown.markdown(text, extensions=["extra", "sane_lists", "footnotes"])
    body = helpers._render_task_lists(body)
    return helpers._render_strikethrough(body)
