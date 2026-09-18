# CleanMarkdown Web Companion & PWA

Der **CleanMarkdown Web Companion** ist eine vollkommen autonome, offlinefähige Webanwendung (Progressive Web App - PWA) zur Anzeige, Bereinigung und Bearbeitung von Markdown-Dokumenten und CleanMarkdown-Sessions.

---

## 1. Architektur & Kernmerkmale

- **Zero-Egress Invariante:** Keine Verbindung zu externen Servern, CDNs oder Telemetrie-Diensten. Alle Skripte (`app.js`), Stile (`app.css`) und Schriftarten nutzen native System-Fonts.
- **100% Offline via Service Worker:** Caching aller Kernkomponenten über `sw.js` (Cache-First-Strategie).
- **Dualer Workspace:**
  - **Lesemodus (`view`):** Ruhige, typografisch optimierte Darstellung von Überschriften, Listen, Tabellen, Code-Blöcken und Bildern.
  - **Editor (`editor`):** Minimalistischer Editor mit Monospace-Schriftart, Tabulator-Unterstützung und Drag-and-Drop.
- **Formatierungs-Cleaner (`stripMarkdown`):**
  - Befreit Markdown per Mausklick oder Tastenkombination (`Ctrl+Shift+K`) von allen Syntaxzeichen (Überschriften, Listenpunkte, Links, Fett-/Kursivschrift, Codeblöcke), erhält dabei die saubere Absatzstruktur.
- **Echtzeit-Statistiken:** Live-Berechnung von Wörtern, Zeichen (mit/ohne Leerzeichen) und geschätzter Lesezeit (200 WPM).
- **Session-Austauschvertrag v1:**
  - Volle Unterstützung von `cleanmarkdown-session-v1.json` zum nahtlosen Austausch zwischen Windows Desktop (PySide6), Mobile Companion (Flutter) und Web Companion.
- **Mehrsprachig:** Integrierte UI-Lokalisierung für Deutsch (DE), Englisch (EN) und Spanisch (ES).
- **Designs:** Paper (hell) und Night (dunkel).

---

## 2. Lokale Ausführung & Test

Da moderne Browser (insbesondere für Service Worker und Webmanifests) HTTP/HTTPS voraussetzen, kann der Web Companion lokal über jeden statischen Webserver gestartet werden:

```bash
cd web_companion
python -m http.server 8080
```

Anschließend im Browser öffnen: `http://localhost:8080`

---

## 3. Tastaturkürzel

| Tastenkombination | Aktion |
|---|---|
| `Ctrl+1` / `Cmd+1` | Lesemodus aktivieren |
| `Ctrl+2` / `Cmd+2` | Editor-Modus aktivieren |
| `Ctrl+O` / `Cmd+O` | Datei öffnen (.md, .txt, .json) |
| `Ctrl+S` / `Cmd+S` | Markdown speichern (.md) |
| `Ctrl+Shift+S` / `Cmd+Shift+S` | Session exportieren (.json) |
| `Ctrl+Shift+K` / `Cmd+Shift+K` | Formatierung bereinigen (Tx) |

---

## 4. Dateistruktur

```
web_companion/
├── index.html                  # Semantisches HTML5-Layout & PWA-Shell
├── app.css                     # Autarkes Design & Typografie (Paper/Night)
├── app.js                      # Reines Vanilla-ES6 Anwendungsmodul
├── sw.js                       # Service Worker für 100% Offline-Betrieb
├── manifest.json               # W3C Web App Manifest
├── favicon.ico / favicon.png   # Browser-Favicons
├── apple-touch-icon-180.png    # iOS PWA Touch-Icon
├── icon-192.png / icon-512.png # PWA Web Icons
├── icons/                      # Maskable & High-Res App-Icons
└── README.md                   # Dieses Dokument
```
