# CleanMarkdown Web/PWA-Portierung – Status

**Quelle:** `../` (Python, PySide6)
**Ziel:** Web/PWA mit späterem Capacitor-Wrapper für Android + iOS
**App-ID:** `com.lukas.cleanmarkdown`
**Erstellt:** 2026-05-25
**Aktualisiert:** 2026-07-17

## Status

| Schritt | Status | Dateien |
|---------|--------|---------|
| 1. Projektstruktur | ERLEDIGT | Vite + React + TypeScript + Tailwind + Capacitor-Grundlage |
| 2. Austauschformat | TEILWEISE | `.md` und `cleanmarkdown-session-v1.json` lokal importierbar/exportierbar |
| 3. Lokaler Speicher | ERLEDIGT | letzter Stand in `localStorage` |
| 4. UI-Screens | ERLEDIGT | nutzbarer Lese-/Schreib-MVP mit mobiler Oberfläche |
| 5. PWA-Manifest + Icons | ERLEDIGT | Manifest via `vite-plugin-pwa`, SVG-Icons in `public/icons/` |
| 6. Capacitor-Wrapper | ERLEDIGT | Android-Wrapper unter `android/` erzeugt, App-ID `com.lukas.cleanmarkdown` |
| 7. Build verifizieren | TEILWEISE | `npm run build`, `npm run test:cap` und der neue `android:doctor` sind lokal prüfbar; der stale DragLeave-Guard ist korrigiert, das fremd-dirty Apple-Touch-Icon bleibt transparent und hält genau einen PWA-Test rot |

## Was jetzt umgesetzt ist

- Dateidialog und Drag-and-drop für Markdown oder Session-JSON
- Gerenderte Markdown-Vorschau mit lokalem Sanitizing
- Editor, Dateiname, Theme-Umschaltung und Arbeitsmodi
- Export als `.md` oder `cleanmarkdown-session-v1.json`
- Lokale Fortsetzung über Browser-Speicher
- PWA-Metadaten für spätere Installation
- Statistik-Erweiterung: Zeilen + Links neben Wörtern, Zeichen und Lesezeit
- Kopier-Button: Markdown-Inhalt direkt in die Zwischenablage
- Pure-Logic-Modul `src/lib/markdownStats.mjs` mit Node:test-Suite (31 Tests)
- Android-Readiness-Doctor für Wrapper, Capacitor 7, Node.js 20+, JDK 17+,
  Android SDK 35, Build-Tools und `adb`; optionaler Gradle-Lauf hat einen
  harten 30-Sekunden-Timeout statt unbegrenzt zu hängen

## Nächste Schritte

1. `npm run android:doctor:json` ausführen und die gemeldeten lokalen Blocker schließen.
2. Erst danach `npm run android:gradle-doctor`, `npm run cap:sync` und `npm run cap:android` ausführen.
3. Mobile Browser-Checks auf Android/iOS mit echter Dateiöffnung durchführen.
4. Asset-Bundle `cleanmarkdown-bundle-v1.zip` definieren, damit relative Bilder später mitwandern.

## Warum PWA statt nativ?

Diese Entscheidung folgt `../PORTIERUNGSPLAN.md`.

- Eine Codebasis für Browser, Android und iOS
- Desktop bleibt die führende Vollversion
- Mobile Companion konzentriert sich auf kurze, dateibasierte Aufgaben
- Weniger Wartung als drei getrennte Native-Apps

## iOS-Status

Bis ein Xcode-fähiger Mac-Lauf vorhanden ist, bleibt iOS über Safari/PWA der erste Testpfad.

## Wichtig: `node_modules` nicht in OneDrive halten

Für ernsthafte Frontend-Arbeit den Ordner spiegeln oder `node_modules` strikt lokal lassen, damit der Sync nicht ausbremst.
