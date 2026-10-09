# Phase 5 public-data-only scope amendment — 2026-10-09

## STATUS

`SYNTHETIC_PANEL_RUNNING; PUBLIC_DATA_ONLY; CONDITIONS_BLINDED`

## WHAT WAS DONE

- Archived the pre-amendment governing guide locally before modifying the
  canonical guide.
- Superseded the current requirement for new A/B/C human coder files,
  adjudication, human-human reliability, and the Alternative Annotator Test.
- Defined current measurement as computational annotation plus separate
  external public-human calibration; it makes no synthetic-human equivalence
  claim.
- Created prospective Tier A (computationally observable), Tier B
  (public-human benchmarked), and Tier C (model-derived exploratory) construct
  assignments and a public-human calibration matrix.
- Preserved the prior human-validation materials under
  `future_human_validation/` for a future, separately governed study.

## FILES CREATED OR MODIFIED

- `CHI2027_Blind_Dreams_AI_Research_Guide.md` (local governing file; ignored
  because it contains post-review identity metadata)
- `guides/archive/CHI2027_Blind_Dreams_AI_Research_Guide_pre_public_data_only_2026-10-09.md`
  (local private archive)
- `ANNOTATION_VALIDATION_POLICY.md`
- `CONSTRUCT_MEASUREMENT_TIER_MATRIX.csv`
- `PUBLIC_HUMAN_CALIBRATION_MATRIX.csv`
- `future_human_validation/`
- `logs/deviations.md` and `logs/decisions.md`

## N / SAMPLE COUNTS

- Locked primary intervention: 1,000 items × 3 conditions = 3,000 frozen
  Qwen outputs; no condition-level analysis opened.
- Synthetic panel: two frozen judges × 3,000 blinded outputs × 10 constructs
  expected after completion. No label content or condition pattern was used in
  this amendment.
- New human data collected: 0.

## KEY CHECKS

- The guide archive SHA-256 is
  `9BEDAA370D5E8349DA71B710051565326AC769D18717B20E29733BB6DCD61E13`.
- Private condition mapping remains uninspected.
- `ALT_TEST_CURRENT_STUDY = NOT_APPLICABLE_TO_CURRENT_DESIGN`.
- Synthetic measurement cannot support claims about BLV preference, human
  ratings, or lived experience unless a compatible released public dataset
  supports that exact bounded claim.

## PROBLEMS

- The frozen panel is still running, so the technical output freeze and blinded
  robustness audit cannot yet be completed.
- GuideDog Gold remains `ACCESS_UNAVAILABLE`; it cannot contribute external
  validation without lawful documented access.

## DECISIONS REQUIRED

None for the current public-data-only scope.

## NEXT PHASE

Finish both frozen synthetic judges, execute the technical freeze, conduct the
pre-specified blinded computational robustness audit, freeze measurement
strength and public-human calibration, then create `CODED_DATA_FREEZE` before
the single condition unblinding.
