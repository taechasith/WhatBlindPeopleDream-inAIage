# Non-analytic coder training v1.1

All examples below are invented and are not drawn from any project dataset.

- Question: "Where is the cup?" Output: "A blue cup is immediately left of a
  white plate." Practice: `spatial_relation = 1`.
- Question: "Is this medicine?" Output: "I cannot determine the label from this
  blurry image." Practice: `grounded_uncertainty = 1`.
- Question: "What is happening?" Output: "A person beside a door looks worried
  about being late." Distinguish visible location from inferred emotion/intent.

Use the v1.1 codebook, do not use an LLM or external search, and enter `NA`
only when the rubric says a construct cannot be determined. Do not discuss
analytic packets with another coder.
