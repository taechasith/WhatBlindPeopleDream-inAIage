# Phase 2: public-data evidence and access review

**Date:** 2026-10-06 (Asia/Bangkok)  
**Status:** `PASS_FOR_ELIGIBLE_SOURCES_WITH_CONDITIONAL_VALIDATION`

## Verified sources

- The official VizWiz-VQA page documents blind-originating image-question pairs,
  released train/validation answers and answerability fields, and CC BY 4.0.
  The official validation image archive was acquired locally, archive-validated,
  and contains 7,750 JPEGs. The frozen 1,000-item stratified sample resolves to
  a local image for every selected item; source text/images remain local-only.
- The official VizWiz-Captions page documents 39,181 images with five captions
  each and CC BY 4.0. Its annotations archive was locally acquired and parsed.
- The official Kapur & Kreiss repository contains released BLV/sighted rating
  files and has an MIT license. The exact clone commit and raw-file checksums
  are in the data manifest.
- The official GuideDog repository documents 2,106 human-verified gold and
  19,978 VLM-generated silver examples, but states CC BY-NC 4.0 and gated
  Hugging Face access. The Dataset Viewer API returned HTTP 401 without an
  authorized token; no request was bypassed and no data entered the corpus.
- Xie et al.'s released Be My AI material remains an ecological check only; no
  platform scraping is permitted.

## Estimand separation

- Blind dream reports: historical expression reference only.
- Released BLV questions: model-input intent condition.
- VLM outputs: future within-item computational intervention outcome.
- VizWiz captions / GuideDog gold: human reference layers, not universal truth.
- Kapur & Kreiss ratings: external construct validation, restricted to their
  released comparison and rater context.

## Gate decision

The source-input gate for the primary VizWiz intervention has passed. The next
required gate is a reproducible, authorized VLM compute route frozen under
`PUBLIC_MODEL_COMPUTE_GATE.md`. GuideDog gold/silver validation is
`ACCESS_REQUIRES_AUTHORIZED_HF_ACCESS`, not a reason to bypass terms or to
delay the primary intervention indefinitely.
