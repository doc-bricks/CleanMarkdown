"""Tests for UX and accessibility enhancements in CleanMarkdown.

Validates WCAG 2.1 AA screen reader semantics, QLabel buddies, keyboard shortcuts,
Help menu, Shortcuts and About dialogs, and German umlauts invariants.
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from translator import TranslationSystem

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def ensure_qapp(main_module):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    return app


@pytest.fixture
def main_window(main_module):
    window = main_module.MainWindow()
    yield window
    window.close()


def test_new_document_action_and_lifecycle(main_window):
    assert hasattr(main_window, "new_action"), "MainWindow should have new_action"
    assert main_window.new_action.shortcut().toString() in ("Ctrl+N", "Ctrl+n")
    assert main_window.new_action.toolTip() != ""

    # Simulate dirty editor
    main_window.editor.setPlainText("# Dirty content")
    main_window.is_modified = True

    # User cancels discard
    main_window._confirm_discard = lambda: False
    main_window.new_file()
    assert main_window.editor.toPlainText() == "# Dirty content"
    assert main_window.is_modified is True

    # User confirms discard
    main_window._confirm_discard = lambda: True
    main_window.new_file()
    assert main_window.editor.toPlainText() == ""
    assert main_window.is_modified is False
    assert main_window.current_file is None
    assert main_window.tabs.currentIndex() == 1  # Switched to editor tab
    assert main_window.t("new_document_created") in main_window.statusBar().currentMessage()


def test_keyboard_shortcuts_and_help_menu(main_window):
    assert main_window.new_action.shortcut().toString() in ("Ctrl+N", "Ctrl+n")
    assert main_window.open_action.shortcut().toString() in ("Ctrl+O", "Ctrl+o")
    assert main_window.save_action.shortcut().toString() in ("Ctrl+S", "Ctrl+s")
    assert main_window.save_as_action.shortcut().toString() in ("Ctrl+Shift+S", "Ctrl+Shift+s")
    assert main_window.export_session_action.shortcut().toString() in ("Ctrl+Shift+E", "Ctrl+Shift+e")
    assert main_window.export_pdf_action.shortcut().toString() in ("Ctrl+Shift+P", "Ctrl+Shift+p")
    assert main_window.settings_action.shortcut().toString() == "Ctrl+,"
    assert main_window.shortcuts_action.shortcut().toString() == "F1"

    # Help menu verification
    assert hasattr(main_window, "help_menu")
    help_actions = main_window.help_menu.actions()
    assert main_window.shortcuts_action in help_actions
    assert main_window.about_action in help_actions


def test_settings_dialog_buddies_and_accessibility(main_module):
    settings = main_module.AppSettings()
    translator = TranslationSystem("de", app_dir=PROJECT_ROOT)
    dialog = main_module.SettingsDialog(settings, translator.t)

    # Form label buddies
    assert dialog.language_label.buddy() == dialog.language_combo
    assert dialog.theme_label.buddy() == dialog.theme_combo
    assert dialog.default_mode_label.buddy() == dialog.default_mode_combo
    assert dialog.autosave_interval_label.buddy() == dialog.autosave_interval
    assert dialog.export_mode_label.buddy() == dialog.export_mode_combo
    assert dialog.output_dir_label.buddy() == dialog.output_dir_edit

    # Accessible names
    assert dialog.language_combo.accessibleName() != ""
    assert dialog.theme_combo.accessibleName() != ""
    assert dialog.default_mode_combo.accessibleName() != ""
    assert dialog.autosave_enabled.accessibleName() != ""
    assert dialog.autosave_interval.accessibleName() != ""
    assert dialog.export_mode_combo.accessibleName() != ""
    assert dialog.export_confirm.accessibleName() != ""
    assert dialog.file_toolbar_visible.accessibleName() != ""
    assert dialog.editor_toolbar_collapsed.accessibleName() != ""
    assert dialog.sync_scroll_positions.accessibleName() != ""
    assert dialog.output_dir_edit.accessibleName() != ""

    # Accessible descriptions
    assert dialog.language_combo.accessibleDescription() != ""
    assert dialog.theme_combo.accessibleDescription() != ""
    assert dialog.default_mode_combo.accessibleDescription() != ""
    assert dialog.autosave_interval.accessibleDescription() != ""
    assert dialog.export_mode_combo.accessibleDescription() != ""
    assert dialog.output_dir_edit.accessibleDescription() != ""

    dialog.close()


def test_shortcuts_and_about_dialogs(main_module):
    translator = TranslationSystem("de", app_dir=PROJECT_ROOT)

    # Shortcuts dialog
    sc_dialog = main_module.ShortcutsDialog(translator.t)
    assert sc_dialog.accessibleName() != ""
    assert sc_dialog.table.rowCount() == 14
    assert sc_dialog.table.columnCount() == 2
    assert sc_dialog.table.horizontalHeaderItem(0).text() == translator.t("action")
    assert sc_dialog.table.horizontalHeaderItem(1).text() == translator.t("shortcut")
    sc_dialog.close()

    # About dialog
    about_dialog = main_module.AboutDialog(translator.t)
    assert about_dialog.accessibleName() != ""
    assert main_module.APP_NAME in about_dialog.windowTitle()
    assert "Offline" in about_dialog.accessibleDescription() or "Datenschutz" in about_dialog.accessibleDescription() or "Zero-Egress" in about_dialog.findChildren(main_module.QLabel)[2].text()
    about_dialog.close()


def test_image_preview_dialog_accessibility(main_module):
    translator = TranslationSystem("de", app_dir=PROJECT_ROOT)
    dialog = main_module.ImagePreviewDialog("nonexistent.png", translator.t)

    assert dialog.zoom_in_btn.shortcut().toString() != ""
    assert dialog.zoom_out_btn.shortcut().toString() != ""
    assert dialog.zoom_reset_btn.shortcut().toString() == "Ctrl+0"
    assert dialog.zoom_fit_btn.shortcut().toString() == "F"
    assert dialog.copy_btn.shortcut().toString() in ("Ctrl+C", "Ctrl+c")
    assert dialog.close_btn.shortcut().toString() == "Esc"

    assert dialog.zoom_in_btn.accessibleName() != ""
    assert dialog.zoom_out_btn.accessibleName() != ""
    assert dialog.zoom_reset_btn.accessibleName() != ""
    assert dialog.zoom_fit_btn.accessibleName() != ""
    assert dialog.copy_btn.accessibleName() != ""
    assert dialog.close_btn.accessibleName() != ""

    assert dialog.zoom_in_btn.accessibleDescription() != ""
    assert dialog.zoom_out_btn.accessibleDescription() != ""
    assert dialog.copy_btn.accessibleDescription() != ""
    assert dialog.close_btn.accessibleDescription() != ""

    dialog.close()


def test_translations_all_languages_parity():
    catalog_path = PROJECT_ROOT / "locales" / "translations.json"
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    required_langs = {"de", "en", "es", "zh", "ja", "ru"}

    for key, trans in data.items():
        if key.startswith("_"):
            continue
        assert isinstance(trans, dict), f"Translation for {key} should be dict"
        missing = required_langs - set(trans.keys())
        assert not missing, f"Key '{key}' is missing languages: {missing}"
        for lang in required_langs:
            val = trans[lang]
            assert isinstance(val, str), f"Key '{key}' in lang '{lang}' is not str"
            if key not in ("open", "viewer_empty"):  # open and viewer_empty have intentional empty strings
                assert val != "", f"Key '{key}' in lang '{lang}' is empty"


def test_german_umlauts_invariant():
    catalog_path = PROJECT_ROOT / "locales" / "translations.json"
    data = json.loads(catalog_path.read_text(encoding="utf-8"))

    # Words that must not use ae, oe, ue pseudo-transcriptions in German UI
    forbidden_transcriptions = [
        "Uebersicht", "uebersicht",
        "Menue", "menue",
        "Zurueck", "zurueck",
        "Loeschen", "loeschen",
        "Schliessen",
        "Groesse", "groesse",
        "Auswaehlen", "auswaehlen",
        "Tastaturkuerzel", "tastaturkuerzel",
        "Einfuegen", "einfuegen",
        "Rueckgaengig", "rueckgaengig",
        "Wiederherstellen",
    ]

    for key, trans in data.items():
        de_text = trans.get("de", "")
        for forbidden in forbidden_transcriptions:
            assert forbidden not in de_text, (
                f"German translation for '{key}' contains ASCII transliteration '{forbidden}' instead of real umlauts: '{de_text}'"
            )
