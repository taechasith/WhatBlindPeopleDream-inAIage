<#
Run the deterministic anonymous-publication pipeline only after canonical
RESULTS_FREEZE and final-figure receipts exist.

This controller does not open result tables, raw model outputs, condition
mappings, annotations, or rankings.  It inspects only receipt status/hash
bindings, then delegates to individually fail-closed generators.  Every
output directory is immutable: a valid existing receipt is reused, whereas an
existing partial or unknown directory stops the pipeline rather than being
overwritten.

The controller produces publication artifacts; it does not make a submission
decision.  Institutional ethics determination and live CHI-call checks remain
separate release gates.
#>
[CmdletBinding()]
param(
    [string]$ResultsFreeze = "results/results_freeze/RESULTS_FREEZE.json",
    [string]$FiguresDir = "figures/final_public_data_v1",
    [string]$FactPacketDir = "paper/anonymous/generated",
    [string]$ReferenceAuditDir = "paper/anonymous/reference_audit",
    [string]$RenderPlanDir = "paper/anonymous/render_plan",
    [string]$ManuscriptDir = "paper/anonymous/build/review_source_v1",
    [string]$PdfBuildDir = "paper/anonymous/build/pdf_review_v1",
    [string]$PosterContentDir = "poster/anonymous/content_plan",
    [string]$TraceabilityDir = "paper/anonymous/publication_trace",
    [string]$PosterDir = "poster/anonymous/build/a0_review",
    [string]$FinalAuditDir = "audits/final_anonymous_package_v1"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

function Resolve-RepoPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path $root $Path))
}

function Get-Receipt {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }
    try {
        return (Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json)
    } catch {
        return $null
    }
}

function Test-Receipt {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$ExpectedStatus,
        [string]$ResultsHashField = ''
    )
    $receipt = Get-Receipt -Path $Path
    if ($null -eq $receipt -or $receipt.status -ne $ExpectedStatus) {
        return $false
    }
    if ($ResultsHashField) {
        $property = $receipt.PSObject.Properties[$ResultsHashField]
        if ($null -eq $property -or [string]$property.Value -ne $script:resultsHash) {
            return $false
        }
    }
    return $true
}

function Assert-ExistingDirectoryIsValidOrAbsent {
    param(
        [Parameter(Mandatory = $true)][string]$Directory,
        [Parameter(Mandatory = $true)][string]$Receipt,
        [Parameter(Mandatory = $true)][string]$ExpectedStatus,
        [string]$ResultsHashField = ''
    )
    if (-not (Test-Path -LiteralPath $Directory)) {
        return $false
    }
    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) {
        throw "PUBLICATION_PIPELINE_FAILED: immutable output path is not a directory: $Directory"
    }
    if (-not (Test-Receipt -Path $Receipt -ExpectedStatus $ExpectedStatus -ResultsHashField $ResultsHashField)) {
        throw "PUBLICATION_PIPELINE_FAILED: immutable output directory exists without the expected receipt: $Directory"
    }
    return $true
}

function Invoke-PythonTool {
    param(
        [Parameter(Mandatory = $true)][string]$Script,
        [Parameter(Mandatory = $true)][string[]]$ToolArguments,
        [Parameter(Mandatory = $true)][string]$Label
    )
    & $script:analysisPython $Script @ToolArguments
    if ($LASTEXITCODE -ne 0) {
        throw "PUBLICATION_PIPELINE_FAILED: $Label exited with code $LASTEXITCODE."
    }
}

function Find-Executable {
    param([Parameter(Mandatory = $true)][string[]]$Names, [Parameter(Mandatory = $true)][string]$Label)
    foreach ($name in $Names) {
        $command = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            return $command.Source
        }
    }
    # MiKTeX's per-user installer does not always update PATH for already-open
    # PowerShell sessions.  This is a deterministic local fallback, not a
    # toolchain substitution: the same named executable is still required.
    $miktexBin = Join-Path $env:LOCALAPPDATA 'Programs\MiKTeX\miktex\bin\x64'
    foreach ($name in $Names) {
        $candidate = Join-Path $miktexBin $name
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }
    throw "PUBLICATION_PIPELINE_FAILED: required $Label executable is unavailable. No partial compile/build will be started."
}

function Invoke-LoggedExternal {
    param(
        [Parameter(Mandatory = $true)][string]$Executable,
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [Parameter(Mandatory = $true)][string]$Log,
        [Parameter(Mandatory = $true)][string]$Label
    )
    & $Executable @Arguments *> $Log
    if ($LASTEXITCODE -ne 0) {
        throw "PUBLICATION_PIPELINE_FAILED: $Label failed; inspect $Log."
    }
}

