# PORTIERUNGSPLAN — CleanMarkdown

Dieses Dokument definiert die plattformübergreifende Portierungsstrategie,
die Zielsystem-Architektur und den Austauschvertrag für **CleanMarkdown**.

---

## 1. Zielplattformen & Priorisierung

| Plattform | Technologie | Priorität | Status | Kanonischer Pfad / Artefakt |
|---|---|---|---|---|
| **Windows Desktop** | Python 3.12, PySide6 (Qt6) | P0 (Kanonisch) | Aktiv (v1.0.2) | `main.py`, `build_exe.bat` |
| **Windows Store (MSIX)** | Desktop-Bridge, AppxManifest, WACK | P0 (Release-Ready) | Bereit | `store_package/CleanMarkdown/`, `scripts/store_assets.py` |
| **Mobile Companion (Android/iOS)** | Flutter 3.x, Dart | P1 (Vollständig) | Getestet (37/37) | `flutter_port/` |
| **Web Companion & PWA** | Statisches HTML5 / WebAssembly | P2 (Konzept) | Spezifiziert | `web_companion/` (geplant) |
| **macOS & Linux Desktop** | PySide6 Source-Execution | P3 (Wartung) | Kompatibel | Source-Start via Python |

---

## 2. Architektur & Schichtenmodell

```
+-------------------------------------------------------------------------+
|                           CleanMarkdown Core                            |
+------------------------------------+------------------------------------+
|          Desktop (PySide6)         |       Mobile (Flutter / Dart)      |
|  - main.py                         |  - flutter_port/lib/               |
|  - MainWindow (Lesen & Raw-Editor) |  - HomeScreen (Responsive UI)      |
|  - MarkdownHighlighter             |  - MarkdownCleaner (Strip/Clean)   |
|  - SettingsStore (JSON lokal)      |  - Mobile Session Manager          |
|  - PDF-Export via QPrinter         |  - Lokalisierung (DE / EN / ES)    |
+------------------------------------+------------------------------------+
|                         Austauschvertrag                                |
|           Format: cleanmarkdown-session-v1.json                         |
|     - Keine Cloud, dateibasiert, UTF-8 ohne BOM, verlustfrei            |
+-------------------------------------------------------------------------+
```

### 2.1 Desktop-Linie (Windows)
- **Framework:** PySide6 (Qt for Python).
- **Philosophie:** Sofort einsatzbereit, reine Einzelfenster-Bedienung ohne überflüssige Menühierarchien.
- **Datenhaltung:** Einstellungen ausschließlich lokal in `%APPDATA%\CleanMarkdown\settings.json`.
- **Packaging:** PyInstaller Einzelfile (`CleanMarkdown-1.0.2-win64.exe`) und MSIX-Package für den Microsoft Store.

### 2.2 Mobile-Linie (`flutter_port/`)
- **Framework:** Flutter (Android & iOS).
- **Zweck:** Mobiles Sichten, Formatieren, Bereinigen und Lesen von Markdown-Dokumenten unterwegs.
- **Funktionen:**
  - Responsive Lesemodus und Bearbeitungsansicht.
  - `MarkdownCleaner`: Entfernen von Markdown-Syntax für sauberen Fließtext.
  - Statistiken: Wort-, Zeichen- und Lesezeitschätzung (200 WPM).
  - Volle Dreisprachigkeit: Deutsch, Englisch und Spanisch (`l10n`).
  - Session-Import und -Export gemäß `EXPORTFORMAT.md`.

---

## 3. Austauschvertrag: Session-Format v1

Der plattformübergreifende Austausch zwischen Desktop und Mobile erfolgt
vollständig offline über JSON-Dateien nach der Spezifikation `cleanmarkdown-session-v1.json`:

```json
{
  "version": "cleanmarkdown-session-v1",
  "document_title": "Beispieldokument",
  "markdown_content": "# Inhalt\n\nText...",
  "clean_text": "Inhalt\n\nText...",
  "stats": {
    "words": 120,
    "characters": 840,
    "reading_time_minutes": 0.6
  },
  "created_at": "2026-09-12T14:30:00Z"
}
```

### Invarianten:
1. **Zero-Egress / Datenschutz:** Keine Cloud-Synchronisation, kein Telemetrie-Egress.
2. **Determinismus:** Identische Wort- und Zeichenzählung auf beiden Plattformen.
3. **Verlustfreiheit:** Der Markdown-Originaltext bleibt beim Im- und Export vollständig erhalten.

---

## 4. Windows Store & MSIX Release-Readiness

### 4.1 Identität & Metadaten
- **Package-ID / Identity Name:** `Geiger.CleanMarkdown`
- **Publisher:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`
- **Publisher Display:** `Geiger`
- **Version:** `1.0.2.0`
- **Restricted Capabilities:** `runFullTrust`
- **File Type Associations:** `.md`, `.markdown`, `.mdown`, `.mkd`

### 4.2 Partner Center Richtlinie 10.1.3 Compliance
- **Schlüsselwörter:** Exakt 7 markenrechtsfreie Suchbegriffe pro Sprache, jeweils maximal 30 Zeichen:
  - Deutsch: `Markdown, Editor, Viewer, Vorschau, PDF-Export, Notizen, Schreiben`
  - Englisch: `Markdown, editor, viewer, preview, PDF export, notes, writing`
- **Screenshots:** 4 standardisierte Präsentations-Screenshots im Format 16:9 (1920x1080) für das Microsoft Store Listing:
  - `01_lesemodus-vorschau.png`
  - `02_raw-editor-struktur.png`
  - `03_dark-mode-theme.png`
  - `04_mobile-companion-session.png`

---

## 5. Verifikations- & Audit-Pipeline

| Prüfschritt | Werkzeug / Befehl | Anforderung |
|---|---|---|
| Desktop-Unit- & Integrationstests | `pytest` | 100% bestanden (145+ Tests) |
| Mobile-Statische-Analyse | `dart analyze` (in `flutter_port`) | 0 Issues |
| Mobile-Test-Suite | `flutter test` (in `flutter_port`) | 100% bestanden (37 Tests) |
| Store-Preflight-Audit | `python scripts/check_store_readiness.py` | 21 Kriterien erfüllt, 0 Findings |
| Store-Asset-Generierung | `python scripts/store_assets.py` | Alle 5 Kachel-Icons + Splash generiert |
| Store-Screenshots | `python scripts/generate_store_screenshots.py` | 16:9 Screenshots (1920x1080) |
| Lock-System-Integrität | `python lock_status.py` | Keine verwaisten Locks |
