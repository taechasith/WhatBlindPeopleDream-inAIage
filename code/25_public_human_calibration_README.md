# Public human-calibration receipt

Run `python code/25_build_public_human_calibration_matrix.py` after an
authorized refresh of the public-reference sources. It writes
`results/public_human_calibration_matrix.csv`, a metadata-only provenance and
source-readiness receipt. Run with `--check` to validate without rewriting the
receipt.

The checker permits only these inputs:

- `PUBLIC_HUMAN_CALIBRATION_MATRIX.csv` and
  `CONSTRUCT_MEASUREMENT_TIER_MATRIX.csv`;
- `data/PUBLIC_DATA_SOURCE_GATE.csv`, `data/MANIFEST.csv`, and
  `data/CHECKSUMS.csv`;
- `data/public_reference/processed/build_manifest.json` plus the three
  allowlisted public VizWiz-Captions/Kapur source files and the two derived
  public-reference CSVs.

It byte-hashes files and reads CSV headers only for derived tables. It validates
one calibration-boundary row for every frozen construct/layer while allowing
separately labelled `external_validation_context` rows. It does not
open, enumerate, join, or analyze primary outputs, condition mappings,
synthetic labels, human-coder files, private paths, or annotation packets. The
receipt must therefore never be reported as a human-validation result,
condition effect, calibration estimate, or synthetic-human equivalence test.

GuideDog remains `NOT_ESTIMABLE_ACCESS_UNAVAILABLE` unless authorized access
is independently documented and a prospective source-and-method amendment is
made. Do not bypass gated access, scrape, or replace it with synthetic labels.
Be My AI / Xie et al. remains `NOT_ESTIMABLE_DESCRIPTIVE_ONLY` for calibration:
it may supply ecological context only and is not a gold-label, same-item,
prevalence, preference, or generalizable-estimate source.

The receipt is a pre-unblinding gate. The current public-data-only study does
not require new human coding, adjudication, reliability, or an Alternative
Annotator Test. It still requires computational robustness, construct-strength
decisions, provenance, and `CODED_DATA_FREEZE` before condition unblinding.