$analysisPython = (Get-Command python.exe -CommandType Application -ErrorAction Stop).Source
$resultsFreeze = Resolve-RepoPath $ResultsFreeze
$figuresDir = Resolve-RepoPath $FiguresDir
$factPacketDir = Resolve-RepoPath $FactPacketDir
$referenceAuditDir = Resolve-RepoPath $ReferenceAuditDir
$renderPlanDir = Resolve-RepoPath $RenderPlanDir
$manuscriptDir = Resolve-RepoPath $ManuscriptDir
$pdfBuildDir = Resolve-RepoPath $PdfBuildDir
$posterContentDir = Resolve-RepoPath $PosterContentDir
$traceabilityDir = Resolve-RepoPath $TraceabilityDir
$posterDir = Resolve-RepoPath $PosterDir
$finalAuditDir = Resolve-RepoPath $FinalAuditDir

$resultsReceipt = Get-Receipt -Path $resultsFreeze
if ($null -eq $resultsReceipt -or $resultsReceipt.status -ne 'RESULTS_FROZEN_PUBLIC_DATA_ONLY') {
    throw "PUBLICATION_PIPELINE_BLOCKED: canonical RESULTS_FREEZE receipt is missing or incomplete."
}
if ($resultsReceipt.new_human_data_collected -ne $false -or $resultsReceipt.condition_unblinded_once -ne $true) {
    throw "PUBLICATION_PIPELINE_BLOCKED: RESULTS_FREEZE does not attest to the public-data-only, one-time-unblinding design."
}
$script:resultsHash = (Get-FileHash -LiteralPath $resultsFreeze -Algorithm SHA256).Hash.ToLowerInvariant()

$figureManifest = Join-Path $figuresDir 'FIGURE_MANIFEST.csv'
if (-not (Test-Path -LiteralPath $figuresDir -PathType Container) -or -not (Test-Path -LiteralPath $figureManifest -PathType Leaf)) {
    throw "PUBLICATION_PIPELINE_BLOCKED: canonical final figures and FIGURE_MANIFEST.csv are required before publication rendering."
}

# 1. Immutable fact packet.
$factPacketReceipt = Join-Path $factPacketDir 'PAPER_FACT_PACKET_MANIFEST.json'
if (-not (Assert-ExistingDirectoryIsValidOrAbsent -Directory $factPacketDir -Receipt $factPacketReceipt -ExpectedStatus 'PAPER_FACT_PACKET_FROZEN_FROM_RESULTS_FREEZE' -ResultsHashField 'source_results_freeze_sha256')) {
    Invoke-PythonTool -Script (Join-Path $root 'code\31_build_paper_fact_packet.py') -ToolArguments @(
        '--results-freeze', $resultsFreeze, '--outdir', $factPacketDir
    ) -Label 'paper fact-packet construction'
}

# 2. Predeclared reference selection.  The canonical refs directory exists for
# source evidence, so inspect only its three immutable selection artifacts.
$refsDir = Join-Path $root 'refs'
$selection = Join-Path $refsDir 'reference_selection.json'
$selectionReceipt = Join-Path $refsDir 'reference_selection_manifest.json'
$selectionChecksums = Join-Path $refsDir 'reference_selection_checksums.csv'
$selectionAnyExists = (Test-Path -LiteralPath $selection) -or (Test-Path -LiteralPath $selectionReceipt) -or (Test-Path -LiteralPath $selectionChecksums)
if ($selectionAnyExists) {
    if (-not (Test-Receipt -Path $selectionReceipt -ExpectedStatus 'REFERENCE_SELECTION_FROZEN_ANONYMOUS' -ResultsHashField 'results_freeze_sha256') -or -not (Test-Path -LiteralPath $selection -PathType Leaf) -or -not (Test-Path -LiteralPath $selectionChecksums -PathType Leaf)) {
        throw "PUBLICATION_PIPELINE_FAILED: reference-selection artifacts are partial, invalid, or not bound to this RESULTS_FREEZE."
    }
} else {
    Invoke-PythonTool -Script (Join-Path $root 'code\35_build_reference_selection.py') -ToolArguments @(
        '--results-freeze', $resultsFreeze, '--outdir', $refsDir
    ) -Label 'reference-selection binding'
}

# 3. Immutable audited bibliography.
$referenceAuditReceipt = Join-Path $referenceAuditDir 'FINAL_REFERENCE_AUDIT.json'
if (-not (Assert-ExistingDirectoryIsValidOrAbsent -Directory $referenceAuditDir -Receipt $referenceAuditReceipt -ExpectedStatus 'REFERENCE_AUDIT_CLEAN_ANONYMOUS' -ResultsHashField 'results_freeze_sha256')) {
    Invoke-PythonTool -Script (Join-Path $root 'code\33_generate_audited_references.py') -ToolArguments @(
        '--results-freeze', $resultsFreeze, '--selection', $selection, '--outdir', $referenceAuditDir
    ) -Label 'audited bibliography generation'
}

