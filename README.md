# CleanMarkdown

CleanMarkdown ist ein schnelles, lokales Desktop-Tool zum Lesen, Bearbeiten und Exportieren von Markdown-Dateien.
CleanMarkdown is a fast local desktop tool for reading, editing, and exporting Markdown files.

## Funktionen / Features

- Zwei klare Tabs: `Lesen` und `Editor`
- Reiner Markdown-Editor mit Struktur-Buttons statt WYSIWYG
- Gerenderte Leseansicht für ruhiges Lesen
- PDF-Export mit Zeitstempel-Suffix
- Autosave mit Intervall und Ein/Aus
- Deutsch und Englisch
- Dark und Light Theme
- Konfigurierbare Sichtbarkeit der oberen Aktionsleiste
- Syntaxhervorhebung für zentrale Markdown-Gruppen im Editor

## Screenshot / Screenshot

Ein GUI-Screenshot wird vor der ersten öffentlichen GitHub-Veröffentlichung ergänzt.
A GUI screenshot will be added before the first public GitHub release.

Vorbereiteter Pfad:
`README/screenshots/main_view.png`

## Installation

### Voraussetzungen / Requirements

- Windows 11 oder aktuelles Windows mit Python 3.12+
- Python-Pakete aus `requirements.txt`

### Schritte / Steps

```powershell
python -m pip install -r requirements.txt
python main.py
```

Oder per Doppelklick:

```bat
start.bat
```

## Verwendung / Usage

1. Markdown-Datei im Menü `Datei -> Öffnen...` laden oder direkt im Editor schreiben.
2. Zwischen `Lesen` und `Editor` über die Tabs wechseln.
3. Markdown-Strukturen im Editor über die Buttonleiste einfügen oder vorhandenen Text formatieren.
4. Über `Datei -> PDF exportieren` ein PDF neben der Quelldatei oder in einen eigenen Output-Ordner schreiben.
5. Design, Sprache, Autosave und Leistenverhalten in `Ansicht -> Einstellungen` anpassen.

## Editor-Hervorhebung / Editor Highlighting

Der Raw-Editor nutzt eine ruhige 4er-Gruppierung:

- Blau für Überschriften und Emphasis
- Grün für Code und Codeblöcke
- Pink/Magenta für Links, Bilder und Fußnoten
- Grau-Violett für Listen, Tabellen, Zitate und andere Strukturelemente

## Projektstatus / Project Status

Aktueller Stand: `0.2.0`

Der aktuelle Stand ist ein stabiler MVP mit funktionierendem Öffnen, Speichern, Autosave, Rendern, Syntaxhervorhebung und PDF-Export. Vor einer öffentlichen Veröffentlichung sind vor allem noch reale Testläufe mit mehreren Markdown-Dateien, Screenshot-Erstellung und eine letzte Qualitätsrunde für Rendering und PDF-Ausgabe geplant.

## Entwicklung / Development

Start für lokale Entwicklung:

```powershell
python -m py_compile main.py
python main.py --self-test
python main.py
```

## Lizenz / License

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).
This project is licensed under the [MIT License](LICENSE).
