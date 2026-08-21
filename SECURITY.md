# Sicherheitsrichtlinie / Security Policy

## Deutsch

### Sicherheitsphilosophie & Local-First Invarianten

CleanMarkdown ist als 100% lokales Werkzeug ohne Cloud-Zwang konzipiert:
- **Zero-Egress**: Dokumente und gerenderte Inhalte werden zu keinem Zeitpunkt an externe Server übertragen.
- **Lokale Dateigrenzen**: Dateioperationen (Öffnen, Speichern, PDF-Export) agieren ausschließlich auf dem lokalen Dateisystem des Nutzers.
- **Benutzerrechte**: CleanMarkdown benötigt und verlangt keine Administratorrechte (Non-Elevation / User-Mode-Betrieb).

### Sicherheitslücke melden

Wenn du in CleanMarkdown eine Sicherheitslücke findest:

1. Bitte **kein** öffentliches Issue eröffnen.
2. Nutze das private Vulnerability Reporting von GitHub: [Security Advisories](https://github.com/doc-bricks/CleanMarkdown/security/advisories).
3. Alternativ per E-Mail an: `security@ellmos.ai` oder `support@lukasgeiger.com`.
4. Beschreibe die Lücke mit Reproduktionsschritten, betroffenem Bereich und möglicher Auswirkung.

### Relevante Bereiche

Für dieses Projekt sind vor allem diese Bereiche sicherheitsrelevant:

- Lokales Öffnen und Speichern von Dateien (Pfadsicherheit / Directory Traversal Schutz)
- PDF-Export und HTML-Rendering-Sicherheit
- Öffnen externer Links aus gerendertem Markdown (keine ungesicherten Protokollausführungen)
- Einstellungsdatei und Pfadbehandlung (`settings.json`)

### Reaktionszeit

Kritische Sicherheitsmeldungen werden innerhalb von 48 Stunden bestätigt und prioritär bearbeitet.

---

## English

### Security Philosophy & Local-First Invariants

CleanMarkdown is built from the ground up as a 100% offline, local-first tool:
- **Zero-Egress**: Documents and rendered content are never transmitted to external servers.
- **Local File Boundaries**: File operations (open, save, PDF export) act strictly within the user's local filesystem.
- **User-Mode Execution**: CleanMarkdown runs strictly in non-elevated user mode without requiring administrative privileges.

### Reporting a Vulnerability

If you discover a security issue in CleanMarkdown:

1. Do **not** open a public issue.
2. Use GitHub's private vulnerability reporting: [Security Advisories](https://github.com/doc-bricks/CleanMarkdown/security/advisories).
3. Alternatively, contact security via email: `security@ellmos.ai` or `support@lukasgeiger.com`.
4. Include a clear description, reproduction steps, affected area, and potential impact.

### Relevant Areas

The most relevant security-related areas in this project are:

- Local file open/save behavior (path sanitation / directory traversal prevention)
- PDF export and HTML rendering safety
- Opening external links from rendered markdown (safe URI protocol handling)
- Settings persistence and configuration paths (`settings.json`)

### Response Time

Critical security reports are acknowledged within 48 hours and addressed with high priority.
