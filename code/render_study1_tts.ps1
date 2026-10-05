<#!
Render local, pre-approved Study 1 static scripts using the same Windows SAPI
voice. This is a non-human preparation utility. It must not be run on a
participant transcript or on a candidate script that has not passed the recorded
grounding/ethics gates.

Example after all final script gates:
  .\code\render_study1_tts.ps1 -InputCsv private\final_static_scripts.csv -OutputDirectory private\study1_tts
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $InputCsv,
    [Parameter(Mandatory = $true)] [string] $OutputDirectory,
    [string] $VoiceName = 'Microsoft Zira Desktop',
    [ValidateRange(-10, 10)] [int] $Rate = 0,
    [ValidateRange(0, 100)] [int] $Volume = 100
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $InputCsv -PathType Leaf)) {
    throw "Input CSV not found: $InputCsv"
}
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$available = @($synth.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object { $_.VoiceInfo.Name })
if ($available -notcontains $VoiceName) {
    throw "Required local voice is unavailable: $VoiceName. Available: $($available -join '; ')"
}
$synth.SelectVoice($VoiceName)
$synth.Rate = $Rate
$synth.Volume = $Volume

function Get-Sha256([string] $Path) {
    (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

$rows = Import-Csv -LiteralPath $InputCsv
$required = @('data_status', 'stimulus_id', 'condition', 'script_text', 'script_status')
foreach ($field in $required) {
    if (-not ($rows | Get-Member -Name $field)) { throw "Input CSV missing required field: $field" }
}
$manifest = @()
foreach ($row in $rows) {
    if ($row.script_status -ne 'APPROVED_FOR_TTS_RENDER_AFTER_ETHICS') {
        throw "Refusing unapproved script $($row.stimulus_id)/$($row.condition): $($row.script_status)"
    }
    $safeName = "$($row.stimulus_id)_$($row.condition).wav"
    $destination = Join-Path $OutputDirectory $safeName
    $synth.SetOutputToWaveFile($destination)
    $synth.Speak($row.script_text)
    $synth.SetOutputToNull()
    $wave = Get-Item -LiteralPath $destination
    $manifest += [pscustomobject]@{
        data_status = 'NONHUMAN_RENDERED_STATIC_AUDIO_NOT_PARTICIPANT_DATA'
        stimulus_id = $row.stimulus_id
        condition = $row.condition
        source_script_status = $row.script_status
        voice = $VoiceName
        rate = $Rate
        volume = $Volume
        wav_file = $safeName
        wav_bytes = $wave.Length
        wav_sha256 = Get-Sha256 $destination
        script_sha256 = [System.BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash([System.Text.Encoding]::UTF8.GetBytes($row.script_text))).Replace('-', '').ToLowerInvariant()
    }
}
$manifest | Export-Csv -NoTypeInformation -Encoding utf8 -LiteralPath (Join-Path $OutputDirectory 'tts_manifest.csv')
$synth.Dispose()
Write-Output "Rendered $($manifest.Count) approved non-human static scripts with $VoiceName."
