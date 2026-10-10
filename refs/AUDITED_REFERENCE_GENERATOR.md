# Post-results anonymous reference generator

`code/33_generate_audited_references.py` creates an immutable bibliography
bundle only after `RESULTS_FREEZE` exists. It does not inspect result values,
raw VLM outputs, private condition mappings, or participant material.

## Inputs

- `refs/doi_audit.csv`: the DOI/status/classification authority.
- `refs/audited_reference_metadata.csv`: a local snapshot of title, author,
  venue, and publication metadata verified against Crossref or DataCite on
  2026-10-10. It is not refreshed from a mutable API during final rendering.
- a completed copy of `refs/reference_selection.template.json`: the finite
  anonymous citation list, with the exact `RESULTS_FREEZE` SHA-256 and a
  bounded use for each cited work.

The template is deliberately not executable. Do not cite every audited paper
by default; select only sources actually used in the anonymous manuscript.

## Run after the results freeze

```powershell
python code/33_generate_audited_references.py `
  --results-freeze results/results_freeze/RESULTS_FREEZE.json `
  --selection refs/reference_selection.json `
  --outdir refs/final_reference_audit_v1
```

The new output directory contains:

- `audited_references.bib`
- `REFERENCE_TRACEABILITY.csv`
- `FINAL_REFERENCE_AUDIT.json`
- `AUDITED_METADATA_USED.csv`
- `CHECKSUMS.csv`

Pass the first and third files to the manuscript renderer. The renderer copies
the BibTeX file into its anonymous render directory. Do not manually edit any
generated artifact.

## Fail-closed boundaries

The generator rejects a citation unless it is DOI-audit `PASS`, has verified
title/year/venue metadata, and has a supported publication classification. It
also requires an explicit boundary for protocols, preprints, workshops, and
systematic reviews. A protocol cannot be used as completed outcome evidence;
a preprint must be labelled as not peer reviewed. The reference audit is
bibliographic provenance, not permission to strengthen a source's scientific
claim.
