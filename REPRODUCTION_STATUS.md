# Reproduction status

**Checked:** 2026-10-08 (Asia/Bangkok)
**Overall status:** `PARTIAL_REPRODUCTION`

`PARTIAL_REPRODUCTION` is used because raw Study 0 corpora are intentionally not
versioned and a clean-clone rerun against authorized local inputs has not been
archived. The historical future-human-study power material is not a dependency
of the active public-data submission.

| Component | Status | Evidence / remaining condition |
| --- | --- | --- |
| Study 0 source provenance | PARTIAL_REPRODUCTION | Manifest, license register, and hashes exist for local snapshots; source data must be independently acquired under their terms. |
| Study 0 processing | PARTIAL_REPRODUCTION | Tracked scripts name local inputs, but no clean-environment regeneration log is archived. |
| Study 0 exploratory analysis | PARTIAL_REPRODUCTION | Aggregate outputs are tracked and labeled exploratory; completed human coding/reliability are absent. |
| Active public-data source inputs | PARTIAL_REPRODUCTION | VizWiz validation images and annotations, caption annotations, Kapur ratings, frozen 1,000-item sample, and input-validation manifest are locally acquired/validated; raw content remains excluded from Git. |
| Active public-data intervention outputs | FROZEN_MEASUREMENT_VALIDATION_PENDING | A locally reproducible, pinned Qwen2.5-VL-3B run generated and froze 3,000 primary outputs for the locked 1,000-item sample. Condition mapping remains private; no RQ2--RQ5 result has been opened. |
| Synthetic annotation panel | RUNNING_BLINDED | Phi-3.5-mini and Qwen2.5-1.5B are frozen judges; their outputs remain model-derived and cannot support confirmatory claims until same-item human validation. |
| Future human-study synthetic pipeline | HISTORICAL_NONEMPIRICAL | Isolated under `future_human_study/`; no participant data exist. |
| Anonymous review export | PARTIAL_REPRODUCTION | An allowlisted, non-writing checker is supplied; final archive, PDF, and link review have not occurred. |

No component may be described as `CLEAN_REPRODUCTION_PASSED` until a fresh,
documented environment regenerates the relevant permitted outputs and records
all unresolved external dependencies.
