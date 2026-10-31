"""Hermetic contract and regression tests for manage_translations.py CLI and TranslationSystem."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import manage_translations
from translator import TranslationSystem

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_manage_translations_help():
    result = subprocess.run(
        [sys.executable, "manage_translations.py", "--help"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "--check" in result.stdout
    assert "--dir" in result.stdout


def test_manage_translations_check_flag_exits_cleanly():
    result = subprocess.run(
        [sys.executable, "manage_translations.py", "--check"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "100%" in result.stdout
    assert "143" in result.stdout


def test_manage_translations_check_flag_does_not_create_phantom_directory(tmp_path):
    phantom_dir = tmp_path / "--check"
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "manage_translations.py"), "--check", "--dir", str(tmp_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert not phantom_dir.exists()


def test_check_translations_detects_missing_keys(tmp_path):
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    catalog = {
        "_meta": {"version": "1.0"},
        "viewer_empty": {"de": "", "en": "", "es": "", "zh": "", "ja": "", "ru": ""},
        "sample_key": {
            "de": "Datei",
            "en": "File",
            "es": "Archivo",
            "zh": "",  # missing in zh
            "ja": "ファイル",
            "ru": "Файл",
        },
    }
    (locales_dir / "translations.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")

    exit_code = manage_translations.check_translations(str(tmp_path))
    assert exit_code == 1


def test_check_translations_passes_with_viewer_empty_and_full_parity(tmp_path):
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    catalog = {
        "_meta": {"version": "1.0"},
        "viewer_empty": {"de": "", "en": "", "es": "", "zh": "", "ja": "", "ru": ""},
        "sample_key": {
            "de": "Datei",
            "en": "File",
            "es": "Archivo",
            "zh": "文件",
            "ja": "ファイル",
            "ru": "Файл",
        },
    }
    (locales_dir / "translations.json").write_text(json.dumps(catalog, ensure_ascii=False), encoding="utf-8")

    exit_code = manage_translations.check_translations(str(tmp_path))
    assert exit_code == 0


def test_find_german_strings_excludes_tests_and_helpers(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "source_platform_smoke.py").write_text(
        'sample = "# Überschrift\\n\\nÄpfel, Öl, Übergabe."', encoding="utf-8"
    )
    (tests_dir / "test_sample.py").write_text('text = "Fehler im Test"', encoding="utf-8")

    src_file = tmp_path / "gui_widget.py"
    src_file.write_text('btn = QPushButton("Datei öffnen")', encoding="utf-8")

    found = manage_translations.find_german_strings(str(tmp_path))
    assert "Datei öffnen" in found
    assert not any("Äpfel" in s for s in found)
    assert not any("Fehler im Test" in s for s in found)


def test_atomic_write_json_creates_clean_file(tmp_path):
    target = tmp_path / "locales" / "translations.json"
    data = {"hello": {"de": "Hallo", "en": "Hello"}}
    manage_translations._atomic_write_json(str(target), data)

    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == data
    # Verify no left-over .tmp files
    tmp_files = list(tmp_path.glob("**/*.tmp*"))
    assert tmp_files == []


def test_ensure_utf8_streams_safe_execution():
    # Calling this must not crash or raise regardless of stream state
    manage_translations._ensure_utf8_streams()


def test_translator_find_german_strings_excludes_tests_and_helpers(tmp_path):
    ts = TranslationSystem("de", app_dir=tmp_path)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "source_platform_smoke.py").write_text(
        'sample = "# Überschrift\\n\\nÄpfel, Öl, Übergabe."', encoding="utf-8"
    )
    (tmp_path / "component.py").write_text('lbl = QLabel("Einstellungen")', encoding="utf-8")

    found = ts._find_german_strings(tmp_path)
    assert "Einstellungen" in found
    assert not any("Äpfel" in s for s in found)
