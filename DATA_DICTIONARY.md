# Data dictionary and release classification

This dictionary describes schemas used by the repository without reproducing
source text. It is a companion to `data/MANIFEST.csv`, `data/CHECKSUMS.csv`,
`data/LICENSES.md`, `STUDY1_DATA_DICTIONARY.md`, and
`DATA_SHARING_PLAN_FINAL.md`.

## Status vocabulary

- **PUBLIC**: may be included in a reviewed release after an anonymity check.
- **CONTROLLED**: may be shared only under an approved access arrangement and
  applicable source terms.
- **AGGREGATE_ONLY**: may be reported only as non-identifying aggregate output.
- **DO_NOT_SHARE**: not included in any release, supplement, or anonymous
  repository.

## Study 0 local source schemas

| Dataset/file | Key fields | Classification | Notes |
| --- | --- | --- | --- |
| DreamBank processed corpus | `dream_id`, pseudonymous dreamer fields, blindness metadata, `dream_text`, collection metadata, license/provenance | DO_NOT_SHARE | Free text may contain sensitive narrative, locations, relationships, or indirect identifiers. Reacquire only from the original source where permitted. |
| VizWiz-derived corpus | `item_id`, source/task metadata, `input_text`, `output_text`, image identifier, license/provenance | DO_NOT_SHARE | Question/answer text and image identifiers are source-derived material; source images are never released here. |
| Released AI-description snapshot | item metadata and `output_text` derived from released documentation | DO_NOT_SHARE | Treat descriptions and linked source-platform context as sensitive source-derived text even if publicly visible elsewhere. |
| `results/automated_candidate_labels.csv` | source/item identifier plus category indicators | CONTROLLED | Contains no free text, but identifiers can facilitate linkage to restricted source material. Regenerate locally rather than distribute by default. |
| Aggregate Study 0 results | source type, category, denominators, proportions, uncertainty, status | PUBLIC | Only when marked exploratory and after the anonymous-release audit. |

### Study 0 processed-corpus fields

| Field group | Meaning | Release handling |
| --- | --- | --- |
| IDs and source metadata | Dataset-specific item/report ID, source, series, task, split, date, and provenance | CONTROLLED if linkage can reveal source text; otherwise aggregate only |
| Blindness metadata | Reported group, onset/duration fields, source confidence | AGGREGATE_ONLY unless an approved controlled-access plan permits de-identified records |
| Free text | Dream report, question, human description, or AI description | DO_NOT_SHARE |
| Image/source references | Image identifier, source link, screenshot path, or original-link field | DO_NOT_SHARE |
| Licensing/provenance | License label, manifest record, checksum | PUBLIC as metadata only |

## Study 0 result schemas

| File family | Fields | Interpretation/release handling |
| --- | --- | --- |
| `automated_candidate_distribution`, `blv_intent_distribution`, `ai_output_distribution` | source type, ontology category, counts, proportion, analysis status | Aggregate exploratory output; PUBLIC only with the exploratory label retained. |
| `alignment_metrics` | comparison, sample counts, divergence/similarity metrics, uncertainty, status | Aggregate exploratory output; not evidence of cognitive transfer. |
| `human_ai_mismatch`, `social_impact_matrix` | category/finding, aggregate contrast, limitations, design implication | Aggregate exploratory output; plausible consequences are not measured harm. |
| `dream_meta_summary`, `sample_flow`, `robustness`, `reliability` | aggregate counts, subsets, status, limitations | PUBLIC only with status and non-estimable fields preserved. |

## Study 1 prospective schema

No Study 1 participant record exists. The planned analysis schema is defined in
`STUDY1_DATA_DICTIONARY.md`; its fields have the following release rules.

| Field group | Classification | Rationale |
| --- | --- | --- |
| Contact details, consent records, recruitment log, allocation key | DO_NOT_SHARE | Directly identifying or re-identification-enabling. |
| Raw audio, dream transcript, free-text reconstruction, AI interaction transcript | DO_NOT_SHARE | Sensitive narrative and potentially identifying content. |
| Exact timestamps, device/network metadata, location, access logs | DO_NOT_SHARE | Can reveal routine, identity, or household information. |
| Detailed demographic combinations and rare accessibility characteristics | CONTROLLED or AGGREGATE_ONLY | Re-identification risk must be assessed after approved collection. |
| Random study ID and de-identified session data | CONTROLLED | Only after approval, de-identification review, and source-consent compatibility. |
| Coded primary outcome and non-identifying aggregate tables | AGGREGATE_ONLY or PUBLIC | Release only when disclosure risk is acceptable and approved. |
| Synthetic fixtures, codebook, and non-identifying schemas | PUBLIC | Must retain the `SYNTHETIC_ONLY_NOT_EMPIRICAL` label where applicable. |
