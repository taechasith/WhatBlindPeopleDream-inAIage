# Alternative Annotator Test implementation audit

**Checked:** 2026-10-08 (Asia/Bangkok)
**Purpose:** pre-human-label implementation/provenance check only. No study
labels, condition mapping, or model-effect result was used.

## Official implementation identified

- Repository: https://github.com/nitaytech/AltTest
- Default branch: `main`
- Resolved `HEAD` on check date: `18428b1f4f34ac61c4978bc180263b90111e7337`
- Official materials advertised by the repository: Python implementation and
  `alt_test_example.ipynb`.
- Frozen project policy: primary epsilon is `0.10`; this audit does not alter
  that policy.

## License/use status

GitHub's repository metadata returned no SPDX license identifier and the root
listing did not identify a license file on the check date. Therefore the source
has **not** been vendored, copied into this repository, modified, or executed
on research labels.

Status: `LICENSE_UNSPECIFIED_FOR_LOCAL_EXECUTION_OR_REDISTRIBUTION`.

Before running the official code on locked human/model labels, record a
permitted route for local use (for example, an explicit upstream license,
written permission, or another official distribution with applicable terms).
Do not replace it with an improvised approximation. This is a legal/provenance
gate, independent of and subsequent to the human-coder gate.

## Required future environment record

Once a permitted route exists, record before execution:

- immutable upstream commit or release;
- license/permission locator and date;
- Python and SciPy versions;
- command and input schema;
- a non-analytic toy-fixture smoke test;
- epsilon `0.10`, multiplicity method, and construct applicability handling;
- checksums for the exact local source snapshot and result files.

The official repository states that the test requires annotations from at least
two humans and recommends at least three for a stronger consensus reference.
This project retains the stricter three-human policy already frozen in its
annotation governance.
