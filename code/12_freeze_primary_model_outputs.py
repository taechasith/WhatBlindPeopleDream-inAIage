"""Validate and freeze the completed 3,000-row primary VLM output corpus.

This is a provenance gate, not analysis. It refuses incomplete runs, duplicate
successful keys, unaccounted failure records, a changed model manifest, or a
different frozen VizWiz sample.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv"
OUTPUTS = ROOT / "data" / "model_outputs" / "validated" / "primary_model_outputs.csv"
ATTEMPTS = ROOT / "data" / "model_outputs" / "raw" / "primary_attempts.jsonl"
MODEL_MANIFEST = ROOT / "config" / "public_vlm_models.json"
MANIFEST = ROOT / "data" / "model_outputs" / "OUTPUT_MANIFEST.csv"
CHECKSUMS = ROOT / "data" / "model_outputs" / "CHECKSUMS.csv"
FREEZE = ROOT / "MODEL_OUTPUT_FREEZE.md"
CONDITIONS = {"generic", "intent_steered", "accessibility_steered"}
MODEL_ID = "Qwen2.5-VL-3B-Instruct_FP16_66285546"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> None:
    if not all(path.is_file() for path in (SAMPLE, OUTPUTS, ATTEMPTS, MODEL_MANIFEST)):
        raise FileNotFoundError("Frozen sample, outputs, attempt log, and model manifest are required.")
    sample = pd.read_csv(SAMPLE, usecols=["sample_row_id"])
    outputs = pd.read_csv(OUTPUTS)
    keys = ["sample_row_id", "model_id", "condition"]
    required = set(keys) | {"output_text", "model_manifest_sha256", "validator_status"}
    if not required.issubset(outputs.columns) or outputs.duplicated(keys).any():
        raise ValueError("Output schema or unique key check failed.")
    expected = {(item, MODEL_ID, condition) for item in sample["sample_row_id"] for condition in CONDITIONS}
    found = set(map(tuple, outputs[keys].itertuples(index=False, name=None)))
    if len(sample) != 1000 or found != expected:
        raise ValueError(f"Expected exactly 3000 frozen primary keys; found {len(found)}.")
    manifest_hash = digest(MODEL_MANIFEST)
    if set(outputs["model_manifest_sha256"]) != {manifest_hash}:
        raise ValueError("Output model-manifest hash does not match the frozen manifest.")
    if not (outputs["validator_status"] == "VALID_NONEMPTY_UTF8").all() or outputs["output_text"].astype(str).str.strip().eq("").any():
        raise ValueError("A completed primary output must be valid and nonempty.")
    attempts = [json.loads(line) for line in ATTEMPTS.read_text(encoding="utf-8").splitlines() if line.strip()]
    unresolved = [row for row in attempts if row.get("validator_status") != "VALID_NONEMPTY_UTF8" and row.get("run_key") not in {
        f"{item}|{MODEL_ID}|{condition}" for item, _, condition in expected
    }]
    if unresolved:
        raise ValueError("Attempt log contains an unaccounted unsuccessful key.")
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["artifact", "sha256", "rows", "status"])
        writer.writeheader()
        writer.writerow({"artifact": "validated/primary_model_outputs.csv", "sha256": digest(OUTPUTS), "rows": len(outputs), "status": "FROZEN"})
        writer.writerow({"artifact": "raw/primary_attempts.jsonl", "sha256": digest(ATTEMPTS), "rows": len(attempts), "status": "APPEND_ONLY_LOG"})
        writer.writerow({"artifact": "frozen_vizwiz_sample", "sha256": digest(SAMPLE), "rows": len(sample), "status": "FROZEN"})
        writer.writerow({"artifact": "public_vlm_models.json", "sha256": manifest_hash, "rows": 1, "status": "FROZEN"})
    with CHECKSUMS.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["path", "algorithm", "checksum"])
        writer.writeheader()
        for path in (OUTPUTS, ATTEMPTS, SAMPLE, MODEL_MANIFEST):
            writer.writerow({"path": str(path.relative_to(ROOT)), "algorithm": "SHA256", "checksum": digest(path)})
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    FREEZE.write_text(
        "# Primary model-output freeze\n\n"
        f"**Frozen:** {now}  \n**Status:** `FROZEN_PRIMARY_OUTPUTS_NOT_YET_ANALYZED`\n\n"
        "- Design validation: 1,000 locked items × 3 frozen conditions = 3,000 valid primary outputs.\n"
        "- Model/configuration/sample hashes are in `data/model_outputs/OUTPUT_MANIFEST.csv` and `data/model_outputs/CHECKSUMS.csv`.\n"
        "- This gate contains no outcome statistics or claim. Analysis begins only from these frozen files.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "OUTPUT_FREEZE_PASS", "rows": len(outputs), "manifest_sha256": manifest_hash}, sort_keys=True))


if __name__ == "__main__":
    main()
