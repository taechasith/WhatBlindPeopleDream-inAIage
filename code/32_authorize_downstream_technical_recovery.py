"""Authorize hash-bound downstream recovery after a pre-RQ4 provenance fault.

The tool only examines receipts, paths, and SHA-256 values.  It does not read
condition-level result content or the private condition map.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"DOWNSTREAM_TECHNICAL_RECOVERY_FAILED: {message}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coded-data-freeze", type=Path, required=True)
    parser.add_argument("--post-analysis", type=Path, required=True)
    parser.add_argument("--rq4-script", type=Path, required=True)
    parser.add_argument("--results-freeze-script", type=Path, required=True)
    parser.add_argument("--rq4-outdir", type=Path, required=True)
    parser.add_argument("--results-freeze-outdir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite immutable authorization")
    freeze = json.loads(args.coded_data_freeze.read_text(encoding="utf-8"))
    if freeze.get("status") != "CODED_DATA_FROZEN_PUBLIC_DATA_ONLY":
        fail("coded-data freeze is not authorized")
    analysis = json.loads((args.post_analysis / "ANALYSIS_MANIFEST.json").read_text(encoding="utf-8"))
    if analysis.get("status") != "RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY":
        fail("post-freeze analysis receipt is incomplete")
    if args.rq4_outdir.exists() or args.results_freeze_outdir.exists():
        fail("downstream artifacts already exist; recovery after RQ4 is prohibited")
    originals = dict(freeze.get("source_checksums", {}))
    # The post-analysis manifest records map-access recovery.  The distinct
    # coded-data recovery receipt is the one that binds the replacement script
    # hash used for the completed RQ2/RQ3/RQ5 run.
    initial_recovery_path = args.coded_data_freeze.parent.parent / "coded_data_recovery" / "TECHNICAL_RECOVERY_AUTHORIZATION.json"
    if not initial_recovery_path.is_file():
        fail("post-analysis receipt does not provide its initial technical recovery authorization")
    initial_recovery = json.loads(initial_recovery_path.read_text(encoding="utf-8"))
    if initial_recovery.get("status") != "TECHNICAL_RECOVERY_AUTHORIZED_PRE_RESULT_ONLY":
        fail("initial technical recovery receipt has an invalid status")
    current_analysis = str(initial_recovery.get("replacement_analysis_script_sha256", ""))
    if not current_analysis:
        fail("initial technical recovery receipt lacks replacement analysis-script hash")
    replacements = {
        "analysis_script": {"original_sha256": str(originals.get("analysis_script", "")), "replacement_sha256": current_analysis},
        "rq4_script": {"original_sha256": str(originals.get("rq4_script", "")), "replacement_sha256": sha256(args.rq4_script)},
        "results_freeze_script": {"original_sha256": str(originals.get("results_freeze_script", "")), "replacement_sha256": sha256(args.results_freeze_script)},
    }
    if any(not item["original_sha256"] or item["original_sha256"] == item["replacement_sha256"] for item in replacements.values()):
        fail("recovery must document a changed, frozen source for every declared replacement")
    args.outdir.mkdir(parents=True, exist_ok=False)
    receipt = {
        "status": "DOWNSTREAM_TECHNICAL_RECOVERY_AUTHORIZED_PRE_RQ4_ONLY",
        "coded_data_freeze_sha256": sha256(args.coded_data_freeze),
        "post_analysis_manifest_sha256": sha256(args.post_analysis / "ANALYSIS_MANIFEST.json"),
        "condition_effects_reinterpreted_before_recovery": False,
        "new_human_data_collected": False,
        "replacements": replacements,
        "scope": "Permit only the listed hash-bound script replacements to complete RQ4, results freeze, and figures after a provenance-check ordering fault; no scientific design or estimand changes are authorized.",
    }
    path = args.outdir / "DOWNSTREAM_TECHNICAL_RECOVERY_AUTHORIZATION.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "condition_effects_reinterpreted_before_recovery": False}, sort_keys=True))


if __name__ == "__main__":
    main()
