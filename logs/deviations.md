# Protocol deviations

No deviations logged at protocol freeze.

For each later deviation, record: date; original plan; new plan; reason;
whether relevant results had already been seen; and confirmatory/exploratory
status.

## 2026-10-05 -- Add distinct prospective Study 1 after Study 0 audit

- **Original plan:** BD-AI-CHI27-v1.0 was a public-data, cross-domain sensory
  alignment audit and expressly made no causal AI-to-dream claim.
- **New plan:** retain that audit as exploratory Study 0 and add a separately
  preregistered, ethics-approved prospective Study 1 testing immediate
  AI-mediated dream-report incorporation and post-exposure reconstruction.
- **Reason:** targeted evidence review identified distinct empirical precedents
  for nonvisual learning, accessible descriptions supporting internal models,
  and presleep narrative incorporation into dreams. The intersection has not
  been established and is therefore an experimental question, not a conclusion.
- **Relevant results already seen:** yes. Study 0 automated candidate-label
  diagnostics had been observed. Study 1 is explicitly a new confirmatory
  protocol; Study 0 cannot determine Study 1's outcomes or be recast as causal
  evidence.
- **Status:** Study 1 is prospective and blocked before recruitment/data
  collection pending institutional ethics determination, finalized materials,
  and preregistered power analysis.

## 2026-10-05 -- Replace false-source-only control in Study 1

- **Original plan:** v1.0 specified an undisclosed false-source stimulus/marker
  set as the matched control.
- **New plan:** retain false-source foil units as the blinded coding negative
  control and add matched human-reference-description (HUM) and active-neutral-
  narrative (ANC) exposure conditions, yielding four weekly conditions.
- **Reason:** an unexposed foil cannot balance pre-sleep audio, duration, lexical
  content, emotional/spatial information, interaction, or expectancy. The
  revised design permits source and exposure-context contrasts while preserving
  the source-specific primary target-versus-foil test.
- **Relevant results already seen:** no Study 1 outcomes exist; Study 0 results
  remain exploratory and did not set this decision.
- **Status:** prospective protocol amendment; requires ethics review and
  preregistration before use.

## 2026-10-05 -- Formalize Study 1 v2.0 and remove pre-sleep reconstruction rehearsal

- **Phase:** pre-ethics design finalization.
- **Original rule:** v1.0 used a false-source-only control and placed a brief
  reconstruction task before sleep.
- **New rule:** v2.0 formalizes DAI, SAI, HUM, and ANC; retains target/decoy
  scoring as the primary estimand; and prohibits explicit target reconstruction
  between exposure and sleep. A delayed post-report task, if used, is secondary.
- **Reason:** active audio controls improve interpretability, while pre-sleep
  reconstruction would rehearse target material and contaminate the primary
  dream-incorporation exposure.
- **Outcome data existed:** no Study 1 participant outcomes exist.
- **Relevant outcome data inspected:** no Study 1 outcome data; existing Study 0
  exploratory outputs were not used as effect evidence for this choice.
- **Effect on confirmatory status:** preserves a prospective confirmatory primary
  estimand; immediate-reconstruction claims are removed from the main overnight
  confirmatory design.
- **Person/agent making change:** autonomous research execution agent under the
  documented protocol-amendment rule.

## 2026-10-05 -- Correct unavailable Study 0 lexical candidate-label categories

- **Original plan/output:** the exploratory lexical script emitted binary values
  for all 29 codebook columns in every source type, and pairwise diagnostics
  used all columns.
- **New plan/output:** encode unavailable category/source combinations as empty
  applicability values and calculate pairwise lexical diagnostics using only
  columns available for both source groups. `task_relevance`, `intent_match`,
  and `unsupported_information` are excluded from current pairwise profiles;
  each profile uses 26 lexical columns.
- **Reason:** the frozen codebook requires a request/output relationship for
  task relevance and intent match, and a validation basis for unsupported
  information. Those prerequisites are absent for the affected source roles;
  a binary zero would incorrectly mean observed absence.
- **Relevant results already seen:** yes. The earlier 29-column exploratory
  diagnostics had been observed before this audit.
- **Confirmatory/exploratory status:** exploratory correction only. No human
  labels, reliability statistic, model-performance validation, cluster-aware
  inference, or causal conclusion has been created. The current values are
  documented in `STUDY0_REGENERATION_NOTES.md`.

## 2026-10-05 -- Clarify the Study 1 primary mixed-model estimand

- **Phase:** pre-ethics design finalization.
- **Original rule:** some v2 planning prose included a target-by-condition
  interaction and potential delivery covariates in the displayed primary model,
  while the stated primary estimand was the AI-condition-averaged target-versus-
  decoy contrast.
- **New rule:** the primary model is
  `incorporated ~ target_status + condition + period + order + stimulus_block +
  (1 | participant)`. The target-by-condition interaction and any model using
  post-randomization delivery measures are secondary/sensitivity analyses.
- **Reason:** testing the reference-condition coefficient in an interaction
  model would not test the stated AI-condition-averaged estimand. Delivery
  duration, word count, and question count can be components or mediators of
  the intervention package, so primary adjustment could change its causal
  interpretation.
- **Outcome data existed:** no Study 1 participant outcomes exist.
- **Relevant outcome data inspected:** no; only synthetic test fixtures and
  non-empirical power simulations existed.
- **Effect on confirmatory status:** preserves a single, interpretable primary
  contrast and aligns the protocol, power simulation, and analysis code.
- **Person/agent making change:** autonomous research execution agent under the
  protocol-amendment rule.

## 2026-10-05 -- Reject under-grounded local VLM candidate before exposure

- **Phase:** pre-ethics, non-human stimulus-system validation.
- **Original plan:** use a locally reproducible small open-weight VLM candidate
  to generate deterministic default-AI scene descriptions.
- **New plan:** reject `HuggingFaceTB/SmolVLM2-2.2B-Instruct` at revision
  `482adb537c021c86670beed01cd58990d01e72e4` and evaluate a replacement under
  the same prompt, rendering, and fail-closed audit procedure.
- **Reason:** all four non-human candidate outputs were 12--14 words despite a
  60--85 word request and omitted most registered markers; no manual rewrite
  was substituted for model output.
- **Outcome data existed:** no Study 1 participant outcomes exist.
- **Relevant outcome data inspected:** only non-human local model outputs and
  lexical audit rows, all retained under `private/`.
- **Effect on confirmatory status:** none; this prevents an invalid exposure
  system from entering the prospective protocol.
- **Person/agent making change:** autonomous research execution agent under the
  protocol-amendment rule.
