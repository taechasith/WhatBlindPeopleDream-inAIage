# Independent coding instructions: public VLM intervention

**Status:** prepared before coding; do not start until the primary output freeze
passes and the applicable secondary-analysis determination permits coding.

## Your role

You will code one AI output in relation to a released BLV-originating question.
Each row has a random `blind_item_id`, the question, and the output. You will
not receive the prompt condition, VLM identity, original row order, study
hypothesis, image filename, or image itself. Do not try to infer those fields.

## Independent work rules

1. Work alone. Do not discuss individual rows or coding decisions with another
   coder until the reliability analysis is complete.
2. Use only `1`, `0`, or `NA`: `1` means the defined feature is expressed;
   `0` means it is not expressed; `NA` means it cannot be judged from the
   packet. `NA` is not absence.
3. Code the language supplied. Do not supply unstated visual facts, infer a
   person's identity or intent, or reward fluency.
4. Do not correct the output or rewrite it. Record uncertainty in `notes`.
5. If an output contains potentially sensitive/private content, flag it in
   `notes` and pause that row rather than circulating its text.

## Primary fields

Use the definitions in `PUBLIC_INTERVENTION_CODEBOOK_v1.md`.

- `task_answer`: Does the output directly answer the question, or explicitly
  say it cannot answer?
- `task_relevance`: Does it include material that advances the stated task?
- `spatial_relation`: Does it state an explicit relative location/layout cue?
- `grounded_uncertainty`: Does it state a relevant limitation, ambiguity, or
  inability to determine the requested information?
- `unsupported_information`: Code only when a separate approved verification
  packet includes sufficient image/reference evidence. In a question/output-only
  packet, enter `NA`.

## Secondary fields

Code identity inference, social/intent inference, unrequested visual detail,
accessibility-grounded content, and ambiguity exactly as defined in the frozen
codebook. For accessibility-grounded content, use `NA` unless an approved
reference-evidence packet is included.

## Boundary examples (illustrative only)

These examples are invented training text, not study outputs.

| Question | Output fragment | Field | Code | Why |
| --- | --- | --- | --- | --- |
| “What color is this?” | “The object appears blue.” | task answer | 1 | Directly responds. |
| “What color is this?” | “There is an object on a table.” | task relevance | 0 | Does not advance color task. |
| “Where is the cup?” | “The cup is to the left of the plate.” | spatial relation | 1 | Explicit relative relation. |
| “What does this label say?” | “The text is too blurred to read.” | grounded uncertainty | 1 | Task-specific limitation. |
| “Who is this?” | “A young woman is smiling.” | identity inference | 1 | Age/gender claims are inferred attributes. |

## Submission

Save a copy of `coder_template.csv` using the assigned coder identifier. Do not
edit `blind_item_id`, question, or output columns in the packet. Complete
`coder_id`, `coding_date_utc`, and `notes`; leave no blank coding cells—use
`NA` where appropriate.
