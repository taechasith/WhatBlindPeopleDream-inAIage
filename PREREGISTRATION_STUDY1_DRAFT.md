# Study 1 preregistration draft -- v2-aligned

**Protocol version:** BD-AI-CHI27-Study1-v2.0
**Registration status:** draft only. Ethics status is NOT_SUBMITTED; do not
publicly register, recruit, consent, expose, or collect data until the
institutional sequence and final implementation gates are documented.

## Title

When AI becomes a sensory channel: a preregistered study of AI-mediated
information and dream-report incorporation in blind and low-vision adults.

## Research questions and hypotheses

**RQ1 / H1 (primary, confirmatory).** In DAI and SAI sessions, are
preregistered semantic units explicitly delivered about the target scene more
likely than matched, non-delivered decoy units to occur in the first eligible
subsequent free dream report? The primary claim is limited to target-specific
reported incorporation after controlled AI-mediated information. It is not an
AI-versus-human effect, a general language effect, a claim that AI caused a
dream, or a neural/cognitive-reorganization claim.

**RQ2 / H2 (secondary).** Does the target-minus-decoy incorporation contrast
differ between default-AI (DAI) and participant-steered-AI (SAI) sessions?
This is a comparison of information-interaction packages; no direction is
preregistered, and it does not isolate agency, wording, duration, or question
count.

**RQ3 / H3 (secondary).** Do the prespecified DAI-versus-HUM description-package
contrast and the ANC contextual comparison differ in their reported
incorporation profiles? A delayed post-report reconstruction task may be
included only if ethics-approved and implemented after the first free dream
report. There is no immediate or pre-sleep reconstruction outcome.

## Design and conditions

This is a randomized, within-participant, four-session home crossover study.
Sessions are scheduled 6--8 days apart. Every participant is assigned one of
each condition:

| Code | Condition | Pre-sleep delivery |
|---|---|---|
| DAI | Default AI | Frozen default AI scene description through the common TTS route. |
| SAI | Participant-steered AI | Frozen-system, participant-steered AI interaction within the fixed session envelope. |
| HUM | Human reference description | Matched human-authored scene description through the common TTS route. |
| ANC | Active narrative control | Matched neutral, non-scene audio narrative through the common TTS route. |

All sessions use a 12-minute envelope, common playback controls, neutral study
framing, a pre-sleep timing target, and the same first-morning neutral free-report
prompt. Final AI, TTS, transcript, and content-audit metadata remain a required
pre-exposure freeze in `AI_EXPOSURE_PROTOCOL.md` and `MODEL_PROVENANCE.md`.

The allocation design uses four-condition Williams sequences crossed with four
stimulus sequences. Its current balanced configuration has **208 anonymous
allocation slots** (13 blocks of 16 slots). The master allocation is not a
participant roster and must remain inaccessible to dream coders. It will be
generated, validated, and locked only after the final power/implementation gate.

## Sample size and stopping rule

The 208-slot balanced allocation is a pre-collection design configuration, not
an enrollment authorization or an effect-derived final sample-size claim. The
final recruitment target must be locked before registration through the expanded,
reproducible simulation of the final primary model with at least 1,000
repetitions, explicit attrition/missing-report scenarios, and Monte Carlo
uncertainty. Study 0 metrics will not be used as effect-size inputs.

There is no efficacy stopping rule and no interim hypothesis testing. New
sessions pause for an unanticipated problem, serious distress, material
accessibility failure, integrity concern, or an ethics-body instruction. A
participant may stop or withdraw at any time; handling of previously supplied
records follows the approved consent and applicable law.

## Population, eligibility, and session exclusions

Planned participants are adults who self-identify as blind or low-vision, can
provide informed consent, can use the approved accessible materials independently
or with a chosen accommodation, and are willing to complete up to four home
sessions. Blindness onset, residual vision, and diagnostic labels are never
inferred or used as automatic eligibility proxies.

Planned pre-enrollment exclusions are inability to provide informed consent,
participation in a conflicting sleep intervention, or an ethics-approved safety
screening determination that sleep/dream-focused participation would pose an
unacceptable risk. The approved language, screening route, and safety criteria
must be inserted before registration and recruitment.

