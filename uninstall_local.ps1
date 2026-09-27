# Rueckbau der lokalen Installation aus install_local.ps1, sobald das
# Store-Paket (MSIX) uebernommen hat.
#
# Hintergrund (T-20260927-699609650, Blocker D): install_local.ps1 legt eine
# eigene ProgID "CleanMarkdown.mdfile" mit DefaultIcon auf die lokale EXE in
# %LOCALAPPDATA%\Programs\CleanMarkdown an. Diese lokale Installation bleibt
# nach einer Store-Installation unveraendert bestehen und "gewinnt" weiterhin
# die .md-Dateizuordnung (bzw. haengt als olivgruene Kachel am Desktop) --
# das MSIX ersetzt sie NICHT automatisch, egal wie oft es aktualisiert wird.
# Dieses Skript raeumt genau das auf, was install_local.ps1 angelegt hat --
# und NUR, wenn ein Store-Paket mit einem tatsaechlichen .md-Handler bereits
# installiert ist (sonst bliebe der User ganz ohne .md-Handler zurueck).
#
# Empfohlene Reihenfolge (astra-Abnahme, T-20260927-699609650):
#   1. Passende Store-Version installieren/aktualisieren (mit .md-FileTypeAssociation
#      im Manifest -- eine Version OHNE das, z.B. 1.0.3, wird von diesem Skript
#      bewusst abgelehnt, siehe Schritt 1 unten).
#   2. .\uninstall_local.ps1 -WhatIf   # Vorschau, keine Aenderung
#   3. .\uninstall_local.ps1           # gesicherter Rueckbau (fragt vorher nach)
#   4. Windows-Einstellungen > Apps > Standard-Apps > ".md" -> CleanMarkdown
#      (Store) manuell als Standard waehlen -- der Rueckbau entfernt nur die
#      ALTE Zuordnung, er setzt keine neue.
#   5. Ergebnis pruefen (.md-Icon im Explorer/Desktop).
#
# Nutzung:
#   .\uninstall_local.ps1              # fuehrt den Rueckbau aus (fragt vorher nach)
#   .\uninstall_local.ps1 -WhatIf      # zeigt nur, was getan wuerde, KEINE Aenderung
#   .\uninstall_local.ps1 -Force       # ohne Rueckfrage (fuer Automatisierung)
#
# Sicherheitsnetz: Vor jeder Aenderung werden die betroffenen Registry-Zweige
# per `reg export` in einen eindeutigen Ordner je Lauf gesichert; schlaegt
# auch nur ein Export fehl, bricht das Skript VOR jeder Loeschung ab.

