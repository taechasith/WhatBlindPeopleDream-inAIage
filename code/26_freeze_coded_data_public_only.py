"""Freeze the blinded public-data computational measurement dataset.

This gate may run only after the frozen synthetic panel, blind technical
robustness checks, construct-strength decisions, and public-human calibration
receipt all exist.  It deliberately accepts no condition map, unblinding key,
or outcome table.  Its role is provenance closure, not statistical analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TIER_MATRIX = ROOT / "CONSTRUCT_MEASUREMENT_TIER_MATRIX.csv"
DEFAULT_CALIBRATION_MATRIX = ROOT / "PUBLIC_HUMAN_CALIBRATION_MATRIX.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"CODED_DATA_FREEZE_FAILED: {message}")


def read_json(path: Path, expected_status: str) -> dict[str, Any]:
    if not path.is_file():
        fail(f"required receipt is unavailable: {path}")
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("status") != expected_status:
        fail(f"unexpected receipt status for {path.name}: {record.get('status')!r}")
    if record.get("condition_labels_exposed") is not False:
        fail(f"receipt records condition-label exposure: {path.name}")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-freeze", type=Path, required=True)
    parser.add_argument("--subset-manifest", type=Path, required=True)
    parser.add_argument("--measurement-audit-dir", type=Path, required=True)
    parser.add_argument("--rule-anchor-dir", type=Path, required=True)
    parser.add_argument("--construct-strength-dir", type=Path, required=True)
    parser.add_argument("--calibration-receipt", type=Path, required=True)
    parser.add_argument("--tier-matrix", type=Path, default=DEFAULT_TIER_MATRIX)
    parser.add_argument("--calibration-matrix", type=Path, default=DEFAULT_CALIBRATION_MATRIX)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    if args.outdir.exists():
        fail("refuse to overwrite an immutable coded-data freeze")

    panel = read_json(args.panel_freeze, "FROZEN_BLINDED_SYNTHETIC_PANEL_OUTPUTS")
    subset = read_json(args.subset_manifest, "FROZEN_BLINDED_MEASUREMENT_ROBUSTNESS_SUBSETS")
    audit = read_json(
        args.measurement_audit_dir / "AUDIT_MANIFEST.json",
        "BLINDED_COMPUTATIONAL_MEASUREMENT_AUDIT_COMPLETE",
    )
    anchors = read_json(
        args.rule_anchor_dir / "RULE_ANCHOR_MANIFEST.json",
        "BLINDED_RULE_ANCHORS_COMPLETE",
    )
    strength = read_json(
        args.construct_strength_dir / "CONSTRUCT_STRENGTH_MANIFEST.json",
        "BLINDED_CONSTRUCT_MEASUREMENT_STRENGTH_FROZEN",
    )

    required_files = {
        "panel_manifest": args.panel_freeze.parent / "synthetic_panel_manifest.csv",
        "panel_checksums": args.panel_freeze.parent / "synthetic_panel_checksums.csv",
        "disagreement_map": args.panel_freeze.parent / "blinded_disagreement_map.csv",
        "audit_metrics": args.measurement_audit_dir / "blinded_measurement_audit_metrics.csv",
        "rule_anchor_summary": args.rule_anchor_dir / "blinded_rule_anchor_summary.csv",
        "construct_strength": args.construct_strength_dir / "construct_measurement_strength.csv",
        "tier_matrix": args.tier_matrix,
        "calibration_matrix": args.calibration_matrix,
        "calibration_receipt": args.calibration_receipt,
    }
    missing = [name for name, path in required_files.items() if not path.is_file()]
    if missing:
        fail(f"required file(s) unavailable: {', '.join(missing)}")

    panel_manifest = pd.read_csv(required_files["panel_manifest"], dtype=str, keep_default_na=False)
    if len(panel_manifest) < 2:
        fail("frozen panel manifest does not include multiple judges")
    if not {"judge_id", "label_rows", "distinct_blind_item_ids", "expected_label_rows"}.issubset(panel_manifest.columns):
        fail("frozen panel manifest schema is incomplete")
    expected_rows = int(panel["expected_labels_per_judge"])
    packet_rows = int(panel["packet_rows"])
    if not (panel_manifest["label_rows"].astype(int) == expected_rows).all():
        fail("a judge has incomplete frozen label coverage")
    if not (panel_manifest["expected_label_rows"].astype(int) == expected_rows).all():
        fail("panel-manifest expected label count differs from freeze receipt")
    if not (panel_manifest["distinct_blind_item_ids"].astype(int) == packet_rows).all():
        fail("a judge does not cover every frozen blinded item")
    if set(panel_manifest["judge_id"]) != set(panel["judge_ids"]):
        fail("panel manifest judge identities do not match freeze receipt")

    disagreement = pd.read_csv(required_files["disagreement_map"], dtype=str, keep_default_na=False)
    expected_disagreement = packet_rows * len(panel["constructs"])
    if len(disagreement) != expected_disagreement:
        fail("disagreement map does not cover every blinded item/construct")
    if {"condition", "condition_label", "prompt_type", "treatment", "arm"}.intersection(disagreement.columns):
        fail("disagreement map contains an unblinding field")

    construct_strength = pd.read_csv(required_files["construct_strength"], dtype=str, keep_default_na=False)
    tiers = pd.read_csv(required_files["tier_matrix"], dtype=str, keep_default_na=False)
    if not {"construct", "measurement_layer", "final_measurement_status", "condition_labels_exposed"}.issubset(construct_strength.columns):
        fail("construct-strength table schema is incomplete")
    if not (construct_strength["condition_labels_exposed"].str.casefold() == "false").all():
        fail("construct-strength table records condition exposure")
    tier_keys = set(zip(tiers["construct"], tiers["measurement_layer"]))
    strength_keys = set(zip(construct_strength["construct"], construct_strength["measurement_layer"]))
    if tier_keys != strength_keys:
        fail("construct-strength table does not cover the frozen tier matrix exactly")
    allowed_statuses = {
        "COMPUTATIONAL_PRIMARY",
        "PUBLIC_HUMAN_BENCHMARKED",
        "COMPUTATIONAL_SECONDARY",
        "MODEL_DERIVED_EXPLORATORY",
        "MEASUREMENT_UNSTABLE",
    }
    if not set(construct_strength["final_measurement_status"]).issubset(allowed_statuses):
        fail("construct-strength table includes an unknown measurement status")

    calibration = pd.read_csv(args.calibration_receipt, dtype=str, keep_default_na=False)
    if "provenance_validation_status" not in calibration.columns or not (calibration["provenance_validation_status"] == "PASS").all():
        fail("public-human calibration receipt has incomplete or failed provenance")
    if "condition_labels_exposed" in calibration.columns and not (calibration["condition_labels_exposed"].str.casefold() == "false").all():
        fail("calibration receipt records condition exposure")

    if int(subset["prompt_paraphrase_rows"]) <= 0 or int(subset["exact_rerun_rows"]) <= 0:
        fail("robustness subset receipt records no technical checks")
    if audit.get("baseline_records", 0) <= 0 or audit.get("prompt_paraphrase_records", 0) <= 0 or audit.get("exact_rerun_records", 0) <= 0:
        fail("measurement-audit receipt is incomplete")

    args.outdir.mkdir(parents=True, exist_ok=False)
    source_rows = []
    for name, path in required_files.items():
        source_rows.append({"artifact": name, "path": str(path), "sha256": sha256(path)})
    for name, path in {
        "panel_freeze": args.panel_freeze,
        "subset_manifest": args.subset_manifest,
        "audit_manifest": args.measurement_audit_dir / "AUDIT_MANIFEST.json",
        "rule_anchor_manifest": args.rule_anchor_dir / "RULE_ANCHOR_MANIFEST.json",
        "construct_strength_manifest": args.construct_strength_dir / "CONSTRUCT_STRENGTH_MANIFEST.json",
    }.items():
        source_rows.append({"artifact": name, "path": str(path), "sha256": sha256(path)})
    checksums_path = args.outdir / "CODED_DATA_CHECKSUMS.csv"
    pd.DataFrame(source_rows).to_csv(checksums_path, index=False)

    status_counts = construct_strength["final_measurement_status"].value_counts().sort_index().to_dict()
    manifest = {
        "status": "CODED_DATA_FROZEN_PUBLIC_DATA_ONLY",
        "condition_labels_exposed": False,
        "new_human_data_collected": False,
        "alt_test_current_study": "NOT_APPLICABLE_TO_CURRENT_DESIGN",
        "packet_rows": packet_rows,
        "constructs_per_judge": len(panel["constructs"]),
        "frozen_judges": list(panel["judge_ids"]),
        "expected_labels_per_judge": expected_rows,
        "technical_robustness_subsets": {
            "prompt_paraphrase_rows": int(subset["prompt_paraphrase_rows"]),
            "exact_rerun_rows": int(subset["exact_rerun_rows"]),
        },
        "construct_status_counts": status_counts,
        "source_checksums": {row["artifact"]: row["sha256"] for row in source_rows},
        "authorization_after_freeze": (
            "Condition mapping may be unblinded once for the prespecified RQ2--RQ5 analysis. "
            "This freeze does not authorize human-equivalence, preference, lived-experience, "
            "or cognitive-equivalence claims."
        ),
        "limitations": (
            "Synthetic annotation is a computational instrument. Existing public human-labelled "
            "sources provide external calibration only; they are not same-item ratings of the "
            "frozen VLM outputs."
        ),
    }
    manifest_path = args.outdir / "CODED_DATA_FREEZE.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.outdir / "CODED_DATA_FREEZE.md").write_text(
        "# Coded-data freeze: public-data computational measurement\n\n"
        "Status: `CODED_DATA_FROZEN_PUBLIC_DATA_ONLY`\n\n"
        f"- Condition labels exposed before this gate: `False`\n"
        f"- New human data collected: `False`\n"
        f"- Frozen blinded outputs: {packet_rows} rows × {len(panel['constructs'])} constructs × {len(panel['judge_ids'])} judges\n"
        f"- Prompt-paraphrase technical subset: {subset['prompt_paraphrase_rows']} rows\n"
        f"- Exact deterministic-rerun subset: {subset['exact_rerun_rows']} rows\n"
        f"- Construct statuses: `{json.dumps(status_counts, sort_keys=True)}`\n"
        "- Alternative Annotator Test: `NOT_APPLICABLE_TO_CURRENT_DESIGN`\n\n"
        "This provenance gate authorizes one condition unblinding for the frozen RQ2--RQ5 plan. "
        "It does not establish human equivalence, BLV preference, lived experience, cognitive "
        "equivalence, or image-grounded truth beyond the bounded public-human validation analyses.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": manifest["status"], "condition_labels_exposed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
