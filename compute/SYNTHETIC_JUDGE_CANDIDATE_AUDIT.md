# Synthetic judge candidate audit

## SmolLM2-1.7B-Instruct

- Model: `HuggingFaceTB/SmolLM2-1.7B-Instruct`
- Immutable revision: `31b70e2e869a7173562077fd711b654946d38674`
- License: Apache-2.0
- Intended role: text-only blinded synthetic annotation judge.
- Technical test material: one researcher-created, non-analytic fixture; no
  VizWiz item, frozen model output, condition mapping, or human label was used.
- Result: rejected before analytic annotation. CUDA model loading and generation
  completed, but two deterministic preflights failed the required multi-
  construct JSON schema (`PARSE_ERROR:KeyError`): the response supplied a
  single schema-example object rather than the required labels array.
- Decision basis: schema reliability only, not any research outcome.
- Consequence: it must not generate analytic synthetic labels under panel v1.
