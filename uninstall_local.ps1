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
# nicht mehr, nicht weniger -- und NUR, wenn das Store-Paket bereits
# installiert ist (sonst bliebe der User ganz ohne .md-Handler zurueck).
#
# Nutzung:
#   .\uninstall_local.ps1              # fuehrt den Rueckbau aus (fragt vorher nach)
#   .\uninstall_local.ps1 -WhatIf      # zeigt nur, was getan wuerde
#   .\uninstall_local.ps1 -Force       # ohne Rueckfrage (fuer Automatisierung)
#
# Sicherheitsnetz: Vor jeder Aenderung werden die betroffenen Registry-Zweige
# per `reg export` gesichert (Pfad wird am Ende ausgegeben).

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

# --- 1. Voraussetzung: Store-Paket muss installiert sein -------------------
$storePkg = Get-AppxPackage -Name "Geiger.CleanMarkdown" -ErrorAction SilentlyContinue
if (-not $storePkg) {
    Write-Host "ABBRUCH: Kein Store-Paket 'Geiger.CleanMarkdown' installiert." -ForegroundColor Red
    Write-Host "Ohne Store-Paket wuerde dieser Rueckbau den User ganz ohne .md-Handler zuruecklassen."
    Write-Host "Zuerst CleanMarkdown aus dem Microsoft Store installieren/aktualisieren, dann erneut ausfuehren."
    exit 1
}
Write-Host "Store-Paket gefunden: $($storePkg.PackageFullName)" -ForegroundColor Green

# --- 2. Registry-Sicherung vor jeder Aenderung ------------------------------
$backupDir = Join-Path $env:TEMP "CleanMarkdown-migration-backup"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupFile = Join-Path $backupDir "registry-backup_$timestamp.reg"

$keysToBackup = @(
    "HKCU\Software\Classes\$progId",
    "HKCU\Software\Classes\.md",
    "HKCU\Software\Classes\Applications\CleanMarkdown.exe",
    "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.md"
)
if (-not $WhatIf) {
    foreach ($key in $keysToBackup) {
        $psPath = "Registry::$key"
        if (Test-Path $psPath) {
            $exportName = ($key -replace '[\\]', '_') + ".reg"
            & reg export $key (Join-Path $backupDir $exportName) /y 2>&1 | Out-Null
        }
    }
    Write-Host "Registry-Sicherung: $backupDir" -ForegroundColor Cyan
}

# --- 3. Was wird entfernt? (Uebersicht + WhatIf) ----------------------------
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
    $actions += "Default-Wert von $classesRoot\.md loeschen (zeigte auf $progId)"
} elseif ($mdDefault) {
    $actions += "UEBERSPRUNGEN: $classesRoot\.md zeigt bereits auf '$mdDefault' (nicht mehr $progId) -- unveraendert gelassen"
}
if (Test-Path "$classesRoot\.md\OpenWithProgids") {
    $prop = Get-ItemProperty -Path "$classesRoot\.md\OpenWithProgids" -Name $progId -ErrorAction SilentlyContinue
    if ($prop) { $actions += "OpenWithProgids-Eintrag '$progId' unter $classesRoot\.md\OpenWithProgids entfernen" }
}
if (Test-Path $fileExtsMd) {
    $userChoice = Get-ItemProperty -Path "$fileExtsMd\UserChoice" -Name "ProgId" -ErrorAction SilentlyContinue
    if ($userChoice -and $userChoice.ProgId -eq $progId) {
        $actions += "UserChoice-Zweig entfernen: $fileExtsMd (Explorer erinnerte sich an $progId als gewaehlten Handler)"
    } elseif ($userChoice) {
        $actions += "UEBERSPRUNGEN: UserChoice unter $fileExtsMd zeigt bereits auf '$($userChoice.ProgId)' -- unveraendert gelassen"
    }
}
if (Test-Path $shortcutPath) {
    $actions += "Startmenü-Verknuepfung entfernen: $shortcutPath"
}
if (Test-Path $exeTarget) {
    $actions += "Lokale Installation entfernen: $installDir"
}

if ($actions.Count -eq 0) {
    Write-Host "Nichts zu tun -- keine Spuren der lokalen Installation gefunden." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nFolgende Aenderungen werden vorgenommen:"
$actions | ForEach-Object { Write-Host "  - $_" }

if ($WhatIf) {
    Write-Host "`n-WhatIf: keine Aenderung vorgenommen." -ForegroundColor Yellow
    exit 0
}

if (-not $Force) {
    $confirm = Read-Host "`nFortfahren? (j/N)"
    if ($confirm -notin @("j", "J", "y", "Y")) {
        Write-Host "Abgebrochen." -ForegroundColor Yellow
        exit 0
    }
}

# --- 4. Rueckbau durchfuehren ------------------------------------------------
if (Test-Path "$classesRoot\$progId") {
    Remove-Item -Path "$classesRoot\$progId" -Recurse -Force
}
if (Test-Path "$classesRoot\Applications\CleanMarkdown.exe") {
    Remove-Item -Path "$classesRoot\Applications\CleanMarkdown.exe" -Recurse -Force
}
if ($mdDefault -eq $progId) {
    Set-Item -Path "$classesRoot\.md" -Value ""
}
if (Test-Path "$classesRoot\.md\OpenWithProgids") {
    Remove-ItemProperty -Path "$classesRoot\.md\OpenWithProgids" -Name $progId -ErrorAction SilentlyContinue
}
if (Test-Path $fileExtsMd) {
    $userChoice = Get-ItemProperty -Path "$fileExtsMd\UserChoice" -Name "ProgId" -ErrorAction SilentlyContinue
    if ($userChoice -and $userChoice.ProgId -eq $progId) {
        try {
            Remove-Item -Path $fileExtsMd -Recurse -Force
        } catch {
            Write-Host "  HINWEIS: UserChoice-Zweig ($fileExtsMd) konnte nicht geloescht werden (Windows schuetzt diesen Schluessel oft per ACL gegen programmatisches Loeschen): $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "  Der User kann die Zuordnung manuell neu setzen: Einstellungen > Apps > Standard-Apps > '.md' waehlen."
        }
    }
}
if (Test-Path $shortcutPath) {
    Remove-Item -Path $shortcutPath -Force
}
if (Test-Path $exeTarget) {
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

Write-Host "`nRueckbau abgeschlossen. Registry-Sicherung liegt in: $backupDir" -ForegroundColor Green
Write-Host "Falls .md danach kein korrektes Icon zeigt: einmal abmelden/anmelden oder Explorer neu starten"
Write-Host "(taskkill /f /im explorer.exe && start explorer.exe), damit der Icon-Cache neu aufbaut."
