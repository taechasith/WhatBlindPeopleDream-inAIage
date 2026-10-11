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

## 2026-10-06 -- Supersede current CHI human-study path with a public-data-only protocol

- **Original plan:** The active CHI submission path included a prospective
  human dream-incorporation experiment after ethics approval.
- **New plan:** The current submission instead uses a public-data-only,
  within-item computational intervention with released VizWiz image-question
  pairs. Dream reports are a historical sensory-expression reference, not an
  AI-exposure outcome. The former human protocol is retained under
  `future_human_study/` for separately approved future work.
- **Reason:** The new question identifies observable human-to-AI information
  grounding while avoiding unsupported causal claims about cognition or dreams
  and the recruitment/ethics dependency of the former path.
- **Relevant results already seen:** Yes. Study 0 exploratory automated-label
  results and non-human model-candidate tests had been seen. No new
  computational-intervention output exists; the new protocol does not elevate
  prior results to confirmatory evidence.
- **Confirmatory/exploratory status:** The new intervention is prospectively
  specified in `PROTOCOL_PUBLIC_DATA_v2.md`; retained Study 0 outputs remain
  exploratory.

## 2026-10-08 -- Amend annotation gate for human-validated synthetic scaling

- **Reason:** The primary 3,000-output computational intervention had been
  frozen, but its measurement layer needed an explicit separation between
  same-item human validation, synthetic scaling, and external construct
  validation before any condition-level hypothesis was opened.
- **Old rule:** A 20% human double-coded sample and optional LLM assistance
  were specified, but the guide did not operationalize the same-item subset,
  construct-by-construct scaling decision, synthetic-panel provenance, or the
  boundary between external human evidence and same-rubric annotation.
- **New rule:** Select 200 locked items and all three outputs per item
  (`200 x 3 = 600`; 20% of 3,000) for blinded, independent double-human coding.
  Freeze synthetic judges separately; compare them construct by construct to
  adjudicated human labels; use synthetic labels at full scale only after the
  predefined validation gate passes; and keep VizWiz, GuideDog, Kapur-Kreiss,
  and Be My AI evidence as external construct validation.
- **Why this occurred before condition unblinding:** The 3,000 outputs,
  prompts, sample, model revision, and configuration were already frozen, but
  no RQ2-RQ5 condition-level result had been opened and no private mapping was
  inspected. The amendment therefore changes measurement governance before
  outcome interpretation rather than after observing a hypothesis result.
- **Effect on confirmatory status:** Confirmatory full-dataset claims require
  human reliability and same-item, same-rubric validation for each scaled
  construct. Nonpassing or unvalidated synthetic constructs are restricted to
  human-subset or exploratory status.
- **References motivating amendment:** Calderon, Reichart, and Dror (2025),
  DOI 10.18653/v1/2025.acl-long.782; Pataranutaporn et al. (2025), DOI
  10.1073/pnas.2519394122; Kapur and Kreiss (2024), DOI
  10.18653/v1/2024.nlp4pi-1.26.

## 2026-10-08 -- Require three independent human coders for formal Alt-Test scaling

- **Original plan:** Two independent human coders would code the same blinded
  600-output validation subset before adjudication and construct-level
  synthetic validation.
- **New plan:** Three independent human coders (A, B, and C) will independently
  code the exact same frozen 600 rows under the same rubric. All three raw
  files will be locked before reliability and adjudication. The official
  Calderon et al. Alt-Test implementation will be run construct by construct
  only after the raw human files and adjudicated labels are locked.
- **Reason:** The official Alt-Test FAQ states that two-human leave-one-out
  comparisons lack a robust consensus reference and recommends at least three
  human annotators for more reliable comparison.
- **Outcome visibility:** This amendment occurs before any human labels exist.
  The 600-row subset, fixed seed, row order, frozen model outputs, synthetic
  judges, condition blinding, and RQ2-RQ5 results remain unchanged and unseen.
- **Fallback:** If only two genuine human coders can ultimately be obtained,
  do not fabricate a third. Record `ALT_TEST_TWO_HUMAN_LIMITATION`, interpret
  Alt-Test evidence as weaker, and preserve the original confirmatory
  human-coded analysis independently of synthetic scaling.

## 2026-10-08 -- Freeze Alt-Test epsilon policy before human labels

- **Original plan:** The protocol required a documented Alt-Test epsilon
  rationale but did not set its numerical value before human labels,
  human--synthetic agreement, or Alt-Test outcomes were available.
- **New plan:** Set primary `epsilon = 0.10` for every compatible construct
  and frozen judge. It treats the planned annotators as trained, independent
  non-expert rubric coders and grants no expert-annotator efficiency premium.
