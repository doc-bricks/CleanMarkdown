from __future__ import annotations

from pathlib import Path

from translator import SUPPORTED_LANGUAGES, TranslationSystem


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_language_names_cover_all_supported_languages(main_module):
    assert set(SUPPORTED_LANGUAGES) == set(main_module.LANGUAGE_NAMES)


def test_settings_dialog_lists_all_supported_languages(main_module):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    translator = TranslationSystem("de", app_dir=PROJECT_ROOT)
    dialog = main_module.SettingsDialog(main_module.AppSettings(), translator.t)

    entries = {
        dialog.language_combo.itemData(index): dialog.language_combo.itemText(index)
        for index in range(dialog.language_combo.count())
    }

    assert entries == {
        "de": "Deutsch",
        "en": "English",
        "es": "Español",
        "zh": "中文",
        "ja": "日本語",
        "ru": "Русский",
    }

    dialog.close()
    app.processEvents()


def test_translation_system_reads_extended_catalog_languages():
    translator = TranslationSystem("de", app_dir=PROJECT_ROOT)

    expected = {
        "es": "Configuración",
        "zh": "设置",
        "ja": "設定",
        "ru": "Ошибка",
    }

    for language, value in expected.items():
        translator.set_language(language)
        key = "settings" if language != "ru" else "error"
        assert translator.t(key) == value


def test_translation_system_returns_explicit_empty_string_instead_of_key():
    translator = TranslationSystem.__new__(TranslationSystem)
    translator.current_lang = "zh"
    translator.translations = {
        "viewer_empty": {
            "de": "",
            "en": "",
            "es": "",
            "zh": "",
            "ja": "",
            "ru": "",
        }
    }

    assert translator.t("viewer_empty") == ""
