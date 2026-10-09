# Post-results manuscript and poster audit

**Status:** BLOCKED_PENDING_RESULTS_FREEZE

This checklist prevents this anonymous source scaffold from becoming a paper
with planned, synthetic, or untraceable findings. Complete it only after the
computational analysis pipeline has produced and committed its results freeze.

## Required evidence inputs

- [ ] `RESULTS_FREEZE` receipt exists, has a committed checksum, and records the
  authorized single condition unblinding.
- [ ] RQ2--RQ5 output tables, sample/missingness accounting, robustness outputs,
  and effect estimates are present and schema-validated.
- [ ] The construct measurement-strength table is available and every reported
  result states its label source and construct status.
- [ ] Each reported number, sample count, confidence interval, and p/q value
  maps to a machine-readable result artifact.
- [ ] Null, contradictory, and unstable-measurement findings are retained.
- [ ] External public-human calibration is described as cross-dataset
  calibration/validation, not as same-item human ratings of the current outputs.
- [ ] The ethics note and data-license/provenance records support each dataset
  mentioned in the manuscript.

## Writing controls

- [ ] Abstract contains real, frozen results only; no planned result language.
- [ ] Methods distinguish computational measurement from human judgment and
  disclose the frozen generator/judge roles and external calibration boundary.
- [ ] Results use only `COMPUTATIONAL_PRIMARY`, `PUBLIC_HUMAN_BENCHMARKED`, or
  otherwise explicitly qualified measurement statuses.
- [ ] Model-derived exploratory measures are visibly labelled and do not support
  human-centered primary claims.
- [ ] No wording claims that AI changes dreams, cognition, brains, neural
  organization, or blind people's lived experience.
- [ ] Distributional DreamSpace similarity is not described as cognitive or
  psychological equivalence.
- [ ] Social-impact language distinguishes plausible design implications from
  measured harm or safety performance.

## References, figures, and anonymization

- [ ] Every BibTeX entry is resolved and reconciled with the DOI/reference
  audit; protocol papers are not cited as completed results.
- [ ] The review manuscript is at most four pages excluding references under the
  current call; the official page-limit wording is rechecked before upload.
- [ ] Figures include exact N, uncertainty where applicable, readable labels,
  useful captions/alt text, and non-color-only distinctions.
- [ ] The A0 poster is built from the same frozen result facts and includes a
  clearly labelled future-hypothesis arrow rather than a causal claim.
- [ ] PDF metadata, filenames, source comments, hyperlinks, supplementary
  materials, and poster contain no author-identifying information.
- [ ] CHI ethics context, AI-use disclosure requirements, accessibility
  requirements, and review-responsibility requirements are rechecked in the
  live call.

## Required final outputs

- [ ] Anonymous four-page review PDF and source package.
- [ ] Anonymous A0 poster PDF and accessible source.
- [ ] Key Discussion Points for the submission system.
- [ ] Reproducibility package that excludes raw/sensitive/identifying material.
- [ ] Claim, reference, anonymity, ethics, and CHI desk-reject audit records.
