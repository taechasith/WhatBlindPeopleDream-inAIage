<#
Run the one authorized condition unblinding only after the blinded
computational coded-data freeze exists. This runner deliberately does no
condition lookup while waiting. Its child analysis script fail-closes on the
same gate and writes a new immutable results directory.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.env_vlm\Scripts\python.exe'
$freeze = Join-Path $root 'results\coded_data_freeze\CODED_DATA_FREEZE.json'
$mapping = Join-Path $root 'annotation_public\private\blinding_map_primary_v1.csv'
$panelDir = Join-Path $root 'annotation_public\private\synthetic_panel_v1'
$strength = Join-Path $root 'annotation_public\private\computational_robustness_v1\summary\construct_measurement_strength.csv'
$outdir = Join-Path $root 'results\post_freeze_analysis_v1'
$spaceOutdir = Join-Path $root 'results\representational_space_v1'
$resultsFreezeDir = Join-Path $root 'results\results_freeze'

if (-not (Test-Path -LiteralPath $python)) { throw 'Dedicated analysis Python is unavailable.' }
while (-not (Test-Path -LiteralPath $freeze)) {
    Start-Sleep -Seconds 60
}

if (-not (Test-Path -LiteralPath (Join-Path $outdir 'ANALYSIS_MANIFEST.json'))) {
    & $python (Join-Path $root 'code\27_run_post_freeze_public_analysis.py') `
        --coded-data-freeze $freeze --mapping $mapping --panel-dir $panelDir `
        --construct-strength $strength --outdir $outdir
    if ($LASTEXITCODE -ne 0) { throw 'Post-freeze RQ2/RQ3/RQ5 analysis failed.' }
}

if (-not (Test-Path -LiteralPath (Join-Path $spaceOutdir 'RQ4_MANIFEST.json'))) {
    & $python (Join-Path $root 'code\28_run_representational_space_analysis.py') `
        --coded-data-freeze $freeze --post-freeze-analysis $outdir --outdir $spaceOutdir
    if ($LASTEXITCODE -ne 0) { throw 'Post-freeze RQ4 representational-space analysis failed.' }
}

if (-not (Test-Path -LiteralPath (Join-Path $resultsFreezeDir 'RESULTS_FREEZE.json'))) {
    & $python (Join-Path $root 'code\29_freeze_public_data_results.py') `
        --coded-data-freeze $freeze --post-freeze-analysis $outdir `
        --space-analysis $spaceOutdir --outdir $resultsFreezeDir
    if ($LASTEXITCODE -ne 0) { throw 'Public-data results freeze failed.' }
}

Write-Output 'RESULTS_FROZEN_READY_FOR_FIGURES_AND_MANUSCRIPT'