# 4. Deterministic manuscript render plan.
$renderPlanReceipt = Join-Path $renderPlanDir 'MANUSCRIPT_RENDER_PLAN_MANIFEST.json'
if (-not (Assert-ExistingDirectoryIsValidOrAbsent -Directory $renderPlanDir -Receipt $renderPlanReceipt -ExpectedStatus 'ANONYMOUS_MANUSCRIPT_RENDER_PLAN_FROZEN_FROM_RESULTS_FREEZE' -ResultsHashField 'results_freeze_sha256')) {
    Invoke-PythonTool -Script (Join-Path $root 'code\33_build_anonymous_manuscript_render_plan.py') -ToolArguments @(
        '--results-freeze', $resultsFreeze, '--fact-packet-dir', $factPacketDir,
        '--figures-dir', $figuresDir, '--outdir', $renderPlanDir
    ) -Label 'manuscript render-plan generation'
}

# 5. Anonymous manuscript source renderer.
$manuscriptReceipt = Join-Path $manuscriptDir 'MANUSCRIPT_RENDER_MANIFEST.json'
if (-not (Assert-ExistingDirectoryIsValidOrAbsent -Directory $manuscriptDir -Receipt $manuscriptReceipt -ExpectedStatus 'ANONYMOUS_CHI_MANUSCRIPT_SOURCE_RENDERED_FROM_RESULTS_FREEZE' -ResultsHashField 'results_freeze_sha256')) {
    Invoke-PythonTool -Script (Join-Path $root 'code\32_render_anonymous_chi_manuscript.py') -ToolArguments @(
        '--results-freeze', $resultsFreeze, '--fact-packet-dir', $factPacketDir,
        '--figures-dir', $figuresDir, '--render-plan', (Join-Path $renderPlanDir 'manuscript_render_plan.json'),
        '--citation-audit', $referenceAuditReceipt, '--bibliography', (Join-Path $referenceAuditDir 'audited_references.bib'),
        '--outdir', $manuscriptDir
    ) -Label 'anonymous manuscript rendering'
}

# 6. Compile only with local, discoverable LaTeX tooling.  A missing compiler
# is a hard stop, not permission to silently deliver source-only material.
if (Test-Path -LiteralPath $pdfBuildDir) {
    throw "PUBLICATION_PIPELINE_FAILED: immutable PDF build directory already exists: $pdfBuildDir"
}
$pdflatex = Find-Executable -Names @('pdflatex.exe', 'pdflatex') -Label 'pdflatex'
$bibtex = Find-Executable -Names @('bibtex.exe', 'bibtex') -Label 'bibtex'
New-Item -ItemType Directory -Path $pdfBuildDir -ErrorAction Stop | Out-Null
$manuscriptPdf = Join-Path $pdfBuildDir 'main.pdf'
try {
    Push-Location $manuscriptDir
    $latexArgs = @('-interaction=nonstopmode', '-halt-on-error', '-file-line-error', "-output-directory=$pdfBuildDir", 'main.tex')
    Invoke-LoggedExternal -Executable $pdflatex -Arguments $latexArgs -Log (Join-Path $pdfBuildDir 'pdflatex_pass1.log') -Label 'LaTeX pass 1'
    $auxBase = Join-Path $pdfBuildDir 'main'
    if (-not (Test-Path -LiteralPath ($auxBase + '.aux') -PathType Leaf)) {
        throw "PUBLICATION_PIPELINE_FAILED: LaTeX pass 1 did not produce main.aux."
    }
    Invoke-LoggedExternal -Executable $bibtex -Arguments @($auxBase) -Log (Join-Path $pdfBuildDir 'bibtex.log') -Label 'BibTeX'
    Invoke-LoggedExternal -Executable $pdflatex -Arguments $latexArgs -Log (Join-Path $pdfBuildDir 'pdflatex_pass2.log') -Label 'LaTeX pass 2'
    Invoke-LoggedExternal -Executable $pdflatex -Arguments $latexArgs -Log (Join-Path $pdfBuildDir 'pdflatex_pass3.log') -Label 'LaTeX pass 3'
} finally {
    Pop-Location -ErrorAction SilentlyContinue
}
if (-not (Test-Path -LiteralPath $manuscriptPdf -PathType Leaf)) {
    throw "PUBLICATION_PIPELINE_FAILED: LaTeX did not produce the required manuscript PDF."
}

