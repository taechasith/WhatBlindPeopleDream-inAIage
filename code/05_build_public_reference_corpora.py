"""Build local-only reference tables for the public-data protocol.

This script reads authorized released files without altering them. Its outputs
contain source-derived text and ratings, so they remain under ignored processed
directories and are never included in an anonymous review bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CAPTION_JSON = ROOT / "data" / "vizwiz_captions" / "processed" / "annotations_source" / "annotations" / "val.json"
KAPUR_DIR = ROOT / "data" / "kapur" / "raw" / "reference-based-bias" / "datasets"
OUT_DIR = ROOT / "data" / "public_reference" / "processed"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_captions(path: Path) -> pd.DataFrame:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if set(payload) != {"info", "images", "annotations"}:
        raise ValueError("Unexpected VizWiz-Captions JSON top-level schema.")
    images = pd.DataFrame(payload["images"])
    annotations = pd.DataFrame(payload["annotations"])
    required_images = {"id", "file_name", "text_detected"}
    required_annotations = {"id", "image_id", "caption", "is_rejected", "is_precanned"}
    if not required_images.issubset(images.columns) or not required_annotations.issubset(annotations.columns):
        raise ValueError("VizWiz-Captions required fields are missing.")
    image_metadata = images[["id", "file_name", "text_detected"]].rename(
        columns={"id": "image_metadata_id", "text_detected": "image_text_detected"}
    )
    rows = annotations.merge(image_metadata, left_on="image_id", right_on="image_metadata_id", how="inner")
    if len(rows) != len(annotations):
        raise ValueError("Caption annotations did not join one-to-one to image metadata.")
    rows = rows.loc[~rows["is_rejected"].astype(bool)].copy()
    rows = rows.rename(columns={"id": "caption_id", "file_name": "image_filename", "caption": "caption_text"})
    rows["source"] = "VIZWIZ_CAPTIONS"
    rows["split"] = "val"
    rows["data_status"] = "RELEASED_SOURCE_TEXT_LOCAL_ONLY"
    return rows[[
        "data_status", "source", "split", "image_id", "image_filename", "caption_id",
        "caption_text", "is_precanned", "text_detected", "image_text_detected",
    ]]


def build_kapur(path: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for filename, sheet in (("context_sensitive.xlsx", "Sheet1"), ("different_context.xlsx", "Sheet 1")):
        source = path / filename
        table = pd.read_excel(source, sheet_name=sheet)
        needed = {"context", "img_id", "hypothesis", "hypothesis_avg_overall_blv_rating", "hypothesis_avg_overall_sighted_rating"}
        if not needed.issubset(table.columns):
            raise ValueError(f"Kapur table missing required fields: {filename}")
        table["comparison_set"] = filename.removesuffix(".xlsx")
        frames.append(table)
    result = pd.concat(frames, ignore_index=True)
    result["source"] = "KAPUR_KREISS_2024"
    result["data_status"] = "RELEASED_SOURCE_TEXT_AND_RATINGS_LOCAL_ONLY"
    columns = [
        "data_status", "source", "comparison_set", "context", "img_id", "hypothesis",
        "hypothesis_avg_overall_blv_rating", "hypothesis_avg_overall_sighted_rating",
        "reference_count", "hypothesis_length", "avg_reference_length", "max_reference_length",
        "min_reference_length", "Bleu_1", "Bleu_2", "Bleu_3", "Bleu_4", "METEOR",
        "ROUGE_L", "Spice",
    ]
    return result[[column for column in columns if column in result.columns]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()
    if not CAPTION_JSON.is_file():
        raise FileNotFoundError(f"Missing authorized VizWiz-Captions file: {CAPTION_JSON}")
    for filename in ("context_sensitive.xlsx", "different_context.xlsx"):
        if not (KAPUR_DIR / filename).is_file():
            raise FileNotFoundError(f"Missing authorized Kapur file: {KAPUR_DIR / filename}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    captions = build_captions(CAPTION_JSON)
    kapur = build_kapur(KAPUR_DIR)
    captions.to_csv(args.output_dir / "vizwiz_captions_val.csv", index=False)
    kapur.to_csv(args.output_dir / "kapur_preference_ratings.csv", index=False)
    manifest = {
        "data_status": "RELEASED_SOURCE_DERIVED_LOCAL_ONLY",
        "inputs": {
            str(CAPTION_JSON.relative_to(ROOT)): sha256(CAPTION_JSON),
            str((KAPUR_DIR / "context_sensitive.xlsx").relative_to(ROOT)): sha256(KAPUR_DIR / "context_sensitive.xlsx"),
            str((KAPUR_DIR / "different_context.xlsx").relative_to(ROOT)): sha256(KAPUR_DIR / "different_context.xlsx"),
        },
        "outputs": {
            "vizwiz_captions_val_rows": len(captions),
            "vizwiz_captions_val_unique_images": int(captions["image_id"].nunique()),
            "kapur_preference_rows": len(kapur),
            "kapur_comparison_sets": sorted(kapur["comparison_set"].unique().tolist()),
        },
    }
    (args.output_dir / "build_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["outputs"], sort_keys=True))


if __name__ == "__main__":
    main()
