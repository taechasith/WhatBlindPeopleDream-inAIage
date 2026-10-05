"""Create the frozen VizWiz validation sample before any model generation.

The selector reads only released VQA annotations. It does not inspect images or
generate model outputs. The resulting source-derived table stays local-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "vizwiz" / "processed" / "annotations_source" / "val.json"
OUTPUT_DIR = ROOT / "data" / "public_intervention" / "processed"
SEED = 20261006
N_SAMPLE = 1000


TAXONOMY: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("text_reading", re.compile(r"\b(read|say|label|written|word|letter|sign|menu|ingredients?|date|expiration)\b", re.I)),
    ("price_product", re.compile(r"\b(price|cost|brand|product|food|drink|medicine|pill)\b", re.I)),
    ("color_appearance", re.compile(r"\b(colou?r|look|appearance|style|design)\b", re.I)),
    ("count_quantity", re.compile(r"\b(how many|number of|count|amount|quantity)\b", re.I)),
    ("safety_navigation", re.compile(r"\b(safe|danger|hazard|where|direction|distance|walk|door|stairs?|step|road|cross)\b", re.I)),
    ("object_identification", re.compile(r"\b(what (is|are|does)|identify|thing|object|this)\b", re.I)),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def question_type(question: str) -> str:
    for label, pattern in TAXONOMY:
        if pattern.search(question):
            return label
    return "other"


def answer_summary(answers: list[dict[str, str]]) -> str:
    counts = Counter(answer["answer"].strip() for answer in answers if answer.get("answer", "").strip())
    if not counts:
        return ""
    return counts.most_common(1)[0][0]


def proportional_counts(frame: pd.DataFrame, sample_size: int) -> dict[tuple[int, str], int]:
    counts = frame.groupby(["answerable", "question_type"], observed=True).size()
    desired = counts / counts.sum() * sample_size
    allocated = desired.astype(int)
    remainder = sample_size - int(allocated.sum())
    for key in sorted((desired - allocated).sort_values(ascending=False).index.tolist())[:remainder]:
        allocated.loc[key] += 1
    if (allocated > counts).any():
        raise ValueError("Requested stratum sample exceeds available rows.")
    return {key: int(value) for key, value in allocated.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--sample-size", type=int, default=N_SAMPLE)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(f"Missing authorized VQA annotations: {args.input}")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Expected VizWiz VQA validation annotations as a JSON list.")
    table = pd.DataFrame(raw)
    required = {"image", "question", "answers", "answerable", "answer_type"}
    if not required.issubset(table.columns):
        raise ValueError("VizWiz VQA required fields are missing.")
    table = table.loc[table["question"].astype(str).str.strip().ne("")].copy()
    table["question_type"] = table["question"].map(question_type)
    table["human_answer_mode"] = table["answers"].map(answer_summary)
    table = table.rename(columns={"image": "image_filename", "question": "blv_question"})
    table["source"] = "VIZWIZ_VQA"
    table["split"] = "val"
    table["data_status"] = "RELEASED_SOURCE_TEXT_LOCAL_ONLY_PREGENERATION"
    if args.sample_size > len(table):
        raise ValueError("sample-size exceeds eligible validation rows")
    allocation = proportional_counts(table, args.sample_size)
    generator = np.random.default_rng(args.seed)
    pieces: list[pd.DataFrame] = []
    for (answerable, category), n_rows in allocation.items():
        subset = table.loc[(table["answerable"] == answerable) & (table["question_type"] == category)]
        chosen_indices = generator.choice(subset.index.to_numpy(), size=n_rows, replace=False)
        pieces.append(subset.loc[chosen_indices])
    sample = pd.concat(pieces, ignore_index=True).sort_values("image_filename", kind="stable").reset_index(drop=True)
    if len(sample) != args.sample_size or sample["image_filename"].duplicated().any():
        raise ValueError("Sample is not the expected number of unique image-question items.")
    sample.insert(0, "sample_row_id", [f"VIZWIZ_VAL_{index:04d}" for index in range(1, len(sample) + 1)])
    columns = [
        "sample_row_id", "data_status", "source", "split", "image_filename", "blv_question",
        "answerable", "answer_type", "human_answer_mode", "question_type", "answers",
    ]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "vizwiz_val_sample_1000.csv"
    sample[columns].to_csv(output, index=False)
    summary = {
        "data_status": "PREGENERATION_SAMPLE_NOT_MODEL_OUTPUT",
        "input_path": str(args.input.relative_to(ROOT)),
        "input_sha256": sha256(args.input),
        "sample_size": len(sample),
        "seed": args.seed,
        "question_taxonomy": [label for label, _ in TAXONOMY] + ["other"],
        "strata": [
            {"answerable": int(answerable), "question_type": question_type, "n": int(n_rows)}
            for (answerable, question_type), n_rows in allocation.items()
        ],
    }
    (args.output_dir / "vizwiz_val_sample_1000_manifest.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"sample_size": len(sample), "seed": args.seed, "strata": len(allocation)}, sort_keys=True))


if __name__ == "__main__":
    main()
