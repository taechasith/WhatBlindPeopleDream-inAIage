"""Compute transparent pre-adjudication agreement for blinded human coders.

This tool never creates, changes, or adjudicates coding labels. It validates
that all supplied files cover the same blinded rows, preserves pairwise results,
and calculates a nominal three-coder Krippendorff alpha when Coder C is present.
`NA` is retained as missingness and is never converted to a negative label.
"""
from __future__ import annotations

import argparse
import itertools
from pathlib import Path

import pandas as pd


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


def read_coder(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, dtype=str)
    required = {"blind_item_id", *FIELDS}
    if not required.issubset(frame.columns):
        raise ValueError(f"{path} must include blind_item_id and all codebook fields.")
    if frame.blind_item_id.duplicated().any():
        raise ValueError(f"{path} contains duplicate blind_item_id values.")
    return frame[["blind_item_id", *FIELDS]].copy()


def krippendorff_alpha_nominal(values: pd.DataFrame) -> float | None:
    """Nominal alpha for 0/1 labels with NA missingness; no dependency on a package."""
    observed_disagreements = 0
    observed_pairs = 0
    pooled: list[str] = []
    for _, row in values.iterrows():
        labels = [value for value in row.tolist() if value in {"0", "1"}]
        pooled.extend(labels)
        for left, right in itertools.combinations(labels, 2):
            observed_pairs += 1
            observed_disagreements += int(left != right)
    if observed_pairs == 0 or len(pooled) < 2:
        return None
    n0, n1 = pooled.count("0"), pooled.count("1")
    expected_disagreement = (2 * n0 * n1) / (len(pooled) * (len(pooled) - 1))
    if expected_disagreement == 0:
        return None
    return 1 - (observed_disagreements / observed_pairs) / expected_disagreement


def cohen_kappa_binary(left: pd.Series, right: pd.Series) -> float | None:
    """Binary Cohen's kappa, avoiding an undeclared sklearn dependency."""
    n = len(left)
    if n == 0 or left.nunique() < 2 or right.nunique() < 2:
        return None
    observed = float((left == right).mean())
    p_left_1 = float((left == "1").mean())
    p_right_1 = float((right == "1").mean())
    expected = p_left_1 * p_right_1 + (1 - p_left_1) * (1 - p_right_1)
    if expected == 1:
        return None
    return (observed - expected) / (1 - expected)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coder-a", type=Path, required=True)
    parser.add_argument("--coder-b", type=Path, required=True)
    parser.add_argument("--coder-c", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    coders = {"A": read_coder(args.coder_a), "B": read_coder(args.coder_b)}
    if args.coder_c:
        coders["C"] = read_coder(args.coder_c)

    reference_ids = coders["A"].blind_item_id.tolist()
    if any(frame.blind_item_id.tolist() != reference_ids for frame in coders.values()):
        raise ValueError("All independent coder files must cover the same blinded rows in the same frozen order.")

    rows: list[dict[str, object]] = []
    for field in FIELDS:
        normalized = {coder: frame[field].map(normalize) for coder, frame in coders.items()}
        alpha = krippendorff_alpha_nominal(pd.DataFrame(normalized)) if len(coders) == 3 else None
        for left_name, right_name in itertools.combinations(coders, 2):
            left, right = normalized[left_name], normalized[right_name]
            usable = left.isin({"0", "1"}) & right.isin({"0", "1"})
            n = int(usable.sum())
            agreement = float((left[usable] == right[usable]).mean()) if n else None
            kappa = cohen_kappa_binary(left[usable], right[usable])
            rows.append({
                "field": field,
                "coder_pair": f"{left_name}{right_name}",
                "n_packet": len(reference_ids),
                "n_both_binary": n,
                "n_any_na": int((~usable).sum()),
                "exact_agreement_binary": agreement,
                "cohens_kappa_binary": kappa,
                "krippendorff_alpha_nominal_three_coder": alpha,
                "n_coders_supplied": len(coders),
                "alt_test_status_note": (
                    "THREE_HUMAN_CODERS_AVAILABLE"
                    if len(coders) == 3 else "ALT_TEST_TWO_HUMAN_LIMITATION"
                ),
                "status": "ESTIMABLE" if kappa is not None else "NOT_ESTIMABLE_DEGENERATE_OR_NO_BINARY_PAIR",
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print(f"RELIABILITY_PRE_ADJUDICATION_WRITTEN\t{args.output}")


if __name__ == "__main__":
    main()
