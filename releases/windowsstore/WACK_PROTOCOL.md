# CleanMarkdown - WACK-Protokoll

## Ziel

Nach dem lokalen MSIX-Build soll der Windows App Certification Kit (WACK)-Lauf dokumentiert werden, damit Store-Submission und spätere Regressionen reproduzierbar nachvollziehbar bleiben.

## Vorbereiteter Befehl

```powershell
$projectRoot = "C:\_Local_DEV\repos\CleanMarkdown"
$reportRoot = Join-Path $projectRoot "releases\windowsstore\test_reports"
New-Item -ItemType Directory -Force -Path $reportRoot
& appcert.exe test -appxpackagepath "$projectRoot\releases\CleanMarkdown.msix" -reportoutputpath "$reportRoot\wack_report.xml"
```

## Prüfkriterien (Windows App Certification Kit)
- **Crashes and hangs:** App startet fehlerfrei ohne unhandled exceptions
- **App manifest compliance:** Saubere Deklaration von `runFullTrust`, `TargetDeviceFamily` und 6 Sprachressourcen (`de-DE`, `en-US`, `es-ES`, `zh-CN`, `ja-JP`, `ru-RU`)
- **Package compliance:** Gültige XML-Signaturen und Struktur
- **Security features:** Keine verbotenen APIs oder Elevation-Bypasses
- **Zero-Egress & Privacy:** Keine unberechtigte Datenübertragung, lokale Speicherung in `%APPDATA%\CleanMarkdown\settings.json`
