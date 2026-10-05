# Study 0 status: public-data sensory audit

**Status:** `EXPLORATORY_AUTOMATED_ONLY` / hypothesis-generating; **not**
confirmatory, human-coded, or causal evidence.

Study 0 compares released DreamBank reports (381), BLV-originating VizWiz
questions (24,842), and a small released AI-description set (28) using
deterministic lexical candidate rules. It is not semantic annotation, an LLM
classification, or human coding. Independent double coding is pending and no
reliability statistic is estimable.

## Applicability correction and current diagnostic outputs

The initial automated diagnostic treated all 29 codebook columns as available
for every source type. That was not defensible for three categories whose
definitions require information absent from one or more source roles. The
current files record those cells as unavailable rather than as zero:

- `task_relevance`: unavailable for DreamBank reports and unpaired AI
  descriptions;
- `intent_match`: unavailable without a paired request and response;
- `unsupported_information`: unavailable without a reference/gold validation
  basis.

`results/alignment_metrics.csv` therefore calculates each comparison on the 26
remaining mechanically applicable lexical columns, and explicitly records the
three exclusions. Current exploratory point estimates are:

| Comparison | Jensen--Shannon divergence | Units |
|---|---:|---:|
| AI descriptions vs. BLV questions | 0.350812 | 28 vs. 24,842 |
| AI descriptions vs. DreamBank reports | 0.191052 | 28 vs. 381 |
| BLV questions vs. DreamBank reports | 0.432980 | 24,842 vs. 381 |

These values describe distributions of lexical-rule hits only. They do **not**
measure sensory cognition, user preference, task success, AI hallucination,
or a causal AI effect on dreams. They must not be interpreted as cognitive
transfer or evidence that AI descriptions enter dreams.

The correction is documented in `STUDY0_REGENERATION_NOTES.md` and
`logs/deviations.md`. The primary limitations, sample flow, and current machine
outputs remain in `results/limitations.md`, `results/sample_flow.csv`, and
`results/alignment_metrics.csv`.
