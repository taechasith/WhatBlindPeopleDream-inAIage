# Substantive AI-use log

## Status

This log distinguishes documented use from unknown provenance. It is not
complete merely because a task is absent from the table. Before any conference
submission, the research team must reconcile all substantive assistance with
the then-current conference and publisher policy and produce the required
disclosure. No AI system is an author.

| Record | Workflow activity | System/version | Evidence in repository | Status and publication handling |
| --- | --- | --- | --- | --- |
| AI-001 | Automated candidate coding of Study 0 text | No generative model; deterministic lexical rules | `logs/model_use.md`; `code/04_apply_codebook.py` | Documented. May be described only as exploratory automated lexical coding, never human annotation or semantic ground truth. |
| AI-002 | Non-human future human-study VLM candidate screen | SmolVLM2 2.2B at pinned revision `482adb537c021c86670beed01cd58990d01e72e4`; deterministic local run | `future_human_study/MODEL_CANDIDATE_EVALUATION.md`; ignored private candidate outputs/audit | Rejected for exposure after marker-coverage and length failures. Not a participant result or a model-effect finding. |
| AI-003 | Future human-study VLM candidate preparation | Qwen2.5-VL 7B at pinned revision `cc594898137f460bfe9f0759e9844b3ce807cfb5`; candidate-only preparation | `future_human_study/code/generate_study1_qwen_candidates.py`; `future_human_study/MODEL_PROVENANCE.md` | Artifact verified, but no complete local CPU-only output was written; requires a deterministic run on suitable hardware and fail-closed audit. Not selected for exposure or participant-facing. |
| AI-004 | Literature, drafting, coding, analysis, or figure assistance during repository development | Not fully reconstructable from the current repository | No complete tool/version/prompt provenance is present | Disclosure status unresolved. Do not state that no generative-AI assistance occurred; reconcile the research record before submission. |
| AI-005 | Active public-data computational intervention | `Qwen/Qwen2.5-VL-3B-Instruct`, immutable revision `66285546d2b821cf421d4f5eb2576359d3770cd3`; deterministic local CUDA execution | `compute/MODEL_FREEZE.md`; `MODEL_OUTPUT_FREEZE.md`; `data/model_outputs/OUTPUT_MANIFEST.csv`; `data/model_outputs/CHECKSUMS.csv` | Documented 1,000-item x 3-condition run with 3,000 frozen primary outputs. Designated automated blinded scripts may process protected artifacts for technical and robustness audits; before `CODED_DATA_FREEZE`, no human-readable label substance, private mapping, or condition-level inspection is authorized, and RQ2--RQ5 remain unauthorized. |
| AI-006 | Blinded synthetic annotation panel for computational measurement | `microsoft/Phi-3.5-mini-instruct` and `Qwen/Qwen2.5-1.5B-Instruct`, each pinned in `config/synthetic_annotation_panel_v1.json`; deterministic local execution | `compute/SYNTHETIC_PANEL_FREEZE.md`; `code/15_run_synthetic_annotation_panel.py`; `code/16_freeze_synthetic_panel_outputs.py` | Frozen judges produce model-derived computational measurements, not human coding or human labels. New independent human A/B/C files, adjudication, reliability, and AltTest are not current prerequisites for the public-data-only scope. `future_human_validation/` retains those future safeguards separately; they cannot retroactively convert a computational measurement into human-validated evidence. |

## Required completion checks

- Add a dated record for every substantive tool-assisted literature search,
  extraction, code generation, stimulus generation, annotation assistance,
  manuscript drafting, and figure generation.
- Record the human verification performed and the output artifacts affected.
- When a released human label, rating, or reference calibrates a public-data
  measurement, record its source, unit, provenance, and matched measurement
  target separately; do not describe it as new coding or general human
  equivalence.
- Do not list routine spellchecking unless the applicable policy requires it.
- Do not use a model output as a participant, an independent coder, or an
  empirical result.
