# CleanMarkdown

Schneller lokaler Markdown-Viewer und -Editor mit cleanem Lesemodus, Raw-Markdown-Bearbeitung, PDF-Export und DE/EN-Oberfläche.

[English README](README.md)

## Funktionen

- Zwei klare Tabs: `Lesen` und `Editor`
- Reiner Markdown-Editor mit Hilfsbuttons statt WYSIWYG-Komplexität
- Cleane gerenderte Leseansicht
- PDF-Export mit Zeitstempel-Dateinamen
- Autosave mit einstellbarem Intervall
- Deutsche und englische Oberfläche
- Helles und dunkles Theme
- Optionale obere Aktionsleiste für einen besonders ruhigen Standardaufbau
- Optionale Scroll-Synchronisierung beim Wechsel zwischen `Lesen` und `Editor`
- Leichtgewichtige Mathe-Vorschau für `$...$`, `$$...$$`, `\(...\)` und `\[...\]` in Leseansicht und PDF-Export
- Ruhige Syntaxhervorhebung für zentrale Markdown-Gruppen

## Screenshot

![CleanMarkdown Hauptfenster](README/screenshots/main_view.png)

## Installation

### Voraussetzungen

- Windows mit Python 3.12+
- Pakete aus `requirements.txt`

### Schritte

```powershell
python -m pip install -r requirements.txt
python main.py
```

Oder direkt unter Windows:

```bat
start.bat
```

## Verwendung

1. Markdown-Datei über `Datei -> Öffnen...` laden oder direkt im Editor schreiben.
2. Über die beiden Tabs zwischen `Lesen` und `Editor` wechseln.
3. Mit den Hilfsbuttons Markdown-Strukturen einfügen oder markieren und formatieren.
4. Das aktuelle Dokument über `Datei -> PDF exportieren` als PDF ausgeben.
5. Sprache, Theme, Autosave, Exportverhalten, Sichtbarkeit der Leisten und Scroll-Sync unter `Ansicht -> Einstellungen` anpassen.

Die Mathe-Unterstützung bleibt bewusst schlank: Formeln werden lokal lesbar und dezent dargestellt, ohne separate TeX-Laufzeit.

## Editor-Hervorhebung

Der Raw-Editor nutzt eine reduzierte Vierer-Gruppierung:

- Blau für Überschriften und Hervorhebungen
- Grün für Inline-Code und Codeblöcke
- Pink/Magenta für Links, Bilder und Fußnoten
- Sanftes Grau-Violett für Listen, Zitate, Tabellen und Strukturmarker

## Projektstatus

Aktuelle Version: `0.3.0`

CleanMarkdown ist bereits als kleines öffentliches MVP nutzbar. Der aktuelle Schwerpunkt liegt auf praktischer Qualität bei realem Rendering und PDF-Export, nicht auf unnötigem Feature-Ausbau.

## Entwicklung

```powershell
python -m py_compile main.py
python main.py --self-test
python main.py
```

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).
