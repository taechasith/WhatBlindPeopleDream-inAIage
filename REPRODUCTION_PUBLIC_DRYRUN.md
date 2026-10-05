# Public-intervention analysis dry run

**Date:** 2026-10-06 (Asia/Bangkok)  
**Status:** `SYNTHETIC_ONLY_NOT_EMPIRICAL`

## Purpose

Exercise the output/coding analysis path before a real VLM run exists. The
fixture generator creates invented IDs, output text, labels, probabilities, and
two imaginary model names. It reads no VizWiz question, answer, caption, image,
DreamBank report, or VLM output.

## Commands run

```powershell
python code/09_generate_public_intervention_synthetic.py `
  --outdir results/public_intervention_synthetic --items 40
python code/09_analyze_public_intervention.py `
  --outputs results/public_intervention_synthetic/synthetic_outputs.csv `
  --labels results/public_intervention_synthetic/synthetic_labels.csv `
  --outdir results/public_intervention_synthetic/analysis --bootstrap 200
```

## Checks passed

- 240 synthetic rows were created: 40 invented item IDs × 2 imaginary models ×
  3 conditions.
- The analysis completed condition prevalence and paired item-cluster bootstrap
  tables without schema or merge errors.
- The synthetic output directory is ignored by Git.

## Strict interpretation boundary

The generated values, directions, confidence intervals, labels, model names,
and text are invented test fixtures. They are not included in any result table,
figure, manuscript, poster, or claim. A real run still requires the frozen
model/compute gate, output validation, independent coding, reliability, and
provenance review.
