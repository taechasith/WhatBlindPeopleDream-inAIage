# External Validation Preflight Receipt

**Status:** completed without accessing blinded primary-output content,
condition mapping, human-coder files, or outcome effects.

## Reproducibility checks

`code/05_build_public_reference_corpora.py` was regenerated using the base
analysis Python environment because the isolated VLM environment intentionally
does not include the optional Excel reader dependency. This did not modify the
running VLM environment or any frozen model output.

| Derived source table | SHA-256 | Scope |
|---|---|---|
| `data/public_reference/processed/vizwiz_captions_val.csv` | `c6d344ca2b44524f34da14f4c3c836fe215cbbac1792323e2539a4d0e0561f70` | Released VizWiz Captions validation annotations |
| `data/public_reference/processed/kapur_preference_ratings.csv` | `7f180c1fc98c742b868ec4ce2d4ddd938af25056cf652d08ba1323d501f6c4df` | Released Kapur--Kreiss aggregate comparison ratings |

The regenerated build manifest records both input and derived-output hashes:
`data/public_reference/processed/build_manifest.json`.

`code/verify_provenance.py --allow-missing` passed all eight recorded raw
source checksums on 2026-10-08.

## Pre-label decisions

- VizWiz captions remain HumanSpace references, not universal ground truth or
  BLV preference labels.
- Multiple captions are handled at the image/question-item level under
  `EXTERNAL_VALIDATION_POLICY_v1.md`.
- Kapur--Kreiss comparison sets remain separate and `Spice` is
  `NOT_ESTIMABLE`.
- GuideDog remains `ACCESS_UNAVAILABLE`.
- Be My AI/Xie remains an ecological descriptive check only.

No external source substitutes for the same-item three-human validation subset.
