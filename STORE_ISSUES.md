# CleanMarkdown — Store Issues & Versionsverlauf

## Aktuelle Store-Version: 1.0.3.0
Veroeffentlicht: zuletzt bestaetigt vor 2026-09-27 (Submission `1152921505701981274`, Status `Published`)

## In Zertifizierung: 1.0.5.0
Eingereicht: 2026-09-27 | Submission-ID `1152921505701985229` | Status `Certification`
Sicht-OK Icon-Collage (Policy §7a.2): Nutzer, 2026-09-27, woertlich „sieht gut aus abgenommen"
(Collage `C:\Users\User\OneDrive\Desktop\CleanMarkdown-Icon-Collage_1.0.5_2026-09-27-final.png`).

## Offene Issues

| # | Severity | Beschreibung | Datei:Zeile | Gefunden | Status |
|---|----------|-------------|-------------|----------|--------|
| 1 | P1 | Store-Paket registriert keinen `.md`-Handler: `AppxManifest.xml` deklarierte weder `uap:FileTypeAssociation` noch `uap3:AppExecutionAlias`. Nach Store-Installation existiert keine Dateizuordnung; die App erscheint nicht im Dialog „Öffnen mit". Betrifft alle Store-Kunden. | `store_package/CleanMarkdown/AppxManifest.xml` | 2026-08-23 | GEFIXT (Store, 1.0.5.0, Submission `1152921505701985229`) — war WIEDER OFFEN in 1.0.3 (gemessen 2026-09-27), siehe #6/#9 |
| 2 | P2 | Store-Paket enthielt eine PyInstaller-onefile-EXE, die bei jedem Start ins Temp-Verzeichnis entpackt (Startzeit ~10 s). | `build_exe.bat` / Paketaufbau | 2026-08-23 | GEFIXT (GitHub) |
| 3 | P2 | `build_exe.bat` brach jeden Build ab: ungeschützte Klammern in der `echo`-Zeile des `else`-Zweigs zerreissen den `if`-Block beim Einlesen durch `cmd`. Regression aus `914f6e0`. | `build_exe.bat:64` | 2026-08-23 | GEFIXT (GitHub) |
| 4 | P2 | onefile-Release-EXE (`releases/v1.0.1/CleanMarkdown-1.0.1-win64.exe`) startet nicht zuverlässig (Prozess beendet sich nach ~30 s). Nicht ausgeliefert — das Store-Paket nutzt den geprüften onedir-Build. | `releases/v1.0.1/` | 2026-08-23 | OFFEN |
| 5 | P3 | Store-Paket enthält `setuptools` als Ballast; der Exclude-Scanner lieferte eine leere Ausschlussliste (2 Byte). | `_tools/build_exclude_scanner.py` (Aufruf) | 2026-08-23 | OFFEN |
| 6 | P1 | `.md`-Dateisymbole (Desktop/Explorer) als braune Platte mit kleinem Logo: Das Symbol ist `CleanMarkdown.exe,0`; die 1.0.3-EXE trägt das fehlerhafte Plattendesign (Abweichung 0,35 zur Kachel). Zusätzlich fehlten im MSIX `resources.pri` und alle targetsize/unplated-Varianten. | EXE-Icon-Ressource, `store_assets/`, `_STORE/msstore_build_msix.ps1` | 2026-09-27 | GEFIXT (Store, 1.0.5.0, Submission `1152921505701985229`) |
| 7 | P1 | Nutzersymptom aus #6 blieb trotz 1.0.5 bestehen: `.md` -> UserChoice `CleanMarkdown.mdfile` (aus `install_local.ps1`), `DefaultIcon` zeigt auf die LOKALE EXE unter `%LOCALAPPDATA%\Programs\CleanMarkdown` (installiert per `install_local.ps1`, unabhängig von der Store-Version). Das MSIX ersetzt die lokale Dateizuordnung nicht automatisch — beide Installationsarten dürfen nicht parallel bestehen. | `install_local.ps1`, Registry `HKCU\Software\Classes\CleanMarkdown.mdfile` | 2026-09-27 | GEFIXT (GitHub, `uninstall_local.ps1` gemergt via PR #7, main `42f5249`) — 4 Abnahmerunden (astra x2, Fable x2), zuletzt OK ohne Blocker. Reale Ausfuehrung braucht weiterhin Nutzer-Freigabe (Registry-Änderung), laeuft NACH Installation von 1.0.5.0. |
| 8 | P1 | Vier manipulierte MSIX-Pakete (falsche Pixelgröße, opake unplated-Assets, fehlende Manifest-EXE, falsche PRI-Identität) kamen mit Exit 0 durch `_STORE/icon_consistency_check.py --package`; der Build erzwang `--package` zudem nicht. | `_STORE/icon_consistency_check.py`, `_STORE/msstore_build_msix.ps1` | 2026-09-27 | GEFIXT: Gate prueft jetzt alle ausgelieferten Icon-Groessen (aus Paket/`resources.pri` erkannt statt Festliste), `msstore_build_msix.ps1` erzwingt `--package` real. Alle 7 von astra reproduzierten Manipulationen (inkl. zweiter Application, korrupte Manifest-EXE, Ein-Pixel-Transparenz-Umgehung) korrekt abgelehnt, finale Fable-Abnahme OK ohne Blocker. |
| 9 | P1 | Gebautes 1.0.5-MSIX enthielt den onedir-Laufzeitordner (`_internal`, Python-DLLs, PySide6) nicht — die App wäre nach Installation nicht gestartet, obwohl das Icon-Gate „passed" meldete. Von der 2. astra-Abnahme gefunden. | `_STORE/msstore_build_msix.ps1` | 2026-09-27 | GEFIXT (Store, 1.0.5.0, Submission `1152921505701985229`): Kopierschritt erkennt jetzt das onedir-Layout (Geschwisterordner `_internal` neben der EXE) und übernimmt den kompletten Ordner, analog zu `store_packager.py::copy_app_files`. Eingereichtes MSIX verifiziert: 234 `_internal`-Einträge inkl. `python312.dll`, Icon-Gate grün, Paketgröße 52,8 MB (Bezugsgroessen 1.0.0=73,6MB/1.0.1=52,2MB/1.0.3=48MB, kein Fremdballast — frisches Build-venv gegengeprueft). |

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

### v1.0.5.0 (2026-09-27) — Store (in Zertifizierung, Submission `1152921505701985229`)
- Behebt ein falsches Dateisymbol für `.md`-Dateien sowie ein veraltetes Fenstersymbol;
  verbessert die Stabilität der Store-Installation.
- Gefixt: #1/#6/#9 `.md`-Dateisymbol zeigte eine Platte statt des Dateityp-Icons; MSIX ohne
  echte Laufzeit ausgeliefert (P1)
- Gefixt: #8 Icon/Package-Gate liess manipulierte Pakete durch (P1, Haertung nicht
  nutzersichtbar, aber Voraussetzung fuer #1/#6/#9)
- Gefixt (GitHub, wirkt erst nach Nutzer-Migration): #7 lokale Altinstallation ueberdeckte
  die Store-Dateizuordnung dauerhaft (`uninstall_local.ps1`)
- 1.0.4 uebersprungen (nie eingereicht)
- Ticket: T-20260927-699609650, PR doc-bricks/CleanMarkdown#7 (main `42f5249`)

### v1.0.0.0 (2026-08-10) — Store
- Initialer Store-Release.

