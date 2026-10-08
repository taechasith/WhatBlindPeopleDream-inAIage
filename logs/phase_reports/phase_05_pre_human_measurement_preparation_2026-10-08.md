# Phase 5 pre-human measurement-preparation checkpoint

## STATUS

`SYNTHETIC_PANEL_RUNNING; HUMAN_CODERS_PENDING; CONDITIONS_BLINDED`.

This is a checkpoint, not a coded-data freeze. No RQ2--RQ5 analysis,
condition-level interpretation, adjudication, or unblinding has occurred.

## WHAT WAS DONE

- Preserved the frozen primary intervention: 1,000 locked items and 3,000
  primary Qwen outputs remain unchanged.
- Hardened the post-run synthetic-panel technical freeze validator so it checks
  expected counts, immutable model/revision/prompt/config metadata, raw-to-label
  linkage, allowed parser states, and immutable freeze receipts.
- Recorded that parser/serialization failures are technical invalid measurements,
  not semantic abstentions; they remain in coverage accounting and cannot be
  silently recoded or retried.
- Froze an opaque 200-cluster map for item-cluster bootstrap uncertainty without
  reading any condition, prompt, model, output, or label field.
- Froze a 2,000-replicate, seed-20261008, 95% percentile cluster-bootstrap
  reliability policy before genuine human labels exist.
- Prepared fail-closed A/B/C human-return locking, attestation, and
  pre-adjudication reliability workflows. These tools are not run on blank
  sheets and do not create or substitute labels.
- Separated two structurally unavailable text-only constructs from poor human
  reliability: `unsupported_information` and
  `accessibility_grounded_content` require external approved reference evidence
  and cannot scale from the question/output-only subset.
- Updated source, ethics, AI-use, compute, reproduction, Alt-Test, and CHI
  planning records to distinguish current state from historical Phase-0 state.
- Regenerated the local-only VizWiz Captions and Kapur--Kreiss reference-table
  manifest in the base analysis environment and added SHA-256 provenance for
  derived reference tables as well as their raw inputs.
- Froze an external-validation policy before coded labels or condition effects
  are available. It separates same-item human/synthetic validation from
  VizWiz HumanSpace comparisons, Kapur--Kreiss construct validation, the
  unavailable GuideDog source, and the limited Be My AI ecological check.

## FILES CREATED OR MODIFIED

- Commit `2ac142f`: hardened human validation gate, including
  `code/14_public_coding_reliability.py`,
  `code/17_lock_human_coder_files.py`,
  `code/18_build_reliability_cluster_map.py`, human-return documentation,
  applicability precheck, and reliability bootstrap policy.
- Commit `12a685e`: hardened synthetic-panel provenance and updated
  pre-results/ethics/CHI documentation.
- Private, ignored artifact: opaque reliability-cluster map with a public
  checksum receipt in `annotation_public/RELIABILITY_CLUSTER_MAP_FREEZE_v1.md`.
- Pending commit: `code/05_build_public_reference_corpora.py` records hashes
  for generated reference tables; `validation_drafts/EXTERNAL_VALIDATION_POLICY_v1.md`,
  `validation_drafts/GUIDEDOG_ACCESS_STATUS.md`, and
  `validation_drafts/EXTERNAL_VALIDATION_PREFLIGHT_2026-10-08.md` record
  external-validation boundaries and preflight provenance.

## N / SAMPLE COUNTS

- Primary intervention: 1,000 locked VizWiz image-question items x 3 frozen
  prompt conditions = 3,000 frozen primary outputs.
- Human validation design: 200 locked items x 3 blinded outputs = 600 rows for
  each of three independent coders.
- Bootstrap map: 200 opaque item clusters x 3 rows = 600 rows.
- Synthetic panel target: 3,000 outputs x 10 constructs = 30,000 records per
  judge; technical completion is pending.
- External-reference preflight: the 1,000 locked images join to 4,866 retained
  VizWiz caption references; captions remain clustered within image rather than
  treated as 4,866 independent observations. The local Kapur--Kreiss extract
  has 136 aggregate comparison rows across 18 image IDs.

## KEY CHECKS

- Conditions remain blinded; the private mapping was not used for
  interpretation.
- The reliability cluster-map utility read only `blind_item_id` and
  `sample_row_id`; its public receipt records this boundary.
- Updated Python modules compile in `.env_vlm`; an in-memory, non-study smoke
  test exercised missing-aware nominal alpha and pairwise kappa functions.
- Modified public/nonprivate artifacts passed the project-specific anonymity
  pattern scan.
- `git diff --check` passed before commits.
- On 2026-10-08, `code/verify_provenance.py --allow-missing` passed all eight
  recorded raw-source checksums. The regenerated derived-reference manifest
  records SHA-256 hashes for both output tables.

## PROBLEMS

- The synthetic panel has not yet completed both judges; it cannot be technically
  frozen until each judge has 3,000 raw records and 30,000 construct records.
- No genuine A/B/C human coder returns are present. Blank distributed sheets are
  not evidence and are not used.
- No numerical human-reliability eligibility threshold was frozen. The prepared
  workflow therefore reports `THRESHOLD_NOT_PREDEFINED` and blocks
  confirmatory scaling until a future prospective governance decision, rather
  than inventing a rule after labels are seen.
- The official Alt-Test repository is attributable and pinned, but did not show
  a clear reusable code license at the checked upstream revision. Do not clone,
  execute, vendor, or redistribute it without explicit license/permission; no
  replacement implementation is authorized.
- GuideDog is a gated source without documented authorized access and remains
  `ACCESS_UNAVAILABLE`; no access bypass or substitute is permitted.

## DECISIONS REQUIRED

No routine decision is required while the synthetic panel runs and human coder
files are absent. Before a future Alt-Test execution, a permitted official-code
license/authorization route is required. Before any threshold-based construct
eligibility decision, a transparent prospective governance rule is required
without condition-level outcome access.

## NEXT PHASE

1. Allow the frozen synthetic panel to complete and run its fail-closed
   technical freeze.
2. Wait for three genuine independent human coder returns and attestations.
3. Lock returns, calculate raw human reliability, and preserve the
   non-confirmatory threshold status before any adjudication.
