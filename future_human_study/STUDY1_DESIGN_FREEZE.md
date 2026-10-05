# Study 1 design freeze v1.1 (superseded for implementation)

**Frozen:** 2026-10-05. This is a prospective design only. It authorizes no
recruitment, contact, screening, consent, exposure, or data collection.

> **Historical record only.** This v1.1 document is retained to preserve the
> decision trail. It must not be used for recruitment, ethics submission,
> preregistration, exposure, or analysis. The governing prospective documents
> are `PROTOCOL_STUDY1_v2.md`, `STUDY1_ESTIMANDS.md`, and
> `PRIMARY_OUTCOME_SPECIFICATION.md`. In particular, the v2 primary model has
> no target-status-by-condition interaction or post-randomization delivery
> covariate; those are secondary/sensitivity analyses. The v1.1 200-slot
> planning figure is superseded by the documented 208-slot simulation.

## Confirmatory question and hypothesis

**Primary hypothesis (H1).** In AI-exposure nights, preregistered semantic units
explicitly delivered about the target scene will be more likely to occur in the
next eligible free dream report than matched, non-delivered false-source foil
units. This is a source-specific incorporation test, not a claim that every
participant dreams the material.

**H2 (secondary).** Target-unit incorporation will differ between default-AI and
participant-steered-AI sessions. Direction is not preregistered; steering can
increase, decrease, or redistribute incorporated content.

**H3 (secondary).** Immediate semantic/spatial reconstruction, agency,
understanding, and uncertainty-calibration ratings will differ across output
source/interaction conditions. These are immediate representation measures, not
neural measures.

Long-term neural reorganization is explicitly outside scope and is neither
measured nor inferred.

## Sessions, conditions, and washout

Each participant completes four home-based pre-sleep sessions, one per calendar
week (target spacing 7 days; allowed window 6--8 days). A missed session is
rescheduled within that window where possible; do not substitute an extra
condition or reuse a stimulus. The spacing is a conservative carryover control,
not an assertion that a seven-day interval eliminates all dream-lag effects.

The provisional enrollment target is 200 adults (50 complete counterbalance
blocks), anticipating 180 complete cases under the 10% attrition planning
assumption. It is a resource ceiling only after ethics approval; do not enroll
beyond it or lower it based on interim outcome patterns. It is subject solely to
the documented pre-recruitment expanded GLMM power check.

| Code | Condition | Purpose |
|---|---|---|
| DAI | Default AI | Frozen AI description of a target scene, delivered by the same TTS voice. |
| SAI | Participant-steered AI | Participant asks questions within the 12-minute accessible interaction; system/output are frozen and logged. |
| HUM | Human reference description | Matched human-authored scene description, delivered through the same TTS voice; tests source/output differences without equating human and AI as inherently better. |
| ANC | Active narrative control | Matched neutral, non-scene audio with no target-scene markers; controls pre-sleep audio exposure and expectancy. |

All conditions have a 12-minute total session envelope, identical TTS voice and
playback controls, and the same pre-sleep timing target (start 30 +/- 10 minutes
before intended sleep). DAI/HUM use a 4-minute description followed by neutral
recall instructions and quiet time. SAI permits up to 10 minutes of questions
plus up to 2 minutes of neutral closeout. ANC is a 4-minute neutral narrative
plus the same neutral procedures. Actual exposure and interaction durations are
recorded.

## Randomization and counterbalancing

Generate a concealed allocation schedule before recruitment using a balanced
4x4 Latin square for condition order. Assign each of the four scene sets to each
condition equally often within each order block. Randomize the mapping of scene
set to condition separately from order, stratified only by predeclared dream
recall frequency category if approved and feasible. The allocation file is held
by a study coordinator not involved in coding; coders never receive it.

## Eligibility and exclusion

**Planned inclusion:** adults able to provide informed consent; self-identify as
blind or low-vision; can access the study materials independently or with their
chosen accommodation; use the study language sufficiently for accessible
interaction and dream reporting; willing to complete up to four home sessions.

