"""Tests for mobile platform contract and session exchange format.

Verifies that flutter_port/ aligns with the desktop contracts:
- cleanmarkdown-session-v1 JSON structure
- Localization delegates and ARB files
- Cleaner utilities and models
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FLUTTER_PORT = PROJECT_ROOT / "flutter_port"


def test_flutter_port_structure_exists():
    assert FLUTTER_PORT.is_dir(), "flutter_port Verzeichnis fehlt"
    assert (FLUTTER_PORT / "pubspec.yaml").is_file(), "flutter_port/pubspec.yaml fehlt"
    assert (FLUTTER_PORT / "lib" / "main.dart").is_file(), "flutter_port/lib/main.dart fehlt"
    assert (FLUTTER_PORT / "lib" / "screens" / "home_screen.dart").is_file()


def test_session_format_model_exists_and_implements_v1():
    session_file = FLUTTER_PORT / "lib" / "models" / "session_format.dart"
    assert session_file.is_file(), "session_format.dart fehlt"
    content = session_file.read_text(encoding="utf-8")
    assert "cleanmarkdown-session-v1" in content
    assert "CleanMarkdownSession" in content
    assert "fromJsonString" in content
    assert "toJsonString" in content
    assert "isSessionJson" in content


def test_markdown_cleaner_utility_exists():
    cleaner_file = FLUTTER_PORT / "lib" / "utils" / "markdown_cleaner.dart"
    assert cleaner_file.is_file(), "markdown_cleaner.dart fehlt"
    content = cleaner_file.read_text(encoding="utf-8")
    assert "stripMarkdown" in content
    assert "calculateStats" in content
    assert "DocumentStats" in content


def test_flutter_localizations_contract():
    l10n_dir = FLUTTER_PORT / "lib" / "l10n"
    assert (l10n_dir / "app_localizations.dart").is_file()
    assert (l10n_dir / "app_de.arb").is_file()
    assert (l10n_dir / "app_en.arb").is_file()
    assert (l10n_dir / "app_es.arb").is_file()

    # Verify JSON validity of ARB files
    for arb_name in ("app_de.arb", "app_en.arb", "app_es.arb"):
        data = json.loads((l10n_dir / arb_name).read_text(encoding="utf-8"))
        assert "appTitle" in data
        assert data["appTitle"] == "CleanMarkdown"

    loc_content = (l10n_dir / "app_localizations.dart").read_text(encoding="utf-8")
    assert "AppLocalizationsDe" in loc_content
    assert "AppLocalizationsEn" in loc_content
    assert "AppLocalizationsEs" in loc_content
    assert "exportSession" in loc_content
    assert "clearFormatting" in loc_content
