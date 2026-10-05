"""Generate invented fixtures for an analysis-pipeline dry run only."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


CONDITIONS = ("generic", "intent_steered", "accessibility_steered")
DIMENSIONS = ("task_answer", "task_relevance", "spatial_relation", "grounded_uncertainty", "unsupported_information")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--items", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20261006)
    args = parser.parse_args()
    generator = np.random.default_rng(args.seed)
    probabilities = {
        "generic": (0.42, 0.38, 0.16, 0.10, 0.08),
        "intent_steered": (0.62, 0.61, 0.24, 0.21, 0.07),
        "accessibility_steered": (0.64, 0.64, 0.45, 0.38, 0.06),
    }
    outputs, labels = [], []
    for item in range(args.items):
        for model in ("SYNTHETIC_MODEL_A", "SYNTHETIC_MODEL_B"):
            for condition in CONDITIONS:
                key = {"sample_row_id": f"SYNTHETIC_{item:03d}", "model_id": model, "condition": condition}
                outputs.append({**key, "output_text": "SYNTHETIC_ONLY_NOT_EMPIRICAL"})
                labels.append({**key, **{dimension: int(generator.random() < probability)
                                         for dimension, probability in zip(DIMENSIONS, probabilities[condition])}})
    args.outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(outputs).to_csv(args.outdir / "synthetic_outputs.csv", index=False)
    pd.DataFrame(labels).to_csv(args.outdir / "synthetic_labels.csv", index=False)
    (args.outdir / "README.txt").write_text("SYNTHETIC_ONLY_NOT_EMPIRICAL\n", encoding="utf-8")
    print(f"SYNTHETIC_ONLY_NOT_EMPIRICAL rows={len(outputs)}")


if __name__ == "__main__":
    main()
