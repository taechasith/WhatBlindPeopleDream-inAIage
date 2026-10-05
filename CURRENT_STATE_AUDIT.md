# Current state audit

**Audit date:** 2026-10-05 (Asia/Bangkok)  
**Scope:** research status after Study 0 evidence work and during permitted
pre-collection preparation for Study 1. This document is a status dashboard,
not a claim of completed human-subject research.

## COMPLETE

- Study 0 protocol freeze, novelty audit, systematic-evidence artifacts, DOI
  audit, provenance manifests, and exploratory corpus-processing scripts.
- Study 0 automated lexical-label diagnostic, distributional alignment outputs,
  and bootstrap diagnostics. `STUDY0_STATUS.md` freezes these as
  **exploratory / hypothesis-generating / automated-only**.
- Study 1 v2 prospective protocol, estimand separation, primary-outcome
  specification, washout rationale, control-matching audit, stimulus manifest,
  candidate original vector scenes, randomization generator, and collection /
  blinding / coding drafts.
- A simulation-based power analysis for the v2 target-versus-decoy primary
  estimand: 1,000 simulated replications at 208 allocation slots; the
  preregistered minimum-effect scenario (odds ratio 1.5) has estimated power
  0.891 (Monte Carlo SE 0.0099). This is a design calculation, not an observed
  result.
- Synthetic-only end-to-end analysis dry run, including validation, exclusion
  logic, mixed model, contrasts, cluster bootstrap, tables, and an accessible
  synthetic figure. Synthetic outputs are explicitly excluded from scientific
  results.
- Local reproducibility and anonymity checks: provenance verification,
  anonymous-export allowlist check, data dictionary, requirements file, data
  sharing plan, AI-use log, and release policy.

## PARTIAL

- Final Study 1 exposure system: SmolVLM2 was rejected after its non-human
  grounding screen. A pinned Qwen2.5-VL candidate is undergoing the same
  deterministic, local, non-human generation and fail-closed lexical screen.
  No candidate is approved for participant exposure.
- Final DAI / SAI / HUM / ANC scripts and audio: prototype materials support
  matching analysis, but final transcripts, speech renders, hashes, and
  independent factual/accessibility review remain prospective requirements.
- Ethics submission packet: draft documents are synchronized, but local
  institutional contacts, compensation, retention route, referral process, and
  submission-specific facts cannot be invented.
- Study 0 sharing is reproducible for released local inputs, subject to its
  manifest and upstream terms; it has no independent human semantic coding or
  reliability estimate and must not be converted into confirmatory evidence.

## PENDING (PERMITTED PRE-COLLECTION WORK)

- Finish and log the Qwen candidate technical screen; either reject it or mark
  it *candidate only*, never exposure-approved solely from an automated screen.
- Complete a non-deployed script/audio matching review after the final candidate
  is known. Independent human grounding and accessibility review cannot be
  substituted with model output.
- Refresh this status dashboard and the waiting-period package after the
  candidate decision; run final repository-wide reproducibility, anonymity,
  and claim-language checks.

## BLOCKED

- `ethics/ETHICS_STATUS.md` is `NOT_SUBMITTED`. No authoritative institutional
  determination or approval exists. Therefore recruitment, contact, screening,
  consent, exposure, participant recording, dream-report collection, advisory
  engagement, coding of participant material, and data collection are
  prohibited.
- Independent human coding/reliability and any empirical Study 1 conclusion
  require approved, collected, blinded participant material. They cannot be
  simulated or RAG-generated.

## SUPERSEDED / RETAINED HISTORY

- The original false-source-only Study 1 control and the older v1 documents are
  retained as historical records. `PROTOCOL_STUDY1_v2.md`,
  `PRIMARY_OUTCOME_SPECIFICATION.md`, and `STUDY1_ESTIMANDS.md` govern the
  current prospective study.
- Earlier Study 0 JS values are superseded by the NA-aware regeneration recorded
  in `STUDY0_STATUS.md`; current values must be regenerated from the tracked
  pipeline rather than copied from historical drafts.

## NEXT SAFE ACTION

Finish non-human model-screening and repository validation, then leave Study 1
at `STUDY1_READY_PENDING_ETHICS` only if all technical/documentary gates are
met. That label never authorizes human activity.
