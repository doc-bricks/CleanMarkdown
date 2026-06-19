# Datenschutzrichtlinie / Privacy Policy

**App:** CleanMarkdown
**Version:** 0.3.1
**Autor:** Lukas Geiger

---

## Deutsch

### Zusammenfassung

CleanMarkdown ist eine vollständig lokale Desktop-Anwendung. Es werden **keine Daten erhoben, gespeichert oder übertragen**.

### Datenverarbeitung

- **Keine eigenen Netzwerkverbindungen:** CleanMarkdown stellt selbst keine Internetverbindungen her. Es gibt keine Telemetrie, kein Tracking, keine Cloud-Synchronisation und keinen automatischen Update-Mechanismus. Wenn ein Markdown-Dokument anklickbare Links enthält, öffnet ein Klick darauf den Standard-Browser des Systems — die App selbst überträgt dabei keine Daten.
- **Lokale Dateien:** Alle Markdown-Dateien (.md, .markdown, .txt) werden ausschließlich lokal auf dem Gerät des Nutzers gelesen und geschrieben.
- **Einstellungen:** Benutzereinstellungen (Theme, Sprache, Scroll-Sync) werden lokal über QSettings gespeichert.
- **PDF-Export:** Der PDF-Export erfolgt lokal über QPrinter. Es wird kein externer Dienst genutzt.
- **Session-Export:** Das optionale Session-Format (`cleanmarkdown-session-v1.json`) speichert ausschließlich lokale Metadaten (Dateipfad, Cursor-Position, Scroll-Position) auf dem Gerät des Nutzers.

### Drittanbieter

CleanMarkdown nutzt zwei Open-Source-Bibliotheken (PySide6, Python-Markdown). Keine dieser Bibliotheken erhebt oder überträgt Daten.

### Kontakt

Bei Fragen zum Datenschutz: lukasgeiger@googlemail.com

---

## English

### Summary

CleanMarkdown is a fully local desktop application. **No data is collected, stored or transmitted.**

### Data Processing

- **No outgoing network connections:** CleanMarkdown itself does not establish any internet connections. There is no telemetry, no tracking, no cloud synchronization and no automatic update mechanism. When a Markdown document contains clickable links, clicking one opens the system's default browser — the app itself does not transmit any data.
- **Local files:** All Markdown files (.md, .markdown, .txt) are read and written exclusively on the user's local device.
- **Settings:** User preferences (theme, language, scroll sync) are stored locally via QSettings.
- **PDF export:** PDF export is handled locally via QPrinter. No external service is used.
- **Session export:** The optional session format (`cleanmarkdown-session-v1.json`) stores only local metadata (file path, cursor position, scroll position) on the user's device.

### Third Parties

CleanMarkdown uses two open-source libraries (PySide6, Python-Markdown). Neither of these libraries collects or transmits data.

### Contact

For privacy-related questions: lukasgeiger@googlemail.com
