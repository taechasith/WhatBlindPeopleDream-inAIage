# What Blind People Dream, Ask, and What AI Tells Them

## A public-data study of sensory mediation in the AI age

This repository contains the reproducible research record. It connects four representational spaces:

```text
DreamSpace  -> historical blind dream expression
IntentSpace -> information sought in BLV-originating questions
HumanSpace  -> released human descriptions and accessibility references
AISpace     -> information exposed by a frozen multimodal model
```

The computational intervention holds each image-question item and model fixed
while changing the prompt condition. It tests whether BLV-originating intent
changes observable properties of AI output. It does not test effects on people.

## Read this first

- This is a **public-data-only** study: no new participants, human labels, or
  dream reports were collected for the active scope.
- Synthetic judges are **computational measurement instruments**, not people,
  BLV users, or substitutes for lived experience.
- Dream-language distances are distributional text comparisons. They do not
  establish cognitive equivalence, dream incorporation, neural change, or an
  effect of AI on blind people.
- Public human-labelled datasets provide bounded external calibration only for
  the construct and population documented for that source.

## Current research record

The frozen analysis used 1,000 locked VizWiz image-question items under three
prompt conditions, yielding 3,000 frozen VLM outputs. Two frozen, distinct
model-family judges supplied computational measurements. Results, final figures,
and publication artifacts are bound to checksums and manifests.

Important negative result: preselected RQ2 and RQ5 measurements did not pass
the computational robustness gate. They are retained as `MEASUREMENT_UNSTABLE`
and are reported as not estimable rather than converted into substantive
claims. This repository preserves that limitation.

The local publication audit is recorded in
[`audits/final_anonymous_package_v3_measurement_gated/`](audits/final_anonymous_package_v3_measurement_gated/).
It is a technical package audit, not institutional ethics approval or an
external submission decision.

## Repository map

| Path | What it contains |
| --- | --- |
| `PROTOCOL_PUBLIC_DATA_v2.md` | Active public-data protocol and scope boundary |
| `PUBLIC_DATA_ANALYSIS_PLAN_v2.md` | Frozen analysis plan for RQ2-RQ5 |
| `code/` | Deterministic corpus, validation, analysis, figure, and publication utilities |
| `data/MANIFEST.csv`, `data/LICENSES.md` | Dataset provenance, access routes, and licensing notes |
| `results/` | Frozen computational results, calibration records, robustness records, and ledgers |
| `figures/final_public_data_v1/` | Final figures plus text alternatives and checksums |
| `paper/anonymous/` | Anonymous source, fact packet, references, and publication traceability |
| `poster/anonymous/` | Anonymous poster content plan and provenance |
| `audits/` | Reproducibility, claim, anonymity, reference, and publication audits |
| `future_human_study/`, `future_human_validation/` | Archived future-work materials; not part of the current study |

## Reproduce safely

Use Python 3.10+ in a clean environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Then read [`REPRODUCTION.md`](REPRODUCTION.md) and
[`REPRODUCTION_STATUS.md`](REPRODUCTION_STATUS.md) before running any command.
Local raw corpora, images, private model manifests, model caches, and output
text are intentionally excluded from Git. Acquire sources only through the
documented provenance routes and only where their licenses permit it.

Useful non-destructive checks:

```powershell
python code/verify_provenance.py
python code/32_audit_final_anonymous_package.py --help
```

Do not run a script merely because it is present: frozen outputs and build
directories are immutable by design. A new reproduction run must use a new
output directory and retain its provenance receipt.

## Outputs and submission boundary

The anonymous manuscript and A0 poster are generated locally from frozen
artifacts. Rendered PDFs are deliberately ignored because they are build
outputs; their source, manifests, checksums, and audit records are retained.

Before any external dissemination, complete the applicable institutional ethics
determination, re-check the live CHI call, verify anonymization, and confirm
the data-sharing terms of every included source. Do not add author identities,
affiliations, email addresses, personal repositories, or private data to an
anonymous review package.

## Responsible reuse

Please preserve the measurement tiers and claim boundaries if you reuse this
work. In particular, do not reinterpret model-derived labels as human judgment,
and do not silently remove null, contradictory, unstable, or non-estimable
findings.

No license is asserted by this repository until a maintainer adds an explicit
license file. Third-party datasets and model weights retain their own terms.
