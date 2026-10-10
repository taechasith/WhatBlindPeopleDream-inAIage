# Pre-results anonymous reference-selection binder

`code/35_build_reference_selection.py` binds the exact six predeclared
anonymous citation keys from `config/manuscript_render_plan_policy_v1.json`
to audited DOI records only after `RESULTS_FREEZE` exists. It is intentionally
not a result interpreter and does not read a results ledger, result table, raw
output, synthetic label, or private condition mapping.

## Frozen selection

The policy is [reference_selection_policy_v1.json](../config/reference_selection_policy_v1.json).
It contains exactly these citation keys, in order:

1. `KANG2023`
2. `XIE2025`
3. `KREISS2022`
4. `KAPUR2024`
5. `GUIDEDOG2026`
6. `PATARANUTAPORN2025`

Each has a bounded use and an evidence boundary. `KAPUR2024` remains explicitly
identified as a peer-reviewed workshop article. The policy cannot be expanded
or ranked after results are seen.

## Static pre-results check

```powershell
python code/35_build_reference_selection.py --check-policy
```

This validates only the frozen citation mapping against the local DOI audit and
metadata snapshots. It reads no `RESULTS_FREEZE` receipt and writes nothing.

## Post-results binding

```powershell
python code/35_build_reference_selection.py `
  --results-freeze results/results_freeze/RESULTS_FREEZE.json
```

The command requires a completed public-data `RESULTS_FREEZE` receipt, binds
its SHA-256, and atomically creates the immutable artifacts below. It reads
only that receipt JSON—not the result ledger or any result values.

- `refs/reference_selection.json` — input compatible with
  `code/33_generate_audited_references.py`.
- `refs/reference_selection_manifest.json` — scope and provenance receipt.
- `refs/reference_selection_checksums.csv` — artifact checksums.

The later audited-reference generator independently validates the full results
ledger before it produces a BibTeX bundle. This separation keeps citation
selection from becoming outcome-driven.
