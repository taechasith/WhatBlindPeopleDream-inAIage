# Phase 5 pre-human packet and literature update

## STATUS

`SYNTHETIC_PANEL_RUNNING; HUMAN_CODERS_PENDING; CONDITIONS_BLINDED`.

## WHAT WAS DONE

- Issued a distribution-ready human-coder packet v1.1 that byte-preserves the
  frozen 600 analytic rows and sheets while pinning the codebook, instructions,
  attestation, return protocol, adjudication protocol, and per-coder receipt.
- Corrected only malformed quotation characters and an ambiguous return-file
  instruction; no construct, label option, sample, row order, output, prompt,
  model, judge, or condition changed.
- Updated the closest-work and DOI audit with verified 2025--2026 comparators.
  The record now explicitly rejects a novelty claim that BLV questions have
  never been used to guide MLLM descriptions.
- Corrected active public-data wording from `preregistered` to `frozen` /
  `pre-specified`, because no dated public registration receipt is documented.

## FILES CREATED OR MODIFIED

- Commit `c5da170`: v1.1 package builder, fail-closed locking expectations,
  codebook/instructions/attestation/return/runbook materials, and amendment.
- Pending literature-audit commit: closest-work records, evidence matrices,
  candidate library, DOI audit, and reproducible updater.

## N / SAMPLE COUNTS

- v1.1 data are byte-identical to v1: 200 locked items x 3 blinded outputs =
  600 rows. Subset SHA-256:
  `cf9d6207fbd71d0777230d8675a020be6bd96fe3eb658f8816a16d31aadce0cd`.
- No genuine coder return exists. No human or synthetic label was used as a
  scientific result.

## KEY CHECKS

- The v1.1 builder verifies base checksums before byte copying; package
  validation reported zero mechanical errors across 600 rows and 26 artifacts.
- CSV schema audit found no malformed rows or duplicate paper IDs after the
  literature update.
- No condition mapping or condition-level model-output effect was opened.

## PROBLEMS

- Synthetic panel completion and its technical freeze are still pending.
- Three genuine independent human coder files remain required.
- Official Alt-Test code remains unusable locally until an explicit license or
  permission route exists; no reimplementation is authorized.

## DECISIONS REQUIRED

No routine decision is required. Do not distribute v1; distribute only v1.1
when ethics sequencing permits independent coding.

## NEXT PHASE

Finish and technically freeze the blinded synthetic panel, then wait for A/B/C
genuine human coder files. Do not unblind, adjudicate, scale synthetic labels,
or run RQ2--RQ5 first.
