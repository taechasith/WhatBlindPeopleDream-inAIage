# Computational Measurement Robustness Protocol v1

**Status:** `FROZEN_BLINDED_PUBLIC_DATA_ONLY`

This protocol is an additive technical audit of the already frozen synthetic
panel. It does not alter baseline panel artifacts, access a private condition
map, inspect condition assignments, or authorize condition-level analysis.
Its reporting unit is a blinded construct-level metric.

## Preconditions and boundary

Run this protocol only after a baseline
`SYNTHETIC_PANEL_OUTPUT_FREEZE.json` has been created. The packet supplied to
these utilities must have exactly `blind_item_id`, `blv_question`, and
`output_text`; a packet with a condition-bearing field fails immediately.

No person should manually inspect label substance while this workflow runs.
The designated scripts may mechanically process blinded labels and visible
packet text only to test schema, provenance, evidence-span grounding, and
reproducibility. They never receive a condition-mapping argument.

Documented `EVIDENCE_SPAN_INVALID` and `PARSE_ERROR:*` records remain in
coverage accounting. They are not silently relabeled, removed, retried, or
treated as semantic abstentions. Undocumented schema, provenance, label, or
abstention inconsistencies are fail-closed errors.

## Frozen subsets

`code/21_build_measurement_robustness_subsets.py` ranks only
`blind_item_id` values using the fixed SHA-256 ranking rule and seed in
`config/computational_measurement_robustness_v1.json`.

- The first 300 ranked IDs form the prompt-paraphrase subset.
- The first 60 of those same ranked IDs form the exact-rerun subset.
- Thus the exact-rerun subset is necessarily nested in the 300-row subset.

Neither question text, answer text, labels, constructs, model identity,
condition metadata, nor an outcome statistic may influence selection.

## Execution sequence

1. Freeze the two public blinded subset packets and their receipt:

   ```powershell
   python code/21_build_measurement_robustness_subsets.py `
     --config config/computational_measurement_robustness_v1.json `
     --packet <baseline-blinded-packet.csv> `
     --baseline-freeze <baseline-freeze-dir/SYNTHETIC_PANEL_OUTPUT_FREEZE.json> `
     --outdir <new-subset-dir>
   ```

2. Run each already frozen synthetic judge separately on
   `prompt_paraphrase_subset_v1.csv`, using
   `SYNTHETIC_PANEL_PROMPT_PARAPHRASE_v1.md`. Run those same frozen judges on
   `exact_rerun_subset_v1.csv`, using the canonical baseline prompt and the
   unchanged baseline panel configuration. Keep all three label directories
   distinct; do not overwrite or append to baseline outputs.

3. Mechanically audit the baseline, paraphrase, and rerun labels:

   ```powershell
   python code/22_audit_synthetic_measurements.py `
     --config config/computational_measurement_robustness_v1.json `
     --subset-manifest <subset-dir/COMPUTATIONAL_MEASUREMENT_SUBSET_MANIFEST_v1.json> `
     --baseline-freeze <baseline-freeze-dir/SYNTHETIC_PANEL_OUTPUT_FREEZE.json> `
     --baseline-packet <baseline-blinded-packet.csv> `
     --baseline-labels-dir <baseline-panel-labels-dir> `
     --prompt-paraphrase-packet <subset-dir/prompt_paraphrase_subset_v1.csv> `
     --prompt-paraphrase-labels-dir <paraphrase-labels-dir> `
     --exact-rerun-packet <subset-dir/exact_rerun_subset_v1.csv> `
     --exact-rerun-labels-dir <rerun-labels-dir> `
     --outdir <new-audit-dir>
   ```

4. Apply only the predeclared schema and lexical rule anchors to blinded,
   construct-level audit aggregates:

   ```powershell
   python code/23_apply_computational_rule_anchors.py `
     --config config/computational_measurement_robustness_v1.json `
     --subset-manifest <subset-dir/COMPUTATIONAL_MEASUREMENT_SUBSET_MANIFEST_v1.json> `
     --measurement-audit-dir <audit-dir> `
     --outdir <new-rule-anchor-dir>
   ```

5. Write the blinded construct-level robustness summary:

   ```powershell
   python code/24_summarize_blinded_measurement_robustness.py `
     --config config/computational_measurement_robustness_v1.json `
     --subset-manifest <subset-dir/COMPUTATIONAL_MEASUREMENT_SUBSET_MANIFEST_v1.json> `
     --measurement-audit-dir <audit-dir> `
     --rule-anchor-dir <rule-anchor-dir> `
     --calibration-receipt results/public_human_calibration_matrix.csv `
     --outdir <new-summary-dir>
   ```

Every output directory is immutable: it must not exist before the command
starts. A failed validation produces no completed receipt and must be corrected
through a new derivative run, preserving source artifacts.

## Measurements and interpretation

The audit reports only blinded construct-level counts and rates: parser and
coverage accounting, evidence-span integrity, label/abstain coherence,
inter-judge agreement, prompt-paraphrase agreement, exact-rerun agreement,
and a deterministic label-flip code-path control. The rule-anchor layer is
generic by design: it uses no construct-specific lexicon and no condition
information.

The exact-rerun and paraphrase comparisons are technical robustness measures,
not evidence of human validity. The label-flip control checks that the
measurement code reacts to a deliberately in-memory binary change; it is not a
substantive sensitivity result. Before any audit is run, the frozen JSON
configuration requires a primary candidate to meet all of the following: at
least 95% valid audited records and 95% valid positive evidence spans in each
judge; at least 20 positive records per judge; exact rerun-label consistency;
at least 0.80 prompt-paraphrase binary agreement; at least 0.60 cross-judge
binary agreement; no more than 0.20 binary label-flip rate; and at least 20
comparable binary records for each applicable comparison. A rare construct that
cannot support those estimates is not promoted merely because raw agreement is
high. The configuration never grants unblinding; its construct-strength receipt
remains subject to public-human calibration and the coded-data-freeze gate.
