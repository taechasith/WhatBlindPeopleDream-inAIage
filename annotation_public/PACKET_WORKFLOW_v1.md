# Blinded packet workflow

## Preconditions

1. `MODEL_OUTPUT_FREEZE.md` must report a complete 3,000-output primary run.
2. `code/08_validate_public_intervention_outputs.py` must pass on the frozen
   output table.
3. The coding lead records whether a local ethics determination is required
   for researcher annotation of released source/model material.

## Prepare packets

1. Generate a private random salt outside shell history and set it only in the
   local `PUBLIC_CODING_BLIND_SALT` environment variable.
2. Run `code/10_build_public_annotation_packet.py` against the frozen output
   CSV. Store the condition/model mapping separately from all coder packets.
3. Copy the same randomized packet to three independent coders. Give each coder a
   blank copy of `coder_template.csv` and `CODER_INSTRUCTIONS_v1.md`.
4. Register packet hash, coder IDs, codebook version, assignment date, and
   blinding statement in a local `coding_assignment_manifest.csv`.

## Keep blinded

- Coders receive no condition, model, hypothesis direction, item sequence,
  image filename, or mapping table.
- The coding lead does not reveal condition labels while collecting independent
  files.
- A separate verification packet may include source image/reference material
  only for categories requiring a ground basis; it still omits condition/model.

## Reliability then adjudication

1. Lock all three independent files unchanged.
2. Run `code/14_public_coding_reliability.py` and archive its output.
3. Calculate agreement before any discussion. Report field-level usable N,
   prevalence, pairwise exact agreement, pairwise Cohen's kappa when estimable,
   and a three-coder reliability coefficient where appropriate.
4. Discuss only disagreements after that record is locked. Log each resolution,
   rationale, and adjudicator in a separate adjudication table.
5. The adjudicated labels are for analysis; they do not replace independent
   labels or reliability records.

## Explicit non-permissions

No coder may use an LLM as a co-coder, inspect the mapping, change the frozen
codebook, or omit inconvenient records. A coding difficulty is documented as a
limitation or `NA`, not silently solved by inference.

If only two genuine human coder files are ultimately available, record
`ALT_TEST_TWO_HUMAN_LIMITATION`; do not fabricate a third file. Keep the
human-coded subset analysis independent of any weaker Alt-Test-based synthetic
scaling decision.
