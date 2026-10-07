# Coding and validation gate

## Status

`PRIMARY_MODEL_OUTPUTS_FROZEN_INTERPRETATION_STILL_BLINDED`

The frozen primary run contains 3,000 valid outputs: the 1,000-item locked
VizWiz validation sample crossed with the three frozen prompt conditions. The
schema validator passed against the frozen model manifest. This gate contains
no condition-level outcome, contrast, or hypothesis interpretation.

## Required sequence

1. Provide the shuffled blinded packet to two independent human coders using
   `annotation_public/CODER_INSTRUCTIONS_v1.md` and the frozen template.
2. Preserve both completed coding files unchanged and calculate reliability
   before any discussion or adjudication.
3. Perform documented adjudication only after the pre-adjudication record is
   locked.
4. Conduct external validation as separate evidence streams:
   - VizWiz human captions/answers: item-level human-description reference;
     not a proxy for BLV preference.
   - released BLV preference evidence: construct validation only.
   - GuideDog human-verified guidance: domain-external accessibility reference;
     not pooled with VizWiz as one ground truth.
5. Freeze coded and validation datasets, then and only then unblind condition
   labels and run RQ2--RQ5.

## Blinding controls

The coding packet contains a shuffled neutral identifier, the BLV-originating
question, and the model output. It excludes model ID, condition, source-image
filename, original order, prompt text, and hypothesis direction. The mapping is
local-only and excluded from version control and review materials.

## Non-permissions

Automated lexical or model-assisted labels cannot be substituted for the
independent human coding required for confirmatory results. Synthetic labels
cannot be used. No RQ2--RQ5 result is estimable until the coded-data freeze.
