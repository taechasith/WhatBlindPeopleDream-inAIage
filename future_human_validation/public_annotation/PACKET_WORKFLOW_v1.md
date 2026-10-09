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
4. Before analytic coding begins, give each coder the separate administrative
   `HUMAN_CODER_INDEPENDENCE_ATTESTATION_TEMPLATE.csv`. It records the packet and
   material hashes, a pseudonymous coder ID, completion time, and affirmations
   that the coder did not see condition metadata, synthetic labels, or another
   coder's labels and did not use an LLM as a co-coder. This form does not alter
   the frozen analytic rows or rubric.
5. Register packet hash, coder IDs, codebook version, assignment date, and
   blinding statement in a local `coding_assignment_manifest.csv`.

## Keep blinded

- Coders receive no condition, model, hypothesis direction, item sequence,
  image filename, or mapping table.
- The coding lead does not reveal condition labels while collecting independent
  files.
- A separate verification packet may include source image/reference material
  only for categories requiring a ground basis; it still omits condition/model.

## Reliability then adjudication

1. Run `code/17_lock_human_coder_files.py` first. It accepts only three genuine
   returned files plus three separate attestations, verifies the exact frozen
   600-row packet/schema/order and distributed-material hashes, and creates an
   atomic immutable lock directory. Do not run reliability on email attachments
   or arbitrary working copies.
2. Run `code/14_public_coding_reliability.py` against a directory containing
   `LOCK_COMPLETE.json`, the three byte-locked raw returns, and the pre-frozen
   opaque cluster map. Archive all generated outputs.
3. Calculate agreement before any discussion. Report field-level usable N,
   prevalence, pairwise exact agreement, pairwise Cohen's kappa when estimable,
   three-coder nominal Krippendorff alpha where appropriate, bootstrap
   uncertainty, and abstention/missingness. Do not turn `NA` into `0`.
4. The current protocol has no frozen numerical reliability threshold. The
   report therefore records `THRESHOLD_NOT_PREDEFINED` and blocks confirmatory
   scaling pending a prospective governance decision; it must not create a
   post-hoc PASS/BORDERLINE label.
5. Discuss only disagreements after that record is locked. Log each resolution,
   rationale, and adjudicator in a separate adjudication table.
6. The adjudicated labels are for analysis; they do not replace independent
   labels or reliability records.

## Explicit non-permissions

No coder may use an LLM as a co-coder, inspect the mapping, change the frozen
codebook, or omit inconvenient records. A coding difficulty is documented as a
limitation or `NA`, not silently solved by inference.

If only two genuine human coder files are ultimately available, record
`ALT_TEST_TWO_HUMAN_LIMITATION`; do not fabricate a third file or pass two files
through the three-coder lock/reliability workflow. Preserve the human-coded
subset separately under a documented fallback protocol, keep it independent of
any weaker Alt-Test evidence, and do not treat it as a robust three-human
consensus reference.
