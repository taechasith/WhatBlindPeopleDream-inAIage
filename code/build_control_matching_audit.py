"""Create a deterministic, non-human descriptive matching audit for Study 1 prototypes."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "stimuli" / "CANDIDATE_EXPOSURE_SCRIPTS.csv"
OUTPUT = ROOT / "CONTROL_MATCHING_AUDIT.csv"

SPATIAL = {"above", "below", "beneath", "behind", "before", "beside", "left", "right", "front", "back", "toward", "under"}
COLOR = {"yellow", "red", "blue", "green", "black", "white", "brown", "grey", "gray"}
ORIENTATION = {"above", "below", "beneath", "behind", "before", "beside", "left", "right", "front", "back", "toward", "under"}

def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text.lower())

def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        tokens = words(row["text"])
        sentences = [s for s in re.split(r"[.!?]+", row["text"]) if s.strip()]
        wpm = int(row["planned_speech_rate_wpm"])
        out.append({
            "stimulus_id": row["stimulus_id"], "condition": row["condition"],
            "script_id": row["script_id"], "script_status": row["script_status"],
            "word_count": len(tokens), "sentence_count": len(sentences),
            "estimated_speech_seconds": round(len(tokens) / wpm * 60, 1),
            "mean_word_length": round(sum(map(len, tokens)) / len(tokens), 2),
            "type_token_ratio": round(len(set(tokens)) / len(tokens), 3),
            "spatial_term_count": sum(t in SPATIAL for t in tokens),
            "color_term_count": sum(t in COLOR for t in tokens),
            "number_term_count": sum(t.isdigit() for t in tokens),
            "orientation_term_count": sum(t in ORIENTATION for t in tokens),
            "proper_nouns": "NONE_EXPECTED_PROTOTYPE", "social_context": "NONE_OR_GENERIC",
            "emotional_salience": "PENDING_HUMAN_VALIDATION",
            "unusualness": "PENDING_HUMAN_VALIDATION",
            "memorability": "PENDING_HUMAN_VALIDATION",
            "object_frequency": "PENDING_CORPUS_CHECK",
            "voice": row["voice_id"], "speech_rate_wpm": wpm,
            "total_exposure_minutes": row["session_envelope_minutes"],
            "questions_allowed": row["participant_questions_allowed"],
            "source_framing": row["source_framing"], "expectation_framing": row["expectation_framing"],
            "agency": "HIGH_BY_DESIGN" if row["condition"] == "SAI" else "LOW_STANDARDIZED",
            "audit_status": "PROTOTYPE_NONHUMAN_ONLY",
        })
    OUTPUT.parent.mkdir(exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out[0]))
        writer.writeheader(); writer.writerows(out)
    print(f"Wrote {OUTPUT} ({len(out)} prototype scripts)")

if __name__ == "__main__":
    main()
