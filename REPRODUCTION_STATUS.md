# Reproduction status

**Checked:** 2026-10-09 (Asia/Bangkok)
**Overall status:** `PARTIAL_REPRODUCTION`

`PARTIAL_REPRODUCTION` is used because raw Study 0 corpora are intentionally not
versioned and a clean-clone rerun against authorized local inputs has not been
archived. The historical future-human-study power material is not a dependency
of the active public-data submission.

The 2026-10-09 scope correction removes new human coding, adjudication,
reliability calculation, and an Alternative Annotator Test (AltTest) as current
dependencies of public-data computational measurement. It does not open private
condition mappings or permit human-readable label substance or condition-level
inspection before `CODED_DATA_FREEZE`, or authorize RQ2--RQ5. Designated
automated blinded scripts may process protected artifacts for technical and
robustness audits.
Released human references remain source-specific calibration inputs, not newly
collected coding or a general human-equivalence claim.

| Component | Status | Evidence / remaining condition |
| --- | --- | --- |
| Study 0 source provenance | PARTIAL_REPRODUCTION | Manifest, license register, and hashes exist for local snapshots; source data must be independently acquired under their terms. |
| Study 0 processing | PARTIAL_REPRODUCTION | Tracked scripts name local inputs, but no clean-environment regeneration log is archived. |
| Study 0 exploratory analysis | PARTIAL_REPRODUCTION | Aggregate outputs are tracked and labeled exploratory; no human semantic-label or reliability claim is made. |
| Active public-data source inputs | PARTIAL_REPRODUCTION | VizWiz validation images and annotations, caption annotations, Kapur ratings, frozen 1,000-item sample, and input-validation manifest are locally acquired/validated; raw content remains excluded from Git. |
| Active public-data computational measurement | SCOPE_CORRECTED_BLINDED | Current work is limited to blinded computational measurement and documented source-specific public-human calibration; new human coding or AltTest is not a prerequisite. |
| Active public-data intervention outputs | FROZEN_BLINDED_COMPUTE_ONLY | A locally reproducible, pinned Qwen2.5-VL-3B run generated and froze 3,000 primary outputs for the locked 1,000-item sample. Designated automated scripts may process protected artifacts for technical and robustness audits; before `CODED_DATA_FREEZE`, no human-readable label substance, private mapping, or condition-level inspection is authorized, and RQ2--RQ5 remain unauthorized. |
| Synthetic annotation panel | RUNNING_BLINDED_COMPUTATIONAL_MEASUREMENT | Phi-3.5-mini and Qwen2.5-1.5B are active model-derived computational instruments, not human coders. Their outputs remain condition-blinded until the technical freeze, robustness audit, public-human calibration, and `CODED_DATA_FREEZE` are complete. |
| Future human validation archive | RETAINED_NONACTIVE | `future_human_validation/` preserves planned independent coding, adjudication, and AltTest materials for a possible future human study; it cannot retroactively validate current computational measurements. |
| Future human-study synthetic pipeline | HISTORICAL_NONEMPIRICAL | Isolated under `future_human_study/`; no participant data exist. |
| Anonymous review export | PARTIAL_REPRODUCTION | An allowlisted, non-writing checker is supplied; final archive, PDF, and link review have not occurred. |

No component may be described as `CLEAN_REPRODUCTION_PASSED` until a fresh,
documented environment regenerates the relevant permitted outputs and records
all unresolved external dependencies.
