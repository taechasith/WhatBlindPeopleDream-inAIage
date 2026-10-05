"""Generate deterministic, explicitly synthetic rows for Study 1 pipeline tests.

The generated labels are simulated test fixtures, never coder labels, participant
reports, estimates, or evidence for the planned study.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "synthetic" / "study1_synthetic_unit_data.csv"
RNG = np.random.default_rng(20261005)
CONDITIONS = ["DAI", "SAI", "HUM", "ANC"]
STIMULI = ["S01", "S02", "S03", "S04"]
CONDITION_WILLIAMS = [("DAI", "SAI", "ANC", "HUM"), ("SAI", "HUM", "DAI", "ANC"),
                      ("HUM", "ANC", "SAI", "DAI"), ("ANC", "DAI", "HUM", "SAI")]
STIMULUS_WILLIAMS = [("S01", "S02", "S04", "S03"), ("S02", "S03", "S01", "S04"),
                     ("S03", "S04", "S02", "S01"), ("S04", "S01", "S03", "S02")]


def synthetic_code(probability: float) -> tuple[int, float]:
    """Create a test-only ordinal code consistent with the frozen mapping."""
    draw = RNG.random()
    if draw < probability * 0.28:
        return 3, 1.0
    if draw < probability:
        return 2, 1.0
    if draw < probability + 0.04:
        return 1, np.nan
    if draw < probability + 0.06:
        return 9, np.nan
    return 0, 0.0


def main() -> None:
    rows = []
    for participant_index in range(48):
        participant = f"SYN_P{participant_index + 1:03d}"
        participant_effect = RNG.normal(0, 0.65)
        sequence_cell = participant_index % 16
        condition_order = sequence_cell // 4
        stimulus_order = sequence_cell % 4
        order = condition_order + 1
        condition_schedule = CONDITION_WILLIAMS[condition_order]
        stimulus_schedule = STIMULUS_WILLIAMS[stimulus_order]
        for period, (condition, stimulus) in enumerate(zip(condition_schedule, stimulus_schedule), start=1):
            report_status = "ELIGIBLE" if RNG.random() >= 0.18 else "NO_RECALL"
            report_eligible = int(report_status == "ELIGIBLE")
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
                    if report_status == "ELIGIBLE":
                        ordinal_code, primary_binary = synthetic_code(probability)
                    else:
                        ordinal_code, primary_binary = np.nan, np.nan
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
                        "report_eligible": report_eligible,
                        "report_status": report_status,
                        "ordinal_code": ordinal_code,
                        "primary_binary": primary_binary,
                        "delivered_word_count": 430 if condition != "SAI" else 430 + int(RNG.normal(0, 30)),
                        "synthetic_fixture_note": "Generated solely to test code; not human-coded data.",
                    })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {OUT} with synthetic rows only.")


if __name__ == "__main__":
    main()
