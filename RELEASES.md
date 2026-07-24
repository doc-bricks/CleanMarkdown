# Releases — CleanMarkdown

Kanonisches Inventar der unter `releases/` abgelegten Build-Artefakte: Dateien,
SHA256-Prüfsummen, Build-Commit (soweit aus der lokalen Git-Historie
rekonstruierbar) und die Abgrenzung zwischen lokal/OneDrive gehaltenen
Artefakten und einem tatsächlich veröffentlichten GitHub-Release.

Stand: 2026-07-24 (Welle-1-U1/U2/U4-Fixes, v0.3.2-Eintrag ergänzt). Frühere
Fassung: 2026-07-23 (TASKSOLVER-Lauf, Task TW-CM-03/#1009). Alle Hashes in
diesem Dokument wurden direkt aus den Dateien in `releases/` neu berechnet,
nicht aus vorherigen Notizen übernommen.

## Wichtig: `releases/` ist kein Teil des Git-Repos

`.gitignore` (Zeile 61–62) schließt den gesamten Ordner aus:

```
# Releases and build artifacts
releases/
```

Alle Dateien unter `releases/` liegen ausschließlich lokal/in der
OneDrive-Synchronisation und wurden nie nach GitHub gepusht. `doc-bricks/CleanMarkdown`
hat aktuell **keinen** veröffentlichten GitHub-Release. Die "Releases" in
diesem Dokument sind lokale Build-Stände, kein öffentliches Release-Artefakt.
Das Erstellen eines GitHub-Release ist ausdrücklich nicht Teil dieser Aufgabe
(TW-CM-03-Nicht-Ziel) und separat vom User zu entscheiden (siehe
`AUFGABEN.txt`, Punkt "GitHub-Entscheidung … privat zuerst oder direkt
öffentlich").

## v0.3.2 — `releases/v0.3.2/`

| Datei | Bytes | SHA256 |
|---|---|---|
| `CleanMarkdown-0.3.2-win64.exe` | 49.944.801 | `0295e954606fa93196bc84ff408091f627f024ce88f673790e49d841ea4d3efd` |
| `CleanMarkdown-fast/CleanMarkdown.exe` | 4.235.033 | `953c3f2673f0d3b0f429a7ff599da3391801e59c7cb7df67dd9612f2135886e3` |

Beide Hashes stehen in `SHA256SUMS.txt` bzw. `SHA256SUMS-fast.txt`. Die
Checksummen wurden manuell per `Get-FileHash` erzeugt, weil der in
`build_exe.bat` eingebettete `powershell -NoProfile -ExecutionPolicy Bypass
-Command "Get-FileHash …"`-Aufruf auf diesem Host wiederholt mit
"Get-FileHash wurde nicht als Cmdlet erkannt" fehlschlug (Umgebungseigenheit
beim verschachtelten Windows-PowerShell-5.1-Aufruf aus dieser Session heraus
— direkter Aufruf von `powershell.exe -NoProfile … Get-Command Get-FileHash`
funktionierte isoliert einwandfrei; nicht weiter untersucht, da außerhalb des
Auftragsumfangs).

**Build-Commit: verifiziert.** Der Git-Blob-Hash von `main.py` in Commit
[`23d8eaa`](https://github.com/doc-bricks/CleanMarkdown/commit/23d8eaa)
(`a018731b011f61a5c5289846ed66f391a54c471b`) ist die Quelle dieses Builds —
`build_exe.bat` wurde direkt im Anschluss an diesen Commit-Stand ausgeführt
(lokaler Klon `C:\_Local_DEV\repos\CleanMarkdown`, kein Zwischenstand).

Anlass: Welle-1-Usertest 2026-07-23 (siehe `AUFGABEN.txt`) — U1 (PDF-Export
immer hell), U2 (Auto-Save vor Export bei ungespeichertem Dokument + korrekter
Documents-Ordner), U3 (Store-Screenshot-Tofu-Bug, Fix von Themen-Worker
"thema-screenshots", Commit `bf5f226`) und U4 (doppelte `.ico` entfernt).
Alle vier Punkte sind damit erledigt; ein Sprung auf `1.0.0` erfolgt bewusst
NICHT, weil unabhängig davon mehrere Store-Blocker (MSIX/WACK-Signierung,
Android-SDK-Smoke, Flutter-Testclaims) laut `AUFGABEN.txt` weiterhin offen
sind.

## v0.3.1 — `releases/v0.3.1/`

| Datei | Bytes | SHA256 |
|---|---|---|
| `CleanMarkdown-0.3.1-win64.exe` | 49.933.445 | `54051ccc50e1be64323c004f39750ba3580305f56da2fd27ef8d61763c6a052c` |
| `CleanMarkdown-0.3.1-source.zip` | 280.734 | `8031aefc20988c3bbdf697ca8f6a9affd5894c5ff4e6e6ddb57987d0ffb56fb1` |
| `CHANGELOG.txt` | 3.020 | `c9a1b7710b566888ebb98749ed1f3280e221ce2a6453bce8afc87900f9c36aec` |
| `CleanMarkdown-fast/CleanMarkdown.exe` | 4.231.139 | `a912d807d8f673b4fff4352c13aa5f95c9c2920bba88a6dab4f2370f6f5bc605` |

Alle vier Hashes stehen jetzt vollständig in `SHA256SUMS.txt` (EXE, Source-ZIP,
CHANGELOG.txt) bzw. `SHA256SUMS-fast.txt` (Fast-EXE). Vor diesem Lauf fehlten
Source-ZIP und CHANGELOG.txt in `SHA256SUMS.txt` — beide wurden ergänzt,
nachdem ihr SHA256 direkt aus der Datei neu berechnet wurde.

`CleanMarkdown-fast/` ist ein PyInstaller-`onedir`-Build mit 235 Dateien
(~118 MB, Launcher-EXE + `_internal/`-DLLs/Runtime). Wie bei v0.3.0/v0.2.0
wird nur die oberste, tatsächlich weiterzugebende Datei (`CleanMarkdown.exe`)
gehasht — die mitgelieferten Windows-/Python-Runtime-DLLs sind
PyInstaller-Bundling-Details, kein eigenständiges Release-Artefakt.

**Build-Commit: nicht rekonstruierbar.** `releases/v0.3.1/CleanMarkdown-0.3.1-source.zip`
enthält u. a. `__pycache__/*.pyc` — es ist kein `git archive`-Export, sondern
ein Zip eines Arbeitsverzeichnis-Stands. Der Git-Blob-Hash von `main.py` aus
dem ZIP (`933c90d076fcc1ccc188d3efef7037ce869b4c68`, git-blob-SHA1) wurde
gegen **jeden** Commit in `git log --all -- main.py` geprüft (`git rev-parse
<commit>:main.py`) — kein Treffer. Es existiert kein Git-Tag `v0.3.1`. Die im
release-internen `CHANGELOG.txt` dokumentierte Version datiert auf
`2026-05-01`, die EXE-Dateizeit ist dagegen `2026-06-14` (Fast-EXE-Ordner
sogar `2026-06-18`) — die Build-Artefakte wurden also sichtbar später
erzeugt als der Quelltext-Stand im ZIP. Diese Diskrepanz wird hier nur
dokumentiert, nicht aufgelöst (kein Ersetzen von Release-Artefakten ohne
Freigabe, TW-CM-03-Nicht-Ziel).

## v0.3.0 — `releases/v0.3.0/`

| Datei | Bytes | SHA256 |
|---|---|---|
| `CleanMarkdown-0.3.0-win64.exe` | 70.112.714 | `b9f9b0c99dc623d8cbe28152673541e1470472129523593dbcfaa27a7820649b` |
| `CleanMarkdown-0.3.0-source.zip` | 248.286 | `47d995f463b761c5ba10ddc3b180111acb0d91eed92d8d2cc4817081f259ae5b` |
| `CHANGELOG.txt` | 2.079 | `34d5585886ce0b11052f7cfc7e6e7d8472f373c1c2217fcdcdd5c0187928fa86` |

`SHA256SUMS.txt` war für v0.3.0 bereits vollständig und korrekt (Readback
gegen neu berechnete Hashes: alle 3 Einträge grün, unverändert gelassen).

**Build-Commit: verifiziert.** Der Git-Blob-Hash von `main.py` aus
`CleanMarkdown-0.3.0-source.zip` (`54d7a774c1947e1fced9b5e30edc9c12ebba0ca0`)
stimmt exakt mit dem `main.py`-Blob in Commit
[`68ed593`](https://github.com/doc-bricks/CleanMarkdown/commit/68ed5931ce4caa78c0ecd1c12672db916ddc6660)
überein (`Fix relative asset preview handling`, 2026-05-01 14:06:15 +0200,
liegt auf `origin/main`). Auch kein Git-Tag vorhanden, aber im Unterschied zu
v0.3.1 ist die Quelltext-Herkunft hier durch exakten Blob-Abgleich belegt.

## v0.2.0 — `releases/v0.2.0/`

| Datei | Bytes | SHA256 |
|---|---|---|
| `CleanMarkdown-0.2.0-win64.exe` | 70.088.571 | `904607d6a9394c7cae6fcb32ab655a5c26de23cd26b6f35166c7dad6aef39296` |

`SHA256SUMS.txt` vollständig und korrekt (1/1 Eintrag grün).

**Build-Commit: eindeutig.** Git-Tag `v0.2.0` zeigt auf Commit
`d18926b6ead1569e0b1aaf01fb2a7d45dd1da24a` ("Initial public release v0.2.0",
2026-04-23 04:05:41 +0200) — einziges Release mit echtem Git-Tag.

## Prüfmethode (reproduzierbar)

```
python -c "
import hashlib
h = hashlib.sha256()
with open(PFAD, 'rb') as f:
    for chunk in iter(lambda: f.read(1024*1024), b''):
        h.update(chunk)
print(h.hexdigest())
"
```

Die vorhandenen `SHA256SUMS*.txt`-Dateien nutzen CRLF-Zeilenenden; GNU
`sha256sum -c` scheitert dadurch am Zeilenumbruch im Dateinamen
(`$'\r': No such file or directory`) — das ist ein reines
Zeilenenden-Artefakt der Windows-Erzeugung, kein Hash-Fehler. Für einen
CRLF-robusten Readback jede Zeile mit `.rstrip('\r\n')` einlesen, bevor
`<hash> *<datei>` an Leerzeichen+Stern gesplittet wird.

Für den Blob-Abgleich (Source-ZIP-Provenienz) wurde der Git-Objektname exakt
wie von Git selbst gebildet: `sha1("blob " + len(data) + "\0" + data)`, bzw.
direkt per `git rev-parse <commit>:<pfad>` gegen jeden Commit aus
`git log --all --format=%H -- <pfad>` verglichen.
