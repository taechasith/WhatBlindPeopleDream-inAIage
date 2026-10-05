"""Analyze independently coded outputs from the public prompt intervention.

This program neither invokes a model nor creates labels. It reports paired,
image-cluster bootstrap contrasts when supplied real, independently coded data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


DIMENSIONS = ("task_answer", "task_relevance", "spatial_relation", "grounded_uncertainty", "unsupported_information")
KEYS = ("sample_row_id", "model_id", "condition")
CONTRASTS = (("intent_minus_generic", "intent_steered", "generic"),
             ("accessibility_minus_intent", "accessibility_steered", "intent_steered"))


def binary(values: pd.Series) -> pd.Series:
    return values.astype(str).isin({"0", "1"})


def cluster_bootstrap(paired: pd.DataFrame, repetitions: int, seed: int) -> tuple[float, float, float]:
    observed = float(paired["difference"].mean())
    generator = np.random.default_rng(seed)
    clusters = paired["sample_row_id"].unique()
    estimates: list[float] = []
    for _ in range(repetitions):
        sampled = generator.choice(clusters, size=len(clusters), replace=True)
        parts = [paired.loc[paired["sample_row_id"] == item, "difference"] for item in sampled]
        estimates.append(float(pd.concat(parts).mean()))
    low, high = np.quantile(estimates, [0.025, 0.975])
    return observed, float(low), float(high)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20261006)
    args = parser.parse_args()
    if args.bootstrap < 200:
        raise ValueError("Use at least 200 bootstrap repetitions.")
    outputs, labels = pd.read_csv(args.outputs), pd.read_csv(args.labels)
    expected = set(KEYS) | set(DIMENSIONS)
    if not set(KEYS).issubset(outputs.columns) or not expected.issubset(labels.columns):
        raise ValueError("Unexpected output or independent-coding schema.")
    if outputs.duplicated(list(KEYS)).any() or labels.duplicated(list(KEYS)).any():
        raise ValueError("Records must be unique by model/item/condition.")
    merged = outputs[list(KEYS)].merge(labels[list(expected)], on=list(KEYS), how="outer", indicator=True)
    if not (merged["_merge"] == "both").all():
        raise ValueError("Coding records must exactly match model outputs.")
    prevalence, comparisons = [], []
    for model_id, frame in merged.groupby("model_id", observed=True):
        for dimension in DIMENSIONS:
            for condition, group in frame.groupby("condition", observed=True):
                usable = group.loc[binary(group[dimension])]
                prevalence.append({"model_id": model_id, "condition": condition, "dimension": dimension,
                                   "n_outputs": len(group), "n_estimable": len(usable),
                                   "proportion": float(usable[dimension].astype(int).mean()) if len(usable) else np.nan,
                                   "analysis_status": "INPUT_PROVENANCE_MUST_BE_VERIFIED"})
            pivot = frame.loc[binary(frame[dimension])].pivot(index="sample_row_id", columns="condition", values=dimension)
            for name, numerator, denominator in CONTRASTS:
                if numerator not in pivot or denominator not in pivot:
                    comparisons.append({"model_id": model_id, "dimension": dimension, "contrast": name, "n_paired_items": 0,
                                        "difference": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                                        "analysis_status": "NOT_ESTIMABLE_MISSING_PAIRED_CODING"})
                    continue
                paired = pivot[[numerator, denominator]].dropna().reset_index()
                paired["difference"] = paired[numerator].astype(int) - paired[denominator].astype(int)
                if paired.empty:
                    comparisons.append({"model_id": model_id, "dimension": dimension, "contrast": name, "n_paired_items": 0,
                                        "difference": np.nan, "ci_low": np.nan, "ci_high": np.nan,
                                        "analysis_status": "NOT_ESTIMABLE_NO_PAIRED_CODING"})
                    continue
                effect, low, high = cluster_bootstrap(paired, args.bootstrap, args.seed)
                comparisons.append({"model_id": model_id, "dimension": dimension, "contrast": name,
                                    "n_paired_items": len(paired), "difference": effect, "ci_low": low, "ci_high": high,
                                    "analysis_status": "INPUT_PROVENANCE_MUST_BE_VERIFIED"})
    args.outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(prevalence).to_csv(args.outdir / "condition_prevalence.csv", index=False)
    pd.DataFrame(comparisons).to_csv(args.outdir / "paired_cluster_bootstrap.csv", index=False)
    manifest = {"status": "ANALYSIS_COMPLETE_ON_SUPPLIED_INPUTS_NOT_AUTOMATICALLY_EMPIRICAL",
                "n_outputs": len(outputs), "n_labels": len(labels), "models": sorted(merged.model_id.astype(str).unique().tolist()),
                "dimensions": list(DIMENSIONS), "bootstrap_repetitions": args.bootstrap, "seed": args.seed}
    (args.outdir / "analysis_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
