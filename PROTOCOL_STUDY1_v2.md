# Study 1 protocol v2.0: controlled AI-mediated dream incorporation

**Protocol identifier:** BD-AI-CHI27-Study1-v2.0  
**Date frozen:** 2026-10-05  
**Supersedes for prospective implementation:** v1.0 only; v1.0 remains an
immutable historical record.  
**Status:** pre-ethics, non-deployed. No human activity is authorized.

## Why v2.0 exists

V1.0's false-source-only control could establish a coding baseline but could not
balance pre-sleep audio exposure, semantic content, duration, or expectancy. V2.0
formalizes the pre-outcome active-control amendment and removes an explicit
pre-sleep reconstruction task that would rehearse targets.

## Aim and causal boundary

The primary question is whether semantic units explicitly delivered through
AI-mediated pre-sleep scene information are more likely than matched,
non-delivered decoy units to appear in eligible subsequent free dream reports.
The study tests reported incorporation, not neural change, enduring cognitive
change, or a general effect of AI on dreams.

## Design

Randomized within-participant crossover with four home sessions 6--8 days apart:

| Condition | Delivery |
|---|---|
| DAI | Frozen default AI scene description through the common TTS route. |
| SAI | Frozen-system participant-steered AI interaction within a fixed session envelope. |
| HUM | Matched human-authored reference scene description through the common TTS route. |
| ANC | Matched neutral, non-scene audio narrative through the common TTS route. |

All sessions use a 12-minute envelope and identical neutral study framing,
pre-sleep timing target, playback controls, and first-morning free-report prompt.
DAI/SAI target-versus-decoy scoring is the primary analysis. DAI-versus-SAI,
DAI-versus-HUM, and ANC contextual contrasts are secondary; their package-level
confounds are stated in `STUDY1_ESTIMANDS.md`.

## Population

Adults who self-identify as blind or low-vision, subject to the approved
accessibility, consent, and safety procedure. Onset/diagnosis is never inferred
or used as an automatic exclusion. The final recruitment, compensation,
language, and safety criteria require institutional review.

## Primary outcome

The unit-level target-specific dream-incorporation indicator is frozen in
`PRIMARY_OUTCOME_SPECIFICATION.md`. It is a blinded binary indicator derived
from exact/semantic coding of delivered target versus matched decoy units in the
first eligible post-session free dream report. No-dream/no-recall is missing,
not absent incorporation.

## Level 2 boundary

No explicit target reconstruction task occurs between exposure and sleep. A
delayed post-report reconstruction task, if retained after ethics review, is
secondary and cannot be called immediate representation. See
`LEVEL2_MEASUREMENT_VALIDITY.md`.

## Randomization, washout, and analyses

Use a pre-generated concealed balanced allocation with coder separation. Session
spacing, deviations, and carryover sensitivity are set in
`WASHOUT_RATIONALE.md`. The primary model uses a participant-random-intercept
logistic model with target status, condition, period/order, fixed stimulus
block, and a participant random intercept. The target-by-condition interaction
and models involving post-randomization delivery measures are secondary. The
exact model, multiplicity, and sensitivity suite are locked in the
preregistration before human data exist.

## Gates

Before human activity: final AI/TTS system/output freeze, licensed-final
stimuli, expanded power run, institutional ethics determination/approval,
approved accessible materials, and preregistration consistent with local
sequencing. Nothing in this protocol authorizes recruitment or data collection.
