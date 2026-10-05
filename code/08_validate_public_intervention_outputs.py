"""Fail-closed validator for real VLM outputs from the frozen prompt intervention.

This script deliberately does not invoke a model. It accepts only a completed
local output table created by an independently documented frozen model run and
checks that every frozen sample item has exactly one output per condition.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv"
CONDITIONS = {"generic", "intent_steered", "accessibility_steered"}
REQUIRED = {
    "sample_row_id", "model_id", "condition", "output_text", "model_manifest_sha256",
    "prompt_template_id", "generation_timestamp_utc",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--model-manifest", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not args.outputs.is_file() or not args.model_manifest.is_file() or not SAMPLE.is_file():
        raise FileNotFoundError("Outputs, a model manifest, and the frozen sample are all required.")
    manifest = json.loads(args.model_manifest.read_text(encoding="utf-8"))
    if manifest.get("status") == "EXAMPLE_ONLY_NOT_A_MODEL_FREEZE":
        raise ValueError("Example model manifest cannot authorize output validation.")
    models = manifest.get("models")
    if not isinstance(models, list) or not models:
        raise ValueError("Frozen model manifest must contain at least one model record.")
    required_model_fields = {
        "model_id", "provider_or_checkpoint", "immutable_revision", "license", "runtime",
        "hardware", "decoding", "image_preprocessing", "execution_command", "authorized_use_confirmed",
    }
    if any(not required_model_fields.issubset(record) for record in models if isinstance(record, dict)):
        raise ValueError("Frozen model manifest has an incomplete model record.")
    if any(not isinstance(record, dict) for record in models):
        raise ValueError("Frozen model manifest must contain object records.")
    if any(record["authorized_use_confirmed"] is not True for record in models):
        raise ValueError("Every frozen model must record authorized_use_confirmed=true.")
    frozen_model_ids = {str(record["model_id"]) for record in models}
    if len(frozen_model_ids) != len(models) or "REPLACE_WITH_STABLE_MODEL_ID" in frozen_model_ids:
        raise ValueError("Frozen model identifiers must be unique and non-placeholder values.")
    outputs = pd.read_csv(args.outputs)
    if not REQUIRED.issubset(outputs.columns):
        raise ValueError(f"Output table is missing required columns: {sorted(REQUIRED - set(outputs.columns))}")
    if outputs["output_text"].isna().any() or outputs["output_text"].astype(str).str.strip().eq("").any():
        raise ValueError("Output table contains blank model output.")
    if set(outputs["condition"].dropna()) - CONDITIONS:
        raise ValueError("Output table contains an unknown condition.")
    if set(outputs["model_id"].astype(str)) != frozen_model_ids:
        raise ValueError("Output model identifiers do not exactly match the frozen model manifest.")
    sample_ids = set(pd.read_csv(SAMPLE, usecols=["sample_row_id"])["sample_row_id"])
    if set(outputs["sample_row_id"]) != sample_ids:
        raise ValueError("Output items do not exactly match the frozen sample.")
    manifest_hash = sha256(args.model_manifest)
    if set(outputs["model_manifest_sha256"].astype(str)) != {manifest_hash}:
        raise ValueError("Every output must record the exact provided frozen model-manifest hash.")
    counts = outputs.groupby(["model_id", "sample_row_id"], observed=True)["condition"].agg(list)
    invalid = counts.loc[counts.map(lambda values: set(values) != CONDITIONS or len(values) != len(CONDITIONS))]
    if not invalid.empty:
        raise ValueError(f"{len(invalid)} model/item groups do not have exactly the three required conditions.")
    report = {
        "status": "REAL_OUTPUT_SCHEMA_VALIDATED_NOT_ANALYZED",
        "outputs_sha256": sha256(args.outputs),
        "model_manifest_sha256": manifest_hash,
        "models": sorted(outputs["model_id"].astype(str).unique().tolist()),
        "n_models": int(outputs["model_id"].nunique()),
        "n_outputs": int(len(outputs)),
        "n_frozen_items": int(len(sample_ids)),
        "conditions": sorted(CONDITIONS),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
