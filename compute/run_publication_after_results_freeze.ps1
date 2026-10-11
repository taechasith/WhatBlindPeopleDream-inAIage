<#
Wait for the canonical frozen public-data results, then run the fail-closed
anonymous publication controller exactly once.

This worker deliberately does not access raw model outputs, synthetic labels,
the condition map, or condition-level tables.  It reads only the status field
of RESULTS_FREEZE while waiting.  The invoked controller performs its own
provenance checks before generating any paper or poster artifact.
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$resultsFreeze = Join-Path $root 'results\results_freeze\RESULTS_FREEZE.json'
$controller = Join-Path $root 'compute\run_post_results_publication_pipeline.ps1'

function Test-ReceiptStatus {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$ExpectedStatus)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    try {
        $receipt = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
        return $receipt.status -eq $ExpectedStatus
    } catch {
        return $false
    }
}

if (-not (Test-Path -LiteralPath $controller -PathType Leaf)) {
    throw "PUBLICATION_WATCHER_BLOCKED: controller is missing: $controller"
}
while (-not (Test-ReceiptStatus -Path $resultsFreeze -ExpectedStatus 'RESULTS_FROZEN_PUBLIC_DATA_ONLY')) {
    Start-Sleep -Seconds 60
}

& $controller
if ($LASTEXITCODE -ne 0) {
    throw "PUBLICATION_WATCHER_FAILED: post-results publication controller exited with code $LASTEXITCODE."
}
Write-Output 'PAPER_POSTER_PIPELINE_COMPLETE_PENDING_VISUAL_QA_AND_ETHICS_GATE'