# 7. Deterministic poster-content plan.
$posterContentReceipt = Join-Path $posterContentDir 'POSTER_CONTENT_MANIFEST.json'
if (-not (Assert-ExistingDirectoryIsValidOrAbsent -Directory $posterContentDir -Receipt $posterContentReceipt -ExpectedStatus 'ANONYMOUS_A0_POSTER_CONTENT_FROZEN_FROM_RESULTS_FREEZE' -ResultsHashField 'results_freeze_sha256')) {
    Invoke-PythonTool -Script (Join-Path $root 'code\34_build_anonymous_poster_content.py') -ToolArguments @(
        '--results-freeze', $resultsFreeze, '--fact-packet-dir', $factPacketDir,
        '--figures-dir', $figuresDir, '--outdir', $posterContentDir
    ) -Label 'poster-content plan generation'
}
$posterContent = Join-Path $posterContentDir 'POSTER_CONTENT.json'

# 8. Post-render numeric traceability and conservative page accounting.  This
# is generated from source/receipt/PDF artifacts, never from a manual ledger.
$traceReceipt = Join-Path $traceabilityDir 'PUBLICATION_TRACEABILITY_MANIFEST.json'
if (-not (Assert-ExistingDirectoryIsValidOrAbsent -Directory $traceabilityDir -Receipt $traceReceipt -ExpectedStatus 'PUBLICATION_TRACEABILITY_FROZEN_FROM_RENDERED_ARTIFACTS' -ResultsHashField 'results_freeze_sha256')) {
    Invoke-PythonTool -Script (Join-Path $root 'code\36_build_publication_traceability.py') -ToolArguments @(
        '--results-freeze', $resultsFreeze, '--fact-packet-dir', $factPacketDir,
        '--manuscript-dir', $manuscriptDir, '--manuscript-pdf', $manuscriptPdf,
        '--poster-content', $posterContent, '--outdir', $traceabilityDir
    ) -Label 'post-render traceability construction'
}

# 9. Existing A0 renderer.  The renderer itself selects its audited local
# Inkscape-or-Edge PDF route before writing the final receipt, then performs
# anonymous metadata and A0-geometry verification.
if (Test-Path -LiteralPath $posterDir) {
    $posterReceipt = Join-Path $posterDir 'POSTER_MANIFEST.json'
    if (-not (Test-Receipt -Path $posterReceipt -ExpectedStatus 'ANONYMOUS_A0_POSTER_COMPLETE' -ResultsHashField 'results_freeze_sha256')) {
        throw "PUBLICATION_PIPELINE_FAILED: immutable poster directory exists without a valid completed receipt: $posterDir"
    }
} else {
    Invoke-PythonTool -Script (Join-Path $root 'code\31_generate_anonymous_a0_poster.py') -ToolArguments @(
        '--results-freeze', $resultsFreeze, '--figures-dir', $figuresDir,
        '--content-json', $posterContent, '--outdir', $posterDir, '--require-pdf'
    ) -Label 'anonymous A0 poster rendering'
}
$posterPdf = Join-Path $posterDir 'A0_anonymous_poster.pdf'
if (-not (Test-Path -LiteralPath $posterPdf -PathType Leaf)) {
    throw "PUBLICATION_PIPELINE_FAILED: completed poster receipt lacks A0_anonymous_poster.pdf."
}

# 10. Terminal audit.  It is intentionally new-on-each-run: a prior failed
# audit must not be silently reused as an apparently current package audit.
if (Test-Path -LiteralPath $finalAuditDir) {
    throw "PUBLICATION_PIPELINE_FAILED: final audit directory already exists; preserve it and choose a new immutable audit path after remediation."
}
Invoke-PythonTool -Script (Join-Path $root 'code\32_audit_final_anonymous_package.py') -ToolArguments @(
    '--results-freeze', $resultsFreeze,
    '--fact-packet-dir', $factPacketDir,
    '--traceability-manifest', $traceReceipt,
    '--claim-ledger', (Join-Path $traceabilityDir 'CLAIM_TRACEABILITY.csv'),
    '--manuscript-dir', $manuscriptDir,
    '--manuscript-pdf', $manuscriptPdf,
    '--page-accounting', (Join-Path $traceabilityDir 'PAGE_ACCOUNTING.json'),
    '--figures-dir', $figuresDir,
    '--poster-content', $posterContent,
    '--poster-pdf', $posterPdf,
    '--reference-traceability', (Join-Path $referenceAuditDir 'REFERENCE_TRACEABILITY.csv'),
    '--doi-audit', (Join-Path $refsDir 'doi_audit.csv'),
    '--identity-patterns', (Join-Path $root 'private\anonymous_release_forbidden_patterns.txt'),
    '--outdir', $finalAuditDir
) -Label 'final anonymous package audit'

$finalReceipt = Join-Path $finalAuditDir 'FINAL_PUBLICATION_AUDIT.json'
if (-not (Test-Receipt -Path $finalReceipt -ExpectedStatus 'FINAL_PUBLICATION_AUDIT_PASS')) {
    throw "PUBLICATION_PIPELINE_FAILED: final audit did not produce a clean pass receipt."
}

Write-Output 'ANONYMOUS_PUBLICATION_ARTIFACTS_AUDITED'
