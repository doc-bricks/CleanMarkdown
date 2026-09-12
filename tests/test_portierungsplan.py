"""Tests for PORTIERUNGSPLAN.md."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_portierungsplan_exists_and_content():
    path = PROJECT_ROOT / "PORTIERUNGSPLAN.md"
    assert path.is_file(), "PORTIERUNGSPLAN.md fehlt"

    content = path.read_text(encoding="utf-8")

    # Target platforms
    assert "Windows Desktop" in content
    assert "Windows Store" in content
    assert "Mobile Companion" in content
    assert "Web Companion" in content

    # Architecture & contracts
    assert "cleanmarkdown-session-v1.json" in content
    assert "Zero-Egress" in content or "Datenschutz" in content
    assert "flutter_port" in content

    # Store specifications
    assert "Geiger.CleanMarkdown" in content
    assert "CN=52596601-BAB4-4F3F-B182-E8F3F273B202" in content
    assert "10.1.3" in content
