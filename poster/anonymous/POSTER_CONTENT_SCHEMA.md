# Post-results Content Contract for the Anonymous A0 Poster

Create `POSTER_CONTENT.json` only after the manuscript fact packet, result ledger, claim audit, and anonymity audit are complete. Do not create a placeholder content record.

The JSON object must contain these fields:

| Field | Requirement |
|---|---|
| `schema_version` | Integer `1`. |
| `review_stage` | Exact string `ANONYMOUS_REVIEW`. |
| `results_freeze_sha256` | SHA-256 of the `RESULTS_FREEZE.json` used for the poster. |
| `figure_manifest_sha256` | SHA-256 of the final `FIGURE_MANIFEST.csv`. |
| `title` | Anonymous final title, maximum 190 characters. |
| `subtitle` | Ledger-backed study summary, maximum 280 characters. |
| `sample_summary` | Exact N and scope text from frozen records, maximum 220 characters. |
| `sections.methods` | Two to five concise method bullets. |
| `sections.findings` | Two to five result-ledger-backed finding bullets. |
| `sections.implications` | One to four bounded design-implication bullets. |
| `sections.limitations` | Two to five limitation bullets, including the causal boundary where applicable. |
| `ethics_note` | Anonymous statement of the public-data/secondary-analysis ethics context. |
| `discussion_points` | Two to five anonymous key discussion-point bullets. |
| `result_trace_ids` | Non-empty IDs or paths that point from poster claims to the final result/claim ledger. |

Every textual field is scanned for placeholder markers, email addresses, URLs, repository links, and contact/affiliation language. The content record must not introduce author or institution metadata. The renderer verifies the two input hashes before it lays out any text.

Use final accessible figures from `figures/final_public_data_v1/`; do not substitute figures, rerun calculations, or include synthetic planning results.