**Planned exclusion before enrollment:** a current condition or circumstance for
which altered sleep, dream-focused reporting, or study media would pose an
unacceptable risk as determined by the ethics-approved screening process;
inability to give informed consent; or participation in a conflicting sleep
intervention. Blindness onset, residual vision, and diagnostic labels are never
eligibility proxies and may be declined.

No participant is excluded because they do not report a dream on a given night,
because their report is brief, or because they fail to incorporate a marker.

## Primary outcome

The single primary confirmatory outcome is a **unit-level binary,
target-specific dream-incorporation indicator**. For each eligible report from a
DAI or SAI night, independent blinded coders assess each explicitly delivered
target semantic unit and an equal number of matched false-source foil units.

- `1` = confirmed exact or semantic incorporation under the codebook;
- `0` = absent after coding;
- `NA` = report ineligible or unit undecidable, retained as missing rather than
  converted to absent.

The primary model compares target versus foil status in DAI+SAI reports. A
target unit is eligible only if it was actually delivered in that session;
undelivered units are not failures. Exact, spatial, sensory-transformation,
emotional, and recombination forms are separately coded but are secondary or
exploratory. The primary outcome is not a participant prevalence and must not be
reported as one without a separate denominator.

**Timing window:** the first free dream report recorded upon the first main
awakening after the session, before any target-specific question and within two
hours of final awakening. If a participant records multiple spontaneous reports,
the first is primary; later reports are retained for exploratory sensitivity
analysis.

**Eligible report:** a participant-confirmed sleep episode after the session; a
free report containing at least one describable dream/mentation element; received
before target cues; and adequate audio/text to transcribe. "No dream recalled" is
valid missing primary outcome, not a zero-incorporation report.

## Manipulation checks

- delivered-unit log and target-marker coverage;
- audio duration, word count, lexical complexity, and TTS duration;
- SAI question count, interaction duration, and participant-selected categories;
- post-exposure source recognition, perceived agency, understanding, and
  uncertainty ratings; and
- next-morning report time, sleep timing, and perceived sleep disruption.

Manipulation checks describe delivery fidelity. They are not criteria for
excluding outcomes except an unrecoverable delivery failure.

## Missing data, withdrawals, and stopping

Report-level missingness remains missing. Do not impute dream incorporation.
Primary analysis uses all eligible unit observations and reports missingness by
condition and reason. A session with audio delivery failure, wrong stimulus,
target cue before free report, or unverifiable report timing is excluded from the
primary analysis but preserved and reported. Participant-level withdrawal stops
future sessions; data already retained or deleted follows the consent choice and
applicable policy.

There is no efficacy stopping rule and no interim hypothesis testing. Pause new
sessions and notify the ethics authority according to its determination if an
unanticipated problem, serious distress, or material accessibility failure is
observed. The principal investigator may stop the study for safety, integrity,
or approval-related reasons; all accumulated data and the reason are retained as
permitted and reported.

## Analysis

The preregistered primary analysis is a logistic mixed-effects model over coded
semantic units in AI nights:

`incorporated ~ target_status + condition + target_status:condition + period + order + delivered_word_count + (1|participant) + (1|stimulus)`.

The primary confirmatory contrast is target versus foil averaged over DAI+SAI;
the interaction is secondary. Condition comparisons, HUM/ANC analyses,
reconstruction, ordinal code variants, vision/onset moderation, and longer
reports are secondary/exploratory as specified in the preregistration. Report
odds ratios, model-based probabilities, 95% confidence intervals, exact
denominators, and participant-cluster bootstrap intervals.

## Adverse events and withdrawal

No session proceeds when a participant says they are distressed, overly fatigued,
or unable to access the technology. They may skip content, pause, stop without
penalty, withdraw future participation, and choose the handling of already
provided data to the extent legally possible. The detailed non-deployed response
path is in `ethics/DISTRESS_RESPONSE_PROTOCOL.md`.