param(
    [switch]$WhatIf,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$progId = "CleanMarkdown.mdfile"
$installDir = Join-Path $env:LOCALAPPDATA "Programs\CleanMarkdown"
$exeTarget = Join-Path $installDir "CleanMarkdown.exe"
$startMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$shortcutPath = Join-Path $startMenuDir "CleanMarkdown.lnk"
$classesRoot = "HKCU:\Software\Classes"
$fileExtsMd = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.md"
$userChoiceKey = "$fileExtsMd\UserChoice"

# --- 1. Voraussetzung: Store-Paket MIT .md-Handler muss installiert sein ---
# Ein installiertes Paket allein genuegt nicht (astra-Fund D3): die auf
# diesem Host reale Version 1.0.3 ist installiert, ihr Manifest deklariert
# aber NULL FileTypeAssociation-Knoten fuer .md -- ein Rueckbau haette den
# User ganz ohne Handler zurueckgelassen. Deshalb zusaetzlich das Manifest
# des gefundenen Pakets pruefen, nicht nur seine blosse Existenz.
$storePkg = Get-AppxPackage -Name "Geiger.CleanMarkdown" -ErrorAction SilentlyContinue
if (-not $storePkg) {
    Write-Host "ABBRUCH: Kein Store-Paket 'Geiger.CleanMarkdown' installiert." -ForegroundColor Red
    Write-Host "Ohne Store-Paket wuerde dieser Rueckbau den User ganz ohne .md-Handler zuruecklassen."
    Write-Host "Zuerst CleanMarkdown aus dem Microsoft Store installieren/aktualisieren, dann erneut ausfuehren."
    exit 1
}

$manifestPath = Join-Path $storePkg.InstallLocation "AppxManifest.xml"
$hasMdHandler = $false
if (Test-Path $manifestPath) {
    [xml]$manifestXml = Get-Content $manifestPath -Raw
    $ns = New-Object System.Xml.XmlNamespaceManager($manifestXml.NameTable)
    $ns.AddNamespace("uap", "http://schemas.microsoft.com/appx/manifest/uap/windows10")
    $fileTypeNodes = $manifestXml.SelectNodes("//uap:FileTypeAssociation/uap:SupportedFileTypes/uap:FileType", $ns)
    foreach ($node in $fileTypeNodes) {
        if ($node.InnerText.Trim().ToLower() -eq ".md") { $hasMdHandler = $true; break }
    }
}
if (-not $hasMdHandler) {
    Write-Host "ABBRUCH: Store-Paket $($storePkg.PackageFullName) ist installiert, deklariert aber KEINE .md-FileTypeAssociation." -ForegroundColor Red
    Write-Host "Ein Rueckbau jetzt wuerde den User ganz ohne .md-Handler zuruecklassen."
    Write-Host "Zuerst auf eine Store-Version mit .md-Dateizuordnung aktualisieren, dann erneut ausfuehren."
    exit 1
}
Write-Host "Store-Paket mit .md-Handler gefunden: $($storePkg.PackageFullName)" -ForegroundColor Green

# --- 2. Was wird entfernt? (reine Vorschau, KEINE Aenderung, KEIN Backup) ---
$actions = @()

if (Test-Path "$classesRoot\$progId") {
    $actions += "ProgID-Zweig entfernen: $classesRoot\$progId (inkl. DefaultIcon, shell\open\command)"
}
if (Test-Path "$classesRoot\Applications\CleanMarkdown.exe") {
    $actions += "Applications-Zweig entfernen: $classesRoot\Applications\CleanMarkdown.exe"
}
$mdDefault = $null
if (Test-Path "$classesRoot\.md") {
    $mdDefault = (Get-Item "$classesRoot\.md").GetValue("")
}
if ($mdDefault -eq $progId) {
    $actions += "Default-Wert von $classesRoot\.md entfernen (zeigte auf $progId)"
} elseif ($mdDefault) {
    $actions += "UEBERSPRUNGEN: $classesRoot\.md zeigt bereits auf '$mdDefault' (nicht mehr $progId) -- unveraendert gelassen"
}
if (Test-Path "$classesRoot\.md\OpenWithProgids") {
    $prop = Get-ItemProperty -Path "$classesRoot\.md\OpenWithProgids" -Name $progId -ErrorAction SilentlyContinue
    if ($prop) { $actions += "OpenWithProgids-Eintrag '$progId' unter $classesRoot\.md\OpenWithProgids entfernen" }
}
$userChoiceProgId = $null
if (Test-Path $userChoiceKey) {
    $uc = Get-ItemProperty -Path $userChoiceKey -Name "ProgId" -ErrorAction SilentlyContinue
    if ($uc) { $userChoiceProgId = $uc.ProgId }
}
if ($userChoiceProgId -eq $progId) {
    # Nur den UserChoice-Unterschluessel selbst, NICHT den Elternzweig
    # FileExts\.md (astra-Fund D1): der enthaelt auf realen Hosts zusaetzlich
    # OpenWithList/OpenWithProgids/UserChoiceLatest, die install_local.ps1
    # nicht angelegt hat und die diesem Skript nicht gehoeren.
    $actions += "UserChoice-Unterschluessel entfernen: $userChoiceKey (Explorer erinnerte sich an $progId als gewaehlten Handler; Geschwisterzweige unter FileExts\.md bleiben unangetastet)"
} elseif ($userChoiceProgId) {
    $actions += "UEBERSPRUNGEN: UserChoice unter $fileExtsMd zeigt bereits auf '$userChoiceProgId' -- unveraendert gelassen"
}
if (Test-Path $shortcutPath) {
    $actions += "Startmenü-Verknuepfung entfernen: $shortcutPath"
}
if (Test-Path $installDir) {
    $actions += "Lokale Installation entfernen: $installDir"
}

if ($actions.Count -eq 0) {
    Write-Host "Nichts zu tun -- keine Spuren der lokalen Installation gefunden." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nFolgende Aenderungen werden vorgenommen:"
$actions | ForEach-Object { Write-Host "  - $_" }

if ($WhatIf) {
    Write-Host "`n-WhatIf: keine Aenderung vorgenommen, kein Backup angelegt." -ForegroundColor Yellow
    exit 0
}

if (-not $Force) {
    $confirm = Read-Host "`nFortfahren? (j/N)"
    if ($confirm -notin @("j", "J", "y", "Y")) {
        Write-Host "Abgebrochen." -ForegroundColor Yellow
        exit 0
    }
}

# --- 3. Registry-Sicherung -- eindeutiger Ordner je Lauf, JEDER Export ------
#     wird geprueft; schlaegt auch nur einer fehl, bricht das Skript VOR
#     jeder Loeschung ab (astra-Fund D2: ein gemockter Lauf mit 4 fehl-
#     geschlagenen Exporten fuehrte vorher trotzdem alle Loeschungen aus).
$runId = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $env:TEMP "CleanMarkdown-migration-backup\$runId"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

$keysToBackup = @(
    "HKCU\Software\Classes\$progId",
    "HKCU\Software\Classes\.md",
    "HKCU\Software\Classes\Applications\CleanMarkdown.exe",
    "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.md"
)
$backupFailed = $false
foreach ($key in $keysToBackup) {
    $psPath = "Registry::$key"
    if (-not (Test-Path $psPath)) { continue }
    $exportName = ($key -replace '[\\]', '_') + ".reg"
    $exportPath = Join-Path $backupDir $exportName
    & reg export $key $exportPath /y 2>&1 | Out-Null
    $exportOk = ($LASTEXITCODE -eq 0) -and (Test-Path $exportPath) -and ((Get-Item $exportPath).Length -gt 0)
    if (-not $exportOk) {
        Write-Host "  FEHLER: Backup fehlgeschlagen fuer $key (Exit $LASTEXITCODE, Datei $exportPath)" -ForegroundColor Red
        $backupFailed = $true
    }
}
if ($backupFailed) {
    Write-Host "`nABBRUCH: Mindestens eine Registry-Sicherung ist fehlgeschlagen -- KEINE Aenderung vorgenommen." -ForegroundColor Red
    Write-Host "Teilweise angelegte Sicherungen liegen (zur Fehlersuche) in: $backupDir"
    exit 1
}
Write-Host "Registry-Sicherung vollstaendig: $backupDir" -ForegroundColor Cyan

# --- 4. Rueckbau durchfuehren ------------------------------------------------
$incomplete = $false

if (Test-Path "$classesRoot\$progId") {
    Remove-Item -Path "$classesRoot\$progId" -Recurse -Force
}
if (Test-Path "$classesRoot\Applications\CleanMarkdown.exe") {
    Remove-Item -Path "$classesRoot\Applications\CleanMarkdown.exe" -Recurse -Force
}
if ($mdDefault -eq $progId) {
    Remove-ItemProperty -Path "$classesRoot\.md" -Name "(Default)" -ErrorAction SilentlyContinue
}
if (Test-Path "$classesRoot\.md\OpenWithProgids") {
    Remove-ItemProperty -Path "$classesRoot\.md\OpenWithProgids" -Name $progId -ErrorAction SilentlyContinue
}
if ($userChoiceProgId -eq $progId) {
    try {
        # Nur den Unterschluessel, siehe Begruendung in der Vorschau oben.
        Remove-Item -Path $userChoiceKey -Recurse -Force
    } catch {
        $incomplete = $true
        Write-Host "  HINWEIS: UserChoice-Unterschluessel ($userChoiceKey) konnte nicht geloescht werden (Windows schuetzt diesen Schluessel oft per ACL gegen programmatisches Loeschen): $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "  Der User muss die Zuordnung manuell neu setzen: Einstellungen > Apps > Standard-Apps > '.md' waehlen."
    }
}
if (Test-Path $shortcutPath) {
    Remove-Item -Path $shortcutPath -Force
}
if (Test-Path $installDir) {
    Remove-Item -Path $installDir -Recurse -Force
}

# --- 5. Shell-Icon-Cache aktualisieren --------------------------------------
$signature = @'
using System;
using System.Runtime.InteropServices;
public static class ShellNotify {
    [DllImport("shell32.dll")]
    public static extern void SHChangeNotify(uint wEventId, uint uFlags, IntPtr dwItem1, IntPtr dwItem2);
}
'@
Add-Type -TypeDefinition $signature | Out-Null
[ShellNotify]::SHChangeNotify(0x08000000, 0x0000, [IntPtr]::Zero, [IntPtr]::Zero)

if ($incomplete) {
    Write-Host "`nRueckbau ABGESCHLOSSEN MIT EINSCHRAENKUNG -- siehe Hinweis oben (manueller Folgeschritt noetig)." -ForegroundColor Yellow
} else {
    Write-Host "`nRueckbau abgeschlossen." -ForegroundColor Green
}
Write-Host "Registry-Sicherung liegt in: $backupDir"
Write-Host "Als NAECHSTES: Einstellungen > Apps > Standard-Apps > '.md' -> CleanMarkdown (Store) waehlen --"
Write-Host "dieses Skript entfernt nur die alte Zuordnung, es setzt keine neue."
Write-Host "Falls .md danach kein korrektes Icon zeigt: einmal abmelden/anmelden oder Explorer neu starten"
Write-Host "(taskkill /f /im explorer.exe && start explorer.exe), damit der Icon-Cache neu aufbaut."
