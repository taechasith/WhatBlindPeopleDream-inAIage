# Study 1 control-validity assessment

## Audit result

**Status:** `PARTIAL / PROTOTYPE ONLY`.

`CONTROL_MATCHING_AUDIT.csv` provides deterministic text statistics for the
non-human prototype scripts. DAI/HUM scripts are closely matched on nominal word
count (67--77), speech duration (28.7--33.0 seconds at 140 wpm), target-unit
inventory, common TTS route, neutral prompt, session envelope, and low agency.
They are not yet final AI/human outputs.

ANC matches pre-sleep audio route, approximate word count, speech duration,
session envelope, neutral reporting instructions, and low agency. It deliberately
lacks target-scene objects and spatial relations; it therefore controls generic
audio/narrative exposure but is not a spatial-content-matched comparator.

SAI is intentionally not text-matched to DAI: user questions, agency, interaction
duration, and delivered content differ. Its estimand is an interaction package,
not a pure wording/source effect.

## What passes prospectively

- Same nominal TTS route, rate target, volume policy, timing target, session
  envelope, and neutral reporting framing.
- DAI/HUM approximate nominal text length and planned delivery duration.
- Decoys remain a false-positive coding control rather than an exposure control.

## What remains required before exposure

- Final provider/model/TTS freeze and actual transcript/audio measurement.
- Independent content audit against visual source, marker inventory, unsupported
  claims, and target/decoy leakage.
- Final word/sentence/rate/voice/volume/lexical metrics; any material mismatch
  requires a documented prospective adjustment.
- Human validation of emotional salience, unusualness, memorability, cultural
  familiarity, and accessibility wording. These values are not invented here.
- Exact SAI interaction policy and transcript-level delivered-unit log.

## Interpretive rule

DAI/HUM can support a comparison of these specific frozen description packages;
ANC contextualizes generic pre-sleep audio exposure; neither establishes a
general AI-specific causal effect. See `STUDY1_ESTIMANDS.md`.
