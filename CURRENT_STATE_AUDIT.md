# Current state audit

**Audit date:** 2026-10-06 (Asia/Bangkok)
**Active scope:** public-data sensory-mediation study for CHI 2027 Posters.

## COMPLETE

- The new scope, nonclaims, public-data-only intervention design, sampling rule,
  validation hierarchy, and analysis family are frozen in
  `PROTOCOL_PUBLIC_DATA_v2.md` and `PUBLIC_DATA_ANALYSIS_PLAN_v2.md`.
- Historical Study 0 DreamBank/VizWiz/Xie processing, provenance, and
  exploratory diagnostics are preserved. They remain exploratory and cannot be
  rebranded as the new intervention results.
- The former prospective human study was isolated under
  `future_human_study/`; it is not part of the current CHI submission.
- VizWiz-VQA and VizWiz-Captions source pages and terms were re-verified.
  Released validation questions/answers, 7,750 archive-validated VizWiz
  validation images, and caption annotations support the intended local-only
  IntentSpace and HumanSpace inputs.

## NEXT PUBLIC-DATA GATES

1. Complete the revised evidence/source gate for each new corpus, including
   exact release revision, terms, consent/release context, fields, and permitted
   redistribution.
2. Validate that each item in the frozen 1,000-item stratified sample resolves
   to its archive-validated local image before generating or inspecting VLM
   outputs.
3. Freeze at least one reproducible VLM, and preferably two, with a feasible
   compute route. The earlier local CPU-only candidate run does not satisfy this
   gate.
4. Produce the three prompt-condition outputs, then validate the ontology and
   intent-grounded measures against released labels and any ethically permitted
   independent coding.
5. Obtain GuideDog only if the required gated noncommercial access is granted;
   otherwise retain its metadata and mark gold/silver comparisons
   `ACCESS_UNAVAILABLE`/`NOT_ESTIMABLE`.

## ETHICS AND LICENSE BOUNDARY

The active project includes no recruitment, contact, consent, exposure, or new
human-data collection. It remains a secondary analysis of released research
data and a model-output experiment. Public availability does not waive source
terms or institutional policy: do not bypass gated access and obtain a local
secondary-analysis determination if required by the applicable research
environment.

## NOT YET COMPLETE

No new confirmatory computational-intervention output, independent coding,
external preference validation, final paper, or A0 poster exists. Therefore no
claim about user benefit, safety improvement, model generality, or the
AI-to-dream pathway is licensed.
