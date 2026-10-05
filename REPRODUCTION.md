# Reproduction guide

## Scope and constraints

This guide supports transparent regeneration where permitted; it does not
authorize access to restricted data or any human-participant activity. Raw and
processed corpora are excluded from version control by design. Do not replace
them with scraped copies, public reposts, or fabricated fixtures.

The authoritative current status is in `REPRODUCTION_STATUS.md`. A successful
run of one component does not convert historical Study 0 into confirmatory
evidence or establish an effect on people.

## Python environment

Use Python 3.10 or a compatible interpreter and install the pinned audit
environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The pinned packages are sufficient for the tracked Python scripts. Do not treat
the local environment as an immutable archive; record the interpreter and
package versions for every regenerated result.

## Verify locally acquired sources

Acquire source data only through the provenance and access routes in
`data/MANIFEST.csv`, respecting `data/LICENSES.md`. Place authorized local files
at the paths named in the manifest, then verify recorded bytes without exposing
their contents:

```powershell
python code/verify_provenance.py
```

The command fails for absent or mismatching local files. It does not download
data and does not bypass source access controls.

## Study 0 processing and exploratory outputs

With authorized local source files in place, regenerate in this order:

```powershell
python code/02_build_dream_corpus.py
python code/03_build_ai_corpus.py
python code/04_apply_codebook.py
python code/07_ai_alignment.py
python code/08_robustness.py
python code/10_export_tables.py
```

The resulting distributions, alignment metrics, and robustness tables must keep
their `EXPLORATORY_AUTOMATED_CANDIDATE` status. The current repository does not
contain completed independent human coding or a human reliability statistic.

## Active public-data intervention: pre-generation gates

The public-data intervention cannot be run by substituting placeholder AI text.
After acquiring local sources through the documented routes, reproduce its
pre-generation state as follows:

```powershell
python code/05_build_public_reference_corpora.py
python code/06_select_public_intervention_sample.py
python code/07_validate_public_intervention_inputs.py
python code/verify_provenance.py
```

The final command records a validated 1,000-item sample with a local image for
every item. It does not inspect pixel content or produce a model output. Before
generation, replace `config/public_vlm_models.example.json` with a private,
complete frozen model manifest satisfying `PUBLIC_MODEL_COMPUTE_GATE.md`.
For each real model run, validate the completed output table before analysis:

```powershell
python code/08_validate_public_intervention_outputs.py `
  --outputs C:\authorized-local-path\model_outputs.csv `
  --model-manifest C:\authorized-local-path\public_vlm_models.json `
  --report C:\authorized-local-path\output_validation_report.json
```

The validator is fail-closed: it requires exactly the frozen sample, one output
for every condition per model/item, nonblank output, and a matching model
manifest hash. Validation is not analysis, coding, or a scientific finding.

After two independent blinded coding files have been created according to
`PUBLIC_INTERVENTION_CODEBOOK_v1.md` and reconciled under
`annotation_public/adjudication_protocol.md`, run the analysis locally:

```powershell
python code/09_analyze_public_intervention.py `
  --outputs C:\authorized-local-path\model_outputs.csv `
  --labels C:\authorized-local-path\adjudicated_labels.csv `
  --outdir C:\authorized-local-path\analysis
```

The script produces condition prevalence and paired image-cluster bootstrap
tables, but it does not decide whether supplied records are real, independent,
or publishable. `code/09_generate_public_intervention_synthetic.py` exercises
only the plumbing; its output is ignored and documented in
`REPRODUCTION_PUBLIC_DRYRUN.md`.

## Future human-study synthetic-only dry run

The following runs exercise synthetic fixtures only and must never be used as
participant findings:

```powershell
python future_human_study/code/generate_study1_synthetic.py
python future_human_study/code/study1_analysis.py --bootstrap-repetitions 100
python -m unittest discover -s future_human_study/tests -v
$env:R_LIBS_USER = 'C:/Users/HP OMEN/Documents/R/win-library/4.6'
& 'C:/Program Files/R/R-4.6.1/bin/Rscript.exe' future_human_study/code/study1_analysis.R --bootstrap 50
& 'C:/Program Files/R/R-4.6.1/bin/Rscript.exe' future_human_study/code/power_study1.R --reps 1000 --slots 208 --workers 4
```

The prospective R commands require `lme4` and a recorded R environment. They
were executed locally with R 4.6.1/lme4 2.0-6; session information is recorded
with the outputs. These synthetic/planning checks are not substitutes for a
future empirical human-study analysis and do not authorize recruitment.

## Anonymous review export

First run a non-writing content check:

```powershell
python code/export_anonymous_review.py --check
```

To create a review bundle, supply an empty directory outside this repository:

```powershell
python code/export_anonymous_review.py --output C:\path\outside\this-repository\anonymous-review
```

The exporter is intentionally narrow. Read `ANONYMOUS_RELEASE_POLICY.md` and
perform a human review of every final archive, PDF, image, filename, and link.
