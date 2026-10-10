# Final Anonymous CHI Package Audit

This is a post-results control for the anonymous CHI poster submission. It is
not a scientific analysis step and must not be used before `RESULTS_FREEZE`.
The audit verifies the final package without re-running the study or opening
private condition mappings.

## What the audit checks

- The final `RESULTS_FREEZE` and every ledger-backed table reconcile by hash
  and recorded row count.
- The paper fact packet is tied to that exact freeze.
- Every reported numerical assertion has a `CLAIM-ID` and maps to a frozen fact
  packet row through `CLAIM_TRACEABILITY.csv`.
- The anonymous manuscript/poster sources and PDFs have no author, affiliation,
  email, personal repository, or locally-defined identity pattern.
- Causal language that would overclaim dream, cognitive, brain, or human-
  equivalence effects is rejected. Explicitly negative limitation language is
  reported for review rather than treated as a violation.
- The five final figures have matching hashes, useful standalone alt text, and
  no externally loaded resources.
- The bibliography cites only records reconciled to the DOI audit, with an
  explicit evidence boundary per citation.
- The manuscript page accounting, poster A0 geometry, PDF metadata, and
  reproducibility/provenance artifacts are present.

Passing the program is necessary but not sufficient for submission. Recheck the
live CHI call, upload-form requirements, and accessibility of rendered PDFs
before upload.

## Required ledgers created after results freeze

Create the following with real content only. Do not enter planned values or
invented facts.

### `paper/anonymous/CLAIM_TRACEABILITY.csv`

Use the exact header below. One row represents one displayed numerical value.
If one prose sentence reports several values, give each value its own row with
the same `claim_id`.

```csv
claim_id,delivery,location,fact_id,source_column,reported_value,rounding_decimals,claim_type,measurement_status,claim_boundary
```

- `claim_id`: stable ID such as `C001`. In `main.tex`, place exactly one source
  marker immediately before its claim: `% CLAIM-ID: C001`.
- `delivery`: `paper` or `poster`.
- `location`: source location, e.g., `main.tex:84` or
  `POSTER_CONTENT.json:sections.findings[1]`.
- `fact_id`: a `fact_id` from the generated `paper_fact_packet.csv`.
- `source_column`: the numerical column in that fact row.
- `reported_value`: the literal displayed number only (not `N=` or `p <`).
- `rounding_decimals`: non-negative integer if rounded, or `EXACT` for an
  unrounded string/integer.
- `claim_type`: concise value such as `effect`, `ci`, `n`, `p_value`, or
  `distance`.
- `measurement_status`: copied from the appropriate frozen fact row.
- `claim_boundary`: a concise scope statement, e.g.,
  `computational output property; not human judgment`.

### `paper/anonymous/REFERENCE_TRACEABILITY.csv`

Use the exact header below and include every cited BibTeX key exactly once.

```csv
citation_key,paper_id,doi,doi_audit_status,classification,claim_use,evidence_boundary
```

`paper_id`, DOI, status, and classification must match `refs/doi_audit.csv`.
For a protocol, preprint, workshop, or methodological precedent, the
`evidence_boundary` must state the narrower use. Never use `BLINDREAM2025` as
completed outcome evidence.

### `paper/anonymous/PAGE_ACCOUNTING.json`

Use this exact JSON shape after rendering the anonymous review PDF:

```json
{
  "main_pages_excluding_references": 4,
  "reference_pages": 1,
  "total_pdf_pages": 5,
  "call_checked_date": "YYYY-MM-DD",
  "call_url": "https://chi2027.acm.org/authors/posters/"
}
```

The audit requires the main section to be at most four pages and cross-checks
the total against the PDF page count. The live call must be checked again at
submission time.

## Run after paper and poster builds

Generate the fact packet first:

```powershell
python code/31_build_paper_fact_packet.py `
  --results-freeze results/results_freeze/RESULTS_FREEZE.json `
  --outdir paper/anonymous/generated
```

Then run the audit in a new immutable output directory. The private patterns
file is local, Git-ignored, and is never copied into the review package.

The PowerShell wrapper below supplies these same canonical paths and may be
used when the final filenames remain unchanged:

```powershell
./compute/run_final_anonymous_package_audit.ps1
```

Or invoke the Python program directly:

```powershell
python code/32_audit_final_anonymous_package.py `
  --results-freeze results/results_freeze/RESULTS_FREEZE.json `
  --fact-packet-dir paper/anonymous/generated `
  --claim-ledger paper/anonymous/CLAIM_TRACEABILITY.csv `
  --manuscript-dir paper/anonymous `
  --manuscript-pdf paper/anonymous/build/anonymous_review.pdf `
  --page-accounting paper/anonymous/PAGE_ACCOUNTING.json `
  --figures-dir figures/final_public_data_v1 `
  --poster-content poster/anonymous/POSTER_CONTENT.json `
  --poster-pdf poster/anonymous/build/a0_review/A0_anonymous_poster.pdf `
  --reference-traceability paper/anonymous/REFERENCE_TRACEABILITY.csv `
  --doi-audit refs/doi_audit.csv `
  --identity-patterns private/anonymous_release_forbidden_patterns.txt `
  --outdir audits/final_anonymous_package_v1
```

The required completion state is `FINAL_PUBLICATION_AUDIT_PASS` with no errors.
Warnings are not silent: resolve them or record a concise, evidence-backed
rationale in the final submission checklist.

## Boundaries

- Do not create or alter results while running this audit.
- Do not add raw model output, source images, DreamBank narratives, private
  mapping files, or identity-bearing metadata to anonymous materials.
- Do not treat synthetic measurements as actual human judgments. The audit
  checks wording and provenance; it does not make a computational construct
  human-validated.
- Do not convert a plausible design implication into measured harm, safety,
  preference, or cognitive effect.