- **Reason:** The official Alt-Test FAQ identifies epsilon as a cost-benefit
  hyperparameter, recommends a lower value for lower-cost annotators, and
  requires reporting the rationale with human reliability, advantage
  probability, and winning rate. Freezing it prevents selection after seeing
  which judge would pass.
- **Outcome visibility:** No human coder labels, adjudicated labels,
  human--synthetic validation results, Alt-Test results, or condition-level
  effects have been opened. Synthetic-panel output remains blinded and is not
  inspected for substantive label patterns.
- **Constraint:** Poor human reliability downgrades the construct to
  `CONSTRUCT_NOT_RELIABLE`; epsilon may not be increased to rescue synthetic
  scaling.

## 2026-10-08 -- Separate technical parser failures from semantic abstention

- **Original plan:** The frozen synthetic runner preserved a rectangular table
  by writing `label=NA, abstain=true` rows when a raw response could not be
  parsed. The policy did not explicitly distinguish these technical
  placeholders from an LLM's semantically justified abstention.
- **New plan:** Retain every raw parser-failure record and placeholder row, but
  mark `PARSE_ERROR:*` rows `TECHNICALLY_INVALID_FOR_MEASUREMENT`; exclude them
  from prevalence, same-item human validation, Alt-Test, and scaled analyses.
  Treat PRESENT labels marked `EVIDENCE_SPAN_INVALID` as invalid positive
  measurements as well. Report both categories as coverage/failure counts.
- **Reason:** A technical audit of the blinded running panel showed that a
  parser failure could otherwise be mistakenly counted as semantic abstention.
  The new rule prevents a serialization defect from being converted into a
  scientific label, while preserving all artifacts and avoiding retry or
  regeneration of substantive outputs.
- **Outcome visibility:** Parser-status counts were inspected as permitted
  technical metadata; no label substance by condition, private mapping, RQ2--RQ5
  effect, human label, or human--synthetic result was inspected.
- **Confirmatory effect:** This is a prospective validity/coverage rule applied
  before any human reference exists. It cannot improve a judge by deleting
  inconvenient semantic outcomes because invalid rows remain visible and are
  reported in the technical freeze.

## 2026-10-08 -- Harden pre-human reliability governance and preserve cluster structure

- **Original plan:** The annotation policy required construct-level reliability
  before adjudication, but did not specify a numerical reliability threshold,
  a complete human-return locking protocol, an item-cluster uncertainty method,
  or a distinction between structurally unavailable text-only constructs and
  poor human agreement.
- **New plan:** Before any genuine human labels exist, freeze an opaque
  200-cluster bootstrap map and the 2,000-replicate percentile-bootstrap policy;
  require locked independent A/B/C returns and attestation provenance; and
  report `THRESHOLD_NOT_PREDEFINED` with non-confirmatory use rather than
  deriving a pass/borderline/fail threshold after observing labels. The
  applicability precheck records that `unsupported_information` and
  `accessibility_grounded_content` are structurally `NA` in the current
  question/output-only packet.
- **Reason:** A source-only audit found that technical missingness, source-item
  clustering, and structurally absent reference evidence could otherwise be
  misread as substantive human disagreement, and that an unannounced threshold
  would invite post-hoc eligibility decisions.
- **Outcome visibility:** No human coder labels, adjudicated labels,
  human--synthetic validation, synthetic label substance, private condition
  mapping, or RQ2--RQ5 outcome was inspected. The opaque map was built
  mechanically using only blind IDs and source-item IDs, without reading
  condition fields.
- **Confirmatory effect:** This amendment strengthens measurement provenance
  but does not authorize full-scale synthetic measurement. A later prospective
  governance decision remains necessary before any threshold-based construct
  eligibility claim can be made.

## 2026-10-08 -- Correct public-data preregistration wording to frozen/prospective wording

- **Original plan/text:** Active public-data documents described the internally
  frozen sample, question taxonomy, subset, and intervention as
  `preregistered`.
- **New plan/text:** Describe those elements as `frozen` and `pre-specified`.
  Reserve `preregistered` for a study only when a dated public registration can
  be documented.
- **Reason:** The repository records a protocol freeze but no public
  preregistration receipt. The correction prevents an unsupported provenance
  claim and does not alter the locked sample, prompts, ontology, model,
  analysis plan, or confirmation boundary.
- **Outcome visibility:** No condition mapping, model-output label substance,
  RQ2--RQ5 result, human label, human--synthetic validation, or external
  validation outcome was inspected to make this correction.
- **Confirmatory effect:** The study remains a prospectively frozen internal
  protocol; this wording correction does not convert it into a publicly
  preregistered study.

