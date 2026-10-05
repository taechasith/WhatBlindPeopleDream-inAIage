# Reproduction guide

## Scope and constraints

This guide supports transparent regeneration where permitted; it does not
authorize access to restricted data or any human-participant activity. Raw and
processed corpora are excluded from version control by design. Do not replace
them with scraped copies, public reposts, or fabricated fixtures.

The authoritative current status is in `REPRODUCTION_STATUS.md`. A successful
run of one component does not convert Study 0 into confirmatory evidence or
authorize Study 1 data collection.

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

## Study 1 synthetic-only dry run

The following runs exercise synthetic fixtures only and must never be used as
participant findings:

```powershell
python code/generate_study1_synthetic.py
python code/study1_analysis.py --bootstrap-repetitions 100
python -m unittest discover -s tests -v
$env:R_LIBS_USER = 'C:/Users/HP OMEN/Documents/R/win-library/4.6'
& 'C:/Program Files/R/R-4.6.1/bin/Rscript.exe' code/study1_analysis.R --bootstrap 50
& 'C:/Program Files/R/R-4.6.1/bin/Rscript.exe' code/power_study1.R --reps 1000 --slots 208 --workers 4
```

The prospective R commands require `lme4` and a recorded R environment. They
were executed locally with R 4.6.1/lme4 2.0-6; session information is recorded
with the outputs. These synthetic/planning checks are not substitutes for a
future empirical Study 1 analysis and do not authorize recruitment.

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
