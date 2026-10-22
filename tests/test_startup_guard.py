"""Bound only startup/confirmed shutdown; never a user's editable session."""
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

import launcher


class FakeChild:
    def __init__(self, poll):
        self._poll = poll
        self.killed = False

    def poll(self):
        return -9 if self.killed else self._poll()

    def kill(self):
        self.killed = True

    def wait(self, timeout=None):
        return -9 if self.killed else 0


def test_importing_supervisor_does_not_import_gui():
    result = subprocess.run(
        [sys.executable, "-c", "import launcher,sys; assert not any(x.startswith(('PySide6','shiboken6')) for x in sys.modules)"],
        cwd=Path(launcher.__file__).parent, capture_output=True, timeout=10,
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("payload", ["[]", "null", "42", '"bad settings"'])
def test_failure_message_survives_wrongly_typed_settings(tmp_path, monkeypatch, payload):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    path = tmp_path / "CleanMarkdown" / "settings.json"
    path.parent.mkdir()
    path.write_text(payload, encoding="utf-8")
    assert "CleanMarkdown" in launcher._startup_error_message()


def test_all_packaged_entries_install_guard_before_qt_runtime_hooks():
    root = Path(launcher.__file__).parent
    assert "runtime_hooks=['scripts/startup_guard_hook.py']" in (root / "CleanMarkdown.spec").read_text()
    bat = (root / "build_exe.bat").read_text()
    assert bat.count('--runtime-hook "%PROJECT_ROOT%\\scripts\\startup_guard_hook.py"') == 2
    assert bat.count('"%PROJECT_ROOT%\\launcher.py"') == 2


def test_startup_hang_is_terminated(tmp_path):
    now = [0.0]
    child = FakeChild(lambda: None)
    result = launcher.supervise(
        child, tmp_path, startup_seconds=1,
        clock=lambda: now[0], sleep=lambda step: now.__setitem__(0, now[0] + step),
    )
    assert result == (124, "startup_timeout")
    assert child.killed
    assert not (tmp_path / "ack").exists()


def test_acknowledged_editable_session_has_no_timeout(tmp_path):
    launcher._publish(tmp_path, "ready")
    now = [0.0]
    child = FakeChild(lambda: 0 if now[0] > 48 * 3600 else None)
    result = launcher.supervise(
        child, tmp_path, startup_seconds=0.1, shutdown_seconds=0.1,
        clock=lambda: now[0], sleep=lambda step: now.__setitem__(0, now[0] + 3600),
    )
    assert (tmp_path / "ack").is_file()
    assert result == (0, "exited")
    assert not child.killed


@pytest.mark.parametrize("code", [0, 7])
def test_only_confirmed_main_return_allows_teardown_timeout(tmp_path, code):
    launcher._publish(tmp_path, "ready")
    launcher._publish(tmp_path, "finished", str(code))
    now = [0.0]
    child = FakeChild(lambda: None)
    result = launcher.supervise(
        child, tmp_path, shutdown_seconds=0.2,
        clock=lambda: now[0], sleep=lambda step: now.__setitem__(0, now[0] + step),
    )
    assert result == (code, "shutdown_timeout")
    assert child.killed


def test_ack_published_even_if_readiness_arrives_at_deadline(tmp_path):
    launcher._publish(tmp_path, "ready")
    polls = [0]

    def poll():
        polls[0] += 1
        return 0 if polls[0] > 1 else None

    child = FakeChild(poll)
    assert launcher.supervise(child, tmp_path, startup_seconds=0) == (0, "exited")
    assert not child.killed


def test_failed_readiness_publication_does_not_enter_editable_ui(tmp_path, monkeypatch):
    monkeypatch.setenv(launcher.GUARD_ENV, str(tmp_path / "missing"))
    with pytest.raises(OSError):
        launcher.notify_ready()
    assert not (tmp_path / "ack").exists()


def test_supervisor_failure_after_deleted_ack_does_not_kill_session(monkeypatch):
    child = FakeChild(lambda: None)
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda *args, **kwargs: child)

    def fail_after_ack(child, directory, state):
        state.editable = True
        launcher._publish(directory, "ack")
        (directory / "ack").unlink()
        raise OSError("simulated supervisor failure")

    monkeypatch.setattr(launcher, "supervise", fail_after_ack)
    monkeypatch.setattr(sys, "argv", ["launcher.py"])
    assert launcher.run() == 0
    assert not child.killed


