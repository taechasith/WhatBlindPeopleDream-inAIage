"""Authorize a hash-bound recovery after a pre-result post-freeze fault.

This utility never opens the condition map or any model output.  It preserves
the original coded-data freeze and documents one replacement analysis-script
hash when an authorized process failed before it produced results.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"TECHNICAL_RECOVERY_AUTHORIZATION_FAILED: {message}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coded-data-freeze", type=Path, required=True)
    parser.add_argument("--unblinding-ledger", type=Path, required=True)
    parser.add_argument("--analysis-script", type=Path, required=True)
    parser.add_argument("--result-dir", type=Path, required=True)
    parser.add_argument("--completion-receipt", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite an immutable recovery authorization")
    freeze = json.loads(args.coded_data_freeze.read_text(encoding="utf-8"))
    if freeze.get("status") != "CODED_DATA_FROZEN_PUBLIC_DATA_ONLY":
        fail("coded-data freeze status is not authorized")
    original_hash = str(freeze.get("source_checksums", {}).get("analysis_script", ""))
    if not original_hash:
        fail("coded-data freeze does not commit an analysis script")
    ledger = json.loads(args.unblinding_ledger.read_text(encoding="utf-8"))
    if ledger.get("status") != "UNBLINDING_STARTED_PUBLIC_DATA_ONLY":
        fail("initial unblinding ledger does not have the expected pre-result status")
    if ledger.get("coded_data_freeze_sha256") != sha256(args.coded_data_freeze):
        fail("initial ledger does not match the coded-data freeze")
    if args.result_dir.exists() or args.completion_receipt.exists():
        fail("results or completion receipt exist; recovery after results is prohibited")
    replacement_hash = sha256(args.analysis_script)
    if replacement_hash == original_hash:
        fail("replacement script does not differ from frozen script; recovery is not applicable")
    args.outdir.mkdir(parents=True, exist_ok=False)
    receipt = {
        "status": "TECHNICAL_RECOVERY_AUTHORIZED_PRE_RESULT_ONLY",
        "condition_labels_exposed_before_recovery": True,
        "condition_effects_estimated_before_recovery": False,
        "new_human_data_collected": False,
        "original_coded_data_freeze_sha256": sha256(args.coded_data_freeze),
        "original_analysis_script_sha256": original_hash,
        "replacement_analysis_script_sha256": replacement_hash,
        "initial_unblinding_ledger_sha256": sha256(args.unblinding_ledger),
        "scope": "Permit the exact replacement analysis script solely to complete the previously authorized analysis after a pre-result provenance-path fault.",
    }
    path = args.outdir / "TECHNICAL_RECOVERY_AUTHORIZATION.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "condition_effects_estimated_before_recovery": False}, sort_keys=True))


if __name__ == "__main__":
    main()
