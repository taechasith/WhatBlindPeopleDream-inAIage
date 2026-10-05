# Data-sharing plan and decision matrix

## Scope and governing rule

This is the release decision matrix for the current repository state. It does
not override source-data licenses, an eventual institutional determination,
participant consent, or law. If any of those impose a stricter rule, the
stricter rule controls.

No Study 1 participant data exist. The prospective portions of this plan are
binding design commitments, subject to approved ethics requirements.

| Data field or artifact | Classification | Release decision |
| --- | --- | --- |
| Protocols, codebooks, aggregate result tables, synthetic fixtures, source code | PUBLIC | Only after the anonymous-release scan and removal of author-identifying metadata. Synthetic labels must remain visible. |
| Source manifest, licenses, checksums | PUBLIC in canonical reproducibility materials | Exclude web addresses and identity-bearing links from anonymous review bundles. |
| Raw DreamBank dream text and derived text-bearing coder packets | DO_NOT_SHARE | Sensitive free text; redistribute only through the original source if its terms permit. |
| VizWiz question/answer text, image IDs, answers, and source images | DO_NOT_SHARE | Reacquire through the authorized source; never package images or text here. |
| Released AI-description text and source-platform context | DO_NOT_SHARE | Treat as sensitive source-derived material; do not republish in a supplement. |
| Study 0 item-level category labels and linkable IDs | CONTROLLED | Regenerate locally where authorized; aggregate outputs are preferred for release. |
| Study 0 aggregate counts, prevalence, divergence metrics, and limitations | PUBLIC | Preserve exploratory/automated-candidate status and small-sample caveats. |
| Study 1 raw voice recordings | DO_NOT_SHARE | Sensitive audio and biometric/identity-bearing information. |
| Study 1 transcripts, free dream reports, reconstruction text, and AI transcripts | DO_NOT_SHARE | Sensitive narrative, possible third-party information, and re-identification risk. |
| Study 1 contact information, consent records, recruitment log, allocation key | DO_NOT_SHARE | Directly identifying operational records. |
| Study 1 timestamps, device metadata, network metadata, location, access logs | DO_NOT_SHARE | Routine and identity disclosure risk. |
| Study 1 detailed demographics and rare disability/accessibility combinations | CONTROLLED or AGGREGATE_ONLY | Decision requires approved collection, disclosure-risk review, and consent compatibility. |
| Study 1 de-identified coded records | CONTROLLED | No release by default; only after ethical approval, de-identification review, and an approved request process. |
| Study 1 non-identifying aggregate outcome tables | AGGREGATE_ONLY | Release only when cell sizes and narrative detail do not create re-identification risk. |

## Operational safeguards

- Keep contact/consent records separate from study IDs and analysis data.
- Keep allocation, coder-blinding, and raw-text access separate from any review
  or publication package.
- Do not place raw source text in CSV templates, issue trackers, code comments,
  screenshots, demonstrations, or supplementary archives.
- Do not promise deletion, confidentiality, or retention periods beyond the
  final approved institutional policy.
- Before any future release, perform a content, metadata, filename, link, and
  Git-history audit; a license label alone is not a privacy clearance.
