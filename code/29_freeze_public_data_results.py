"""Freeze completed public-data RQ2--RQ5 artifacts before interpretation.

This gate does not recompute effects or generate prose. It checks immutable
receipts and hashes the tables that later figures and the manuscript must cite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"RESULTS_FREEZE_FAILED: {message}")


def read_receipt(path: Path, status: str) -> dict[str, object]:
    if not path.is_file():
        fail(f"required receipt unavailable: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != status:
        fail(f"unexpected receipt status for {path.name}: {payload.get('status')!r}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coded-data-freeze", type=Path, required=True)
    parser.add_argument("--post-freeze-analysis", type=Path, required=True)
    parser.add_argument("--space-analysis", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite immutable results freeze")
    coded = read_receipt(args.coded_data_freeze, "CODED_DATA_FROZEN_PUBLIC_DATA_ONLY")
    post = read_receipt(args.post_freeze_analysis / "ANALYSIS_MANIFEST.json", "RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY")
    space = read_receipt(args.space_analysis / "RQ4_MANIFEST.json", "RQ4_COMPLETE_DISTRIBUTIONAL_PUBLIC_DATA_ONLY")
    required = {
        "RQ2": args.post_freeze_analysis / "RQ2_results.csv",
        "RQ3": args.post_freeze_analysis / "RQ3_results.csv",
        "RQ5": args.post_freeze_analysis / "RQ5_results.csv",
        "RQ4": args.space_analysis / "RQ4_results.csv",
        "RQ4_profiles": args.space_analysis / "RQ4_space_profiles.csv",
        "RQ4_association_status": args.space_analysis / "RQ4_association_status.csv",
    }
    missing = [name for name, path in required.items() if not path.is_file()]
    if missing:
        fail(f"missing result table(s): {', '.join(missing)}")
    rq2 = pd.read_csv(required["RQ2"])
    rq3 = pd.read_csv(required["RQ3"])
    rq4 = pd.read_csv(required["RQ4"])
    rq5 = pd.read_csv(required["RQ5"])
    if rq2.empty or rq3.empty or rq4.empty or rq5.empty:
        fail("one or more results tables are empty")
    args.outdir.mkdir(parents=True, exist_ok=False)
    ledger = pd.DataFrame([
        {"result_family": name, "path": str(path), "sha256": sha256(path), "rows": len(pd.read_csv(path))}
        for name, path in required.items()
    ])
    ledger.to_csv(args.outdir / "RESULTS_LEDGER.csv", index=False)
    manifest = {
        "status": "RESULTS_FROZEN_PUBLIC_DATA_ONLY",
        "coded_data_status": coded["status"],
        "condition_unblinded_once": bool(post.get("condition_unblinded_once")),
        "new_human_data_collected": False,
        "alt_test_current_study": "NOT_APPLICABLE_TO_CURRENT_DESIGN",
        "tables": {name: {"sha256": sha256(path), "rows": len(pd.read_csv(path))} for name, path in required.items()},
        "interpretation_boundary": "Frozen VLM-output and distributional text results only; no human-equivalence, lived-experience, cognitive, dream-causation, or user-benefit claim is authorized.",
    }
    (args.outdir / "RESULTS_FREEZE.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.outdir / "RESULTS_FREEZE.md").write_text(
        "# Results freeze: public-data study\n\n"
        "Status: `RESULTS_FROZEN_PUBLIC_DATA_ONLY`\n\n"
        "All listed table hashes are in `RESULTS_LEDGER.csv`. The analysis was performed after the coded-data freeze and one authorized unblinding. Results concern model outputs and textual distributions only.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": manifest["status"], "tables": list(required)}, sort_keys=True))


if __name__ == "__main__":
    main()
