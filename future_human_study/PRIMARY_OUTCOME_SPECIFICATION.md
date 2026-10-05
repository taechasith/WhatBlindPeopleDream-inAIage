# Study 1 primary outcome specification

## Confirmatory outcome

**Name:** target-specific dream-incorporation indicator  
**Unit:** participant × session/night × semantic unit

For each eligible first free dream report from a DAI or SAI session, blinded
coders independently score every explicitly delivered target semantic unit and
an equal number of matched decoy units. The data steward randomly labels the
sets, so coders do not know target/decoy status.

## Definitions

- **Target semantic unit:** a preregistered, distinctive object, action, or
  relation explicitly delivered in that session's frozen output transcript.
- **Decoy semantic unit:** a preregistered unit drawn from the matched, unexposed
  foil stimulus; it is not delivered in the session.
- **Exact match (code 3):** exact term or unambiguous synonym with relevant
  referent.
- **Semantic match (code 2):** clearly related concept, action, or relation,
  without the exact term.
- **Ambiguous/possible (code 1):** generic or competing-source material; not
  primary-positive.
- **Spatial match:** secondary flag for a target relation/direction.
- **Sensory transformation:** secondary flag where a target is reported in a
  different sensory form.
- **Non-match (code 0):** no defensible reference.
- **Undecidable (code 9):** insufficient/unclear record; missing, not absent.

## Numerator, denominator, and scale

The primary binary score is `1` for code 2 or 3, `0` for code 0. Code 1 is
excluded from the primary outcome and examined only in a sensitivity analysis.
Code 9 is missing. The numerator is the number of primary-positive unit scores;
the denominator is all target or decoy units with an eligible report and a
decidable independent/adjudicated score. Undelivered target units are excluded,
not failures.

## Time window and eligibility

The primary report is the first participant-initiated free dream report from the
first main awakening after the session, recorded within two hours of final
awakening and before any target-specific question. Eligible reports require a
participant-confirmed sleep episode, at least one describable dream/mentation
element, verifiable session/report timing, and usable audio/text. A reported
absence of recall, no submitted report, or no sleep produces missing primary
outcome data, never a zero.

Later spontaneous reports are preserved but secondary/exploratory. Multiple
target references do not increase a unit above one; multiple semantic units are
separate rows. Participants are never prompted with target terms before the
primary report.

## Blinding, adjudication, and contrast

Coders are blind to condition, participant, sequence, true source, and hypothesis
direction. At least 20% of eligible reports are double-coded before adjudication.
Reliability is calculated on independent labels; originals are immutable;
adjudication follows `annotation/adjudication_protocol.md`.

The primary confirmatory contrast is target versus decoy status averaged over
DAI+SAI sessions in a participant-random-intercept logistic model with fixed
session period, condition, and stimulus block. Post-randomization delivery
measures are not covariates in the primary model; they are manipulation checks
or sensitivity variables. Report odds ratio, model-based probability difference,
95% CI, p value, sample/unit denominators, and participant-cluster bootstrap
CI. The target-status-by-condition interaction is secondary.
