# Blinded dream-incorporation coding manual v1.0

## Blinding and materials

Each coder receives only a de-identified report ID, transcription, target-unit
list, matched foil-unit list, and a codebook version. They must not receive
participant ID, condition, session order, stimulus identity, delivery transcript,
hypothesis direction, or another coder's decision. Target and foil lists are
randomly relabeled `Set A`/`Set B` by a data steward.

Coders first determine report eligibility. They then code every unit separately,
using the report alone. Never infer an experience from a missing word; never use
the participant's blindness/onset label; and do not treat a dreamer's statement
of uncertainty as confirmation.

## Eligibility

`ELIGIBLE`: free dream/mentation report before target prompting, associated with
the first main awakening after a logged session, and transcribable. `INELIGIBLE`:
not asleep, no report submitted, target-cued before free report, unusable
recording, wrong session/stimulus, or timing cannot be verified. `NO_RECALL` is
eligible for reporting but has missing—not absent—unit scores.

## Unit scoring scale

For each unit, use one ordinal evidence code:

| Code | Label | Definition |
|---|---|---|
| 0 | Absent | No defensible reference to the unit. |
| 1 | Possible/ambiguous | A weak, generic, polysemous, or competing-source reference; never counts in the primary outcome. |
| 2 | Semantic incorporation | Clearly related concept/action/relation without the exact lexical marker; counts in the primary outcome. |
| 3 | Exact incorporation | Exact marker or an unambiguous synonym plus its relevant referent; counts in the primary outcome. |
| 9 | Undecidable | Audio/transcription ambiguity or insufficient context prevents a judgment; treated as missing. |

`primary_binary = 1` for code 2 or 3 and `0` for code 0. Code 1 is excluded
from the primary binary analysis and is included only in a preregistered
sensitivity analysis. Code 9 is missing.

## Form flags (secondary/exploratory)

- `spatial_relation`: target directional/relational meaning is present;
- `sensory_transformation`: target content occurs primarily as another sensory
  modality or bodily experience (for example, violin -> music); 
- `emotional_incorporation`: target scene's preregistered affective tone occurs;
- `novel_recombination`: target unit is combined with clearly non-target dream
  material;
- `unsupported_inference`: coder would need to infer identity, intention, or
  unstated detail. This flag requires code 0/1, never 2/3 by itself.

Examples: "I heard music while climbing stairs" can be a semantic violin and
spatial-staircase reference only if both are in the unit list and the link is
defensible; otherwise code possible/absent. "There was an instrument" is
possible for `violin`, not semantic. "A dog hid under a table" is exact for
`dog_beneath_table`. "Someone looked sad" cannot support an unlisted identity
or emotion.

## Disagreement and reliability

At least 20% of eligible reports, stratified by condition and report length, are
independently double coded before adjudication. Report weighted kappa for the
0/1/2/3 ordinal scale where estimable, plus binary Cohen's kappa and
prevalence-adjusted agreement with confidence intervals. Report each category's
confusion matrix and `NOT_ESTIMABLE` rather than fabricate reliability where
counts are sparse. Adjudication occurs only after independent files are locked.
