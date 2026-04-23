$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$exeSource = Join-Path $projectRoot "dist\CleanMarkdown.exe"

if (-not (Test-Path $exeSource)) {
    throw "Build output not found: $exeSource"
}

$installDir = Join-Path $env:LOCALAPPDATA "Programs\CleanMarkdown"
$exeTarget = Join-Path $installDir "CleanMarkdown.exe"
$startMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$shortcutPath = Join-Path $startMenuDir "CleanMarkdown.lnk"
$progId = "CleanMarkdown.mdfile"
$friendlyName = "CleanMarkdown Markdown File"

New-Item -ItemType Directory -Force -Path $installDir | Out-Null
Copy-Item -LiteralPath $exeSource -Destination $exeTarget -Force

$classesRoot = "HKCU:\Software\Classes"
New-Item -Path "$classesRoot\$progId" -Force | Out-Null
Set-Item -Path "$classesRoot\$progId" -Value $friendlyName

New-Item -Path "$classesRoot\$progId\DefaultIcon" -Force | Out-Null
Set-Item -Path "$classesRoot\$progId\DefaultIcon" -Value "$exeTarget,0"

New-Item -Path "$classesRoot\$progId\shell\open\command" -Force | Out-Null
Set-Item -Path "$classesRoot\$progId\shell\open\command" -Value "`"$exeTarget`" `"%1`""

New-Item -Path "$classesRoot\.md" -Force | Out-Null
Set-Item -Path "$classesRoot\.md" -Value $progId

New-Item -Path "$classesRoot\.md\OpenWithProgids" -Force | Out-Null
New-ItemProperty -Path "$classesRoot\.md\OpenWithProgids" -Name $progId -PropertyType String -Value "" -Force | Out-Null

New-Item -Path "$classesRoot\Applications\CleanMarkdown.exe\shell\open\command" -Force | Out-Null
Set-Item -Path "$classesRoot\Applications\CleanMarkdown.exe\shell\open\command" -Value "`"$exeTarget`" `"%1`""

New-Item -Path "$classesRoot\Applications\CleanMarkdown.exe" -Force | Out-Null
Set-ItemProperty -Path "$classesRoot\Applications\CleanMarkdown.exe" -Name "FriendlyAppName" -Value "CleanMarkdown"

$wshShell = New-Object -ComObject WScript.Shell
$shortcut = $wshShell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exeTarget
$shortcut.WorkingDirectory = $installDir
$shortcut.IconLocation = "$exeTarget,0"
$shortcut.Save()

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

Write-Output $exeTarget
