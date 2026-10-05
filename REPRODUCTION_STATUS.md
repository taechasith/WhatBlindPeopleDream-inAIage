# Reproduction status

**Checked:** 2026-10-06 (Asia/Bangkok)
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
| Active public-data source inputs | PARTIAL_REPRODUCTION | VizWiz validation images and annotations, caption annotations, Kapur ratings, frozen 1,000-item sample, and input-validation manifest are locally acquired/validated; raw content remains excluded from Git. |
| Active public-data intervention outputs | BLOCKED_AT_MODEL_COMPUTE_GATE | No authorized frozen executable VLM/runtime exists in the current environment; no intervention output or outcome has been generated. |
| Future human-study synthetic pipeline | HISTORICAL_NONEMPIRICAL | Isolated under `future_human_study/`; no participant data exist. |
| Anonymous review export | PARTIAL_REPRODUCTION | An allowlisted, non-writing checker is supplied; final archive, PDF, and link review have not occurred. |

No component may be described as `CLEAN_REPRODUCTION_PASSED` until a fresh,
documented environment regenerates the relevant permitted outputs and records
all unresolved external dependencies.
