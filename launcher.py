"""Bound GUI startup and teardown, without timing out an editable session.

The supervisor imports only the standard library. It can therefore stop its
own child even if importing Qt or native text layout holds Python's GIL.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

GUARD_ENV = "_CLEANMARKDOWN_GUARD_DIR"
WORKER_FLAG = "--cleanmarkdown-guard-worker"
STARTUP_SECONDS = 60.0
SHUTDOWN_SECONDS = 15.0


@dataclass
class GuardState:
    # This decision must survive IPC deletion/failure and supervisor errors.
    editable: bool = False


def _publish(directory: Path, state: str, content: str = "") -> None:
    temporary = directory / (state + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(directory / state)


def notify_ready() -> None:
    """Called with the window disabled, after show(), before the event loop.

    The supervisor must acknowledge (and permanently disarm its startup
    timeout) before the window becomes editable. Failed IPC never enables it.
    """
    raw = os.environ.get(GUARD_ENV)
    if not raw:
        return
    directory = Path(raw)
    _publish(directory, "ready")
    deadline = time.monotonic() + 5.0
    while not (directory / "ack").exists():
        if time.monotonic() >= deadline:
            raise RuntimeError("Startup supervisor did not acknowledge readiness")
        time.sleep(0.02)


def notify_ui_closed(code: int) -> None:
    """Only called after an accepted close AND the GUI event loop returned."""
    raw = os.environ.get(GUARD_ENV)
    if raw:
        try:
            _publish(Path(raw), "finished", str(code))
        except OSError:
            _record("shutdown_notification_failed", code)


def supervise(child, directory: Path, *, startup_seconds=STARTUP_SECONDS,
              shutdown_seconds=SHUTDOWN_SECONDS, clock=time.monotonic,
              sleep=time.sleep, state: GuardState | None = None) -> tuple[int, str]:
    """Only kill before ACK or after an explicitly accepted GUI close."""
    startup_deadline = clock() + startup_seconds
    state = state if state is not None else GuardState()
    acknowledged = False
    shutdown_deadline = None
    finished_code = 0
    while True:
        code = child.poll()
        if code is not None:
            return code, "exited" if acknowledged or code == 0 else "startup_failed"
        if not acknowledged:
            if (directory / "ready").exists():
                # Once this file is published, no elapsed-time limit may
                # terminate this session while main() is still running.
                state.editable = True  # fail closed even if publishing fails
                _publish(directory, "ack")
                acknowledged = True
            elif clock() >= startup_deadline:
                child.kill()
                child.wait(timeout=5)
                return 124, "startup_timeout"
        if (directory / "finished").exists():
            if shutdown_deadline is None:
                finished_code = int((directory / "finished").read_text(encoding="utf-8"))
                shutdown_deadline = clock() + shutdown_seconds
            elif clock() >= shutdown_deadline:
                # The event loop returned after an accepted close/save decision. Native Qt
                # destructors can no longer leave a windowless child spinning.
                child.kill()
                child.wait(timeout=5)
                return finished_code, "shutdown_timeout"
        sleep(0.25 if acknowledged else 0.05)


def _record(reason: str, code: int) -> None:
    try:
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "state"))
        path = base / "CleanMarkdown" / "logs" / "launcher.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(path, maxBytes=262144, backupCount=1, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        logger = logging.getLogger("cleanmarkdown.launcher")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        try:
            logger.info("%s exit=%s", reason, code)
        finally:
            logger.removeHandler(handler)
            handler.close()
    except OSError:
        pass


def _startup_error_message() -> str:
    message = "CleanMarkdown could not finish starting. Please try again."
    try:
        base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        translations = json.loads((base / "locales" / "translations.json").read_text(encoding="utf-8"))
        settings_path = Path(os.environ.get("APPDATA", Path.home() / ".config")) / "CleanMarkdown" / "settings.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8")) if settings_path.is_file() else {}
        if not isinstance(settings, dict):
            settings = {}
        message = translations["startup_failed_guard"].get(settings.get("language", "de"), message)
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return message


def _show_startup_error() -> None:
    message = _startup_error_message()
    if os.name == "nt":
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, message, "CleanMarkdown", 0x10)
    elif sys.stderr is not None:
        print(message, file=sys.stderr)


def _run_worker() -> int:
    # Import only inside the supervised child, never in the guardian process.
    import main
    return main.main()


def run() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == WORKER_FLAG and os.environ.get(GUARD_ENV):
        del sys.argv[1]
        return _run_worker()
    command = [sys.executable]
    if not getattr(sys, "frozen", False):
        command.append(str(Path(__file__).resolve()))
    command += [WORKER_FLAG, *sys.argv[1:]]
    with TemporaryDirectory(prefix="cleanmarkdown-startup-") as temporary:
        directory = Path(temporary)
        env = dict(os.environ, **{GUARD_ENV: temporary})
        child = subprocess.Popen(
            command, env=env, stdin=subprocess.DEVNULL,
            stdout=None if sys.stdout is not None else subprocess.DEVNULL,
            stderr=None if sys.stderr is not None else subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        state = GuardState()
        try:
            code, reason = supervise(child, directory, state=state)
        except BaseException:
            if state.editable:
                # Keep the guardian (and onefile extraction tree) alive until
                # its child exits. IPC state cannot revoke editing permission.
                _record("supervisor_error_after_readiness", 1)
                while True:
                    try:
                        return child.wait()
                    except BaseException:
                        # A failed wait also cannot revoke editing permission
                        # or release a onefile child's shared extraction tree.
                        time.sleep(0.25)
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)
            raise
        _record(reason, code)
        if reason in {"startup_timeout", "startup_failed"}:
            _show_startup_error()
        return code


if __name__ == "__main__":
    raise SystemExit(run())
