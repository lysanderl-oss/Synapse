# Install Synapse Weekly Harness Audit as Windows Scheduled Task
# ================================================================
# Per CLAUDE.md P0 rule + president 2026-04-27 demand
# 'no paper-only mechanisms' - weekly-audit must have real scheduling.
#
# Schedule: Sunday 23:00 Asia/Dubai = Sunday 19:00 UTC
#
# Usage (requires Administrator):
#   powershell.exe -ExecutionPolicy Bypass -File scripts\install-windows-scheduled-task.ps1
#
# Verify:
#   Get-ScheduledTask -TaskName SynapseWeeklyHarnessAudit | Get-ScheduledTaskInfo
#
# Uninstall:
#   Unregister-ScheduledTask -TaskName SynapseWeeklyHarnessAudit -Confirm:$false

$ErrorActionPreference = "Stop"

$taskName  = "SynapseWeeklyHarnessAudit"
$pythonExe = (Get-Command python -ErrorAction SilentlyContinue).Path
if (-not $pythonExe) {
    $pythonExe = (Get-Command python3 -ErrorAction SilentlyContinue).Path
}
if (-not $pythonExe) {
    Write-Error "Python executable not found in PATH. Install Python 3 first."
    exit 1
}

$repoRoot   = (Resolve-Path "$PSScriptRoot\..").Path
$scriptPath = Join-Path $repoRoot "agent-CEO\dispatch_weekly_audit.py"

if (-not (Test-Path $scriptPath)) {
    Write-Error "dispatch_weekly_audit.py not found at: $scriptPath"
    exit 1
}

Write-Host "Synapse Weekly Harness Audit - Task Scheduler Installer"
Write-Host "========================================================"
Write-Host "Task name : $taskName"
Write-Host "Python    : $pythonExe"
Write-Host "Script    : $scriptPath"
Write-Host "Work dir  : $repoRoot"
Write-Host ""

# Remove existing task (idempotent)
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Removing existing task..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Action: run python -X utf8 dispatch_weekly_audit.py
$argString = '-X utf8 "' + $scriptPath + '"'
$action = New-ScheduledTaskAction -Execute $pythonExe -Argument $argString -WorkingDirectory $repoRoot

# Trigger: Sunday 19:00 UTC = Sunday 23:00 Dubai (UTC+4)
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At "19:00"

# Settings: run if missed, no battery stop, 30min limit
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 30) -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 5)

# Register (current user, run only when logged in to avoid storing creds)
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Synapse Harness Engineering weekly audit. Runs Sunday 23:00 Dubai." | Out-Null

$info = Get-ScheduledTask -TaskName $taskName | Get-ScheduledTaskInfo
Write-Host ""
Write-Host "[OK] Task '$taskName' registered."
Write-Host "     Next run: $($info.NextRunTime)"
Write-Host ""
Write-Host "Manual test run:"
Write-Host ("  Start-ScheduledTask -TaskName " + $taskName)
