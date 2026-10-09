<#!
Build the anonymous A0 poster only after results and figures have been frozen.
This wrapper deliberately has no defaults for the factual content file: a
claim-audited, ledger-backed file must be supplied after RESULTS_FREEZE.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ContentJson,
    [string]$ResultsFreeze = "results/results_freeze/RESULTS_FREEZE.json",
    [string]$FiguresDir = "figures/final_public_data_v1",
    [string]$OutDir = "poster/anonymous/build/a0_review"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path -LiteralPath $ResultsFreeze -PathType Leaf)) {
    throw "POSTER_GATE_FAILED: RESULTS_FREEZE is required before poster construction."
}
if (-not (Test-Path -LiteralPath $FiguresDir -PathType Container)) {
    throw "POSTER_GATE_FAILED: final accessible figures are required before poster construction."
}
if (-not (Test-Path -LiteralPath $ContentJson -PathType Leaf)) {
    throw "POSTER_GATE_FAILED: supply the post-results, claim-audited anonymous content JSON."
}

& python code/31_generate_anonymous_a0_poster.py `
    --results-freeze $ResultsFreeze `
    --figures-dir $FiguresDir `
    --content-json $ContentJson `
    --outdir $OutDir `
    --require-pdf
if ($LASTEXITCODE -ne 0) {
    throw "POSTER_GATE_FAILED: A0 poster renderer exited with code $LASTEXITCODE."
}
