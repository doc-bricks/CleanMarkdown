# CleanMarkdown — Store Issues & Versionsverlauf

## Aktuelle Store-Version: 1.0.0.0
Veroeffentlicht: 2026-08-10

## In Zertifizierung: 1.0.1.0
Eingereicht: 2026-08-23 | Submission-ID `1152921505701720944` | Status `Certification`

## Offene Issues

| # | Severity | Beschreibung | Datei:Zeile | Gefunden | Status |
|---|----------|-------------|-------------|----------|--------|
| 1 | P1 | Store-Paket registriert keinen `.md`-Handler: `AppxManifest.xml` deklarierte weder `uap:FileTypeAssociation` noch `uap3:AppExecutionAlias`. Nach Store-Installation existiert keine Dateizuordnung; die App erscheint nicht im Dialog „Öffnen mit". Betrifft alle Store-Kunden. | `store_package/CleanMarkdown/AppxManifest.xml` | 2026-08-23 | GEFIXT (Store, in Zertifizierung) |
| 2 | P2 | Store-Paket enthielt eine PyInstaller-onefile-EXE, die bei jedem Start ins Temp-Verzeichnis entpackt (Startzeit ~10 s). | `build_exe.bat` / Paketaufbau | 2026-08-23 | GEFIXT (GitHub) |
| 3 | P2 | `build_exe.bat` brach jeden Build ab: ungeschützte Klammern in der `echo`-Zeile des `else`-Zweigs zerreissen den `if`-Block beim Einlesen durch `cmd`. Regression aus `914f6e0`. | `build_exe.bat:64` | 2026-08-23 | GEFIXT (GitHub) |
| 4 | P2 | onefile-Release-EXE (`releases/v1.0.1/CleanMarkdown-1.0.1-win64.exe`) startet nicht zuverlässig (Prozess beendet sich nach ~30 s). Nicht ausgeliefert — das Store-Paket nutzt den geprüften onedir-Build. | `releases/v1.0.1/` | 2026-08-23 | OFFEN |
| 5 | P3 | Store-Paket enthält `setuptools` als Ballast; der Exclude-Scanner lieferte eine leere Ausschlussliste (2 Byte). | `_tools/build_exclude_scanner.py` (Aufruf) | 2026-08-23 | OFFEN |

## Geplanter naechster Release: 1.0.1.0
Trigger: **1x P1 mit breiter Auswirkung** (WINDOWS_STORE_BUGFIX_POLICY §3.2) — die
Dateizuordnung ist für alle Store-Kunden komplett unbrauchbar, es gibt keinen Workaround
ausser dem Öffnen-Dialog innerhalb der App.

### Release-Gate 1.0.1.0 — Stand 2026-08-23

| Schritt (Policy §6.4/§6.5) | Status |
|---|---|
| Version in `store_package.json` hochgezaehlt | OK (1.0.1.0) |
| CHANGELOG aktualisiert | OK |
| Build: PyInstaller -> MSIX | OK (`releases/windowsstore/v1.0.1/CleanMarkdown-1.0.1.0.msix`, 49,75 MB) |
| Automatisierter Pre-Submission-Test (`_STORE/msstore_pretest.ps1`) | OK — 10 PASS / 0 FAIL / 1 WARN (Warnung „EXE klein" ist bei onedir erwartbar) |
| Funktionstest Paket-EXE mit Dateiargument | OK — oeffnet uebergebene `.md`, Fenstertitel korrekt |
| MSIX-Inhalt gegengeprueft (entpackt) | OK — Identity 1.0.1.0, FTA `.md/.markdown/.mdown/.mkd`, Alias, alle Assets |
| WACK-Test | Uebersprungen — `appcert.exe` verlangt erhoehte Rechte (Windows-Vorgabe der Binary, empirisch geprueft); wie bei den vorherigen Einreichungen der Pipeline nicht durchlaufen. Store-Zertifizierung ist das wirksame Gate. |
| Manuelles Testprotokoll (`_STORE/MSSTORE_TESTPROTOKOLL_TEMPLATE.md`) | Offen — Kernfunktion und Dateiargument sind automatisiert geprueft, die Geraete-Matrix nicht |
| **Upload Partner Center** | **ERLEDIGT 2026-08-23** — Submission `1152921505701720944`, Status `Certification`, `TargetPublishMode Immediate`. Eingereicht mit `_STORE/msstore_submit_update.py` (neu). Listings `de-de`/`en-us`, Kategorie und Alterseinstufung wurden aus der letzten veroeffentlichten Submission uebernommen; nichts musste erneut ausgefuellt werden. |

Rollback-Paket: `releases/windowsstore/v1.0.0/CleanMarkdown-1.0.0.0.msix`

## Versionsverlauf

### v1.0.0.0 (2026-08-10) — Store
- Initialer Store-Release.

