<img src="assets/banner.png" width="100%" alt="CleanMarkdown Banner"/>

# CleanMarkdown

Deutsch · **[English](README.md)**

Schneller lokaler Markdown-Viewer und -Editor mit cleanem Lesemodus, Raw-Markdown-Bearbeitung, PDF-Export und 6-Sprachen-Oberfläche (`de`, `en`, `es`, `zh`, `ja`, `ru`).

[![Ökosystem: doc-bricks](https://img.shields.io/badge/%C3%96kosystem-doc--bricks-blue.svg)](https://github.com/doc-bricks)
[![Umbrella: open-bricks](https://img.shields.io/badge/Umbrella-open--bricks-purple.svg)](https://github.com/open-bricks)
[![CI](https://github.com/doc-bricks/CleanMarkdown/actions/workflows/tests.yml/badge.svg)](https://github.com/doc-bricks/CleanMarkdown/actions/workflows/tests.yml)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-teal.svg)](LICENSE)
[![Python 3.10 - 3.13](https://img.shields.io/badge/Python-3.10--3.13-blue.svg)](https://python.org)
[![Plattform: Windows | macOS | Linux](https://img.shields.io/badge/Plattform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://github.com/doc-bricks/CleanMarkdown)
[![Zero-Egress](https://img.shields.io/badge/Datenschutz-100%25%20Offline%20%7C%20Zero--Egress-success.svg)](SECURITY.md)
[![Tests: 98 passed](https://img.shields.io/badge/Tests-98%20passed-brightgreen.svg)](tests)
[![Version](https://img.shields.io/badge/Version-1.0.0-teal.svg)](CHANGELOG.md)

> [!NOTE]
> Maschinenlesbare Projektübersicht und KI-Kontext verfügbar in [`llms.txt`](llms.txt).

## Funktionen

- Zwei klare Tabs: `Lesen` und `Editor`
- Reiner Markdown-Editor mit Hilfsbuttons statt WYSIWYG-Komplexität
- Formatierung für markierten Text entfernen, um Markdown-Syntax zu lösen und frisch zu starten
- Cleane gerenderte Leseansicht
- PDF-Export mit Zeitstempel-Dateinamen
- Session-Export und -Import über `cleanmarkdown-session-v1.json` für den lokalen Übergang zum Web-Companion
- Autosave mit einstellbarem Intervall
- 6-Sprachen-Oberfläche (`de`, `en`, `es`, `zh`, `ja`, `ru`)
- Helles und dunkles Theme
- Optionale obere Aktionsleiste für einen besonders ruhigen Standardaufbau
- Optionale Scroll-Synchronisierung beim Wechsel zwischen `Lesen` und `Editor`
- Leichtgewichtige Mathe-Vorschau für `$...$`, `$$...$$`, `\(...\)` und `\[...\]` in Leseansicht und PDF-Export
- Ruhige Syntaxhervorhebung für zentrale Markdown-Gruppen
- Relative Bilder und lokale Asset-Links werden aus dem Ordner der geöffneten Markdown-Datei geladen

## Screenshot

![CleanMarkdown Hauptfenster](README/screenshots/main_view.png)

## Produktfamilie & Core-Workflows

CleanMarkdown besteht aus drei aufeinander abgestimmten Editionen, um lokales Lesen und Schreiben auf jedem Gerät zu unterstützen:

| Feature / Arbeitsbereich | 💻 Desktop App (PySide6) | 🌐 Web Companion (PWA) | 📱 Mobile Port (Flutter) |
| :--- | :--- | :--- | :--- |
| **Primäre Plattform** | Windows (nativ) | Web / Mobile Browser | Android / iOS |
| **Offline-Verfügbarkeit** | Ja (100% offline) | Ja (via Service Worker) | Ja (vollständig offline) |
| **Dateizugriff** | Direktes lokales Dateisystem | Drag & Drop / Dateidialog | Lokaler Speicher / Document Provider |
| **Exportoptionen** | PDF-Export, Raw-Markdown, Session-JSON | Raw-Markdown, Session-JSON | Lokale Markdown-Datei |
| **Autosave** | Konfigurierbares Intervall | Lokaler Browser-Speicher | Manueller Speicher-Workflow |
| **Mathe-Vorschau** | Ja (dezent inline/Block) | Ja (Browser-gerendert) | Ja (Mobile-gerendert) |
| **Daten-Übergabe** | Export/Import `cleanmarkdown-session-v1.json` | Export/Import `cleanmarkdown-session-v1.json` | Standalone Dateitransfer |

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

1. Markdown-Datei oder `cleanmarkdown-session-v1.json` über `Datei -> Öffnen...` laden oder direkt im Editor schreiben.
2. Über die beiden Tabs zwischen `Lesen` und `Editor` wechseln.
3. Mit den Hilfsbuttons Markdown-Strukturen einfügen oder markieren und formatieren.
4. Das aktuelle Dokument über `Datei -> PDF exportieren` als PDF ausgeben oder den Arbeitsstand über `Datei -> Session exportieren` sichern.
5. Sprache, Theme, Autosave, Exportverhalten, Sichtbarkeit der Leisten und Scroll-Sync unter `Ansicht -> Einstellungen` anpassen.

Die Mathe-Unterstützung bleibt bewusst schlank: Formeln werden lokal lesbar und dezent dargestellt, ohne separate TeX-Laufzeit.

Relative Bildlinks wie `![Diagramm](diagramm.png)` werden relativ zum Speicherort der aktuellen Markdown-Datei aufgelöst. Nach `Speichern unter` aktualisiert sich die Vorschau, damit verschobene oder neu angelegte Asset-Verweise sofort den neuen Ordner nutzen.

Das Sessionformat transportiert bewusst keine Asset-Dateien. Für portables Markdown plus relative Bilder beschreibt [`EXPORTFORMAT.md`](EXPORTFORMAT.md) den reservierten Bundle-Vertrag, auch wenn der ZIP-Workflow noch nicht implementiert ist.

## Lokale Privatsphäre

CleanMarkdown öffnet und speichert Dateien lokal. Beim normalen Bearbeiten, Anzeigen und PDF-Export werden keine Dokumente in einen Cloud-Dienst hochgeladen.

## Editor-Hervorhebung

Der Raw-Editor nutzt eine reduzierte Vierer-Gruppierung:

- Blau für Überschriften und Hervorhebungen
- Grün für Inline-Code und Codeblöcke
- Pink/Magenta für Links, Bilder und Fußnoten
- Sanftes Grau-Violett für Listen, Zitate, Tabellen und Strukturmarker

## Projektstatus

Aktuelle Version: `1.0.0`

CleanMarkdown ist bereits als kleines öffentliches MVP nutzbar. Der aktuelle Schwerpunkt liegt auf praktischer Qualität bei realem Rendering und PDF-Export, nicht auf unnötigem Feature-Ausbau.

## Entwicklung

```powershell
python -m pip install -r requirements.txt pytest
python -m py_compile main.py
python -m pytest -q
python main.py --self-test
python main.py
```

Der Selbsttest prüft Öffnen, Speichern/Export, Task-Listen, Mathe-Markup, Scroll-Sync, relative Asset-Auflösung und echte Markdown-Roundtrips über öffentliche Repo-Dokumente. Pytest deckt Renderer-, Formatierungs- und Datei-/Session-Randfälle ab.

## Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).
