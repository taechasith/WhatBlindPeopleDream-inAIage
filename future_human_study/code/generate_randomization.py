"""Generate and validate a balanced Williams-design Study 1 allocation schedule."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

CONDITIONS = ("DAI", "SAI", "HUM", "ANC")
STIMULI = ("S01", "S02", "S03", "S04")

# Each ordered carryover pair occurs once across the four rows.
WILLIAMS = ((0, 1, 3, 2), (1, 2, 0, 3), (2, 3, 1, 0), (3, 0, 2, 1))


def build(n_slots: int) -> list[dict[str, object]]:
    if n_slots % 16:
        raise ValueError("n_slots must be a multiple of 16 for exact condition/stimulus balance.")
    rows = []
    slot = 0
    for repetition in range(n_slots // 16):
        for condition_row in range(4):
            for stimulus_row in range(4):
                slot += 1
                for period in range(4):
                    rows.append({
                        "allocation_slot": f"ALLOC_{slot:03d}",
                        "period": period + 1,
                        "condition": CONDITIONS[WILLIAMS[condition_row][period]],
                        "stimulus_id": STIMULI[WILLIAMS[stimulus_row][period]],
                        "condition_sequence_id": f"W{condition_row + 1}",
                        "stimulus_sequence_id": f"W{stimulus_row + 1}",
                        "repetition_block": repetition + 1,
                    })
    return rows


def validate(rows: list[dict[str, object]]) -> dict[str, int]:
    by_slot: dict[str, list[dict[str, object]]] = {}
    for row in rows: by_slot.setdefault(str(row["allocation_slot"]), []).append(row)
    assert all(len(group) == 4 for group in by_slot.values())
    assert all(len({r["condition"] for r in group}) == 4 for group in by_slot.values())
    assert all(len({r["stimulus_id"] for r in group}) == 4 for group in by_slot.values())
    transitions = Counter()
    assignments = Counter()
    for group in by_slot.values():
        group.sort(key=lambda r: int(r["period"]))
        for a, b in zip(group, group[1:]): transitions[(a["condition"], b["condition"])] += 1
        for row in group: assignments[(row["condition"], row["stimulus_id"])] += 1
    assert len(set(transitions.values())) == 1, transitions
    assert len(set(assignments.values())) == 1, assignments
    return {"slots": len(by_slot), "visits": len(rows), "ordered_condition_transitions_each": next(iter(transitions.values())), "condition_stimulus_cells_each": next(iter(assignments.values()))}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slots", type=int, default=208)
    parser.add_argument("--output", default="randomization/MASTER_RANDOMIZATION_LOCKED.csv")
    parser.add_argument("--validation", default="randomization/validation_summary.csv")
    args = parser.parse_args()
    rows = build(args.slots); summary = validate(rows)
    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    validation = Path(args.validation); validation.parent.mkdir(parents=True, exist_ok=True)
    with validation.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary)); writer.writeheader(); writer.writerow(summary)
    print(f"Wrote {out} and validated {summary}")


if __name__ == "__main__": main()
