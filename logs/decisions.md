# Research decisions

## 2026-10-05 -- Protocol freeze

- **Decision:** Freeze BD-AI-CHI27-v1.0 before data acquisition or outcome inspection.
- **Basis:** Governing research guide Phase 0.
- **Outcome visibility at decision:** No project data acquired or inspected.
- **Consequence:** Changes to primary outcomes, populations, ontology, or analysis family require a deviation record.

## 2026-10-05 -- Novelty position refined

- **Decision:** Do not claim priority for any individual literature layer. Retain the project only as a proposed shared-ontology, cross-domain public-data audit.
- **Basis:** Phase 1 closest-work comparison.
- **Outcome visibility at decision:** No project dataset outcomes inspected.
- **Consequence:** All later claims must be limited to the joint comparison actually completed.

## 2026-10-05 -- Separate causal experiment from observational audit

- **Decision:** Treat the public-data audit as Study 0 hypothesis generation;
  adopt Study 1 only as a separately preregistered prospective experiment with
  an unexposed false-source control, not as a reinterpretation of Study 0.
- **Basis:** An exposed-default versus exposed-steered comparison alone could
  estimate form differences but could not test whether pre-sleep exposure itself
  predicts later dream incorporation.
- **Outcome visibility at decision:** Study 0 exploratory candidate-label
  diagnostics had been observed; no Study 1 data exist.
- **Consequence:** No recruitment or pilot data collection before an institutional
  determination, finalized accessibility/safety materials, and power analysis.

## 2026-10-05 -- Study 1 conservative provisional enrollment target

- **Decision:** Plan for 200 enrolled adults in 50 complete Latin-square blocks,
  anticipating 180 completions under the planning attrition assumption.
- **Basis:** Study 0 was excluded from effect-size selection. A synthetic
  1,000-repetition participant-cluster proxy at N=200 produced 0.944 power for
  the prespecified OR=1.5 scenario; the completed small R GLMM diagnostic showed
  N<=120 was inadequate for that smallest scenario.
- **Outcome visibility at decision:** no Study 1 participant data exist.
- **Consequence:** Before recruitment, expand/re-run the R GLMM simulation to at
  least 1,000 repetitions. It may retain or increase but not outcome-tune the
  target.

## 2026-10-06 -- Replace current CHI human-study scope with public-data intervention

- **Decision:** The active CHI 2027 submission is a public-data study comparing
  DreamSpace, IntentSpace, HumanSpace, and AISpace, with a within-item,
  prompt-condition intervention on released VizWiz image-question pairs.
- **Basis:** The public data can identify changes in AI output caused by
  BLV-originating question context without asserting unmeasured effects on
  people, dreams, or brains. The live CHI 2027 Posters call explicitly accepts
  quantitative, methodological, and self-contained short studies.
- **Outcome visibility at decision:** Historical Study 0 exploratory outputs
  had been observed. No output from the new computational intervention exists.
- **Consequence:** The old prospective human protocol is future work only;
  `PROTOCOL_PUBLIC_DATA_v2.md` and `PUBLIC_DATA_ANALYSIS_PLAN_v2.md` govern
  the current submission. New primary outcomes are not retroactively applied
  to Study 0.

## 2026-10-06 -- Hold computational outcomes at the VLM compute gate

- **Decision:** Do not select or run a VLM until a permitted model, immutable
  revision, license, runtime, deterministic decoding record, and authorized
  compute route are recorded before output inspection.
- **Basis:** The local audit found a GPU but a CPU-only PyTorch runtime and no
  qualifying local VLM checkpoint. Placeholder text, an unpinned hosted model,
  or a single undocumented interactive response would violate the frozen
  intervention design.
- **Outcome visibility at decision:** No new computational-intervention output
  has been generated or inspected.
- **Consequence:** Source acquisition, packet/code preparation, and synthetic
  dry runs may continue. RQ2--RQ5 effects, external validation, final figures,
  and manuscript results remain `NOT_ESTIMABLE` until the gate is met.

## 2026-10-09 -- Use computational measurement with public-human calibration

- **Decision:** Complete the current CHI submission as a zero-new-human-data
  public-data computational study. Synthetic panel outputs are model-derived
  computational measurements, not replacements for human annotation. Current
  gating is computational robustness plus separate, bounded calibration against
  released public human evidence.
- **Basis:** The controlled intervention concerns model-output differences under
  released BLV-originating questions. The study makes no synthetic-human
  equivalence claim and therefore does not require or run the Alternative
  Annotator Test.
- **Outcome visibility at decision:** No condition mapping, condition-level
  RQ2--RQ5 result, or label pattern by condition was accessed.
- **Consequence:** The former three-coder workflow is retained under
  `future_human_validation/`; `ALT_TEST_CURRENT_STUDY` is
  `NOT_APPLICABLE_TO_CURRENT_DESIGN`; constructs must be classified prospectively
  as computationally observable, public-human benchmarked, or model-derived
  exploratory before condition unblinding.

## 2026-10-09 -- Freeze post-gate computational analysis implementation

- **Decision:** Before coded-data freeze and before condition unblinding,
  freeze an executable analysis configuration for the one permitted unblinding.
  It reports synthetic judges separately, applies paired cluster bootstrap and
  paired sign-flip inference, uses BH correction within judge and contrast for
  the primary construct family, and labels released-answer/caption comparisons
  as bounded human-reference alignment.
- **Basis:** The public-data protocol already specifies within-item contrasts,
  model-specific reporting, bootstrap uncertainty, and a distinction between
  human-reference alignment and BLV preference. The executable version makes
  those choices inspectable before outcomes are read.
- **Outcome visibility at decision:** No condition mapping, synthetic-label
  pattern by condition, RQ2--RQ5 effect, or final human-reference comparison
  was accessed.
- **Consequence:** `config/post_freeze_analysis_v1.json`,
  `POST_FREEZE_ANALYSIS_PROTOCOL_v1.md`, and
  `code/27_run_post_freeze_public_analysis.py` may execute only after
  `CODED_DATA_FROZEN_PUBLIC_DATA_ONLY`. The resulting metrics cannot license
  claims of semantic correctness, BLV preference, human usefulness, or lived
  experience.
