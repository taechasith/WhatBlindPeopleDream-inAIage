# Deterministic render-plan generator

`code/33_build_anonymous_manuscript_render_plan.py` is the required
post-`RESULTS_FREEZE` bridge between the immutable fact packet and the
anonymous manuscript renderer. It is deliberately not a result-ranking tool.

The frozen policy at
`config/manuscript_render_plan_policy_v1.json` selects fact IDs with fixed
semantic keys only: research-question family, construct/metric/space pair,
prompt contrast, and both named frozen judges where a judged construct is
selected. It never reads or uses estimates, intervals, p values, FDR values,
directions, or effect rankings to decide what is displayed.

The policy reserves twelve result rows and three figures for a four-page
excluding-references target. It produces:

- `manuscript_render_plan.json`, valid input for the anonymous renderer;
- `MANUSCRIPT_RENDER_PLAN_RATIONALE.md`, documenting the predeclared semantic
  rationale and hash bindings;
- `RENDER_PLAN_SELECTION_TRACE.csv`, fact-level provenance without effect
  values; and
- `MANUSCRIPT_RENDER_PLAN_MANIFEST.json`, an immutable receipt.

Run only after the frozen result receipt, fact packet, and final figure manifest
exist:

```powershell
python code/33_build_anonymous_manuscript_render_plan.py `
  --results-freeze results/results_freeze/RESULTS_FREEZE.json `
  --fact-packet-dir paper/anonymous/generated `
  --figures-dir figures/final_public_data_v1 `
  --outdir paper/anonymous/render_plan
```

The later anonymous reference audit must still verify every policy citation key
against the final bibliography before `code/32_render_anonymous_chi_manuscript.py`
is allowed to render source. The generator does not draft prose from empirical
values and does not replace final claim, reference, anonymity, ethics, PDF, or
CHI-call audits.
