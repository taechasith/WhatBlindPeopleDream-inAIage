"""Compute independent-coder reliability after real blinded coding; never creates labels."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from sklearn.metrics import cohen_kappa_score

KEYS = ["blind_report_id", "unit_blind_id", "set_blind_label"]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("coder_a"); parser.add_argument("coder_b"); parser.add_argument("--output", required=True)
    args = parser.parse_args()
    a, b = pd.read_csv(args.coder_a), pd.read_csv(args.coder_b)
    for data in [a, b]:
        missing = set(KEYS + ["ordinal_code", "primary_binary"]) - set(data.columns)
        if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    merged = a[KEYS + ["ordinal_code", "primary_binary"]].merge(b[KEYS + ["ordinal_code", "primary_binary"]], on=KEYS, suffixes=("_a", "_b"), validate="one_to_one")
    valid_ord = merged.query("ordinal_code_a != 9 and ordinal_code_b != 9")
    valid_bin = merged.dropna(subset=["primary_binary_a", "primary_binary_b"])
    rows = [{"metric": "ordinal_weighted_kappa", "value": cohen_kappa_score(valid_ord.ordinal_code_a, valid_ord.ordinal_code_b, weights="quadratic") if len(valid_ord) else "NOT_ESTIMABLE", "n": len(valid_ord)},
            {"metric": "binary_cohens_kappa", "value": cohen_kappa_score(valid_bin.primary_binary_a, valid_bin.primary_binary_b) if len(valid_bin) else "NOT_ESTIMABLE", "n": len(valid_bin)},
            {"metric": "binary_percent_agreement", "value": (valid_bin.primary_binary_a == valid_bin.primary_binary_b).mean() if len(valid_bin) else "NOT_ESTIMABLE", "n": len(valid_bin)}]
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output, index=False)
    print(f"Wrote {args.output}; independent labels retained unchanged.")

if __name__ == "__main__": main()
