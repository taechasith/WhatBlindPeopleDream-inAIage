# Protocol: public-data sensory mediation study

**Protocol ID:** BD-AI-CHI27-PUBLIC-v2.0  
**Freeze date:** 2026-10-06 (Asia/Bangkok)  
**Status:** active prospective protocol for the public-data CHI 2027 submission

## Research questions

- **RQ1:** How do released blind dream reports, BLV-originating questions,
  human accessibility descriptions, and AI descriptions differ in their
  expressed sensory-information structure under the Cognitive Sensing Ontology?
- **RQ2:** For the same released VizWiz image-question item, does supplying the
  BLV-originating question and accessibility constraints change the information
  profile of a frozen VLM output relative to an image-only prompt?
- **RQ3:** Do intent-steered outputs differ from generic outputs on
  pre-specified computational measures and, where compatible released data
  exist, show different bounded alignment with human references or BLV
  preference evidence?
- **RQ4:** Is similarity to DreamSpace associated with accessibility-relevance
  measures, or are sensory-expression resemblance and user alignment distinct
  constructs?
- **RQ5:** Across the available reference data, which explicit visual-detail,
  identity/social-inference, uncertainty-expression, or model-derived
  unsupported-information patterns are added or omitted by AI text under the
  stated measurement-strength boundaries?

## Evidence spaces and units

| Space | Eligible released source | Unit | Role |
| --- | --- | --- | --- |
| DreamSpace | DreamBank blind series and eligible published evidence | Dream report / source estimate | Historical sensory-expression reference |
| IntentSpace | VizWiz-VQA train/validation question | Image-question item | BLV-originating information intent |
| HumanSpace | VizWiz-Captions and released human-verified guidance | Caption/guidance item | Human reference, not universal ground truth |
| AISpace | Frozen outputs from the computational intervention; GuideDog silver and released Be My AI text where terms permit | Output/description item | AI mediation profile |
| Preference validation | Released Kapur & Kreiss material | Existing rated comparison | External construct validation |

## Confirmatory computational intervention

The intervention uses a frozen, deterministic sample of **1,000
eligible VizWiz validation image-question items**. The sample is selected by a
published seed after source acquisition, stratified by official answerability
and a frozen question taxonomy. Test data and images without a released,
eligible use route are excluded.

For every included item, each frozen VLM is run once under:

1. **Generic:** image only; neutral image description request.
2. **Intent-steered:** image plus the released BLV-originating question; answer
   and describe only information relevant to the question; disclose uncertainty
   where appropriate.
3. **Accessibility-steered:** the Intent-steered input plus a fixed instruction
   to report actionable spatial relations and uncertainty, and not infer
   identity, demographic attributes, emotion, relationships, or intent without
   visible support.

The condition is an *input/prompt intervention on a model output*, not an
intervention on a person. The primary unit is an image-question-model-condition
output. The model and prompt are not selected based on outcome performance.

## Primary outcomes

1. **Intent-grounded answerability:** whether an output supplies an answer or
   explicitly justified uncertainty relative to the released question and
   official answerability/answers, using a locked scoring rule.
2. **CSO output profile:** category prevalence for task relevance, spatial
   relation, distance/direction/motion, uncertainty, visual-detail load,
   identity/social inference, safety/actionability, and ambiguity.
3. **Unsupported-inference rate:** a source-grounded binary/ordinal label only
   where the image and released human references permit verification. It is
   `NOT_ESTIMABLE` otherwise.

Each outcome is assigned prospectively to a measurement tier in
`MEASUREMENT_FRAMEWORK_PUBLIC_DATA_v1.md`. Tier A properties are direct,
text-observable computational measurements subject to the frozen robustness
gate. Tier B measures are additionally calibrated against compatible released
human-labelled public evidence. Tier C measures are model-derived exploratory
constructs and cannot license human-centred claims. No language model is
ground truth, and the study collects no new human annotations.

## Statistical analysis

- The primary comparison is within image-question-model: Intent-steered minus
  Generic, and Accessibility-steered minus Intent-steered.
- For binary CSO outcomes, fit mixed logistic models with prompt condition and
  frozen model as fixed effects and image-question as a random intercept. If
  model convergence is not defensible, use paired permutation tests and
  image-question cluster bootstrap confidence intervals.
- Report model-specific effects first; a pooled model is secondary and does not
  imply all VLMs behave alike.
- Pre-specify one primary family: direct output answer/reference coverage,
  explicit spatial relation, explicit identity inference, explicit social/intent
  inference, and explicit ambiguity. Include a construct in this family only if
  it passes the frozen computational robustness gate; use Benjamini--Hochberg
  correction within that family and report effect sizes and confidence
  intervals. Broad CSO lexical profiles, grounded uncertainty, and general
  unsupported-information judgments remain secondary or exploratory unless a
  direct released reference supports a narrower metric.
- DreamSpace comparisons use Jensen--Shannon divergence, cosine similarity,
  Hellinger distance, and bootstrap intervals. They are descriptive profile
  comparisons, never cognitive transfer or user usefulness claims.

## External validation and robustness

- Evaluate whether proposed alignment measures track released BLV preference
  judgments in the Kapur & Kreiss materials, only within their stated task and
  rating population.
- Compare GuideDog gold and silver only after gated access is formally granted
  and its CC BY-NC 4.0 terms are compatible with this noncommercial research.
- Treat Xie et al.'s released Be My AI material as an ecological check only;
  do not infer prevalence from its platform-shared examples.
- Run prompt-length, output-length, question-type, answerability, text-reading,
  task-context, model, and vocabulary-confound robustness checks. Report every
  unavailable comparison as `NOT_ESTIMABLE`.

## Exclusions and ethics

- Exclude scraped posts, private data, test answers without authorized use,
  items with unavailable images, duplicate image-question pairs, and sources
  without documented release terms.
- Preserve source privacy safeguards, including the VizWiz documentation of
  obfuscated private information. Do not redistribute source images/text unless
  their terms permit it.
- Seek an institutional determination if required for secondary analysis of
  released data; no new recruitment, contact, consent, or data collection is in
  scope.

## Nonclaims

This study cannot establish whether AI changes cognition, dream content, neural
organization, or real-world safety. It establishes only properties of released
text and frozen-model outputs under the stated inputs and measures.
