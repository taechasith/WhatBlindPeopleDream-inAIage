# CHI 2027 Poster requirements: live pre-results check

**Checked:** 2026-10-08 (Asia/Bangkok)
**Scope:** planning and anonymous-submission preflight only; this is not a
claim that a manuscript, poster, or submission package is ready.

## Confirmed live requirements

| Requirement | Current requirement | Project action/status |
| --- | --- | --- |
| Submission deadline | 21 January 2027, Anywhere on Earth | Track externally; not yet submission-ready. |
| Review paper format | ACM Master Article Submission Template, single column | Use anonymous review configuration. |
| Review page limit | Up to 4 pages excluding references | Treat 4 pages as controlling; the review-criteria prose still contains an inconsistent reference to 6 pages. |
| Anonymity | No author names, affiliations, contact information, identifying acknowledgements, or identifying metadata | Required for every future review artifact and supplement. |
| Required submission materials | Paper and A0 poster; optional appendix/supplementary material; key discussion points | Do not create final assets before results freeze. |
| Human-subjects context | Short reviewer-facing ethics note describing applicable research-environment requirements | Existing anonymous ethics note must be updated only from documented determinations. |
| Accessibility | Follow SIGCHI accessible-submission guidance | Require alt text, readable non-color-only figures, and accessible PDF checks. |
| Review responsibility | Four review-responsibility slots assigned to submission authors in PCS | Confirm practical author-slot arrangement in PCS before submission; do not disclose identity in review assets. |
| Publication workflow | TAPS after conditional acceptance; final publication formatting differs from review format | Do not treat current review PDF as publication-ready source. |
| Final presentation | A0 poster; at least one author must register and present if accepted | Future acceptance-stage requirement. |

## Anonymity controls to retain

- Do not place author, institution, email, acknowledgement, personal repository,
  local path, or identifiable metadata in anonymous files.
- Keep raw content-bearing data and private condition mappings outside the review
  bundle.
- Cite prior work normally in the third person; do not use anonymous placeholder
  references.
- Scan PDF metadata and filenames before submission.

## Source record

- https://chi2027.acm.org/authors/posters/
- https://chi2027.acm.org/chi-publication-formats/
- https://chi2027.acm.org/chi-anonymization-policy/
- https://chi2027.acm.org/acm-publication-policies/

## Remaining pre-submission gates

For the active public-data-only scope, new human coding, adjudication,
reliability calculation, and an Alternative Annotator Test (AltTest) are not
preconditions for manuscript creation. Results must instead remain within the
documented blinded computational-measurement and source-specific public-human
calibration boundary, with provenance, anonymous-review, accessibility, and
results-freeze checks complete. This correction permits designated automated
blinded scripts to process protected artifacts for technical and robustness
audits, but before `CODED_DATA_FREEZE` it does not permit human-readable label
substance, a private condition mapping, condition-level inspection, or
RQ2--RQ5.

`future_human_validation/` preserves the independent-coding, adjudication, and
AltTest workflow for possible future human-study claims. It is non-active for
this public-data submission and cannot retroactively turn a computational
measurement into human-validated evidence.
