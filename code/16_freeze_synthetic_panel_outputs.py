"""Validate and freeze blinded synthetic-panel artifacts without condition analysis.

This is a post-run gate for frozen judges. It verifies technical completeness,
records file checksums and parser-status counts, and creates a per-item/
construct disagreement map only after every configured judge has completed.
It never reads a condition map or computes condition-level effects.
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
    raise ValueError(f"SYNTHETIC_PANEL_FREEZE_FAILED: {message}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    packet = pd.read_csv(args.packet, dtype=str)
    required_packet = {"blind_item_id", "blv_question", "output_text"}
    if not required_packet.issubset(packet.columns):
        fail("packet schema is incomplete")
    if any(field in packet.columns for field in ("condition", "prompt_type", "model_id")):
        fail("packet contains forbidden unblinding fields")
    if packet.blind_item_id.duplicated().any():
        fail("packet has duplicate blind_item_id values")
    expected_ids = set(packet.blind_item_id.astype(str))
    constructs = list(config["constructs"])
    expected_rows = len(expected_ids) * len(constructs)
    config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode("utf-8")).hexdigest()

    manifests: list[dict[str, object]] = []
    judge_frames: dict[str, pd.DataFrame] = {}
    required_columns = {
        "blind_item_id", "judge_id", "model_id", "model_revision", "prompt_sha256",
        "panel_config_sha256", "runtime_seconds", "generated_at_utc", "construct",
        "label", "abstain", "evidence_span", "reason_code", "parser_status",
    }
    for judge in config["judges"]:
        judge_id = judge["judge_id"]
        labels_path = args.panel_dir / f"{judge_id}_labels.csv"
        raw_path = args.panel_dir / f"{judge_id}_raw.jsonl"
        if not labels_path.is_file() or not raw_path.is_file():
            fail(f"missing output file(s) for {judge_id}")
        with raw_path.open("r", encoding="utf-8") as stream:
            raw_record_count = sum(1 for line in stream if line.strip())
        if raw_record_count != len(expected_ids):
            fail(f"{judge_id} has {raw_record_count} raw records; expected {len(expected_ids)}")
        labels = pd.read_csv(labels_path, dtype=str)
        if not required_columns.issubset(labels.columns):
            fail(f"label schema is incomplete for {judge_id}")
        labels["blind_item_id"] = labels["blind_item_id"].astype(str)
        if len(labels) != expected_rows:
            fail(f"{judge_id} has {len(labels)} labels; expected {expected_rows}")
        if set(labels.blind_item_id) != expected_ids:
            fail(f"{judge_id} output IDs do not match the frozen packet")
        if labels.duplicated(["blind_item_id", "construct"]).any():
            fail(f"{judge_id} contains duplicate item/construct labels")
        if set(labels.construct) != set(constructs):
            fail(f"{judge_id} construct set does not match frozen configuration")
        if set(labels.judge_id) != {judge_id}:
            fail(f"{judge_id} label file has an unexpected judge ID")
        if set(labels.model_revision) != {judge["immutable_revision"]}:
            fail(f"{judge_id} model revision does not match frozen configuration")
        if set(labels.panel_config_sha256) != {config_hash}:
            fail(f"{judge_id} config hash does not match frozen configuration")
        if not set(labels.label).issubset(set(config["label_values"])):
            fail(f"{judge_id} includes an invalid label")
        judge_frames[judge_id] = labels[["blind_item_id", "construct", "label", "abstain", "parser_status"]].copy()
        status_counts = labels.parser_status.value_counts(dropna=False).to_dict()
        manifests.append({
            "judge_id": judge_id,
            "labels_path": str(labels_path),
            "labels_sha256": sha256(labels_path),
            "raw_path": str(raw_path),
            "raw_sha256": sha256(raw_path),
            "raw_records": raw_record_count,
            "label_rows": len(labels),
            "distinct_blind_item_ids": labels.blind_item_id.nunique(),
            "expected_label_rows": expected_rows,
            "parser_status_counts_json": json.dumps(status_counts, sort_keys=True),
        })

    args.outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(manifests).to_csv(args.outdir / "SYNTHETIC_PANEL_OUTPUT_MANIFEST.csv", index=False)

    judge_ids = list(judge_frames)
    if len(judge_ids) < 2:
        fail("at least two frozen judges are required for a disagreement map")
    merged = judge_frames[judge_ids[0]].rename(columns={
        "label": f"label_{judge_ids[0]}",
        "abstain": f"abstain_{judge_ids[0]}",
        "parser_status": f"parser_status_{judge_ids[0]}",
    })
    for judge_id in judge_ids[1:]:
        frame = judge_frames[judge_id].rename(columns={
            "label": f"label_{judge_id}",
            "abstain": f"abstain_{judge_id}",
            "parser_status": f"parser_status_{judge_id}",
        })
        merged = merged.merge(frame, on=["blind_item_id", "construct"], how="inner", validate="one_to_one")
    if len(merged) != expected_rows:
        fail("judge labels cannot be aligned one-to-one")
    label_columns = [f"label_{judge_id}" for judge_id in judge_ids]
    merged["all_judges_same_label"] = merged[label_columns].nunique(axis=1) == 1
    merged["disagreement_status"] = merged["all_judges_same_label"].map({True: "AGREE", False: "DISAGREE"})
    merged.to_csv(args.outdir / "SYNTHETIC_PANEL_DISAGREEMENT_MAP.csv", index=False)

    summary = {
        "status": "FROZEN_BLINDED_SYNTHETIC_PANEL_OUTPUTS",
        "condition_labels_exposed": False,
        "packet_rows": len(packet),
        "constructs": constructs,
        "expected_labels_per_judge": expected_rows,
        "judge_ids": judge_ids,
        "panel_config_sha256": config_hash,
        "packet_sha256": sha256(args.packet),
        "manifest_sha256": sha256(args.outdir / "SYNTHETIC_PANEL_OUTPUT_MANIFEST.csv"),
        "disagreement_map_sha256": sha256(args.outdir / "SYNTHETIC_PANEL_DISAGREEMENT_MAP.csv"),
        "interpretation_boundary": "No condition-level analysis, consensus collapse, or human-equivalence claim is authorized.",
    }
    (args.outdir / "SYNTHETIC_PANEL_OUTPUT_FREEZE.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
