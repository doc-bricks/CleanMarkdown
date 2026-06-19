"""Store-Material-Tests für CleanMarkdown.

Prüft, ob alle für den Windows Store benötigten Artefakte vorhanden und
inhaltlich korrekt sind.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_store_package_json_exists_and_valid():
    path = PROJECT_ROOT / "store_package.json"
    assert path.exists(), "store_package.json fehlt"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["app_name"] == "CleanMarkdown"
    assert "logo" in data and data["logo"] != "PENDING"
    assert "languages" in data and len(data["languages"]) >= 2


def test_store_listing_has_de_and_en():
    path = PROJECT_ROOT / "STORE_LISTING.md"
    assert path.exists(), "STORE_LISTING.md fehlt"
    content = path.read_text(encoding="utf-8")
    assert "Deutsch" in content or "## DE" in content or "German" in content
    assert "English" in content or "## EN" in content


def test_privacy_policy_mentions_local():
    path = PROJECT_ROOT / "PRIVACY_POLICY.md"
    assert path.exists(), "PRIVACY_POLICY.md fehlt"
    content = path.read_text(encoding="utf-8").lower()
    assert "lokal" in content or "local" in content


def test_support_md_exists():
    path = PROJECT_ROOT / "SUPPORT.md"
    assert path.exists(), "SUPPORT.md fehlt"


def test_windows_store_prep_exists():
    path = PROJECT_ROOT / "WINDOWS_STORE_PREP.md"
    assert path.exists(), "WINDOWS_STORE_PREP.md fehlt"


def test_screenshot_store_dir_exists():
    path = PROJECT_ROOT / "README" / "screenshots" / "store"
    assert path.is_dir(), "README/screenshots/store/ fehlt"
