# Human coder return and independence protocol v1

This administrative protocol is frozen before human labels exist. It supplements
the analytic coding packet without changing its 600 rows, row order, rubric, or
condition blinding.

## Required return materials

Each coder returns two separate files:

1. the completed coding sheet with exactly the distributed schema and rows; and
2. one completed copy of `HUMAN_CODER_INDEPENDENCE_ATTESTATION_TEMPLATE.csv`.

The coder uses the assigned pseudonymous ID consistently in both files. The
attestation must state `YES` for independent work, no condition metadata, no
synthetic labels, no other coder labels, and no LLM co-coder. It also records
the hashes of the distributed packet/materials and an ISO-8601 completion time.

## Locking sequence

The coding lead saves original received files unchanged, then runs
`code/17_lock_human_coder_files.py`. The tool is fail-closed: it rejects altered
rows/text/schema, noncanonical values, missing/duplicate coder identities,
missing attestations, or material-hash mismatches. A successful lock is an
atomic directory containing byte-identical locked copies, validation/missingness
reports, checksums, and `LOCK_COMPLETE.json`.

If an obvious clerical correction is needed, preserve the received original,
create a separately named corrected derivative, and log the exact reason before
rerunning a new lock. Never edit a completed locked raw file.

## Boundary

This protocol does not demonstrate that an attestation is truthful; it preserves
the documented independent-work claim and makes any missing provenance visible.
No condition map, synthetic-label file, or RQ2--RQ5 result is part of the return
or locking workflow.
