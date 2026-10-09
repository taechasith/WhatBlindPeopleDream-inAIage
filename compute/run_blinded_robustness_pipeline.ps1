<#
Run the post-panel computational robustness workflow without condition
unblinding. This watcher consumes only protected blinded artifacts and invokes
scripts that reject condition fields/maps. It never runs RQ2--RQ5.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root '.env_vlm\Scripts\python.exe'
$config = Join-Path $root 'config\synthetic_annotation_panel_v1.json'
$prompt = Join-Path $root 'annotation_public\SYNTHETIC_PANEL_PROMPT_v1.md'
$packet = Join-Path $root 'annotation_public\private\blinded_packet_primary_v1.csv'
$panelDir = Join-Path $root 'annotation_public\private\synthetic_panel_v1'
$baselineFreeze = Join-Path $panelDir 'freeze'
$robustRoot = Join-Path $root 'annotation_public\private\computational_robustness_v1'
$robustConfig = Join-Path $root 'config\computational_measurement_robustness_v1.json'
$paraphrasePrompt = Join-Path $root 'annotation_public\SYNTHETIC_PANEL_PROMPT_PARAPHRASE_v1.md'
$subsets = Join-Path $robustRoot 'subsets'
$paraphraseDir = Join-Path $robustRoot 'prompt_paraphrase'
$rerunDir = Join-Path $robustRoot 'exact_rerun'
$auditDir = Join-Path $robustRoot 'audit'
$anchorDir = Join-Path $robustRoot 'rule_anchors'
$summaryDir = Join-Path $robustRoot 'summary'
$calibration = Join-Path $root 'results\public_human_calibration_matrix.csv'
$codedFreezeDir = Join-Path $root 'results\coded_data_freeze'

if (-not (Test-Path -LiteralPath $python)) { throw 'Dedicated CUDA inference Python is unavailable.' }
if (-not (Test-Path -LiteralPath $packet)) { throw 'Frozen blinded packet is unavailable.' }

$panel = Get-Content -LiteralPath $config -Raw | ConvertFrom-Json
$expectedItems = 3000
$expectedLabels = $expectedItems * @($panel.constructs).Count

function Test-JudgeComplete {
    param([string]$JudgeId)
    $labels = Join-Path $panelDir ($JudgeId + '_labels.csv')
    $raw = Join-Path $panelDir ($JudgeId + '_raw.jsonl')
    if (-not ((Test-Path -LiteralPath $labels) -and (Test-Path -LiteralPath $raw))) { return $false }
    $labelLines = (Get-Content -LiteralPath $labels | Measure-Object -Line).Lines
    $rawLines = (Get-Content -LiteralPath $raw | Measure-Object -Line).Lines
    return $labelLines -eq ($expectedLabels + 1) -and $rawLines -eq $expectedItems
}

while (-not (@($panel.judges | Where-Object { -not (Test-JudgeComplete $_.judge_id) }).Count -eq 0)) {
    Start-Sleep -Seconds 60
}

if (-not (Test-Path -LiteralPath (Join-Path $baselineFreeze 'SYNTHETIC_PANEL_OUTPUT_FREEZE.json'))) {
    & $python (Join-Path $root 'code\16_freeze_synthetic_panel_outputs.py') `
        --config $config --prompt $prompt --packet $packet --panel-dir $panelDir --outdir $baselineFreeze
    if ($LASTEXITCODE -ne 0) { throw 'Baseline synthetic-panel freeze failed.' }
}

$freezeReceipt = Join-Path $baselineFreeze 'SYNTHETIC_PANEL_OUTPUT_FREEZE.json'
if (-not (Test-Path -LiteralPath (Join-Path $subsets 'COMPUTATIONAL_MEASUREMENT_SUBSET_MANIFEST_v1.json'))) {
    & $python (Join-Path $root 'code\21_build_measurement_robustness_subsets.py') `
        --config $robustConfig --packet $packet --baseline-freeze $freezeReceipt --outdir $subsets
    if ($LASTEXITCODE -ne 0) { throw 'Blinded robustness subset build failed.' }
}

$subsetManifest = Join-Path $subsets 'COMPUTATIONAL_MEASUREMENT_SUBSET_MANIFEST_v1.json'
$paraPacket = Join-Path $subsets 'prompt_paraphrase_subset_v1.csv'
$rerunPacket = Join-Path $subsets 'exact_rerun_subset_v1.csv'

function Invoke-FrozenJudgeSet {
    param([string]$PacketPath, [string]$PromptPath, [string]$OutputDir)
    foreach ($judge in $panel.judges) {
        & $python (Join-Path $root 'code\15_run_synthetic_annotation_panel.py') `
            --config $config --prompt $PromptPath --packet $PacketPath --outdir $OutputDir --judge-id $judge.judge_id --resume
        if ($LASTEXITCODE -ne 0) { throw "Frozen judge run failed: $($judge.judge_id)" }
    }
}

Invoke-FrozenJudgeSet -PacketPath $paraPacket -PromptPath $paraphrasePrompt -OutputDir $paraphraseDir
Invoke-FrozenJudgeSet -PacketPath $rerunPacket -PromptPath $prompt -OutputDir $rerunDir

if (-not (Test-Path -LiteralPath (Join-Path $auditDir 'AUDIT_MANIFEST.json'))) {
    & $python (Join-Path $root 'code\22_audit_synthetic_measurements.py') `
        --config $robustConfig --subset-manifest $subsetManifest --baseline-freeze $freezeReceipt `
        --baseline-packet $packet --baseline-labels-dir $panelDir `
        --prompt-paraphrase-packet $paraPacket --prompt-paraphrase-labels-dir $paraphraseDir `
        --exact-rerun-packet $rerunPacket --exact-rerun-labels-dir $rerunDir --outdir $auditDir
    if ($LASTEXITCODE -ne 0) { throw 'Blinded measurement audit failed.' }
}

if (-not (Test-Path -LiteralPath (Join-Path $anchorDir 'RULE_ANCHOR_MANIFEST.json'))) {
    & $python (Join-Path $root 'code\23_apply_computational_rule_anchors.py') `
        --config $robustConfig --subset-manifest $subsetManifest --measurement-audit-dir $auditDir --outdir $anchorDir
    if ($LASTEXITCODE -ne 0) { throw 'Blinded rule-anchor audit failed.' }
}

if (-not (Test-Path -LiteralPath (Join-Path $summaryDir 'CONSTRUCT_STRENGTH_MANIFEST.json'))) {
    & $python (Join-Path $root 'code\24_summarize_blinded_measurement_robustness.py') `
        --config $robustConfig --subset-manifest $subsetManifest --measurement-audit-dir $auditDir `
        --rule-anchor-dir $anchorDir --calibration-receipt $calibration --outdir $summaryDir
    if ($LASTEXITCODE -ne 0) { throw 'Blinded construct-strength summary failed.' }
}

if (-not (Test-Path -LiteralPath (Join-Path $codedFreezeDir 'CODED_DATA_FREEZE.json'))) {
    & $python (Join-Path $root 'code\26_freeze_coded_data_public_only.py') `
        --panel-freeze $freezeReceipt --subset-manifest $subsetManifest `
        --measurement-audit-dir $auditDir --rule-anchor-dir $anchorDir `
        --construct-strength-dir $summaryDir --calibration-receipt $calibration `
        --outdir $codedFreezeDir
    if ($LASTEXITCODE -ne 0) { throw 'Public-data coded-data freeze failed.' }
}

Write-Output 'CODED_DATA_FREEZE_READY_FOR_PRESPECIFIED_UNBLINDING'
