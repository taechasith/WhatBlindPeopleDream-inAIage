# Study 1 synthetic analysis dry run

**Status:** `PASS -- SYNTHETIC ONLY`
**No synthetic output is an empirical Study 1 result.**

## Scope

The dry run exercises the frozen long-format schema, eligibility/missingness
rules, primary row selection, a synthetic-only Python mixed-model check, an R
GLMM implementation, participant-cluster bootstrap, tables, grayscale figure,
alt text, and schema-guard tests. It uses only
`synthetic/study1_synthetic_unit_data.csv`, whose rows are marked
`SYNTHETIC_ONLY_NOT_EMPIRICAL`.

## Commands executed

```powershell
python code/generate_study1_synthetic.py
python code/study1_analysis.py --bootstrap-repetitions 100
$env:R_LIBS_USER = 'C:/Users/HP OMEN/Documents/R/win-library/4.6'
& 'C:/Program Files/R/R-4.6.1/bin/Rscript.exe' code/study1_analysis.R --bootstrap 50
python -m unittest discover -s tests -v
```

## Verified outputs

- `results/study1_synthetic_exclusion_flow.csv`
- `results/study1_synthetic_model_terms.csv`
- `results/study1_synthetic_secondary_interaction_terms.csv` (secondary,
  target-by-condition test fixture only)
- `results/study1_synthetic_primary_summary.csv`
- `results/study1_synthetic_bootstrap.json`
- `results/study1_synthetic_robustness.csv` (ambiguous-code and report-level
  dry-run checks)
- `figures/study1_synthetic_primary.png` and matching `.alt.txt`
- `results/study1_r_synthetic_exclusion_flow.csv`
- `results/study1_r_synthetic_model_terms.csv`
- `results/study1_r_synthetic_primary_estimate.csv`
- `results/study1_r_synthetic_cluster_bootstrap.csv` and summary
- `results/study1_r_synthetic_sessioninfo.txt`

The run generated 3,072 synthetic unit rows and retained 1,230
primary-decidable synthetic AI-condition rows. These counts are test-fixture
facts, not sample counts, expected yield, or evidence for Study 1.

## Safety and failure checks

- The Python pipeline refuses non-synthetic input unless explicitly invoked
  with `--allow-real-data` **and** an authoritative ethics status is documented.
- It rejects unknown conditions, mismatched ordinal/binary labels, coded
  ineligible reports, and no-recall rows coded as zero.
- Five unit tests pass, including rejection of non-synthetic data by default and
  exclusion of ambiguous code 1 from the primary binary outcome.
- The R implementation applies the same primary model structure but has the
  same ethics gate for non-synthetic data. It was run only on synthetic input.
- The Python dry run also exercises a deliberately secondary
  target-by-condition interaction and two prespecified robustness computations:
  code 1 treated as absent (code 9 remains missing), and report-level
  target-minus-decoy aggregation. These test fixtures do not select a model or
  constitute a result.

Synthetic estimates, plots, and bootstrap intervals must never be reported in a
manuscript, poster, abstract, ethics claim, press material, or public summary as
human findings.
