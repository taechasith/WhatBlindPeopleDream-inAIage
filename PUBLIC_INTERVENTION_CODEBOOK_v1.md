# Public intervention codebook v1.0

**Applies to:** frozen VLM outputs, released human captions/guidance, and
released validation material in the public-data protocol.  
**Does not apply to:** unobserved experience, mental imagery, dream content, or
user benefit without an appropriate released label.

## Units and labels

The coding unit is one output in relation to its image-question item. Code
`1 = expressed/supported`, `0 = not expressed`, and `NA = not applicable or not
estimable from the available source`. `NA` is never converted to absence.

| Dimension | Include | Exclude / decision boundary |
| --- | --- | --- |
| Task answer | Direct answer to the released BLV question, or explicit inability to answer it | Generic scene text that does not address the question |
| Task relevance | Detail that materially supports answering the released question | Detail that could be true but does not advance the stated task |
| Grounded uncertainty | Explicit uncertainty, unanswerability, ambiguity, or image-quality limitation appropriate to the item | Vague hedging added without a stated limitation; unjustified certainty |
| Spatial relation | Relative location, containment, ordering, proximity, direction, layout, or depth that is grounded in the image | Object lists with no relation; unsupported orientation/depth |
| Motion/action | Visible motion, action, state transition, or interaction | Inferred goals, plans, or future action |
| Text/reading | Transcription or answer about visible text | Invented text or an unsupported claim that text is readable |
| Safety/actionability | Grounded obstacle, hazard, orientation, or actionable relation relevant to the question | Generic warnings, medical/legal advice, or hazards unsupported by the image |
| Identity inference | Claimed age, gender, race/ethnicity, disability, attractiveness, or personal identity | Neutral visible count such as “a person” where no sensitive attribute is inferred |
| Social/intent inference | Claimed emotion, relationship, social role, ownership, or intention | Directly visible action without a mental-state claim |
| Unrequested visual-detail load | Visual/aesthetic/object detail not task-relevant to the released question | Detail necessary to disambiguate, answer, or communicate uncertainty |
| Unsupported information | A content claim contradicted by or not resolvable against the image plus released answer/reference evidence | Claim cannot be judged because no adequate ground/reference exists: `NA`, not unsupported |
| Accessibility-grounded content | A task-relevant, grounded output feature supported by the released human answer/caption/guidance or image evidence | Mere lexical overlap with a human reference or generic verbosity |
| DreamSpace expression | CSO profile in historical dream-report text only | Any claim that an output causes, predicts, or resembles a person's dream experience |

## Scoring hierarchy

1. Prefer released source labels and source-grounded human evidence.
2. Where a label needs manual judgment, use independent blinded coders on the
   frozen stratified subset and calculate reliability before adjudication.
3. A rule-based or frozen model-assisted label may be used only as a secondary
   diagnostic unless validated against the corresponding independent labels.

## Confirmatory measures

The primary family is task relevance, task answer, spatial relation, grounded
uncertainty, and unsupported information *where estimable*. Identity/social
inference and unrequested detail are secondary harm-relevant diagnostics; they
must not be described as measured harm. DreamSpace distances are descriptive
profile measures only.
