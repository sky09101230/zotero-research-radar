param(
    [string]$WorkingDirectory = (Resolve-Path (Join-Path $PSScriptRoot "..\..")),
    [string]$ConfigDirectory = "config",
    [string]$Time = "08:00"
)

$action = New-ScheduledTaskAction -Execute "uv" -Argument "run radar recommend --config-dir `"$ConfigDirectory`" --format markdown --output reports\daily.md" -WorkingDirectory $WorkingDirectory
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
Register-ScheduledTask -TaskName "ZoteroResearchRadar" -Action $action -Trigger $trigger -Description "Generate a local Zotero research radar report." -Force
