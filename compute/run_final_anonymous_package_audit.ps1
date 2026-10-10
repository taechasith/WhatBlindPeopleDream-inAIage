<#
Run the post-results anonymous manuscript/poster audit in a new immutable
directory. This wrapper does not calculate results or generate scientific prose.
#>
[CmdletBinding()]
param(
    [string]$ResultsFreeze = "results/results_freeze/RESULTS_FREEZE.json",
    [string]$FactPacketDir = "paper/anonymous/generated",
    [string]$ClaimLedger = "paper/anonymous/CLAIM_TRACEABILITY.csv",
    [string]$ManuscriptDir = "paper/anonymous",
    [string]$ManuscriptPdf = "paper/anonymous/build/anonymous_review.pdf",
    [string]$PageAccounting = "paper/anonymous/PAGE_ACCOUNTING.json",
    [string]$FiguresDir = "figures/final_public_data_v1",
    [string]$PosterContent = "poster/anonymous/POSTER_CONTENT.json",
    [string]$PosterPdf = "poster/anonymous/build/a0_review/A0_anonymous_poster.pdf",
    [string]$ReferenceTraceability = "paper/anonymous/REFERENCE_TRACEABILITY.csv",
    [string]$DoiAudit = "refs/doi_audit.csv",
    [string]$IdentityPatterns = "private/anonymous_release_forbidden_patterns.txt",
    [string]$OutDir = "audits/final_anonymous_package_v1"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

& python code/32_audit_final_anonymous_package.py `
    --results-freeze $ResultsFreeze `
    --fact-packet-dir $FactPacketDir `
    --claim-ledger $ClaimLedger `
    --manuscript-dir $ManuscriptDir `
    --manuscript-pdf $ManuscriptPdf `
    --page-accounting $PageAccounting `
    --figures-dir $FiguresDir `
    --poster-content $PosterContent `
    --poster-pdf $PosterPdf `
    --reference-traceability $ReferenceTraceability `
    --doi-audit $DoiAudit `
    --identity-patterns $IdentityPatterns `
    --outdir $OutDir
if ($LASTEXITCODE -ne 0) {
    throw "FINAL_ANONYMOUS_PACKAGE_AUDIT_FAILED: inspect $OutDir\\FINAL_PUBLICATION_AUDIT.md and resolve all errors."
}
