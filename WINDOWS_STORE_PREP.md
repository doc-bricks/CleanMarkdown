# Windows Store Vorbereitung & Release-Readiness — CleanMarkdown

**Stand:** 2026-09-12
**Version:** 1.0.2.0
**Package-ID:** `Geiger.CleanMarkdown`
**Publisher:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202` (Geiger)
**Status:** Release-Ready (Preflight 21/21 Kriterien erfüllt, 0 Findings)

---

## 1. Artefakt- & Dokumentenstatus

| Artefakt | Status | Anmerkung |
|---|---|---|
| `store_package.json` | OK | v1.0.2.0, Identity `Geiger.CleanMarkdown`, Canonical Publisher CN, Kategorie Productivity, DE+EN |
| `STORE_LISTING.md` | OK | DE+EN Listing-Texte vollständig, Partner Center Richtlinie 10.1.3 konform (exakt 7 Keywords <= 30 Zeichen, keine Markennamen) |
| `PRIVACY_POLICY.md` | OK | DE+EN, Offline-Invariante garantiert, kanonischer SettingsStore `%APPDATA%\CleanMarkdown\settings.json` |
| `SUPPORT.md` | OK | DE+EN, Support-URL, FAQ, Settings-Pfad |
| `THIRD_PARTY_LICENSES.txt` | OK | PySide6 (LGPL), Python-Markdown (BSD) |
| `PORTIERUNGSPLAN.md` | OK | Mehrziel-Architektur (Desktop P0, Store P0, Flutter Mobile P1, Web P2, macOS/Linux P3) & Session-Format v1 |
| Store-Kacheln (`store_package/CleanMarkdown/icons/`) | OK | 5 quadratische/rechteckige Kacheln (`icon_44x44.png`, `icon_50x50.png`, `icon_150x150.png`, `icon_310x150.png`, `icon_310x310.png`) + `SplashScreen.png` (620x300) |
| Legacy-Assets (`store_assets/`) | OK | Gespiegelt für ältere Build-Pipelines inkl. `AppxManifest.xml` |
| Store-Screenshots (4x 16:9) | OK | 1920x1080 in `store_package/CleanMarkdown/screenshots/` und `README/screenshots/store/` |
| Preflight-Store-Auditor | OK | `scripts/check_store_readiness.py` (21/21 Kriterien bestanden, 0 Findings) |
| Asset-Generator | OK | `scripts/store_assets.py` (erzeugt Icons, Kacheln und AppxManifest) |
| Screenshot-Generator | OK | `scripts/generate_store_screenshots.py` (native Plattform mit `WA_DontShowOnScreen`) |
| Test-Abdeckung | OK | 23 Store-Tests (`test_store_readiness.py`, `test_store_assets.py`, `test_portierungsplan.py`, `test_store_materials.py`), Gesamt-Pytest: 155/155 grün |

---

## 2. Partner Center Richtlinie 10.1.3 Compliance (Suchbegriffe)

- **Regel:** Maximal 7 Suchbegriffe pro Sprache, jeweils maximal 30 Zeichen, keine fremden Markennamen.
- **Deutsch (7):** `Markdown`, `Editor`, `Viewer`, `Vorschau`, `PDF-Export`, `Notizen`, `Schreiben`
- **Englisch (7):** `Markdown`, `editor`, `viewer`, `preview`, `PDF export`, `notes`, `writing`

---

## 3. AppxManifest.xml Konfiguration

- **Identity Name:** `Geiger.CleanMarkdown`
- **Publisher:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`
- **Version:** `1.0.2.0`
- **Capabilities:** `<rescap:Capability Name="runFullTrust" />` (erforderlich für Dateisystemzugriff via Dialoge)
- **File Type Associations:** `.md`, `.markdown`, `.mdown`, `.mkd`
- **Visual Elements:** Kachel-Icons in allen Standardauflösungen und Splash-Screen integriert.

---

## 4. Audit & Verifikation

```powershell
# Preflight Store Readiness Audit (21 Prüfungen)
python scripts/check_store_readiness.py

# Kachel- & Manifest-Generierung
python scripts/store_assets.py

# 16:9 Screenshots erzeugen
python scripts/generate_store_screenshots.py

# Automatisierte Tests ausführen
python -m pytest tests/test_store_readiness.py tests/test_store_assets.py tests/test_portierungsplan.py tests/test_store_materials.py
```
