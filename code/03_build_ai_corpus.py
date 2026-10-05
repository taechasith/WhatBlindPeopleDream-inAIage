"""Create a text-only BLV question corpus from the official VizWiz VQA archive."""
from __future__ import annotations
import csv, json
from pathlib import Path

SRC = Path("data/vizwiz/processed/annotations_source")
OUT = Path("data/ai_sensory/processed/corpus_items.csv")
XIE = Path("data/ai_sensory/raw/xie_dataset_2026-10-05.md")

def main() -> None:
    rows = []
    for split in ("train", "val"):
        data = json.loads((SRC / f"{split}.json").read_text(encoding="utf-8"))
        for index, item in enumerate(data):
            rows.append({
                "item_id": f"VIZWIZ_{split}_{index:05d}", "dataset": "VizWiz VQA",
                "year": "2018", "source_type": "BLV_USER_QUESTION", "human_or_ai": "human",
                "blind_user_origin": "yes", "input_text": item["question"], "output_text": "",
                "task_type": item.get("answer_type", "unknown"), "image_id_if_allowed": item["image"],
                "gold_or_silver": "human_answers_available", "model_if_known": "NOT_APPLICABLE",
                "license": "CC-BY-4.0", "source_url": "https://vizwiz.org/tasks-and-datasets/vqa/",
                "answerable": item.get("answerable", "NOT_REPORTED"), "split": split,
            })
    # This is a released research artifact, not a new social-media scrape. Keep
    # provenance and do not redistribute the resulting text outside authorized use.
    for line in XIE.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells[0].isdigit() or len(cells) < 7:
            continue
        text = cells[2].replace("<br>", " ").replace("<br/>", " ")
        rows.append({
            "item_id": f"XIE2025_{int(cells[0]):03d}", "dataset": "chi25_lmm released dataset",
            "year": "2025", "source_type": "AI_DESCRIPTION", "human_or_ai": "ai",
            "blind_user_origin": "released_PVI_context", "input_text": "", "output_text": text,
            "task_type": "mixed_real_world", "image_id_if_allowed": "NOT_RETAINED",
            "gold_or_silver": "unknown", "model_if_known": "Be My AI per study", "license": "Apache-2.0 repository",
            "source_url": "https://github.com/see4vision/chi25_lmm", "answerable": "NOT_REPORTED", "split": "released_examples",
        })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    assert len(rows) == 24870

if __name__ == "__main__":
    main()
