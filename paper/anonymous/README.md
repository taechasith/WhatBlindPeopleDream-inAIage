# Anonymous CHI 2027 poster-paper scaffold

This directory is source infrastructure only. It is not a submission and must
not be rendered, shared, or uploaded as a completed paper before
`RESULTS_FREEZE` and the checks in `RESULTS_FREEZE_AUDIT.md` pass.

## Layout

- `main.tex` uses the anonymous single-column ACM review configuration specified
  in the current CHI 2027 poster preflight: `manuscript,review,anonymous`.
- `references.bib` is intentionally empty until every cited source is verified
  in the DOI/reference audit.
- `RESULTS_FREEZE_AUDIT.md` records the required inputs before drafting claims,
  tables, figures, abstract text, or an A0 poster.

## Filling the source after the analysis gate

1. Confirm that `RESULTS_FREEZE` exists, is committed, and that every number is
   traceable to its ledger-backed machine-readable output.
2. Use only result figures with accessible alt text, exact N, uncertainty where
   applicable, and non-color-only encodings.
3. Describe synthetic annotation as computational/model-derived measurement;
   retain the bounded scope of any external public-human calibration.
4. Cite verified prior work normally in the third person. Do not use anonymous
   citation placeholders.
5. Run anonymity, metadata, reference, accessibility, and CHI preflight audits
   after the final PDF and A0 poster are built.

## Reproducible post-freeze fact packet

Do not type empirical values into the manuscript from a terminal, spreadsheet,
or memory. After the immutable `RESULTS_FREEZE` exists, generate an anonymous
fact packet and numeric LaTeX macros with:

```powershell
python code/31_build_paper_fact_packet.py `
  --results-freeze results/results_freeze/RESULTS_FREEZE.json `
  --outdir paper/anonymous/generated
```

The command fails unless the freeze receipt, upstream provenance receipts,
results ledger, table hashes, row counts, canonical schemas, and canonical
artifact paths reconcile. It produces `paper_fact_packet.json`,
`paper_fact_packet.csv`, `results_macros.tex`, and a checksum manifest. The
packet is data only: it does not select results, interpret effects, or write
empirical prose. It does not by itself complete `RESULTS_FREEZE_AUDIT.md`;
complete that audit before interpreting facts or drafting the paper. Never
manually alter generated artifacts; regenerate them from the frozen ledger.

## Review-stage anonymity

Do not add names, affiliations, emails, acknowledgements, institutional details,
personal/repository links, local paths, author-identifying source comments, or
identifying PDF metadata. Keep raw corpora, private mappings, and the working
repository outside the anonymous review bundle.

The live call currently indicates a four-page review paper excluding references
and a required A0 poster. Recheck the current official call before upload,
including its noted wording inconsistency about page limits.
