# Study 1 preregistration draft

**Registration status:** draft only; do not publicly register before the ethics
sequence and final institutional requirements are confirmed.

## Title

When AI becomes a sensory channel: a preregistered study of AI-mediated
information and dream-report incorporation in blind and low-vision adults.

## Research questions and hypotheses

RQ1/H1, RQ2/H2, and RQ3/H3 are frozen in `STUDY1_DESIGN_FREEZE.md`. H1 is the
only primary confirmatory hypothesis. It compares explicitly delivered AI target
semantic units with matched false-source foils in eligible next-morning reports.
H2 and H3 are secondary; no direction is assumed for participant steering.

## Design and conditions

Within-participant four-session home design: DAI, SAI, HUM, and ANC. Sessions
are 6--8 days apart. A 4x4 Latin square balances condition order and scene-set
mapping. Same TTS voice, 12-minute session envelope, pre-sleep timing target,
and detailed fidelity logging apply. See `STUDY1_DESIGN_FREEZE.md` and
`STUDY1_CONTROL_AUDIT.md`.

## Sample size and stopping rule

The provisional target is 200 enrolled adults (50 Latin-square blocks), with
approximately 180 expected to complete under the 10% attrition planning
assumption. This follows conservative synthetic scenario planning, not Study 0
or pilot outcomes. Before recruitment, rerun the expanded R/lme4 simulation with
at least 1,000 repetitions and retain/increase—not outcome-tune—the target based
on that precollection check. There is no efficacy interim analysis. Stop/pause
rules are safety, integrity, and ethics-determination rules only.

## Population and exclusions

Planned inclusion/exclusion criteria are exactly those in `STUDY1_DESIGN_FREEZE.md`.
No one is excluded for lack of dream recall or lack of incorporation. Per-session
exclusions are wrong delivery/stimulus, target cue before free report,
unverifiable timing, unusable recording, or no sleep; all are retained in a
flow table with reasons.

## Outcomes and coding

Primary: unit-level binary incorporation (semantic/exact versus absent) for
delivered target units and matched foils in AI nights. Code `1` possible is not
primary-positive; code `9` is missing. First free report after the session is
primary. The complete manual, coder blinding, reliability plan, and adjudication
process are in `DREAM_INCORPORATION_CODEBOOK_v1.md` and `annotation/`.

Secondary/exploratory: exact-only, spatial, sensory transformation, emotion,
novel recombination; DAI-versus-SAI interaction; AI-versus-HUM/ANC contrasts;
reconstruction; ratings; onset/vision moderation only if estimable; and report
length/missingness sensitivity analyses.

## Analysis

Fit the frozen logistic mixed-effects model from `STUDY1_DESIGN_FREEZE.md`.
Report the primary target-versus-foil contrast averaged across AI conditions with
OR, model probability, 95% CI, and denominators. Secondary category tests use
Benjamini--Hochberg FDR control. Bootstrap participants for clustered CIs.
Missing reports are not imputed. Run exact-only, possible-inclusive,
protocol-deviation-removed, marker-familiarity, description-length, and
coder-disagreement sensitivity analyses.

## Confirmatory boundary and deviations

Only H1 and its stated primary model/contrast are confirmatory. Every other
analysis is labeled secondary/exploratory. Freeze AI system metadata, stimuli,
descriptions, randomization file, coding files, and code hashes before data
collection. Log any deviation before unblinding where possible; preserve raw
records and never silently change an outcome, denominator, or exclusion.