No participant is excluded for no dream recall, a short report, or no marker
incorporation. A session is excluded from the primary analysis only for a wrong
stimulus/delivery, target cue before the free report, unrecoverable delivery
failure, unverifiable timing, unusable record, or no participant-confirmed sleep.
Every excluded or missing session remains in the flow record with its reason.

## Primary outcome and coding

The one primary confirmatory outcome is the unit-level, binary,
target-specific dream-incorporation indicator defined in
`PRIMARY_OUTCOME_SPECIFICATION.md`.

- Unit: participant x session/night x semantic unit.
- Primary-positive: independent/adjudicated code 2 (semantic) or 3 (exact).
- Primary-negative: code 0 (absent).
- Possible/ambiguous code 1 is excluded from the primary binary outcome and
  retained for a prespecified sensitivity analysis.
- Code 9 (undecidable), no dream recall, no report, no sleep, and an ineligible
  report are missing rather than zero incorporation.
- The primary report is the first participant-initiated free report after the
  first main awakening, before target-specific prompts, under the timing and
  eligibility rules in `DREAM_COLLECTION_PROTOCOL.md` and
  `PRIMARY_OUTCOME_SPECIFICATION.md`.

At least 20% of eligible reports, selected by the data steward, will receive
independent double human coding before adjudication. Coders are blind to
condition, participant, sequence, stimulus, target/decoy truth, and hypothesis
direction. No LLM is a ground-truth coder.

## Secondary and exploratory outcomes

Secondary analyses include the DAI-by-SAI target-status interaction;
DAI-versus-HUM package contrast; ANC contextual contrast; exact-only coding;
spatial relation, sensory-transformation, emotional-incorporation, and
novel-recombination flags; delivery fidelity; and post-report outcomes only if
they are ethics-approved and frozen before data collection. Exploratory analyses
may include onset/vision descriptions only when estimable, report length,
marker familiarity, carryover flags, and missingness patterns. No secondary or
exploratory result will be written as neural reorganization or enduring cognitive
change.

## Analysis and multiplicity

The primary model is the v2 logistic mixed-effects model for DAI/SAI unit rows:

`incorporated ~ target_status + condition + period + order + stimulus_block + (1 | participant)`

Stimulus is handled as a fixed effect because there are four source stimuli. A
random-stimulus formulation is sensitivity-only if estimable and will not replace
the primary model. The only primary confirmatory contrast is target versus decoy
averaged over DAI and SAI. It will report an odds ratio, model-based probability
difference, 95% confidence interval, p value, unit/report/participant
denominators, and a participant-cluster bootstrap confidence interval. The
target-status-by-condition interaction is secondary.

No post-randomization delivery measure (for example, word count, duration, or
SAI question count) is adjusted for in the primary causal model because it may
be part of the intervention package. These measures are manipulation checks and
are used only in explicitly labelled sensitivity/descriptive analyses. Semantic-
unit dependence handling is participant-cluster bootstrap plus a report-level
robustness aggregation defined before registration. No multiplicity adjustment
applies to the one primary contrast. Benjamini--Hochberg FDR control will be
applied separately to the final, explicitly listed families of secondary
category tests. Missing incorporation outcomes are not imputed.

Prespecified sensitivity analyses are exact-only, possible-inclusive,
protocol-deviation-removed, participant leave-one-out, stimulus leave-one-out,
first-session-only, carryover-flagged-report exclusion, marker-familiarity,
description/delivery-length, coder-disagreement, and missingness analyses where
estimable.

## Confirmatory boundary and deviations

Only H1 and its stated primary contrast are confirmatory. Study 0 is
exploratory/hypothesis-generating and cannot validate this study or set its
effect size. Before any participant activity, freeze the AI/TTS system and
outputs, final stimuli and licenses, allocation file, coding packets, code hashes,
power analysis, and this preregistration version. Log every deviation before
unblinding where possible; preserve raw records and never silently change an
outcome, denominator, exclusion, or contrast.
