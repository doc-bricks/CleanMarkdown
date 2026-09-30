"""Automatic export copies must never overwrite another document."""
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def autosave(main_module, tmp_path, monkeypatch):
    class FixedTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 9, 30, 12, 0, 0)

    monkeypatch.setattr(main_module, "datetime", FixedTime)
    monkeypatch.setattr(main_module, "_documents_dir", lambda: tmp_path)
    document = SimpleNamespace(session_display_name="Prüfung.md", editor=SimpleNamespace(toPlainText=lambda: "Bücher"))
    return document, lambda: main_module.MainWindow._auto_save_for_export(document)


def test_same_second_autosaves_keep_both_documents(autosave):
    document, save = autosave
    first = save()
    assert first is not None
    original = first.read_bytes()
    document.editor.toPlainText = lambda: "Neue Übergabe"
    second = save()
    assert second is not None and second != first
    assert first.read_bytes() == original
    assert second.read_text(encoding="utf-8") == "Neue Übergabe"


def test_existing_directory_name_is_skipped(autosave, tmp_path):
    _, save = autosave
    directory = tmp_path / "Prüfung_autosave_20260930_120000.md"
    directory.mkdir()
    marker = directory / "keep.txt"
    marker.write_bytes(b"keep")
    result = save()
    assert result is not None and result != directory
    assert marker.read_bytes() == b"keep"
    assert result.read_text(encoding="utf-8") == "Bücher"


def test_concurrent_creator_is_not_overwritten(autosave, tmp_path, monkeypatch):
    _, save = autosave
    target = tmp_path / "Prüfung_autosave_20260930_120000.md"
    original_open = Path.open

    def racing_open(path, mode="r", *args, **kwargs):
        if path == target and mode == "xb" and not path.exists():
            with original_open(path, "wb") as stream:
                stream.write(b"other process")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", racing_open)
    result = save()
    assert target.read_bytes() == b"other process"
    assert result is not None and result != target
    assert result.read_text(encoding="utf-8") == "Bücher"


@pytest.mark.parametrize("short_write", [False, True])
def test_failed_autosave_removes_only_its_partial_file(autosave, tmp_path, monkeypatch, short_write):
    _, save = autosave
    existing = tmp_path / "keep.md"
    existing.write_bytes(b"original")
    original_open = Path.open
    original_write = Path.write_text

    class PartialWrite:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.stream.close()

        def write(self, data):
            self.stream.write(data[:3])
            if short_write:
                return 3
            raise OSError("disk full")

    def failing_open(path, mode="r", *args, **kwargs):
        stream = original_open(path, mode, *args, **kwargs)
        return PartialWrite(stream) if mode == "xb" else stream

    def failing_legacy_write(path, text, *args, **kwargs):
        if "autosave" in path.name:
            path.write_bytes(b"partial")
            raise OSError("disk full")
        return original_write(path, text, *args, **kwargs)

    monkeypatch.setattr(Path, "open", failing_open)
    monkeypatch.setattr(Path, "write_text", failing_legacy_write)
    assert save() is None
    assert list(tmp_path.iterdir()) == [existing]
    assert existing.read_bytes() == b"original"
