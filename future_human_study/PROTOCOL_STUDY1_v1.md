# Study 1 protocol v1.0: AI-mediated dream incorporation

**Protocol identifier:** BD-AI-CHI27-Study1-v1.0  
**Date frozen:** 2026-10-05  
**Status:** prospective protocol only. No recruitment, intervention, or human
data collection has begun. Institutional ethics determination is required before
any such activity.

## Relationship to the frozen public-data protocol

Study 1 is a separate prospective experiment added after Study 0's exploratory
public-data audit. It does not replace, upgrade, or retrospectively confirm
Study 0. Study 0 remains hypothesis-generating (`STUDY0_STATUS.md`). This
protocol must be preregistered without access to Study 1 outcomes.

## Research questions

**RQ1 (primary).** Following a pre-sleep exposure to an AI-mediated description
of an otherwise inaccessible image, is source-coded information from that
exposure incorporated into subsequently collected dream reports more often than
for a matched unexposed control stimulus?

**RQ2.** Does participant-steered AI interaction, compared with a matched
default AI description, alter the rate or form of incorporated information?

**RQ3.** Does description condition alter immediate post-exposure reconstruction
of prespecified semantic and spatial information, and subjective agency,
understanding, uncertainty, and trust?

## Boundaries of inference

The experiment can test immediate dream-report incorporation and immediate
representation/reconstruction outcomes. It cannot establish brain rewiring,
long-term neuroplastic reorganization, a stable new dream phenotype, or a causal
effect of AI use outside the controlled pre-sleep exposure. Sensory-substitution
research is retained only as mechanistic plausibility, not as evidence of an AI
effect.

## Design

Use a randomized, counterbalanced, repeated-measures design across separate
nights. Each participant encounters all conditions, with an image and a unique
marker set assigned to each night. Order, image, and condition must be balanced
using a schedule generated before outcome collection.

1. **Default-AI condition:** a frozen, task-relevant AI description is delivered
   by accessible speech/text. The system selects which available image content to
   describe under a prespecified prompt and response-length constraint.
2. **Participant-steered-AI condition:** the participant can ask prespecified
   open questions of the same frozen system about the same type of image. The
   interaction transcript, timing, prompts, model/version, decoding parameters,
   and any system tools are retained. A standardized time cap applies. The
   participant's questions operationalize human-to-AI grounding rather than
   being treated as a nuisance variable.
3. **Matched control condition:** a distinct image/marker set is not disclosed
   before sleep. It is included in the blinded coding set as a false-source
   control. If an active control is used, it must be semantically unrelated and
   cannot contain the target image's markers. This control is necessary: a
   comparison of only two exposed AI conditions cannot test whether exposure
   itself predicts incorporation.

Images must be licensed for study use, screened for distressing, identifying,
sexual, medical, or highly sensitive content, and not used as a proxy for a
participant's private environment. Each image receives a preregistered marker
inventory covering object, relation, direction, motion/action, affective tone,
and sensory affordance. Markers must be sufficiently distinctive across images
to support blinded source assignment without cueing participants.

## Population and accessibility

Recruit adults who self-identify as blind or low-vision. Record self-described
vision/onset only with an explicit prefer-not-to-say option; do not infer onset.
Stratify or report congenital/early/acquired/unknown groups separately when
sample size permits. The study must not promise that participants will dream of
the material. All consent, instructions, questionnaires, and debriefing must be
screen-reader-compatible and available in the participant's preferred usable
format.

The inclusion/exclusion criteria, compensation, recruitment routes, language,
and whether sleep-lab awakenings are used are **NOT YET APPROVED**. They must be
specified in the ethics submission and preregistration. Home morning reports
should be preferred unless a sleep-lab protocol is justified, resourced, and
ethically approved; sleep interruption adds burden and changes what can be
inferred.

## Procedure

1. Obtain consent and assess preferred accessible format, routine sleep safety,
   and the participant's wish to skip any content.
2. Collect a short baseline for usual dream recall and prior familiarity with
   each marker concept. Do not exclude people merely because a concept is
   unfamiliar; record it for interpretation.
3. Deliver the randomized condition at a fixed pre-sleep interval, recorded for
   every session. No deception about recording or AI use is permitted.
4. Before sleep, obtain a brief reconstruction task and subjective ratings. This
   is a secondary immediate representation outcome, not a measure of neural
   change.
5. On awakening, collect a free dream report before any marker prompts. Follow
   only with a neutral standardized prompt (for example, "Anything else?").
   Participants must not be told which elements are target markers.
6. Record sleep timing, unusual events, and deviations. Provide opt-out and
   distress support/debriefing.

## Outcomes and coding

**Primary outcome:** per-report blinded source-coded incorporation of the
previous night's target marker set versus false-source marker set. Coders must
not know condition, image, participant identity, order, or hypotheses.

**Prespecified incorporation classes:**

- exact: a distinctive marker or relation is explicitly reported;
- semantic: a defensibly related concept is reported without the exact marker;
- spatial: a target relation/direction is reported;
- sensory transformation: source content is represented in another sensory form;
- emotional: target affective tone is represented;
- novel recombination: target material is combined with non-target material.

These labels are not mutually exclusive. The codebook must give positive and
negative examples, prohibit inference from absence, and require an
`UNDECIDABLE` label. At least 20% of reports must be independently double-coded
before adjudication; reliability and category-specific prevalence must be
reported. No LLM can serve as a ground-truth coder. If it assists, its version,
prompt, settings, output, and validation against blinded human labels are
archived and separately reported.

**Secondary outcomes:** blinded scoring of semantic/spatial reconstruction;
participant ratings of agency, understanding, uncertainty calibration, trust,
and burden; and condition-level description properties (length, marker coverage,
unsupported information, actionability). These are not evidence of neural
reorganization.

## Analysis plan

The unit is the dream report nested within participant and stimulus. The primary
confirmatory model is a mixed-effects logistic model for source-coded
incorporation, with fixed condition and planned covariates, plus participant and
stimulus random intercepts. Report effect estimates, confidence intervals,
complete numerator/denominator counts, missing-data handling, and planned
contrasts. Use false discovery-rate adjustment for secondary category tests.

Robustness analyses: exact-only coding; direct plus semantic coding; remove
reports collected after protocol deviations; condition-by-vision/onset group only
when estimable; marker familiarity adjustment; description-length adjustment;
and coder-disagreement sensitivity analysis. Do not pool participant prevalence,
report prevalence, and marker prevalence.

Sample size is **NOT_ESTIMABLE** at v1.0 because no pilot variance, within-person
correlation, number of usable reports per participant, or minimally important
effect has been selected. A simulation-based power analysis using those
prespecified inputs is a preregistration and ethics prerequisite; it cannot be
back-filled after outcome inspection.

## AI audit and reproducibility

Freeze model/provider/version/date/system prompt/user prompts/temperature/top-p,
tools, image input, output transcript, content filters, and accessibility delivery
format before collecting outcomes. Preserve raw records under controlled access;
release only de-identified, consent-compatible derivatives and code. Every
description must be independently audited for unsupported identity, demographic,
emotion, relationship, or safety claims. Human participants may not be exposed
to prompts designed to elicit such claims.

## Social impact and stopping criteria

The participant-steered condition directly tests whether BLV-defined questions
can shape the information channel. It does not assume steering is better. Assess
agency, epistemic autonomy, safety/actionability, dignity/social inference,
privacy, and sensory pluralism as prespecified outcomes or design audits.

Pause a session for distress, fatigue, a participant request, inaccessible
technology, or unanticipated adverse events. The responsible ethics body, not
this protocol, determines reportability and escalation.
