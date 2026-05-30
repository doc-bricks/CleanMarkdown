# Exportformate für CleanMarkdown

Stand: 2026-05-28

## Grundsatz

`*.md` bleibt das Primärformat von CleanMarkdown. Die Markdown-Datei ist weiterhin die führende Wahrheit für Inhalt und relative Pfade.

Ergänzend gibt es zwei definierte Austauschformate:

1. `cleanmarkdown-session-v1.json` für einen lokalen Arbeitsstand inklusive UI-relevanter Einstellungen.
2. `cleanmarkdown-bundle-v1.zip` als reserviertes Containerformat für Markdown plus relative Assets.

## Primärformat: Markdown

- Dateiendungen: `.md`, `.markdown`, optional `.txt`
- Inhalt: reiner UTF-8-Markdown
- Relative Assets wie `![Bild](diagramm.png)` werden gegen den Ordner der Markdown-Datei aufgelöst.
- Stabilitätsregel: Neue App-Versionen dürfen gültige Markdown-Dateien nie unlesbar machen.

## Sessionformat: `cleanmarkdown-session-v1.json`

Zweck:

- Arbeitsstand zwischen Desktop-App und Web-Companion transportieren
- letzte Oberfläche, Theme und Exportpräferenzen mitgeben
- bewusst ohne eingebettete Asset-Dateien

Status:

- Desktop-App: Import und Export unterstützt
- Web-Companion: Import und Export unterstützt

### Pflichtfelder

```json
{
  "version": "cleanmarkdown-session-v1",
  "fileName": "notiz.md",
  "markdown": "# Inhalt",
  "theme": "paper",
  "workspace": "split",
  "updatedAt": "2026-05-28T16:10:00"
}
```

### Erweiterte Felder

```json
{
  "appVersion": "0.3.1",
  "settings": {
    "language": "de",
    "theme": "paper",
    "defaultMode": "view",
    "autosaveEnabled": true,
    "autosaveIntervalSeconds": 12,
    "exportMode": "source",
    "exportConfirm": true,
    "outputDir": "",
    "fileToolbarVisible": false,
    "editorToolbarCollapsed": false,
    "syncScrollPositions": true
  }
}
```

### Feldregeln

- `version`: Muss exakt `cleanmarkdown-session-v1` sein.
- `fileName`: Zielname der Markdown-Datei ohne Pflichteinbettung eines echten Pfads.
- `markdown`: UTF-8-Textinhalt.
- `theme`: `paper` oder `night`.
- `workspace`: `read`, `write` oder `split`.
- `updatedAt`: ISO-8601-Zeitstempel.
- `settings`: optionaler Zusatzblock für Desktop- und Companion-Einstellungen.

### Kompatibilitätsregeln

- Unbekannte Zusatzfelder müssen ignoriert werden.
- Fehlt `settings`, bleibt die Session trotzdem gültig.
- Der Desktop mappt `workspace=split` auf den Editor-Startmodus, weil es dort keine Split-Ansicht gibt.
- Das Sessionformat transportiert keine Binärdateien. Relative Bilder funktionieren nur, wenn die referenzierten Dateien lokal separat vorhanden sind.

## Bundleformat: `cleanmarkdown-bundle-v1.zip`

Zweck:

- Markdown-Datei zusammen mit relativen Bildern und lokalen Assets transportieren
- späterer Brückenschritt für Web/PWA und mobile Nutzung

Status:

- Formatvertrag definiert
- Implementierung bleibt bewusst offen und ist eine eigene Folgeaufgabe

### Reservierte ZIP-Struktur

```text
cleanmarkdown-bundle-v1.zip
├─ manifest.json
├─ document.md
└─ assets/
   ├─ bild.png
   └─ unterordner/diagramm.svg
```

### `manifest.json`

```json
{
  "version": "cleanmarkdown-bundle-v1",
  "document": "document.md",
  "session": "cleanmarkdown-session-v1.json",
  "assetsRoot": "assets/",
  "createdAt": "2026-05-28T16:10:00",
  "appVersion": "0.3.1"
}
```

### Bundle-Regeln

- `document.md` ist Pflicht.
- `manifest.json` ist Pflicht.
- `session` ist optional und referenziert eine zusätzliche Session-Datei im ZIP.
- Es werden nur relative lokale Assets in `assets/` aufgenommen.
- Externe HTTP-Links werden nie in das Bundle gezogen.

## Nicht-Ziele

- kein Cloud-Sync
- keine Datenbank
- keine eingebetteten PDF-Exporte im Sessionformat
- keine automatische Asset-Sammlung im Sessionformat
