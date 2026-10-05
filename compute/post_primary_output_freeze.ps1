param(
    [Parameter(Mandatory = $true)]
    [int]$InferencePid
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
$logDir = Join-Path $PSScriptRoot 'runtime_logs'
$stdout = Join-Path $logDir 'post_freeze_stdout.log'
$stderr = Join-Path $logDir 'post_freeze_stderr.log'

try {
    Wait-Process -Id $InferencePid -ErrorAction Stop
    & .\.env_vlm\Scripts\python.exe code\08_validate_public_intervention_outputs.py `
        --outputs data\model_outputs\validated\primary_model_outputs.csv `
        --model-manifest config\public_vlm_models.json `
        --report data\model_outputs\output_validation_report.json *>> $stdout
    if ($LASTEXITCODE -ne 0) { throw "Output-schema validation failed with exit code $LASTEXITCODE" }
    & .\.env_vlm\Scripts\python.exe code\12_freeze_primary_model_outputs.py *>> $stdout
    if ($LASTEXITCODE -ne 0) { throw "Output freeze failed with exit code $LASTEXITCODE" }
}
catch {
    $_ | Out-String | Add-Content -LiteralPath $stderr
    exit 1
}
