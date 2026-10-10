<#
Start the two independent, fail-closed post-panel watchers with durable logs.

This supervisor is intentionally usable only before a blinded coded-data
freeze exists.  It never opens a condition map, model output, labels, or
result table.  The blinded watcher and the later post-freeze watcher remain
separate processes so that condition unblinding stays controlled by the
receipt-validated analysis script rather than this launcher.
#>
[CmdletBinding()]
param(
    [switch]$RestartExistingWatchers
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$codedFreeze = Join-Path $root 'results\coded_data_freeze\CODED_DATA_FREEZE.json'
$resultsFreeze = Join-Path $root 'results\results_freeze\RESULTS_FREEZE.json'
if ((Test-Path -LiteralPath $codedFreeze) -or (Test-Path -LiteralPath $resultsFreeze)) {
    throw 'SUPERVISOR_BLOCKED: a downstream freeze already exists; do not restart pre-unblinding watchers.'
}

$runnerNames = @('run_blinded_robustness_pipeline.ps1', 'run_post_freeze_analysis.ps1')
$existing = Get-CimInstance Win32_Process | Where-Object {
    $commandLine = $_.CommandLine
    $_.Name -ieq 'powershell.exe' -and $commandLine -and
    $commandLine -like "*$root*" -and
    ($runnerNames | Where-Object { $commandLine -like "*$_*" })
}
if ($existing) {
    if (-not $RestartExistingWatchers) {
        throw 'SUPERVISOR_BLOCKED: matching watchers already run; use -RestartExistingWatchers only before any freeze receipt exists.'
    }
    foreach ($process in $existing) {
        Stop-Process -Id $process.ProcessId -ErrorAction Stop
    }
    foreach ($process in $existing) {
        Wait-Process -Id $process.ProcessId -Timeout 30 -ErrorAction SilentlyContinue
    }
}

$logDir = Join-Path $root 'compute\runtime_logs'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$powerShell = (Get-Command powershell.exe -CommandType Application -ErrorAction Stop).Source

function Start-LoggedWatcher {
    param([Parameter(Mandatory = $true)][string]$ScriptName)
    $scriptPath = Join-Path $root ('compute\' + $ScriptName)
    if (-not (Test-Path -LiteralPath $scriptPath -PathType Leaf)) {
        throw "SUPERVISOR_BLOCKED: watcher script is missing: $scriptPath"
    }
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($ScriptName)
    $stdout = Join-Path $logDir ($stem + '_' + $stamp + '.stdout.log')
    $stderr = Join-Path $logDir ($stem + '_' + $stamp + '.stderr.log')
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
    $process = Start-Process -FilePath $powerShell -ArgumentList $arguments -WorkingDirectory $root `
        -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru
    return [pscustomobject]@{
        watcher = $ScriptName
        process_id = $process.Id
        stdout = $stdout
        stderr = $stderr
    }
}

$launched = @(
    Start-LoggedWatcher -ScriptName 'run_blinded_robustness_pipeline.ps1'
    Start-LoggedWatcher -ScriptName 'run_post_freeze_analysis.ps1'
)
$launched | ConvertTo-Json -Depth 3
