# Deterministic anonymous A0 poster-content rationale

## Status

This plan was generated only after immutable public-data results, a fact packet, and the final figure manifest were supplied. It is a selection-and-content artifact, not an analysis.

## Fixed selection rule

Resolve only predeclared semantic keys. Never rank, filter, break ties, or phrase a claim using effect magnitude, confidence interval, p value, FDR value, direction, or apparent favorability.

Every judged construct selected by this policy retains both predeclared frozen judges. The selector does not access effect estimates, confidence intervals, p values, FDR values, output-change directions, rankings, or favorability.

## Provenance bindings

- RESULTS_FREEZE SHA-256: `e0aa7a206fc64d7613270baee26e979615c606424d30ffe2d482e9162a53e560`
- fact-packet manifest SHA-256: `a32752feb913e5135cc41f33bc14c1f11c71ac39464d9b6382e0493d0d2eaf8a`
- final figure manifest SHA-256: `ce9e10d8a886281c52b6c4b77c5ffc122c68a50321bed1d574b077790a7db5c9`
- policy ID: `anonymous_a0_poster_content_selection_v1`

## Fact-level semantic trace

| Family | Fact ID | Semantic key | Candidate count | Measurement status | Analysis status | Source table hash | Source row |
| --- | --- | --- | ---: | --- | --- | --- | ---: |
| RQ2 | RQ2_0013 | construct=task_answer; contrast=intent_minus_generic; judge=Phi_3.5_mini_2fe19245 | 1 | MEASUREMENT_UNSTABLE | ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `6a62a5fc2f45b1ccecd244a24d35d30198c05403195abddd7f14b615f026a971` | 13 |
| RQ2 | RQ2_0033 | construct=task_answer; contrast=intent_minus_generic; judge=Qwen2.5_1.5B_989aa798 | 1 | MEASUREMENT_UNSTABLE | ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `6a62a5fc2f45b1ccecd244a24d35d30198c05403195abddd7f14b615f026a971` | 33 |
| RQ2 | RQ2_0011 | construct=spatial_relation; contrast=intent_minus_generic; judge=Phi_3.5_mini_2fe19245 | 1 | MEASUREMENT_UNSTABLE | ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `6a62a5fc2f45b1ccecd244a24d35d30198c05403195abddd7f14b615f026a971` | 11 |
| RQ2 | RQ2_0031 | construct=spatial_relation; contrast=intent_minus_generic; judge=Qwen2.5_1.5B_989aa798 | 1 | MEASUREMENT_UNSTABLE | ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `6a62a5fc2f45b1ccecd244a24d35d30198c05403195abddd7f14b615f026a971` | 31 |
| RQ3 | RQ3_0001 | metric=human_answer_mode_string_coverage; contrast=intent_minus_generic | 1 | PUBLIC_HUMAN_BENCHMARKED | ESTIMATED_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `19247d8ab604f52a3396d780061d2c902c295f78e48d622475b30e39b30de73b` | 1 |
| RQ3 | RQ3_0003 | metric=human_caption_max_token_f1; contrast=intent_minus_generic | 1 | PUBLIC_HUMAN_BENCHMARKED | ESTIMATED_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `19247d8ab604f52a3396d780061d2c902c295f78e48d622475b30e39b30de73b` | 3 |
| RQ4 | RQ4_0001 | space_pair=DREAM|BLV_USER_QUESTION | 1 | N/A | DISTRIBUTIONAL_TEXT_PROFILE_ONLY | `cc575e36b81560dced1d4b6441ccdc59446aa84dda5ceb6944af6101e258f6ac` | 1 |
| RQ4 | RQ4_0012 | space_pair=HUMAN_CAPTION|AI_ACCESSIBILITY_STEERED | 1 | N/A | DISTRIBUTIONAL_TEXT_PROFILE_ONLY | `cc575e36b81560dced1d4b6441ccdc59446aa84dda5ceb6944af6101e258f6ac` | 12 |
| RQ5 | RQ5_0008 | construct=identity_inference; contrast=accessibility_minus_intent; judge=Phi_3.5_mini_2fe19245 | 1 | MEASUREMENT_UNSTABLE | ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `85abbd104d5fadcbfe5cf9b8029da66f4d97465c2cd4a6dc6db700ab9948848c` | 8 |
| RQ5 | RQ5_0028 | construct=identity_inference; contrast=accessibility_minus_intent; judge=Qwen2.5_1.5B_989aa798 | 1 | MEASUREMENT_UNSTABLE | ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `85abbd104d5fadcbfe5cf9b8029da66f4d97465c2cd4a6dc6db700ab9948848c` | 28 |
| RQ5 | RQ5_0010 | construct=social_intent_inference; contrast=accessibility_minus_intent; judge=Phi_3.5_mini_2fe19245 | 1 | MEASUREMENT_UNSTABLE | ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `85abbd104d5fadcbfe5cf9b8029da66f4d97465c2cd4a6dc6db700ab9948848c` | 10 |
| RQ5 | RQ5_0030 | construct=social_intent_inference; contrast=accessibility_minus_intent; judge=Qwen2.5_1.5B_989aa798 | 1 | MEASUREMENT_UNSTABLE | ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP | `85abbd104d5fadcbfe5cf9b8029da66f4d97465c2cd4a6dc6db700ab9948848c` | 30 |

## Interpretation boundary

The content plan preserves computational measurement and released-human-reference boundaries. It does not claim that synthetic judges are human-equivalent, that released human references are same-item ratings, or that text-profile similarity establishes cognition, dream change, or lived accessibility value.
