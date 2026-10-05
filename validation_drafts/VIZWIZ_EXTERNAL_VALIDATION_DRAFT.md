# Draft: VizWiz external validation plan

**Status:** design draft only. Do not execute or report as a result until
primary output freeze, source/license review, and analysis-ready labels exist.

## Purpose

Use released VizWiz validation answers and answerability fields as a bounded
external reference for whether condition-specific VLM outputs address the
original BLV-originating question. VizWiz captions are a HumanSpace comparison,
not a universal description ground truth.

## Candidate tests

1. **Answerability calibration:** stratify by released `answerable` field.
   Compare the prevalence of an explicit answer versus grounded uncertainty by
   prompt condition. This tests output behavior, not user success.
2. **Answer-reference coverage:** after blinded human coding, evaluate whether
   output content addresses the released answer concept where the reference is
   adequate. Do not use string overlap alone as correctness.
3. **Caption alignment:** calculate transparent lexical/semantic overlap only
   as a descriptive HumanSpace comparison. Control for output length and do not
   interpret caption similarity as accessibility preference.

## Needed safeguards

- Keep source question/answer/caption text local.
- Pre-specify handling of multiple human answers and unanswerable items.
- Treat a non-match as `NOT_ESTIMABLE` when answer text is too vague, the image
  is unreadable, or source evidence cannot adjudicate the model claim.
- Report condition-specific denominators and bootstrap by image-question item.

## Planned outputs

`results/vizwiz_answerability_validation.csv`,
`results/vizwiz_reference_coverage.csv`, and a limitation record separating
answerability from correctness, usefulness, and safety.
