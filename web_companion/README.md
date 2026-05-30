# CleanMarkdown – Web/PWA Companion

Vite + React + TypeScript + Tailwind + Capacitor.

Die Web-Linie ist bewusst schlank gehalten: lokale Markdown-Dateien öffnen, lesen, bearbeiten und wieder exportieren. Die Desktop-App bleibt die Vollversion; die PWA deckt den mobilen Einzeldatei-Workflow ab.

## Enthaltene Funktionen

- Drag-and-drop oder Dateidialog für `.md`, `.markdown` und `cleanmarkdown-session-v1.json`
- Gerenderter Lesemodus plus Rohtext-Editor
- Lokaler Browser-Speicher für den letzten Stand
- Export als Markdown oder Session-JSON
- Umschaltbare Arbeitsansicht: Lesen, Split, Schreiben
- Papier- und Nacht-Theme
- PWA-Basis mit Manifest und Icons

## Erste Schritte

```bash
# Empfohlen: lokalen Spiegel außerhalb OneDrive nutzen
cp -r web_companion ~/dev/cleanmarkdown-companion/
cd ~/dev/cleanmarkdown-companion/

npm install
npm run dev
npm run build

# Capacitor-Wrapper bei Bedarf
npx cap add android
npm run cap:sync
npm run cap:android
```

## Austauschformat

- Primärformat: `.md`
- Sessionformat: `cleanmarkdown-session-v1.json`
- Asset-Bundles sind noch offen und bleiben ein nächster Portierungsschritt

## App-ID / Bundle

`com.lukas.cleanmarkdown` – für Capacitor sowie spätere Android-/iOS-Wrapper vorgesehen.

## Status

Siehe [`PORTING_STATUS.md`](PORTING_STATUS.md).
