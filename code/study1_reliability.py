"""Compute Study 1 independent-coder reliability after blinded coding.

This script never creates labels. It keeps independent files immutable, rejects
incompatible keys/mappings, and reports NOT_ESTIMABLE for sparse data rather
than manufacturing a reliability estimate.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score


KEYS = ["blind_report_id", "unit_blind_id", "set_blind_label"]
CODE_MAPPING = {0: 0, 2: 1, 3: 1}
VALID_CODES = {0, 1, 2, 3, 9}


def _validate_coder(data: pd.DataFrame, source: str) -> pd.DataFrame:
    required = set(KEYS + ["report_eligibility", "ordinal_code", "primary_binary"])
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"{source}: missing columns {sorted(missing)}")
    if data.duplicated(KEYS).any():
        raise ValueError(f"{source}: duplicate blinded unit key(s).")
    data = data.copy()
    data["ordinal_code"] = pd.to_numeric(data["ordinal_code"], errors="coerce")
    data["primary_binary"] = pd.to_numeric(data["primary_binary"], errors="coerce")
    codes = set(data["ordinal_code"].dropna().unique())
    if not codes.issubset(VALID_CODES):
        raise ValueError(f"{source}: invalid ordinal code.")
    binary = set(data["primary_binary"].dropna().unique())
    if not binary.issubset({0, 1}):
        raise ValueError(f"{source}: invalid primary binary value.")
    mapped = data["ordinal_code"].map(CODE_MAPPING)
    have_mapping = mapped.notna()
    if (data.loc[have_mapping, "primary_binary"] != mapped.loc[have_mapping]).any():
        raise ValueError(f"{source}: primary_binary conflicts with frozen ordinal mapping.")
    if data.loc[data["ordinal_code"].isin([1, 9]), "primary_binary"].notna().any():
        raise ValueError(f"{source}: code 1/9 must have missing primary_binary.")
    valid_eligibility = {"ELIGIBLE", "NO_RECALL", "INELIGIBLE"}
    found = set(data["report_eligibility"].dropna().astype(str))
    if not found.issubset(valid_eligibility):
        raise ValueError(f"{source}: invalid report_eligibility.")
    return data


def _safe_kappa(left: pd.Series, right: pd.Series, weights: str | None = None) -> float:
    if len(left) < 2 or left.nunique() < 2 or right.nunique() < 2:
        return np.nan
    return float(cohen_kappa_score(left, right, weights=weights))


def _metrics(merged: pd.DataFrame) -> dict[str, tuple[float, int]]:
    both_eligible = merged.loc[
        merged["report_eligibility_a"].eq("ELIGIBLE")
        & merged["report_eligibility_b"].eq("ELIGIBLE")
    ].copy()
    ordinal = both_eligible.loc[
        both_eligible["ordinal_code_a"].isin([0, 1, 2, 3])
        & both_eligible["ordinal_code_b"].isin([0, 1, 2, 3])
    ]
    binary = both_eligible.dropna(subset=["primary_binary_a", "primary_binary_b"])
    agreement = np.nan if not len(binary) else float((binary["primary_binary_a"] == binary["primary_binary_b"]).mean())
    eligibility_agreement = float(
        (merged["report_eligibility_a"].astype(str) == merged["report_eligibility_b"].astype(str)).mean()
    )
    return {
        "ordinal_quadratic_weighted_kappa": (_safe_kappa(ordinal["ordinal_code_a"], ordinal["ordinal_code_b"], weights="quadratic"), len(ordinal)),
        "binary_cohens_kappa": (_safe_kappa(binary["primary_binary_a"], binary["primary_binary_b"]), len(binary)),
        "binary_percent_agreement": (agreement, len(binary)),
        "binary_pabak": ((2 * agreement - 1) if not np.isnan(agreement) else np.nan, len(binary)),
        "report_eligibility_percent_agreement": (eligibility_agreement, len(merged)),
    }


def _bootstrap_by_report(merged: pd.DataFrame, repetitions: int, seed: int) -> dict[str, list[float]]:
    rng = np.random.default_rng(seed)
    reports = merged["blind_report_id"].drop_duplicates().to_numpy()
    values: dict[str, list[float]] = {name: [] for name in _metrics(merged)}
    if len(reports) < 2:
        return values
    for _ in range(repetitions):
        selected = rng.choice(reports, size=len(reports), replace=True)
        boot = pd.concat([merged.loc[merged["blind_report_id"].eq(report)] for report in selected], ignore_index=True)
        for name, (value, _) in _metrics(boot).items():
            values[name].append(value)
    return values


def _interval(values: list[float]) -> tuple[float, float]:
    usable = np.asarray([value for value in values if not np.isnan(value)], dtype=float)
    if len(usable) < 20:
        return np.nan, np.nan
    return float(np.quantile(usable, 0.025)), float(np.quantile(usable, 0.975))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("coder_a", type=Path)
    parser.add_argument("coder_b", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap-repetitions", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261005)
    args = parser.parse_args()
    if args.bootstrap_repetitions < 20:
        raise ValueError("Use at least 20 bootstrap repetitions.")

    a = _validate_coder(pd.read_csv(args.coder_a), "coder_a")
    b = _validate_coder(pd.read_csv(args.coder_b), "coder_b")
    merged = a[KEYS + ["report_eligibility", "ordinal_code", "primary_binary"]].merge(
        b[KEYS + ["report_eligibility", "ordinal_code", "primary_binary"]],
        on=KEYS,
        suffixes=("_a", "_b"),
        validate="one_to_one",
    )
    if len(merged) != len(a) or len(merged) != len(b):
        raise ValueError("Coders received/code different blinded unit sets; resolve before reliability analysis.")

    point = _metrics(merged)
    boot = _bootstrap_by_report(merged, args.bootstrap_repetitions, args.seed)
    rows = []
    for metric, (value, n) in point.items():
        low, high = _interval(boot[metric])
        rows.append({
            "metric": metric,
            "value": "NOT_ESTIMABLE" if np.isnan(value) else value,
            "n_unit_rows": n,
            "n_reports": merged["blind_report_id"].nunique(),
            "bootstrap_repetitions": args.bootstrap_repetitions,
            "ci95_low": "NOT_ESTIMABLE" if np.isnan(low) else low,
            "ci95_high": "NOT_ESTIMABLE" if np.isnan(high) else high,
            "bootstrap_cluster": "blind_report_id",
        })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)

    ordinal = merged.loc[
        merged["report_eligibility_a"].eq("ELIGIBLE")
        & merged["report_eligibility_b"].eq("ELIGIBLE")
        & merged["ordinal_code_a"].isin([0, 1, 2, 3])
        & merged["ordinal_code_b"].isin([0, 1, 2, 3])
    ]
    confusion = pd.crosstab(ordinal["ordinal_code_a"], ordinal["ordinal_code_b"], dropna=False)
    confusion.index.name = "coder_a_ordinal_code"
    confusion.columns.name = "coder_b_ordinal_code"
    confusion.to_csv(args.output.with_name(args.output.stem + "_ordinal_confusion.csv"))
    print(f"Wrote {args.output}; independent labels were read only and retained unchanged.")


if __name__ == "__main__":
    main()
