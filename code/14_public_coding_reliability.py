"""Compute transparent pre-adjudication agreement for two blinded coder files.

This tool never creates coding labels. It treats NA as a valid missingness
state, reports its rate, and calculates binary Cohen's kappa only where both
coders made 0/1 judgments.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score


FIELDS = (
    "task_answer", "task_relevance", "spatial_relation", "grounded_uncertainty",
    "unsupported_information", "identity_inference", "social_intent_inference",
    "unrequested_visual_detail", "accessibility_grounded_content", "ambiguity",
)


def normalize(value: object) -> str:
    value = str(value).strip().upper()
    if value in {"0", "1", "NA"}:
        return value
    raise ValueError(f"Unexpected coding value: {value!r}; use only 0, 1, or NA.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coder-a", type=Path, required=True)
    parser.add_argument("--coder-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    a, b = pd.read_csv(args.coder_a, dtype=str), pd.read_csv(args.coder_b, dtype=str)
    required = {"blind_item_id", *FIELDS}
    if not required.issubset(a.columns) or not required.issubset(b.columns):
        raise ValueError("Both coder files must include blind_item_id and all codebook fields.")
    if a.blind_item_id.duplicated().any() or b.blind_item_id.duplicated().any():
        raise ValueError("Coder packets contain duplicate blind_item_id values.")
    merged = a[["blind_item_id", *FIELDS]].merge(b[["blind_item_id", *FIELDS]], on="blind_item_id", suffixes=("_a", "_b"), validate="one_to_one")
    if len(merged) != len(a) or len(merged) != len(b):
        raise ValueError("Independent coder files must cover exactly the same packet rows.")
    summary = []
    for field in FIELDS:
        left, right = merged[f"{field}_a"].map(normalize), merged[f"{field}_b"].map(normalize)
        estimable = left.isin({"0", "1"}) & right.isin({"0", "1"})
        n = int(estimable.sum())
        agreement = float((left[estimable] == right[estimable]).mean()) if n else None
        kappa = float(cohen_kappa_score(left[estimable], right[estimable], labels=["0", "1"])) if n and left[estimable].nunique() > 1 and right[estimable].nunique() > 1 else None
        summary.append({"field": field, "n_packet": len(merged), "n_both_binary": n,
                        "n_any_na": int((~estimable).sum()), "exact_agreement_binary": agreement,
                        "cohens_kappa_binary": kappa,
                        "status": "ESTIMABLE" if kappa is not None else "NOT_ESTIMABLE_DEGENERATE_OR_NO_BINARY_PAIR"})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary).to_csv(args.output, index=False)
    print(f"RELIABILITY_PRE_ADJUDICATION_WRITTEN\t{args.output}")


if __name__ == "__main__":
    main()
