# Non-analytic coder training materials v1

These invented examples are only for training. They are not drawn from VizWiz,
the frozen model-output corpus, the human-validation subset, or any study
dataset. Do not add them to an analysis file.

## Training rules

- Use the frozen coding instructions and code only expressed text.
- Enter `NA` when the rubric says a label cannot be determined; do not guess.
- Do not use an LLM, search engine, condition label, model identity, or another
  coder's work.
- Record a short rationale in notes only when a label is difficult; do not
  revise the codebook while coding.

## Example A: explicit spatial relation

Question: “Where is the cup?”

Description: “A blue cup sits immediately to the left of a white plate.”

Practice: `spatial_relation = 1`. The relation is explicit. Do not infer task
success for any construct that needs a separate verified answer source.

## Example B: uncertainty

Question: “Is this medicine?”

Description: “I cannot determine the label from this blurry image; it may be a
small bottle, but please check the printed text before using it.”

Practice: `grounded_uncertainty = 1`. The uncertainty is explicit and tied to
an observable image limitation. Do not code an unsupported identity claim.

## Example C: unsupported social inference

Question: “What is happening?”

Description: “A person is standing beside a door and looks worried about being
late.”

Practice: distinguish explicitly visible action/location from inferred emotion
or intent. Apply the exact frozen definitions in `CODER_INSTRUCTIONS_v1.md`.

## Example D: abstention / ambiguity

Question: “What color is the object?”

Description: “There is an object on the table.”

Practice: if a construct is not expressed, code its absence when the rubric
permits; use `NA` only when the construct is genuinely not determinable under
the instructions. Do not turn missing detail into an inferred answer.

## Completion check

Before analytic coding, each coder confirms they received the current frozen
instructions, understood condition blinding, and completed no analytic packet
discussion with another coder.
