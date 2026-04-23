# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für dein Interesse an CleanMarkdown.

### Wie du beitragen kannst

1. Fehler sauber beschreiben
2. Verbesserungsideen als Issue formulieren
3. Kleine, gut verständliche Pull Requests einreichen

### Pull Requests

- Bitte pro Pull Request nur eine klar abgegrenzte Änderung
- Bestehendes Verhalten möglichst nicht unnötig umbrechen
- GUI-Änderungen kurz mit Screenshot oder Beschreibung erläutern
- Vor dem Einreichen mindestens `python -m py_compile main.py` und `python main.py --self-test` ausführen

### Entwicklungsstart

```powershell
python -m pip install -r requirements.txt
python -m py_compile main.py
python main.py --self-test
python main.py
```

### Richtlinien

- UTF-8 verwenden
- Keine Secrets oder lokalen Pfade committen
- Rohes Markdown-Verhalten sauber halten
- UI-Änderungen eher ruhig und konsistent als verspielt gestalten

## English

Thank you for your interest in CleanMarkdown.

### How to Contribute

1. Report bugs clearly
2. Open issues for feature ideas
3. Submit small and understandable pull requests

### Pull Requests

- Keep each pull request focused on one clear change
- Avoid unnecessary behavior changes
- Explain GUI changes with a short note or screenshot
- Run at least `python -m py_compile main.py` and `python main.py --self-test` before submitting

### Getting Started

```powershell
python -m pip install -r requirements.txt
python -m py_compile main.py
python main.py --self-test
python main.py
```
