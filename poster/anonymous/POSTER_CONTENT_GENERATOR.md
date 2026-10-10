# Deterministic anonymous A0 poster-content generator

`code/34_build_anonymous_poster_content.py` is the post-`RESULTS_FREEZE`
bridge between the immutable paper fact packet and the `POSTER_CONTENT.json`
required by `code/31_generate_anonymous_a0_poster.py`.

It is deliberately a content-plan generator, not an analysis or a language
model. It consumes only these completed artifacts:

- `RESULTS_FREEZE.json`;
- a verified paper fact packet made by `code/31_build_paper_fact_packet.py`; and
- the final figure manifest and figures made from the same freeze.

The frozen policy in
`config/poster_content_policy_v1.json` selects facts with semantic keys only:
research-question family, construct or metric, prompt contrast, named judge,
and unordered representational-space pair. It rejects a policy that includes
effects, confidence intervals, p values, FDR values, directions, rankings, or
apparent favorability. For every selected judged construct, both predeclared
frozen judges are retained.

The generated prose names the measurement and analysis status carried by the
selected fact records, while figures retain the frozen numeric estimates. It
does not convert model-derived text measurement into human judgment or make
claims about BLV lived experience, cognitive change, neural organization, or
dream incorporation.

## Run after result freeze

```powershell
python code/34_build_anonymous_poster_content.py `
  --results-freeze results/results_freeze/RESULTS_FREEZE.json `
  --fact-packet-dir paper/anonymous/generated `
  --figures-dir figures/final_public_data_v1 `
  --outdir poster/anonymous/content_plan
```

This writes an immutable directory with:

- `POSTER_CONTENT.json` — renderer input matching
  `POSTER_CONTENT_SCHEMA.md`;
- `POSTER_CONTENT_SELECTION_TRACE.csv` — semantic-key-to-fact provenance;
- `POSTER_CONTENT_RATIONALE.md` — selection and interpretation boundary; and
- `POSTER_CONTENT_MANIFEST.json` — hash bindings and checksums.

Then build the review-stage A0 poster only from the generated content record:

```powershell
./compute/run_anonymous_a0_poster.ps1 `
  -ContentJson poster/anonymous/content_plan/POSTER_CONTENT.json
```

The final anonymous reference, claim, ethics, accessibility, PDF, and CHI
compliance audits remain required. The content planner cannot make a paper or
poster submission-ready by itself.
