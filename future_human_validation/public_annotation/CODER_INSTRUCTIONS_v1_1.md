# Independent coding instructions v1.1

**Status:** distribution-ready clarification before human coding. Use only with
the supplied `coding_sheet.csv` and `PUBLIC_INTERVENTION_CODEBOOK_v1_1.md`.

Code one AI output in relation to its released BLV-originating question. You do
not receive prompt condition, model identity, original order, study hypothesis,
image filename, or image. Do not infer them.

1. Work independently; do not discuss rows with another coder before raw
   reliability is locked.
2. Use only `1`, `0`, or `NA`. `NA` is not absence.
3. Code supplied language; do not add unstated visual facts or reward fluency.
4. Do not rewrite output. Record difficult cases in `notes`.
5. Flag sensitive/private content in `notes` and pause that row if needed.

For `unsupported_information` and `accessibility_grounded_content`, enter `NA`
in this question/output-only packet. They require a separately approved
verification-evidence packet.

Illustrative non-analytic examples: "The cup is to the left of the plate" has
`spatial_relation = 1`; "The text is too blurred to read" can have
`grounded_uncertainty = 1`; "A young woman is smiling" includes an age/gender
identity inference. These examples are not study data.

## Submission

Complete the **supplied `coding_sheet.csv` directly**. Do not start from the
standalone public `coder_template.csv`. Do not change its `blind_item_id`,
question, or output columns. Fill every coding cell with `0`, `1`, or `NA` and
complete `coder_id`, `coding_date_utc`, and `notes`. Return the completed sheet
plus the supplied v1.1 independence-attestation form.
