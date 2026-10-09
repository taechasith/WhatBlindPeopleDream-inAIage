# Automated coding record

- Date: 2026-10-05
- Method: deterministic lexical rules in `code/04_apply_codebook.py`, grounded in frozen CSO category labels.
- Model: none. This is not an LLM/RAG output and is not human annotation.
- Settings: Python standard library; no stochastic inference.
- Permitted use: candidate-label exploration and diagnostic distributions only.
- Prohibited use: claims of semantic understanding, lived human experience, or
  replacement for independent coders.

## 2026-10-09 -- Active synthetic computational measurement panel

- Frozen instruments: `microsoft/Phi-3.5-mini-instruct` (primary) and
  `Qwen/Qwen2.5-1.5B-Instruct` (secondary sensitivity), as pinned in
  `config/synthetic_annotation_panel_v1.json`.
- Permitted use: blinded, evidence-span-audited measurement of bounded textual
  properties; inter-model disagreement and computational robustness analyses.
- Prohibited use: claims that synthetic labels are human judgments, BLV ratings,
  preference, lived experience, or interchangeable with human coding.
- Current-study status: the Alternative Annotator Test is not applicable because
  the study makes no synthetic-human equivalence claim. Public human-labelled
  datasets provide separate external calibration only.
- Blinding boundary: designated automated scripts may process protected artifacts
  for technical and robustness audits. Before `CODED_DATA_FREEZE`, no
  human-readable label substance, private condition mapping, or condition-level
  inspection is permitted.
- Future boundary: `future_human_validation/` retains independent-coding,
  adjudication, and AltTest materials for possible future human-study claims. It
  is not a current prerequisite and cannot retroactively validate model-derived
  measurements.
