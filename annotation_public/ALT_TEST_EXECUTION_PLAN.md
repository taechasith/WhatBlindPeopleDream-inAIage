# Alternative Annotator Test execution plan

This plan governs a future construct-by-construct test only. It does not
authorize condition unblinding, RQ2-RQ5 analysis, or substitution of synthetic
labels for human labels.

## Locked inputs required before execution

- Coder A, B, and C raw files for the same blinded 600-row subset;
- pre-adjudication human reliability outputs;
- locked adjudicated labels for the same rows;
- frozen individual synthetic-judge labels aligned by `blind_item_id` and
  construct; and
- a construct eligibility record and the rationale for the selected epsilon.

No Alt-Test run occurs before all of these inputs are locked. It is run with the
official Calderon, Reichart, and Dror implementation at
https://github.com/nitaytech/AltTest, rather than a locally improvised
approximation.

## Frozen epsilon policy

The primary cost-benefit hyperparameter is **epsilon = 0.10** for every
compatible construct and each frozen judge. This treats the three planned
coders as trained, independent non-expert coders following a fixed rubric and
does not claim an expert-annotator efficiency premium. The value is fixed
before human labels, adjudicated labels, human--synthetic comparisons,
advantage probabilities, winning rates, or condition effects are seen.

Human reliability still governs construct eligibility. A poorly reliable
construct is classified `CONSTRUCT_NOT_RELIABLE`; epsilon must not be changed
to make an LLM pass. Every Alt-Test report must state this fixed epsilon,
coder-role rationale, human reliability, average advantage probability, and
winning rate.

## Required procedure

1. Run each compatible construct independently, with all human and synthetic
   labels aligned to the same item identifiers.
2. Preserve the official implementation's per-annotator leave-one-out results,
   assumptions, epsilon rationale, p-values, advantage probabilities, and
   winning rates.
3. Apply the prospectively specified multiplicity procedure across the tested
   constructs; do not select a judge or construct after observing wins.
4. Record one construct status under `ANNOTATION_VALIDATION_POLICY.md`; a pass
   is necessary but not sufficient for the synthetic full-scale measurement
   gate because human reliability and evidence-span validity must also pass.
5. Retain raw inputs, outputs, software revision/environment provenance, and
   checksums in `CODED_DATA_FREEZE.md`.

## Two-human contingency

The official Alt-Test implementation permits two human annotators but its FAQ
recommends at least three: two-human leave-one-out comparisons lack a robust
consensus reference. If Coder C is genuinely unavailable, do not create or
simulate a third coder. Record `ALT_TEST_TWO_HUMAN_LIMITATION`, downgrade the
strength of any Alt-Test evidence, and retain the human-subset confirmatory
analysis independently of synthetic scaling.
