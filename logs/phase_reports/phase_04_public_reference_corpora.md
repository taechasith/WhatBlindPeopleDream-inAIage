# Phase 4: IntentSpace and HumanSpace inputs

**Status:** source-input gate passed; no VLM outcome generated.

## What was done

- Parsed local released VizWiz validation questions/answers and selected the
  deterministic 1,000-item intervention sample before any VLM output.
- Acquired and archive-validated the official VizWiz validation-image archive:
  7,750 JPEGs; every frozen sample item resolves to one local image.
- Parsed local VizWiz-Captions validation annotations and released Kapur/Kreiss
  rating files for local-only HumanSpace/construct-validation preparation.

## Counts

- Frozen intervention sample: 1,000 unique image-question items.
- Answerability: 676 answerable; 324 non-answerable.
- Caption reference: 37,786 retained validation captions across 7,750 images.
- Kapur/Kreiss local reference rows: 136.

## Files / checks

- Builders: `code/05_build_public_reference_corpora.py`,
  `code/06_select_public_intervention_sample.py`, and
  `code/07_validate_public_intervention_inputs.py`.
- Local manifests are ignored with raw/derived source data; their input hashes
  and source-file checksums are recorded locally.
- GuideDog remains `ACCESS_REQUIRES_AUTHORIZED_HF_ACCESS`; it was not bypassed.
