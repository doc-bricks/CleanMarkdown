"""The standalone source smoke must leave an inherited user profile untouched."""
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize("existing_settings", [False, True])
def test_source_smoke_preserves_inherited_profile(main_module, tmp_path, existing_settings):
    profile = tmp_path / "user-profile"
    profile.mkdir()
    if existing_settings:
        settings = profile / main_module.APP_NAME / "settings.json"
        settings.parent.mkdir()
        settings.write_bytes(b'{"language":"en","unknown_user_field":"keep me"}\n')
    before = {p.relative_to(profile): p.read_bytes() for p in profile.rglob("*") if p.is_file()}
    env = dict(os.environ, APPDATA=str(profile), QT_QPA_PLATFORM="offscreen", PYTHONIOENCODING="utf-8")
    # APPDATA also relocates Python's user site on Windows. Keep the already
    # available dependencies reachable while replacing the application profile.
    env["PYTHONPATH"] = os.pathsep.join(sys.path)
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "tests" / "source_platform_smoke.py")],
        cwd=root, env=env, capture_output=True, text=True, encoding="utf-8", timeout=45,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "6/6 Checks bestanden" in result.stdout
    after = {p.relative_to(profile): p.read_bytes() for p in profile.rglob("*") if p.is_file()}
    assert after == before
