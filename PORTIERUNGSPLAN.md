# Portierungsplan: CleanMarkdown

Stand: 2026-05-24

## Kurzfazit

CleanMarkdown hat noch keinen eigenständigen Portierungsplan. Die vorhandene Projektdoku nennt Windows als erstes Ziel und Linux/macOS als spätere Option. Dieser Plan konkretisiert daraus eine bedarfsgerechte Plattformstrategie.

Entscheidung: Windows Store bleibt der erste Release-Kanal für die Desktop-App. macOS und Linux werden als P3-Desktop-Smoke-Ziele aus derselben PySide6-Codebasis geführt. Für Web, Android und iOS wird kein nativer Clone priorisiert, sondern ein späterer Web/PWA-Companion für schnelles Lesen, Bearbeiten und Exportieren einzelner Markdown-Dateien mit optionalem Asset-Bündel.

## Warum plattformübergreifend sinnvoll ist

CleanMarkdown ist ein Single-File-Werkzeug für Arbeits-, Analyse- und Steuerungsdokumente. Diese Dateien entstehen nicht nur am Windows-Desktop: Nutzer lesen Markdown unterwegs, korrigieren kleine Abschnitte auf mobilen Geräten und wollen Dokumente ohne Cloud-Zwang zwischen Geräten bewegen. Gleichzeitig ist der Kernnutzen lokal, schnell und dateibasiert. Deshalb ist eine Web/PWA-Linie sinnvoller als getrennte native Mobile-Apps mit eigener Datenhaltung.

## Bestehender Stand

- Kernprodukt: lokale PySide6-Desktop-App mit zwei Tabs, PDF-Export, DE/EN-Oberfläche und Self-Test.
- Datenmodell: Markdown-Datei bleibt die einzige Wahrheit.
- Mobilitätsfaktor: mittel bis hoch für Lesen, kleine Korrekturen und Export; niedriger für lange Schreibsessions.
- Store-Status: in `WINDOWS_STORE_PIPELINE.md` als Store-Kandidat mit hohem Potential vorgemerkt.
- Vorhandene Plattformhinweise: `Feature_Analyse_CleanMarkdown.md` nennt Windows zuerst, später optional Linux/macOS.
- Fehlend: konkrete Entscheidung zu Web/PWA, Android, iOS, Mac, Linux, Austauschformat und Priorisierung.

## Plattformoptionen

| Option | Bewertung | Entscheidung |
|---|---|---|
| Windows Store Release | Sehr sinnvoll: Hauptzielgruppe, vorhandene EXE-/Start-Skripte, klare Store-Nische als lokales Markdown-Werkzeug. | P0/P1 vorbereiten. |
| Android-Version oder Android-Clone | Native App wäre Mehraufwand und müsste Dateizugriff, PDF-Export und UI neu lösen. Mobile Nutzung ist eher Lesen und kleine Korrektur. | Kein nativer Clone; Android über PWA testen. |
| Webapp | Sinnvoll als leichter Companion für einzelne `.md`-Dateien, Drag-and-drop, Export und Sharing. Keine Cloud-Pflicht. | P2 als PWA-Companion planen. |
| iOS-Version | Native App hätte hohen Aufwand durch Sandbox und Dateizugriff. Nutzen deckt sich weitgehend mit Web/PWA. | Kein nativer Clone; iOS über PWA testen. |
| Mac App | Technisch aus PySide6 plausibel, aber Store-/Signatur-Aufwand erst nach Windows-MVP. | P3 Source-/Build-Smoke, keine eigene Produktlinie. |
| Linux-Version | Technisch aus PySide6 plausibel und für Markdown-Nutzer relevant. | P3 Source-/Build-Smoke, später AppImage/Flatpak prüfen. |

## Zielarchitektur

### Desktop-Linie

- Windows bleibt Referenzplattform.
- PySide6-Codebasis bleibt führend.
- Windows Store/MSIX wird erst nach GitHub-/Store-Readiness abgeschlossen.
- macOS/Linux werden nur als Kompatibilitätsziele geführt, solange keine konkrete Nachfrage oder Contributor-Kapazität existiert.

### Web-/Mobile-Linie

- Web/PWA als getrennte, schlanke Companion-Linie.
- Kein eigener Serverzwang; lokal im Browser nutzbar.
- Unterstützt einzelne Markdown-Dateien und später ein Asset-Bündel.
- Android/iOS laufen über dieselbe PWA, nicht über getrennte native Apps.
- Funktionsumfang bewusst kleiner als Desktop: Lesen, Bearbeiten, Vorschau, Markdown-Export; PDF-Export nur wenn browserseitig robust genug.

### Austauschformat

Da Markdown selbst das führende Format ist, braucht CleanMarkdown kein schweres Projektdatenformat. Für mobile/webbasierte Nutzung reicht zunächst:

1. `.md` als Primärformat.
2. Optional `cleanmarkdown-bundle-v1.zip` für Markdown plus lokale Assets.
3. Optional `cleanmarkdown-session-v1.json` nur für Einstellungen wie Theme, Sprache, zuletzt genutzter Modus und Exportpräferenzen.

## Priorisierte Umsetzung

### P0: Windows-Store-Basis

- `store_package.json` für CleanMarkdown anlegen.
- Store-Listing DE/EN erstellen.
- Screenshot-Set für Store und README konsolidieren.
- `_STORE/msstore_pretest.ps1` gegen die Release-EXE ausführen.

### P1: Desktop-Exportvertrag

- Dokumentieren, dass `.md` das stabile Austauschformat bleibt.
- `cleanmarkdown-bundle-v1.zip` spezifizieren, falls relative Assets mobil/webfähig transportiert werden sollen.
- Prüfen, ob ein CLI-Exportpfad für PDF und HTML sinnvoll ist.

### P2: Web/PWA-Companion

- Minimalen PWA-Prototyp für Drag-and-drop `.md`, Lesen, Editieren und Speichern planen.
- Mobile UX auf Android und iOS im Browser testen.
- Keine Desktop-Funktionen ungeprüft nachbauen; Fokus bleibt schneller Einzeldatei-Workflow.

### P3: macOS/Linux-Smoke

- CI-Matrix oder manuelle Smoke-Anleitung für Linux und macOS vorbereiten.
- PySide6-Start, Datei öffnen/speichern und PDF-Export prüfen.
- Packaging erst nach stabiler Windows-Store-Reife entscheiden.

## Nicht-Ziele

- Kein Vault-System.
- Kein eigener Cloud-Sync.
- Kein nativer Android-/iOS-Clone ohne klare Nachfrage.
- Keine zweite Datenrealität neben Markdown.
- Keine große Suite-Architektur.

