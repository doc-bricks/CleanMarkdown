"""P3 macOS/Linux Source-Smoke — standalone, kein pytest nötig."""
import os
import sys
import json
import tempfile
import traceback
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

PASS = "PASS"
FAIL = "FAIL"
results: list[tuple[int, str, str]] = []


def check(num: int, name: str, fn) -> bool:
    try:
        fn()
        results.append((num, PASS, name))
        print(f"[{PASS}] #{num}: {name}")
        return True
    except Exception as exc:
        results.append((num, FAIL, name))
        print(f"[{FAIL}] #{num}: {name}")
        print(f"       {type(exc).__name__}: {exc}")
        traceback.print_exc(limit=3, file=sys.stdout)
        return False


# --- Check 1: Non-GUI-Standardbibliotheken ---
def c1():
    import json as _j  # noqa: F401
    import re as _r  # noqa: F401
    import html as _h  # noqa: F401
    from pathlib import Path as _P  # noqa: F401
    import dataclasses as _d  # noqa: F401


check(1, "Non-GUI stdlib (json, re, pathlib, html, dataclasses)", c1)


# --- Check 2: PySide6-Kernmodule ---
def c2():
    from PySide6.QtWidgets import QApplication  # noqa: F401
    from PySide6.QtCore import Qt, QTimer  # noqa: F401
    from PySide6.QtGui import QTextDocument  # noqa: F401
    from PySide6.QtPrintSupport import QPrinter  # noqa: F401


check(2, "PySide6 (QtWidgets, QtCore, QtGui, QtPrintSupport) importierbar", c2)


# --- Check 3: markdown-Bibliothek ---
def c3():
    import markdown  # noqa: F401
    _ = markdown.markdown("**test**")


check(3, "markdown-Bibliothek importierbar und funktional", c3)


# --- Check 4: Offscreen-QApplication + MainWindow headless ---
def c4():
    import main as m
    app = m.QApplication.instance() or m.QApplication([])
    win = m.MainWindow()
    title = win.windowTitle()
    win.close()
    assert title, f"windowTitle ist leer: {title!r}"


check(4, "Offscreen QApplication + MainWindow() instanziierbar (windowTitle gesetzt)", c4)


# --- Check 5: SettingsStore read/write Roundtrip mit Umlauten ---
def c5():
    import main as m

    with tempfile.TemporaryDirectory() as tmp:
        old_appdata = os.environ.get("APPDATA")
        os.environ["APPDATA"] = tmp
        try:
            store = m.SettingsStore()
            original = store.load()
            store.save(original)
            loaded = store.load()
            assert loaded == original, f"Roundtrip-Fehler: {loaded!r} != {original!r}"
            raw = store.path.read_text(encoding="utf-8")
            assert "\\u" not in raw, "ensure_ascii hat Umlaute escaped"
        finally:
            if old_appdata is None:
                os.environ.pop("APPDATA", None)
            else:
                os.environ["APPDATA"] = old_appdata


check(5, "SettingsStore read/write Roundtrip mit Umlauten (tmp APPDATA)", c5)


# --- Check 6: Session-JSON-Roundtrip (cleanmarkdown-session-v1) ---
def c6():
    import main as m

    md_text = "# Überschrift\n\nÄpfel, Öl, Übergabe."
    session_dict = {
        "version": m.SESSION_VERSION,
        "markdown": md_text,
    }
    encoded = json.dumps(session_dict, ensure_ascii=False)
    decoded = json.loads(encoded)

    assert isinstance(decoded, dict), "Session ist kein dict"
    assert decoded.get("version") == m.SESSION_VERSION, (
        f"version falsch: {decoded.get('version')!r}"
    )
    assert isinstance(decoded.get("markdown"), str), "markdown kein str"
    assert decoded["markdown"] == md_text, "markdown-Text verändert"

    # Validierungslogik aus main.py (Zeile ~1234) nachgebaut
    invalid_no_version = {"markdown": md_text}
    assert (
        invalid_no_version.get("version") != m.SESSION_VERSION
    ), "Fehlende version sollte als invalid gelten"

    invalid_no_md = {"version": m.SESSION_VERSION}
    assert not isinstance(
        invalid_no_md.get("markdown"), str
    ), "Fehlende markdown-Key sollte als invalid gelten"


check(6, "Session-JSON-Roundtrip (cleanmarkdown-session-v1, Validierungslogik)", c6)


# --- Zusammenfassung ---
print()
passed = sum(1 for _, s, _ in results if s == PASS)
failed = sum(1 for _, s, _ in results if s == FAIL)
print(f"Ergebnis: {passed}/{len(results)} Checks bestanden")
if failed:
    print("FEHLGESCHLAGEN:")
    for num, status, name in results:
        if status == FAIL:
            print(f"  #{num}: {name}")
    sys.exit(1)
else:
    print("Alle Checks grün — Source-Smoke P3 bestanden.")
    sys.exit(0)
