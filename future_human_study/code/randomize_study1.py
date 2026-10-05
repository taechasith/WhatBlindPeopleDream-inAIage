"""Create a concealed 4x4 Latin-square allocation after an approved sample size exists."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

CONDITIONS = ["DAI", "SAI", "HUM", "ANC"]
STIMULI = ["S01", "S02", "S03", "S04"]

def latin_square(values):
    return [values[i:] + values[:i] for i in range(len(values))]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--participants", type=int, required=True)
    parser.add_argument("--output", default="private/study1_allocation.csv")
    args = parser.parse_args()
    if args.participants < 4:
        raise ValueError("Use a multiple of four when possible; at least four allocations are required.")
    condition_orders, stimulus_orders = latin_square(CONDITIONS), latin_square(STIMULI)
    rows = []
    for participant in range(args.participants):
        for period in range(4):
            rows.append({"participant_id": f"P{participant+1:03d}", "period": period+1,
                         "condition": condition_orders[participant % 4][period],
                         "stimulus_id": stimulus_orders[(participant // 4) % 4][period]})
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Wrote concealed allocation schedule: {out}")

if __name__ == "__main__": main()