@pytest.mark.parametrize("error", [RuntimeError("callback failed"), SystemExit(1), KeyboardInterrupt()])
def test_worker_exception_never_confirms_saved_or_closed_ui(tmp_path, monkeypatch, error):
    from types import SimpleNamespace

    def fail():
        raise error

    monkeypatch.setitem(sys.modules, "main", SimpleNamespace(main=fail))
    monkeypatch.setenv(launcher.GUARD_ENV, str(tmp_path))
    with pytest.raises(type(error)):
        launcher._run_worker()
    assert not (tmp_path / "finished").exists()


def test_window_stays_disabled_until_readiness_is_acknowledged(main_module, monkeypatch):
    events = []

    class App:
        def exec(self):
            events.append("exec")
            return 0

    class Window:
        def __init__(self, path):
            events.append("construct")
            self._close_confirmed = False

        def setEnabled(self, value):
            events.append(("enabled", value))

        def show(self):
            events.append("show")

    monkeypatch.setattr(sys, "argv", ["launcher.py"])
    monkeypatch.setattr(main_module, "QApplication", lambda args: App())
    monkeypatch.setattr(main_module, "configure_application", lambda app: None)
    monkeypatch.setattr(main_module, "MainWindow", Window)
    monkeypatch.setattr(main_module, "notify_ready", lambda: events.append("ack"))
    assert main_module.main() == 0
    assert events == ["construct", ("enabled", False), "show", "ack", ("enabled", True), "exec"]


@pytest.mark.parametrize("accepted", [False, True])
def test_only_accepted_close_disables_window_and_notifies_guard(main_module, monkeypatch, accepted):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    events = []
    monkeypatch.setattr(window, "_confirm_discard", lambda: accepted)
    monkeypatch.setattr(main_module, "notify_ui_closed", lambda code: events.append((code, window.isEnabled())))
    try:
        result = window.close()
        assert result is accepted
        assert window._close_confirmed is accepted
        assert window.isEnabled() is not accepted
        assert events == ([(0, False)] if accepted else [])
    finally:
        monkeypatch.setattr(window, "_confirm_discard", lambda: True)
        window.close()
        app.processEvents()


def test_failed_document_save_keeps_editor_enabled_without_shutdown_marker(main_module, monkeypatch):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    window.editor.setPlainText("unsaved document")
    events = []
    monkeypatch.setattr(main_module, "notify_ui_closed", lambda code: events.append(code))
    monkeypatch.setattr(main_module.QMessageBox, "exec", lambda self: None)
    monkeypatch.setattr(main_module.QMessageBox, "clickedButton", lambda self: next(
        button for button in self.buttons()
        if self.buttonRole(button) == main_module.QMessageBox.ButtonRole.AcceptRole
    ))
    monkeypatch.setattr(window, "save_file", lambda: False)
    try:
        assert window.close() is False
        assert window.isEnabled()
        assert window.is_modified
        assert not window._close_confirmed
        assert events == []
    finally:
        monkeypatch.setattr(window, "_confirm_discard", lambda: True)
        window.close()
        app.processEvents()


def test_failed_settings_save_keeps_editor_enabled_without_shutdown_marker(main_module, monkeypatch):
    app = main_module.QApplication.instance() or main_module.QApplication([])
    window = main_module.MainWindow()
    save = window.store.save
    events = []
    monkeypatch.setattr(main_module, "notify_ui_closed", lambda code: events.append(code))
    monkeypatch.setattr(main_module.QMessageBox, "critical", lambda *args: None)

    def fail(settings):
        raise OSError("settings cannot be saved")

    monkeypatch.setattr(window.store, "save", fail)
    try:
        assert window.close() is False
        assert window.isEnabled()
        assert not window._close_confirmed
        assert events == []
    finally:
        monkeypatch.setattr(window.store, "save", save)
        window.close()
        app.processEvents()


@pytest.mark.parametrize("phase", ["startup", "shutdown"])
def test_real_child_hang_leaves_no_live_process(tmp_path, phase):
    script = tmp_path / "child.py"
    prefix = ""
    if phase == "shutdown":
        prefix = "(directory/'ready').touch(); (directory/'finished').write_text('0')\n"
    script.write_text(
        "from pathlib import Path\nimport sys,time\ndirectory=Path(sys.argv[1])\n"
        + prefix + "while True: time.sleep(0.01)\n", encoding="utf-8",
    )
    child = subprocess.Popen(
        [sys.executable, str(script), str(tmp_path)],
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    try:
        start = time.monotonic()
        code, reason = launcher.supervise(child, tmp_path, startup_seconds=2, shutdown_seconds=0.1)
        assert reason == phase + "_timeout"
        assert code == (124 if phase == "startup" else 0)
        assert child.poll() is not None
        assert time.monotonic() - start < 5
    finally:
        if child.poll() is None:
            child.kill()
        child.wait(timeout=5)
