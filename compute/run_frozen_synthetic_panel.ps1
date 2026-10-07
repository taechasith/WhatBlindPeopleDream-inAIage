$ErrorActionPreference = 'Stop'

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $root '.env_vlm\Scripts\python.exe'
$runner = Join-Path $root 'code\15_run_synthetic_annotation_panel.py'
$config = Join-Path $root 'config\synthetic_annotation_panel_v1.json'
$prompt = Join-Path $root 'annotation_public\SYNTHETIC_PANEL_PROMPT_v1.md'
$packet = Join-Path $root 'annotation_public\private\blinded_packet_primary_v1.csv'
$outdir = Join-Path $root 'annotation_public\private\synthetic_panel_v1'

foreach ($judge in @('Phi_3.5_mini_2fe19245', 'Qwen2.5_1.5B_989aa798')) {
    & $python $runner --config $config --prompt $prompt --packet $packet --outdir $outdir --judge-id $judge --resume
    if ($LASTEXITCODE -ne 0) { throw "Synthetic panel judge failed: $judge" }
}
