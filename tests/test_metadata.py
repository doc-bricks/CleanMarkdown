"""Automated metadata and CI contract tests for CleanMarkdown.

Ensures synchronization of CI workflows, PEP 621 metadata, security policy,
documentation badges, and llms.txt discovery files.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_ci_workflow_integrity():
    workflow_path = PROJECT_ROOT / ".github" / "workflows" / "tests.yml"
    assert workflow_path.is_file(), "CI workflow .github/workflows/tests.yml missing"
    content = workflow_path.read_text(encoding="utf-8")

    assert "actions/checkout@v4" in content, "Workflow should use actions/checkout@v4"
    assert "actions/setup-python@v5" in content, "Workflow should use actions/setup-python@v5"
    assert "ubuntu-latest" in content and "windows-latest" in content, "CI should run on ubuntu and windows"
    assert '"3.12"' in content and '"3.13"' in content, "CI should cover Python 3.12 and 3.13"
    assert "ruff check ." in content, "CI should execute ruff linter gate"
    assert "pytest" in content, "CI should run pytest suite"


def test_pyproject_pep621_metadata():
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    assert pyproject_path.is_file(), "pyproject.toml missing"
    content = pyproject_path.read_text(encoding="utf-8")

    assert 'name = "cleanmarkdown"' in content, "Package name mismatch"
    assert 'version = "1.0.0"' in content, "Version mismatch"
    assert "Operating System :: OS Independent" in content, "Missing OS Independent classifier"
    assert "Programming Language :: Python :: 3.13" in content, "Missing Python 3.13 classifier"
    assert "Programming Language :: Python :: 3.12" in content, "Missing Python 3.12 classifier"
    assert "https://github.com/doc-bricks/CleanMarkdown" in content, "Missing repository URL"
    assert "[tool.ruff]" in content, "Missing ruff configuration"


def test_security_policy_bilingual_and_contacts():
    sec_path = PROJECT_ROOT / "SECURITY.md"
    assert sec_path.is_file(), "SECURITY.md missing"
    content = sec_path.read_text(encoding="utf-8")

    assert "## Deutsch" in content, "German section missing in SECURITY.md"
    assert "## English" in content, "English section missing in SECURITY.md"
    assert "Zero-Egress" in content or "zero-egress" in content.lower(), "Zero-Egress guarantee missing"
    assert "security@ellmos.ai" in content, "Security email missing"
    assert "support@lukasgeiger.com" in content, "Support email missing"
    assert "security/advisories" in content, "Security Advisories link missing"


def test_readme_badges_and_structure():
    readme_en = PROJECT_ROOT / "README.md"
    readme_de = PROJECT_ROOT / "README_DE.md"
    assert readme_en.is_file(), "README.md missing"
    assert readme_de.is_file(), "README_DE.md missing"

    content_en = readme_en.read_text(encoding="utf-8")
    content_de = readme_de.read_text(encoding="utf-8")

    for c in (content_en, content_de):
        assert "Ökosystem" in c or "doc-bricks" in c, "Ecosystem badge missing"
        assert "open-bricks" in c, "open-bricks umbrella badge missing"
        assert "tests.yml" in c or "Tests" in c, "CI / Test badge missing"
        assert "llms.txt" in c, "llms.txt reference missing"


def test_llms_txt_integrity():
    llms_path = PROJECT_ROOT / "llms.txt"
    assert llms_path.is_file(), "llms.txt missing"
    content = llms_path.read_text(encoding="utf-8")

    assert "https://github.com/doc-bricks/CleanMarkdown" in content, "Canonical link missing"
    assert "2026-08-21" in content, "llms.txt timestamp not synced to 2026-08-21"
    assert "python -m pytest" in content, "Developer commands missing in llms.txt"
