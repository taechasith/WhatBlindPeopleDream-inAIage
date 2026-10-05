# Reproduction status

**Checked:** 2026-10-05 (Asia/Bangkok)  
**Overall status:** `PARTIAL_REPRODUCTION`

`PARTIAL_REPRODUCTION` is used because raw Study 0 corpora are intentionally not
versioned, a clean-clone rerun against authorized local inputs has not been
archived, and the authoritative Study 1 R power model is not available in the
current environment.

| Component | Status | Evidence / remaining condition |
| --- | --- | --- |
| Study 0 source provenance | PARTIAL_REPRODUCTION | Manifest, license register, and hashes exist for local snapshots; source data must be independently acquired under their terms. |
| Study 0 processing | PARTIAL_REPRODUCTION | Tracked scripts name local inputs, but no clean-environment regeneration log is archived. |
| Study 0 exploratory analysis | PARTIAL_REPRODUCTION | Aggregate outputs are tracked and labeled exploratory; completed human coding/reliability are absent. |
| Study 1 synthetic Python/R pipeline | PARTIAL_REPRODUCTION | A labeled end-to-end synthetic dry run, schema tests, R GLMM, and session records pass locally; it is not an empirical analysis path or a clean-clone validation. |
| Study 1 R power simulation | LOCALLY_REPRODUCED_NONEMPIRICAL | 1,000-repetition GLMM simulation at 208 allocation slots ran under R 4.6.1/lme4 2.0-6; outputs and session information are tracked. |
| Study 1 human-data analysis | NOT_APPLICABLE | No participant data exist and no activity is authorized while ethics status is `NOT_SUBMITTED`. |
| Anonymous review export | PARTIAL_REPRODUCTION | An allowlisted, non-writing checker is supplied; final archive, PDF, and link review have not occurred. |

No component may be described as `CLEAN_REPRODUCTION_PASSED` until a fresh,
documented environment regenerates the relevant permitted outputs and records
all unresolved external dependencies.
