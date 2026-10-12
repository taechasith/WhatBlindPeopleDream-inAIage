# Deterministic anonymous manuscript render-plan rationale

## Status

This plan was generated only after the immutable public-data RESULTS_FREEZE and paper fact packet were supplied. It is a selection and rendering-plan artifact, not an analysis or a manuscript.

## Fixed selection rule

Select predeclared semantic anchors only; never rank, filter, or break ties using effect magnitude, confidence interval, p value, FDR value, direction, or apparent favorability.

The policy reserves at most 12 displayed result rows and 3 manuscript figures for the stated four-page target. Every selected judged construct includes both predeclared frozen judges; neither judge is removed because of its estimate or statistical result.

## Provenance bindings

- RESULTS_FREEZE SHA-256: `e0aa7a206fc64d7613270baee26e979615c606424d30ffe2d482e9162a53e560`
- paper fact-packet manifest SHA-256: `a32752feb913e5135cc41f33bc14c1f11c71ac39464d9b6382e0493d0d2eaf8a`
- final figure manifest SHA-256: `ce9e10d8a886281c52b6c4b77c5ffc122c68a50321bed1d574b077790a7db5c9`
- selection-policy ID: `anonymous_chi_render_selection_v1`

## Semantic selection blocks

### RQ2

These predeclared anchors represent question-linked answer provision and explicit spatial relation under the user-intent prompt contrast. Both frozen measurement judges are retained for each selected construct.

Selected fact IDs: RQ2_0013, RQ2_0033, RQ2_0011, RQ2_0031.

### RQ3

These are the two prospectively specified, bounded released-human-reference metrics for the direct BLV-intent contrast. They remain reference-alignment measures, not human ratings or BLV preference claims.

Selected fact IDs: RQ3_0001, RQ3_0003.

### RQ4

These predeclared comparisons anchor the theoretical distinction between historical dream expression and BLV intent, and the bounded comparison between human captions and accessibility-steered AI text. They are distributional text-profile comparisons only.

Selected fact IDs: RQ4_0001, RQ4_0012.

### RQ5

These predeclared output-text properties directly address the fixed accessibility instruction not to infer identity, relationships, emotion, or intent without visible support. Both frozen measurement judges are retained for each selected construct.

Selected fact IDs: RQ5_0008, RQ5_0028, RQ5_0010, RQ5_0030.

## Fact-level trace

The following IDs are resolved solely by the semantic keys below. This trace deliberately excludes estimates, intervals, p values, FDR values, directions, and rankings.

| Family | Fact ID | Semantic key | Candidate count | Source table hash | Source row |
| --- | --- | --- | ---: | --- | ---: |
| RQ2 | RQ2_0013 | construct=task_answer; contrast=intent_minus_generic; judge=Phi_3.5_mini_2fe19245 | 1 | `6a62a5fc2f45b1ccecd244a24d35d30198c05403195abddd7f14b615f026a971` | 13 |
| RQ2 | RQ2_0033 | construct=task_answer; contrast=intent_minus_generic; judge=Qwen2.5_1.5B_989aa798 | 1 | `6a62a5fc2f45b1ccecd244a24d35d30198c05403195abddd7f14b615f026a971` | 33 |
| RQ2 | RQ2_0011 | construct=spatial_relation; contrast=intent_minus_generic; judge=Phi_3.5_mini_2fe19245 | 1 | `6a62a5fc2f45b1ccecd244a24d35d30198c05403195abddd7f14b615f026a971` | 11 |
| RQ2 | RQ2_0031 | construct=spatial_relation; contrast=intent_minus_generic; judge=Qwen2.5_1.5B_989aa798 | 1 | `6a62a5fc2f45b1ccecd244a24d35d30198c05403195abddd7f14b615f026a971` | 31 |
| RQ3 | RQ3_0001 | metric=human_answer_mode_string_coverage; contrast=intent_minus_generic | 1 | `19247d8ab604f52a3396d780061d2c902c295f78e48d622475b30e39b30de73b` | 1 |
| RQ3 | RQ3_0003 | metric=human_caption_max_token_f1; contrast=intent_minus_generic | 1 | `19247d8ab604f52a3396d780061d2c902c295f78e48d622475b30e39b30de73b` | 3 |
| RQ4 | RQ4_0001 | space_pair=DREAM|BLV_USER_QUESTION | 1 | `cc575e36b81560dced1d4b6441ccdc59446aa84dda5ceb6944af6101e258f6ac` | 1 |
| RQ4 | RQ4_0012 | space_pair=HUMAN_CAPTION|AI_ACCESSIBILITY_STEERED | 1 | `cc575e36b81560dced1d4b6441ccdc59446aa84dda5ceb6944af6101e258f6ac` | 12 |
| RQ5 | RQ5_0008 | construct=identity_inference; contrast=accessibility_minus_intent; judge=Phi_3.5_mini_2fe19245 | 1 | `85abbd104d5fadcbfe5cf9b8029da66f4d97465c2cd4a6dc6db700ab9948848c` | 8 |
| RQ5 | RQ5_0028 | construct=identity_inference; contrast=accessibility_minus_intent; judge=Qwen2.5_1.5B_989aa798 | 1 | `85abbd104d5fadcbfe5cf9b8029da66f4d97465c2cd4a6dc6db700ab9948848c` | 28 |
| RQ5 | RQ5_0010 | construct=social_intent_inference; contrast=accessibility_minus_intent; judge=Phi_3.5_mini_2fe19245 | 1 | `85abbd104d5fadcbfe5cf9b8029da66f4d97465c2cd4a6dc6db700ab9948848c` | 10 |
| RQ5 | RQ5_0030 | construct=social_intent_inference; contrast=accessibility_minus_intent; judge=Qwen2.5_1.5B_989aa798 | 1 | `85abbd104d5fadcbfe5cf9b8029da66f4d97465c2cd4a6dc6db700ab9948848c` | 30 |

## Citation and scope boundary

The plan names predeclared citation keys only. The later anonymous reference audit must verify every key against the final bibliography before manuscript rendering. The rendered paper must retain the public-data scope: model-derived text measurements are not human judgments, and the study does not test changes in dreams, cognition, neural organization, or lived experience.
