# What People Dream in the AI Age

## Research status

This repository contains two deliberately separated research components.

- **Study 0** is an exploratory, public-data sensory-alignment audit. Its
  automated lexical labels, small AI-description sample, and distributional
  comparisons are hypothesis-generating only; they are not confirmatory evidence
  of cognitive change, dream change, or harm.
- **Study 1** is a prospective AI-mediated dream-incorporation study. Only
  non-human planning, synthetic-data testing, and draft materials are present.
  The repository status is `NOT_SUBMITTED` for institutional ethics review. No
  recruitment, contact, consent, participant exposure, recording, or human data
  collection is authorized by this repository.

Read `STUDY0_STATUS.md`, `ethics/ETHICS_STATUS.md`, and
`STUDY1_WAITING_PERIOD_STATUS.md` before interpreting any result.

## Repository map

| Path | Purpose | Release status |
| --- | --- | --- |
| `PROTOCOL.md`, `ANALYSIS_PLAN.md` | Frozen Study 0 protocol and analysis plan | Review-safe after anonymity audit |
| `PROTOCOL_STUDY1_v1.md`, `STUDY1_DESIGN_FREEZE.md` | Prospective Study 1 planning materials | Draft; no participant authorization |
| `code/` | Processing, exploratory-analysis, synthetic-dry-run, provenance, and export utilities | Source-only; inspect before execution |
| `data/MANIFEST.csv`, `data/CHECKSUMS.csv`, `data/LICENSES.md` | Source provenance, local-file hashes, and access restrictions | Metadata only; no corpus text |
| `results/` | Aggregate exploratory and synthetic-only outputs | Never interpret synthetic outputs as empirical |
| `synthetic/` | Clearly labeled data used only to exercise the Study 1 pipeline | Public fixture; not participant data |
| `ethics/` | Non-deployed institutional-review drafts and status record | Do not deploy without determination/approval |

## Reproduction and data access

Start with `REPRODUCTION.md`, `REPRODUCTION_STATUS.md`, and
`DATA_DICTIONARY.md`. The raw and processed source corpora are intentionally
ignored by Git. They are not included in this repository, must not be inferred
from aggregate outputs, and must be independently acquired only where their
licenses and access terms permit it.

The current overall reproduction status is `PARTIAL_REPRODUCTION`, not a clean
reproduction pass. The authoritative Study 1 R power simulation and the
synthetic-only analysis dry run have been re-executed locally; raw Study 0
corpora, human coding, final exposure scripts, and independent clean-clone
reproduction remain unavailable or incomplete.

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
- No claim that AI changes dreams, cognition, or neural organization from Study
  0; Study 1 has not collected human data.
- Synthetic records and planning simulations remain explicitly non-empirical.
- All substantive AI-use disclosures are tracked in `AI_USE_LOG.md`; unresolved
  provenance is marked unresolved rather than reconstructed from guesswork.
