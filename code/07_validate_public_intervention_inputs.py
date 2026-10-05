"""Validate the frozen local inputs for the public prompt intervention.

This pre-generation gate checks only filenames, counts, and file hashes. It
does not load image pixels, generate VLM text, or calculate empirical results.
Source-derived manifests remain ignored by Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv"
IMAGE_DIR = ROOT / "data" / "vizwiz" / "processed" / "images_val" / "val"
OUTPUT = ROOT / "data" / "public_intervention" / "processed" / "input_validation_manifest.json"
EXPECTED_SAMPLE_SIZE = 1000


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, default=SAMPLE)
    parser.add_argument("--image-dir", type=Path, default=IMAGE_DIR)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if not args.sample.is_file():
        raise FileNotFoundError(f"Frozen sample missing: {args.sample}")
    if not args.image_dir.is_dir():
        raise FileNotFoundError(f"Official validation-image directory missing: {args.image_dir}")

    sample = pd.read_csv(args.sample)
    required = {"sample_row_id", "image_filename", "blv_question", "answerable", "question_type"}
    if not required.issubset(sample.columns):
        raise ValueError("Frozen sample has an unexpected schema.")
    if len(sample) != EXPECTED_SAMPLE_SIZE:
        raise ValueError(f"Expected {EXPECTED_SAMPLE_SIZE} frozen rows; found {len(sample)}.")
    if sample["sample_row_id"].duplicated().any() or sample["image_filename"].duplicated().any():
        raise ValueError("Frozen sample must have unique item and image identifiers.")
    if sample["blv_question"].isna().any() or sample["blv_question"].astype(str).str.strip().eq("").any():
        raise ValueError("Frozen sample contains an empty BLV-originating question.")

    expected = sample["image_filename"].astype(str).tolist()
    missing = [name for name in expected if not (args.image_dir / name).is_file()]
    if missing:
        preview = ", ".join(missing[:10])
        raise FileNotFoundError(f"{len(missing)} frozen sample images are absent; first: {preview}")

    manifest = {
        "data_status": "PREGENERATION_INPUT_VALIDATED_NOT_MODEL_OUTPUT",
        "sample_path": str(args.sample.resolve().relative_to(ROOT)),
        "sample_sha256": sha256(args.sample),
        "sample_rows": int(len(sample)),
        "unique_images": int(sample["image_filename"].nunique()),
        "image_directory": str(args.image_dir.resolve().relative_to(ROOT)),
        "image_files_in_directory": len(list(args.image_dir.glob("*.jpg"))),
        "missing_sample_images": 0,
        "answerability_counts": {
            str(key): int(value)
            for key, value in sample["answerable"].value_counts(dropna=False).sort_index().items()
        },
        "question_type_counts": {
            str(key): int(value)
            for key, value in sample["question_type"].value_counts(dropna=False).sort_index().items()
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
