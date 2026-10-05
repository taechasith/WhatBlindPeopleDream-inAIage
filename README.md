# What People Dream in the AI Age

## Research status

This repository's active CHI 2027 scope is a public-data study of three
observable spaces: blind dream expression (DreamSpace), BLV-originating
information intent (IntentSpace), and human/AI accessibility mediation
(MediationSpace). The governing documents are `SCOPE_CHANGE_2026-10-06.md`,
`PROTOCOL_PUBLIC_DATA_v2.md`, and `PUBLIC_DATA_ANALYSIS_PLAN_v2.md`.

Existing Study 0 output remains exploratory/hypothesis-generating. The prior
prospective human dream-incorporation protocol has been preserved under
`future_human_study/` and is outside the current paper. No current claim
concerns AI changing dreams, cognition, or neural organization.

## Repository map

| Path | Purpose | Release status |
| --- | --- | --- |
| `PROTOCOL_PUBLIC_DATA_v2.md`, `PUBLIC_DATA_ANALYSIS_PLAN_v2.md` | Active public-data computational-intervention protocol and plan | Pre-outcome freeze |
| `PROTOCOL.md`, `ANALYSIS_PLAN.md` | Historical Study 0 protocol and analysis plan | Exploratory context |
| `future_human_study/` | Superseded prospective human-study materials | Future work only; no authorization |
| `code/` | Active public-data processing, provenance, and export utilities | Source-only; inspect before execution |
| `data/MANIFEST.csv`, `data/CHECKSUMS.csv`, `data/LICENSES.md` | Source provenance, local-file hashes, and access restrictions | Metadata only; no corpus text |
| `results/` | Aggregate exploratory and synthetic-only outputs | Never interpret synthetic outputs as empirical |
| `future_human_study/synthetic/` | Clearly labeled former human-study test fixtures | Not empirical evidence |

## Reproduction and data access

Start with `REPRODUCTION.md`, `REPRODUCTION_STATUS.md`, and
`DATA_DICTIONARY.md`. The raw and processed source corpora are intentionally
ignored by Git. They are not included in this repository, must not be inferred
from aggregate outputs, and must be independently acquired only where their
licenses and access terms permit it.

The current overall reproduction status is `PARTIAL_REPRODUCTION`, not a clean
reproduction pass. Raw text and images remain excluded from version control;
every new public source must be re-acquired under its recorded terms.

## Privacy, licensing, and anonymous review

Do not publish raw dream reports, raw source-platform text, participant records,
source images, contact information, allocation files, or coder packets that
contain source text. Consult `DATA_SHARING_PLAN_FINAL.md` and
`ANONYMOUS_RELEASE_POLICY.md` before preparing any archive, supplement, or
repository link.

`code/export_anonymous_review.py` creates a deliberately narrow, allowlisted
review bundle after a content scan. It is not a substitute for a final human
anonymity, legal, accessibility, or conference-policy audit.

## Research-integrity commitments

- No fabricated participants, quotations, annotations, results, or citations.
- No inference of blindness onset where source metadata do not state it.
- No claim that AI changes dreams, cognition, or neural organization. The
  current intervention changes model inputs, not human experience.
- Synthetic records and planning simulations remain explicitly non-empirical.
- All substantive AI-use disclosures are tracked in `AI_USE_LOG.md`; unresolved
  provenance is marked unresolved rather than reconstructed from guesswork.
