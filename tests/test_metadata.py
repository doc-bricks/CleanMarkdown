"""Automated metadata and CI contract tests for CleanMarkdown.

Ensures synchronization of CI workflows, PEP 621 metadata, security policy,
documentation badges, bilingual README parity, Mermaid diagrams, sibling ecosystem,
and llms.txt discovery files.
"""

from __future__ import annotations

import json
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
    assert "https://github.com/open-bricks" in content, "Missing open-bricks umbrella URL"
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
        assert "SECURITY.md" in c, "SECURITY.md reference missing"


def test_llms_txt_integrity():
    llms_path = PROJECT_ROOT / "llms.txt"
    assert llms_path.is_file(), "llms.txt missing"
    content = llms_path.read_text(encoding="utf-8")

    assert "https://github.com/doc-bricks/CleanMarkdown" in content, "Canonical link missing"
    assert "2026-08-23" in content, "llms.txt timestamp not synced to 2026-08-23"
    assert "python -m pytest" in content, "Developer commands missing in llms.txt"


def test_readme_de_exists_and_bilingual_parity():
    readme_en = PROJECT_ROOT / "README.md"
    readme_de = PROJECT_ROOT / "README_DE.md"
    assert readme_en.is_file(), "README.md missing"
    assert readme_de.is_file(), "README_DE.md missing"

    content_en = readme_en.read_text(encoding="utf-8")
    content_de = readme_de.read_text(encoding="utf-8")

    assert "assets/banner.png" in content_en and "assets/banner.png" in content_de
    assert "README/screenshots/main_view.png" in content_en and "README/screenshots/main_view.png" in content_de
    assert "reading-bright.png" in content_en and "reading-bright.png" in content_de
    assert "reading-dark.png" in content_en and "reading-dark.png" in content_de
    assert "editor-dark.png" in content_en and "editor-dark.png" in content_de


def test_mermaid_diagrams_syntax():
    readme_en = PROJECT_ROOT / "README.md"
    readme_de = PROJECT_ROOT / "README_DE.md"
    content_en = readme_en.read_text(encoding="utf-8")
    content_de = readme_de.read_text(encoding="utf-8")

    for c in (content_en, content_de):
        assert "```mermaid" in c, "Mermaid block missing"
        assert "flowchart TD" in c, "Architecture flowchart TD missing"
        assert "sequenceDiagram" in c, "Lifecycle sequenceDiagram missing"
        assert "cleanmarkdown-session-v1.json" in c, "Session JSON missing in diagram"


def test_sibling_ecosystem_and_urls():
    readme_en = PROJECT_ROOT / "README.md"
    readme_de = PROJECT_ROOT / "README_DE.md"
    content_en = readme_en.read_text(encoding="utf-8")
    content_de = readme_de.read_text(encoding="utf-8")

    for c in (content_en, content_de):
        assert "doc-bricks/FormularErstellen" in c, "FormularErstellen sibling missing"
        assert "doc-bricks/DokuZen" in c, "DokuZen sibling missing"
        assert "file-bricks/WinStorePackager" in c, "WinStorePackager sibling missing"
        assert "file-bricks/ExplorerPro" in c, "ExplorerPro sibling missing"
        assert "file-bricks/ProSync" in c, "ProSync sibling missing"
        assert "open-bricks/open-bricks" in c, "open-bricks umbrella link missing"


def test_version_parity():
    main_py = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    store_pkg = json.loads((PROJECT_ROOT / "store_package.json").read_text(encoding="utf-8"))

    assert 'APP_VERSION = "1.0.0"' in main_py, "main.py version mismatch"
    assert 'version = "1.0.0"' in pyproject, "pyproject.toml version mismatch"
    assert store_pkg["version"] == "1.0.0.0", "store_package.json version mismatch"


def test_privacy_and_security_offline_invariants():
    readme_en = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (PROJECT_ROOT / "README_DE.md").read_text(encoding="utf-8")
    sec = (PROJECT_ROOT / "SECURITY.md").read_text(encoding="utf-8")

    assert "Zero-Egress" in readme_en and "Zero-Egress" in readme_de
    assert "Non-Elevation" in readme_en and "Non-Elevation" in readme_de
    assert "Non-Elevation" in sec or "User-Mode" in sec
