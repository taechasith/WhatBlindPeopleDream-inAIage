# Study 1 synthetic analysis dry run

## Scope

This dry run tests schemas, validation, missing-data handling, a participant-
random-intercept logistic model, clustered bootstrap, output tables, and one
accessible labeled figure. It uses only `synthetic/study1_synthetic_unit_data.csv`.
That file is deterministically generated and every row is marked
`SYNTHETIC_ONLY_NOT_EMPIRICAL`.

## Commands executed

```powershell
python code/generate_study1_synthetic.py
python code/study1_analysis.py
python code/power_study1.py
```

The dry run validated 2,496 eligible synthetic unit rows after a simulated
missing-report process. It wrote:

- `results/study1_synthetic_model_terms.csv`
- `results/study1_synthetic_primary_summary.csv`
- `results/study1_synthetic_bootstrap.json`
- `figures/study1_synthetic_primary.png`
- `results/power_scenarios.csv` and `results/power_curve.csv`

## Checks and limits

The pipeline rejects input without the required schema, unknown conditions, any
non-synthetic status during this dry run, or missing binary outcomes on eligible
rows. It preserves unavailable reports as missing. The Python dry-run model has
a participant random intercept; the final R analysis adds stimulus effects and
all preregistered covariates. The R executable is absent locally, so
`code/power_study1.R` remains unexecuted and is a required pre-recruitment check.

Synthetic estimates/plots must never appear as Study 1 findings in a manuscript,
poster, abstract, press material, or ethics claim.
