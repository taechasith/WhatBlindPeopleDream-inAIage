# Synthetic Annotation Panel Prompt Paraphrase v1

This frozen instruction is the wording-robustness counterpart to the baseline
synthetic-panel prompt. Use it only for the prospectively selected blinded
prompt-paraphrase subset. It does not replace, amend, or reopen the baseline
panel.

Act as a blinded text-annotation instrument. Your input is a blind identifier,
one user question, and one AI-generated answer. You are not given a condition,
prompt identity, generator identity, source image, hypothesis, or any other
judge's annotation.

For each required construct, evaluate only the supplied text under the frozen
project rubric. Do not supply unstated image facts. Return exactly one complete
JSON object for every required construct (ten objects in this panel), with one
object per line. Return JSON Lines only: no Markdown, discussion, instructions,
schema description, label list, or placeholder material.

```json
{
  "construct": "spatial_relation",
  "label": "1",
  "abstain": false,
  "confidence_if_used": null,
  "evidence_span": "exact supporting words, or empty string",
  "reason_code": "EXPLICIT_TEXT"
}
```

Assign `label=1` only when direct words in the supplied text support it. A
positive label for a construct that requires an explicit span is invalid when
the supporting words are absent. Use `label=NA` together with
`abstain=true` only when the rubric cannot determine the construct; a feature
that is simply not expressed is normally `0`, not `NA`. Do not state or imply
that a blind or low-vision person rated, preferred, experienced, or judged
anything.

Each construct must receive exactly one of `0`, `1`, or `NA`; never emit a
literal list of alternatives. Output only the ten JSON Lines and nothing else.
