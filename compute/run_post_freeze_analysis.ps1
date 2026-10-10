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
$analysisPython = (Get-Command python.exe -CommandType Application -ErrorAction Stop).Source
$freeze = Join-Path $root 'results\coded_data_freeze\CODED_DATA_FREEZE.json'
$mapping = Join-Path $root 'annotation_public\private\blinding_map_primary_v1.csv'
$panelDir = Join-Path $root 'annotation_public\private\synthetic_panel_v1'
$strength = Join-Path $root 'annotation_public\private\computational_robustness_v1\summary\construct_measurement_strength.csv'
$outdir = Join-Path $root 'results\post_freeze_analysis_v1'
$spaceOutdir = Join-Path $root 'results\representational_space_v1'
$resultsFreezeDir = Join-Path $root 'results\results_freeze'
$figureOutdir = Join-Path $root 'figures\final_public_data_v1'

if (-not (Test-Path -LiteralPath $analysisPython)) { throw 'Analysis Python is unavailable.' }

function Test-ReceiptStatus {
    param([string]$Path, [string]$ExpectedStatus)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    try {
        $receipt = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
        return $receipt.status -eq $ExpectedStatus
    } catch {
        return $false
    }
}

function Assert-EmptyOrReceipt {
    param([string]$Directory, [string]$Receipt, [string]$Status)
    if ((Test-Path -LiteralPath $Directory) -and -not (Test-ReceiptStatus -Path $Receipt -ExpectedStatus $Status)) {
        throw "Immutable stage directory exists without its expected valid receipt: $Directory"
    }
}
# A partial/invalid receipt must never authorize condition unblinding.  Wait
# for the exact completed blinded-freeze status rather than file existence.
while (-not (Test-ReceiptStatus -Path $freeze -ExpectedStatus 'CODED_DATA_FROZEN_PUBLIC_DATA_ONLY')) {
    Start-Sleep -Seconds 60
}

$analysisReceipt = Join-Path $outdir 'ANALYSIS_MANIFEST.json'
Assert-EmptyOrReceipt -Directory $outdir -Receipt $analysisReceipt -Status 'RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY'
if (-not (Test-ReceiptStatus -Path $analysisReceipt -ExpectedStatus 'RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY')) {
    & $analysisPython (Join-Path $root 'code\27_run_post_freeze_public_analysis.py') `
        --coded-data-freeze $freeze --mapping $mapping --panel-dir $panelDir `
        --construct-strength $strength --outdir $outdir
    if ($LASTEXITCODE -ne 0) { throw 'Post-freeze RQ2/RQ3/RQ5 analysis failed.' }
}

$spaceReceipt = Join-Path $spaceOutdir 'RQ4_MANIFEST.json'
Assert-EmptyOrReceipt -Directory $spaceOutdir -Receipt $spaceReceipt -Status 'RQ4_COMPLETE_DISTRIBUTIONAL_PUBLIC_DATA_ONLY'
if (-not (Test-ReceiptStatus -Path $spaceReceipt -ExpectedStatus 'RQ4_COMPLETE_DISTRIBUTIONAL_PUBLIC_DATA_ONLY')) {
    & $analysisPython (Join-Path $root 'code\28_run_representational_space_analysis.py') `
        --coded-data-freeze $freeze --post-freeze-analysis $outdir --outdir $spaceOutdir
    if ($LASTEXITCODE -ne 0) { throw 'Post-freeze RQ4 representational-space analysis failed.' }
}

$resultsReceipt = Join-Path $resultsFreezeDir 'RESULTS_FREEZE.json'
Assert-EmptyOrReceipt -Directory $resultsFreezeDir -Receipt $resultsReceipt -Status 'RESULTS_FROZEN_PUBLIC_DATA_ONLY'
if (-not (Test-ReceiptStatus -Path $resultsReceipt -ExpectedStatus 'RESULTS_FROZEN_PUBLIC_DATA_ONLY')) {
    & $analysisPython (Join-Path $root 'code\29_freeze_public_data_results.py') `
        --coded-data-freeze $freeze --post-freeze-analysis $outdir `
        --space-analysis $spaceOutdir --outdir $resultsFreezeDir
    if ($LASTEXITCODE -ne 0) { throw 'Public-data results freeze failed.' }
}

$figureManifest = Join-Path $figureOutdir 'FIGURE_MANIFEST.csv'
if ((Test-Path -LiteralPath $figureOutdir) -and -not (Test-Path -LiteralPath $figureManifest)) {
    throw "Immutable figure directory exists without a manifest: $figureOutdir"
}
if (-not (Test-Path -LiteralPath $figureManifest)) {
    & $analysisPython (Join-Path $root 'code\30_generate_public_data_figures.py') `
        --results-freeze (Join-Path $resultsFreezeDir 'RESULTS_FREEZE.json') `
        --post-freeze-analysis $outdir --space-analysis $spaceOutdir --outdir $figureOutdir
    if ($LASTEXITCODE -ne 0) { throw 'Data-driven figure generation failed.' }
}

Write-Output 'FIGURES_COMPLETE_READY_FOR_MANUSCRIPT_DRAFTING'
