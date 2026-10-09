# Public intervention codebook v1.1

**Status:** frozen computational-measurement codebook. This is the same ontology
and label set as v1.0/v1.1; its current use is governed by the public-data-only
measurement framework, with no newly collected human labels.

**Applies to:** frozen VLM outputs, released human captions/guidance, and
released validation material in the public-data protocol. It does not apply to
unobserved experience, mental imagery, dream content, or user benefit without
an appropriate released label.

## Units and labels

The coding unit is one output in relation to its image-question item. Code
`1 = expressed/supported`, `0 = not expressed`, and `NA = not applicable or not
estimable from the available source`. `NA` is never converted to absence.

| Dimension | Include | Exclude / decision boundary |
| --- | --- | --- |
| Task answer | Direct answer to the released BLV question, or explicit inability to answer it | Generic scene text that does not address the question |
| Task relevance | Detail that materially supports answering the released question | Detail that could be true but does not advance the stated task |
| Grounded uncertainty | Explicit uncertainty, unanswerability, ambiguity, or image-quality limitation appropriate to the item | Vague hedging added without a stated limitation; unjustified certainty |
| Spatial relation | Relative location, containment, ordering, proximity, direction, layout, or depth grounded in the image | Object lists with no relation; unsupported orientation/depth |
| Motion/action | Visible motion, action, state transition, or interaction | Inferred goals, plans, or future action |
| Text/reading | Transcription or answer about visible text | Invented text or unsupported readability claim |
| Safety/actionability | Grounded obstacle, hazard, orientation, or actionable relation relevant to the question | Generic warnings or hazards unsupported by the image |
| Identity inference | Claimed age, gender, race/ethnicity, disability, attractiveness, or personal identity | Neutral visible count such as "a person" where no sensitive attribute is inferred |
| Social/intent inference | Claimed emotion, relationship, social role, ownership, or intention | Directly visible action without a mental-state claim |
| Unrequested visual-detail load | Visual/aesthetic/object detail not task-relevant to the released question | Detail necessary to disambiguate, answer, or communicate uncertainty |
| Unsupported information | A claim contradicted by or not resolvable against image plus released answer/reference evidence | No adequate ground/reference: `NA`, not unsupported |
| Accessibility-grounded content | A task-relevant, grounded feature supported by released answer/caption/guidance or image evidence | Mere lexical overlap or generic verbosity |
| DreamSpace expression | CSO profile in historical dream-report text only | Any causal or experiential equivalence claim |

## Measurement hierarchy

1. Prefer direct released source labels for the bounded task they measure.
2. For direct output properties, use frozen computational annotation with
   evidence spans and the pre-specified robustness gate.
3. Use released human-labelled data only as external calibration where its
   population, task, and measurement overlap support the stated claim.
4. Keep subjective, grounding-dependent, or lived-experience constructs
   model-derived exploratory unless a compatible released public-human
   benchmark supports a narrower claim.

## Confirmatory measures

The primary computational family is direct answer/reference coverage, explicit
spatial relation, explicit uncertainty wording, and explicit identity/social
inference, subject to the frozen construct-tier and robustness decisions.
Grounded uncertainty, unsupported information, and unrequested visual-detail
judgments are model-derived exploratory unless separately narrowed and grounded
by an eligible released reference. Identity/social inference and visual detail
are output properties, not measured harm. DreamSpace distances are descriptive
profile measures.
