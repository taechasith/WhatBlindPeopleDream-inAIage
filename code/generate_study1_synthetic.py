"""Generate clearly labeled synthetic Study 1 data for pipeline testing only."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "synthetic" / "study1_synthetic_unit_data.csv"
RNG = np.random.default_rng(20261005)
CONDITIONS = ["DAI", "SAI", "HUM", "ANC"]
STIMULI = ["S01", "S02", "S03", "S04"]


def main() -> None:
    rows = []
    for participant_index in range(48):
        participant = f"SYN_P{participant_index + 1:03d}"
        participant_effect = RNG.normal(0, 0.65)
        order = participant_index % 4 + 1
        for period, condition in enumerate(CONDITIONS, start=1):
            stimulus = STIMULI[(participant_index + period - 1) % 4]
            # Synthetic missing report process; never represents an empirical rate.
            report_available = RNG.random() >= 0.18
            for unit_no in range(1, 9):
                for target_status in [0, 1]:
                    logit = -3.0 + participant_effect + 0.05 * period
                    if target_status and condition in {"DAI", "SAI"}:
                        logit += 0.85
                    if target_status and condition == "HUM":
                        logit += 0.55
                    if target_status and condition == "ANC":
                        logit += 0.05
                    if condition == "SAI":
                        logit += 0.10
                    probability = 1 / (1 + np.exp(-logit))
                    observed = int(RNG.random() < probability) if report_available else np.nan
                    rows.append({
                        "data_status": "SYNTHETIC_ONLY_NOT_EMPIRICAL",
                        "participant_id": participant,
                        "session_id": f"{participant}_N{period}",
                        "condition": condition,
                        "period": period,
                        "order": order,
                        "stimulus_id": stimulus,
                        "unit_id": f"{stimulus}_U{unit_no:02d}",
                        "target_status": target_status,
                        "report_eligible": int(report_available),
                        "incorporated_binary": observed,
                        "delivered_word_count": 430 if condition != "SAI" else 430 + int(RNG.normal(0, 30)),
                    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
