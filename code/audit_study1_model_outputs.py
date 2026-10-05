"""Fail-closed lexical audit of non-human candidate DAI scripts.

This program detects obvious omissions and prohibited language. It cannot verify
visual grounding, so every output remains pending independent review regardless
of its lexical score.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "private" / "study1_model_candidates" / "dai_model_candidate_outputs.csv"
DEFAULT_OUTPUT = ROOT / "private" / "study1_model_candidates" / "dai_candidate_lexical_audit.csv"
MARKER_PATTERNS: dict[str, dict[str, tuple[str, ...]]] = {
    "S01": {
        "violin": (r"\bviolin\b",),
        "above_bench": (r"\b(above|over)\b.{0,40}\bbench\b|\bbench\b.{0,40}\b(under|below)\b.{0,40}\bviolin\b",),
        "dog_beneath_table": (r"\bdog\b.{0,45}\b(under|beneath)\b.{0,45}\btable\b|\btable\b.{0,45}\b(above|over)\b.{0,45}\bdog\b",),
        "umbrella_beside_fountain": (r"\bumbrella\b.{0,55}\b(near|beside|next to)\b.{0,55}\bfountain\b|\bfountain\b.{0,55}\b(near|beside|next to)\b.{0,55}\bumbrella\b",),
        "cyclist_approaching_gate": (r"\b(cyclist|bicycle|bike)\b", r"\bgate\b"),
        "lantern_behind_fountain": (r"\blantern\b", r"\bfountain\b"),
        "circular_fountain": (r"\bfountain\b",),
        "striped_bench": (r"\bbench\b",),
    },
    "S02": {
        "spiral_staircase": (r"\b(spiral|curving)\b.{0,30}\b(staircase|stairs)\b|\b(staircase|stairs)\b",),
        "toolbox_beneath_window": (r"\btoolbox\b", r"\bwindow\b"),
        "kettle_beside_plant": (r"\bkettle\b", r"\bplant\b"),
        "map_above_toolbox": (r"\bmap\b", r"\btoolbox\b"),
        "bell_at_top": (r"\bbell\b",),
        "stool_in_front_staircase": (r"\bstool\b", r"\b(staircase|stairs)\b"),
        "open_window": (r"\b(open )?window\b",),
        "workshop": (r"\b(workshop|room)\b",),
    },
    "S03": {
        "suitcase_beside_cane": (r"\b(suitcase|luggage)\b", r"\b(cane|white cane)\b"),
        "clock_above_exit_sign": (r"\bclock\b", r"\b(exit|sign)\b"),
        "backpack_behind_vending_machine": (r"\bbackpack\b", r"\b(vending machine|machine)\b"),
        "puddle_before_platform_edge": (r"\bpuddle\b", r"\b(platform|edge)\b"),
        "exit_sign_right": (r"\b(exit|sign)\b",),
        "platform_edge": (r"\bplatform\b",),
        "vending_machine": (r"\b(vending machine|machine)\b",),
        "traveler_waiting": (r"\b(person|traveler|traveller|figure)\b",),
    },
    "S04": {
        "cat_beneath_arch": (r"\bcat\b", r"\barch\b"),
        "watering_can_beside_flowerpot": (r"\bwatering can\b", r"\b(flowerpot|flower pot|pot)\b"),
        "wind_chime_above_path": (r"\bwind chime\b", r"\bpath\b"),
        "wheelbarrow_behind_sign": (r"\bwheelbarrow\b", r"\bsign\b"),
        "curving_path_toward_gate": (r"\b(curv|winding)\w*\b.{0,35}\bpath\b|\bpath\b", r"\bgate\b"),
        "garden_arch": (r"\b(garden|arch)\b",),
        "flowerpot": (r"\b(flowerpot|flower pot|pot)\b",),
        "gate": (r"\bgate\b",),
    },
}
PROHIBITED = {
    "identity_or_demographic": r"\b(man|woman|boy|girl|young|old|elderly|male|female|race|ethnicity)\b",
    "emotion_or_intent": r"\b(happy|sad|angry|afraid|worried|excited|lonely|thinking|wants?|trying to)\b",
    "relationship_or_ownership": r"\b(friend|family|mother|father|owner|belongs to|couple)\b",
    "advice_or_hazard_claim": r"\b(be careful|watch out|danger|hazard|should|must|avoid)\b",
    "dream_suggestion": r"\b(dream|sleep|remember this)\b",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8", newline="") as handle:
        outputs = list(csv.DictReader(handle))
    rows = []
    for output in outputs:
        stimulus = output["stimulus_id"]
        text = output["output_text"].lower()
        for marker, pattern_parts in MARKER_PATTERNS[stimulus].items():
            present = all(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in pattern_parts)
            rows.append({
                "stimulus_id": stimulus,
                "audit_type": "semantic_marker_lexical_presence",
                "item": marker,
                "status": "LEXICALLY_PRESENT" if present else "LEXICALLY_ABSENT",
                "evidence": "pattern_matched" if present else "no_pattern_match",
                "final_disposition": "REQUIRES_INDEPENDENT_GROUNDING_REVIEW",
            })
        words = int(output["output_word_count"])
        rows.append({
            "stimulus_id": stimulus,
            "audit_type": "word_count",
            "item": str(words),
            "status": "WITHIN_60_TO_85" if 60 <= words <= 85 else "OUTSIDE_60_TO_85",
            "evidence": "generated_candidate",
            "final_disposition": "REQUIRES_INDEPENDENT_GROUNDING_REVIEW",
        })
        for category, pattern in PROHIBITED.items():
            found = bool(re.search(pattern, text, re.IGNORECASE))
            rows.append({
                "stimulus_id": stimulus,
                "audit_type": "prohibited_language_screen",
                "item": category,
                "status": "FLAGGED" if found else "NO_LEXICAL_FLAG",
                "evidence": "pattern_matched" if found else "no_pattern_match",
                "final_disposition": "REQUIRE_REWRITE_IF_FLAGGED" if found else "REQUIRES_INDEPENDENT_GROUNDING_REVIEW",
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote lexical audit for {len(outputs)} non-human candidate outputs to {args.output}")


if __name__ == "__main__":
    main()
