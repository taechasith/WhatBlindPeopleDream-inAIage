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
| AI-005 | Active public-data computational intervention | No VLM selected or executed | `PUBLIC_MODEL_COMPUTE_GATE.md`; `config/public_vlm_models.example.json`; `code/08_validate_public_intervention_outputs.py` | No generated output exists. The repository contains only prompt templates, a fail-closed manifest/output validator, and source-input checks. |

## Required completion checks

- Add a dated record for every substantive tool-assisted literature search,
  extraction, code generation, stimulus generation, annotation assistance,
  manuscript drafting, and figure generation.
- Record the human verification performed and the output artifacts affected.
- Do not list routine spellchecking unless the applicable policy requires it.
- Do not use a model output as a participant, an independent coder, or an
  empirical result.