## 2026-10-08 -- Issue distribution-ready human coder packet v1.1

- **Original plan/material:** The frozen v1 package preserved the correct
  blinded 600-row subset and coding sheets, but did not include or checksum the
  referenced codebook, return protocol, attestation, or per-coder assignment
  receipt. Its instructions also ambiguously named the standalone template.
- **New plan/material:** Preserve v1 unchanged and create a separate v1.1
  package by byte-copying its subset and sheets, then adding hash-pinned v1.1
  materials. Coders must complete the supplied `coding_sheet.csv`; v1.1 repairs
  malformed quotation characters without changing any code, construct, or
  rubric decision boundary.
- **Reason:** A pre-distribution mechanical integrity audit identified that the
  original materials could not prove which referenced rubric a coder received.
- **Outcome visibility:** No human labels exist; no model-output content,
  condition mapping, synthetic label substance, or RQ2--RQ5 result was read.
- **Confirmatory effect:** The fixed seed, 200 selected items, 600 rows, row
  order, output text, condition blinding, ontology, judges, and prompts remain
  unchanged. v1.1 strengthens provenance only.

## 2026-10-09 -- Supersede new-human annotation gate for the current public-data study

- **Original plan:** The current CHI submission path required three new,
  independently returned human-coder files for the frozen 600-row subset,
  pre-adjudication reliability, adjudication, same-item synthetic-versus-human
  validation, and Alt-Test decisions before `CODED_DATA_FREEZE`.
- **New plan:** The current submission is deliberately public-data-only and
  collects zero new human data. It uses the frozen synthetic panel as a
  computational measurement instrument; applies a prospective blinded
  computational robustness gate; and uses released human-labelled datasets only
  for bounded external public-human calibration. The previous A/B/C, adjudication,
  and Alt-Test materials are retained under `future_human_validation/` for a
  later matched-human validation study.
- **Reason:** The study does not ask whether a synthetic annotator replaces a
  human. Requiring new human labels would introduce a new collection dependency
  while not matching the current computational intervention claim. The revision
  narrows claims to observable output properties and to the specific external
  human evidence available in released datasets.
- **Archive:** Before amendment, the supplied governing guide was copied to
  `guides/archive/CHI2027_Blind_Dreams_AI_Research_Guide_pre_public_data_only_2026-10-09.md`.
  Its SHA-256 is
  `9BEDAA370D5E8349DA71B710051565326AC769D18717B20E29733BB6DCD61E13`.
- **What did not change:** The locked 1,000-item sample, 3,000 Qwen outputs,
  prompts, generator revision, output freeze, synthetic judge configurations,
  Study 0 data, research questions, condition blinding, and private mapping.
- **Outcome visibility:** No RQ2--RQ5 condition-level effect, private condition
  mapping, human label, adjudicated label, or synthetic-label condition pattern
  was opened to make this amendment. Permitted technical progress metadata only
  were inspected.
- **Confirmatory effect:** `ALT_TEST_CURRENT_STUDY = NOT_APPLICABLE_TO_CURRENT_DESIGN`.
  Synthetic labels are never called human judgments or evidence of lived
  experience. Every construct must receive a prospective Tier A/B/C and
  measurement-strength decision before unblinding; unsupported or unstable
  constructs remain exploratory or `MEASUREMENT_UNSTABLE`.

## 2026-10-12 -- Repair watcher completion check for multiline CSV evidence spans

- **Original plan/implementation:** The blinded robustness watcher treated a
  synthetic judge as complete only when the physical line count of its CSV
  label file equalled the expected record count plus a header.
- **New plan/implementation:** The watcher now uses the PowerShell CSV parser
  and counts logical CSV records, while retaining the existing exact raw JSONL
  line-count requirement. A CSV parse failure remains incomplete and therefore
  fail-closed.
- **Reason:** The frozen rubric permits evidence spans containing newlines. A
  valid quoted multiline span increases physical file lines without adding a
  label record. The Qwen label file contained exactly 30,000 unique
  item--construct CSV records for 3,000 blind IDs and 10 frozen constructs,
  while its physical line count was higher. The original watcher would wait
  indefinitely despite an internally valid panel.
- **Outcome visibility:** Only structural counts, CSV schema/uniqueness, raw
  record counts, and file metadata were inspected. No label content, condition
  mapping, condition-level result, RQ2--RQ5 effect, or public-human validation
  result was accessed.
- **Confirmatory effect:** No model, prompt, sample, ontology, judge,
  generation, raw output, or measurement rule changed. This is a prospective
  technical parsing correction that enables the already frozen blinded workflow
  to validate the same logical records.
