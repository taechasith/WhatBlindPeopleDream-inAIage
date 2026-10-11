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


def valid_parser_status(value: object) -> bool:
    """Accept documented parser outcomes while rejecting empty/unknown states.

    A parse error is a valid *recorded outcome* of the frozen instrument, not a
    successful parse. Its count remains visible in the technical manifest and
    must later be considered as coverage/missingness; an unrecognized status is
    a fail-closed provenance error.
    """
    status = str(value)
    return status in {
        "PARSED",
        "EVIDENCE_SPAN_INVALID",
        "PARSE_ERROR:JSONDecodeError",
        "PARSE_ERROR:ValueError",
    }


def measurement_status(parser_status: object) -> str:
    """Separate a valid label record from documented invalid measurement rows."""
    status = str(parser_status)
    if status == "PARSED":
        return "VALID_SYNTHETIC_RECORD"
    if status == "EVIDENCE_SPAN_INVALID":
        return "EVIDENCE_SPAN_INVALID"
    if status.startswith("PARSE_ERROR:"):
        return "TECHNICALLY_INVALID_FOR_MEASUREMENT"
    fail(f"unrecognized parser status while assigning measurement validity: {status}")
    raise AssertionError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    config_file_hash = sha256(args.config)
    prompt_hash = sha256(args.prompt)
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
    repo_root = args.config.resolve().parents[1]

    manifests: list[dict[str, object]] = []
    judge_frames: dict[str, pd.DataFrame] = {}
    required_columns = {
        "blind_item_id", "judge_id", "model_id", "model_revision", "prompt_sha256",
        "panel_config_sha256", "runtime_seconds", "generated_at_utc", "construct",
        "label", "abstain", "evidence_span", "reason_code", "parser_status",
    }
    for judge in config["judges"]:
        judge_id = judge["judge_id"]
        local_dir = repo_root / judge["local_dir"]
        snapshot_marker = local_dir / ".cache" / "huggingface" / "download" / "config.json.metadata"
        if not local_dir.is_dir() or not snapshot_marker.is_file():
            fail(f"{judge_id} local frozen checkpoint or revision marker is unavailable")
        cached_revision = snapshot_marker.read_text(encoding="utf-8").splitlines()[0].strip()
        if cached_revision != judge["immutable_revision"]:
            fail(f"{judge_id} local cache revision marker does not match frozen configuration")
        labels_path = args.panel_dir / f"{judge_id}_labels.csv"
        raw_path = args.panel_dir / f"{judge_id}_raw.jsonl"
        if not labels_path.is_file() or not raw_path.is_file():
            fail(f"missing output file(s) for {judge_id}")
        raw_metadata: list[dict[str, object]] = []
        with raw_path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    fail(f"{judge_id} raw record {line_number} is invalid JSON: {exc.msg}")
                required_raw = {
                    "blind_item_id", "judge_id", "model_id", "model_revision",
                    "prompt_sha256", "panel_config_sha256", "runtime_seconds",
                    "generated_at_utc", "raw_output", "parse_status",
                }
                if not required_raw.issubset(record):
                    fail(f"{judge_id} raw record {line_number} has incomplete metadata")
                raw_metadata.append(record)
        raw_record_count = len(raw_metadata)
        if raw_record_count != len(expected_ids):
            fail(f"{judge_id} has {raw_record_count} raw records; expected {len(expected_ids)}")
        raw_ids = [str(record["blind_item_id"]) for record in raw_metadata]
        if set(raw_ids) != expected_ids or len(set(raw_ids)) != len(raw_ids):
            fail(f"{judge_id} raw records have missing or duplicate blind IDs (possible unexplained retry)")
        raw_by_id = {str(record["blind_item_id"]): record for record in raw_metadata}
        for record in raw_metadata:
            if record["judge_id"] != judge_id:
                fail(f"{judge_id} raw record has an unexpected judge ID")
            if record["model_id"] != judge["model_id"]:
                fail(f"{judge_id} raw record has a model-ID mismatch")
            if record["model_revision"] != judge["immutable_revision"]:
                fail(f"{judge_id} raw record has a revision mismatch")
            if record["prompt_sha256"] != prompt_hash:
                fail(f"{judge_id} raw record has a prompt-hash mismatch")
            if record["panel_config_sha256"] != config_hash:
                fail(f"{judge_id} raw record has a config-hash mismatch")
            if not valid_parser_status(record["parse_status"]):
                fail(f"{judge_id} raw record has an invalid parser status")
        # ``NA`` is a frozen, literal abstention label—not a missing CSV cell.
        # Preserve it while checking schema and provenance.
        labels = pd.read_csv(labels_path, dtype=str, keep_default_na=False)
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
        if set(labels.model_id) != {judge["model_id"]}:
            fail(f"{judge_id} model ID does not match frozen configuration")
        if set(labels.model_revision) != {judge["immutable_revision"]}:
            fail(f"{judge_id} model revision does not match frozen configuration")
        if set(labels.prompt_sha256) != {prompt_hash}:
            fail(f"{judge_id} prompt hash does not match frozen prompt")
        if set(labels.panel_config_sha256) != {config_hash}:
            fail(f"{judge_id} config hash does not match frozen configuration")
        if not set(labels.label).issubset(set(config["label_values"])):
            fail(f"{judge_id} includes an invalid label")
        if not labels.parser_status.map(valid_parser_status).all():
            fail(f"{judge_id} includes an invalid parser status")
        labels["measurement_status"] = labels.parser_status.map(measurement_status)
        for blind_id, group in labels.groupby("blind_item_id", sort=False):
            raw = raw_by_id[str(blind_id)]
            for field in ("judge_id", "model_id", "model_revision", "prompt_sha256", "panel_config_sha256"):
                if set(group[field]) != {str(raw[field])}:
                    fail(f"{judge_id} raw/label metadata mismatch for blinded item {blind_id}")
            raw_status = str(raw["parse_status"])
            label_statuses = set(group.parser_status)
            if raw_status.startswith("PARSE_ERROR:") and label_statuses != {raw_status}:
                fail(f"{judge_id} raw/label parser-status mismatch for blinded item {blind_id}")
            if raw_status == "PARSED" and not label_statuses.issubset({"PARSED", "EVIDENCE_SPAN_INVALID"}):
                fail(f"{judge_id} parsed raw record has incompatible label parser status")
        judge_frames[judge_id] = labels[[
            "blind_item_id", "construct", "label", "abstain", "parser_status", "measurement_status",
        ]].copy()
        status_counts = labels.parser_status.value_counts(dropna=False).to_dict()
        measurement_counts = labels.measurement_status.value_counts(dropna=False).to_dict()
        manifests.append({
            "judge_id": judge_id,
            "labels_path": str(labels_path),
            "labels_sha256": sha256(labels_path),
            "raw_path": str(raw_path),
            "raw_sha256": sha256(raw_path),
            "raw_records": raw_record_count,
            "prompt_sha256": prompt_hash,
            "config_file_sha256": config_file_hash,
            "config_canonical_json_sha256": config_hash,
            "local_checkpoint_dir": str(local_dir),
            "local_cache_revision_marker": cached_revision,
            "label_rows": len(labels),
            "distinct_blind_item_ids": labels.blind_item_id.nunique(),
            "expected_label_rows": expected_rows,
            "parser_status_counts_json": json.dumps(status_counts, sort_keys=True),
            "measurement_status_counts_json": json.dumps(measurement_counts, sort_keys=True),
        })

    if args.outdir.exists():
        fail("freeze output directory already exists; refuse to overwrite an immutable receipt")
    args.outdir.mkdir(parents=True, exist_ok=False)
    manifest_path = args.outdir / "synthetic_panel_manifest.csv"
    pd.DataFrame(manifests).to_csv(manifest_path, index=False)

    judge_ids = list(judge_frames)
    if len(judge_ids) < 2:
        fail("at least two frozen judges are required for a disagreement map")
    merged = judge_frames[judge_ids[0]].rename(columns={
        "label": f"label_{judge_ids[0]}",
        "abstain": f"abstain_{judge_ids[0]}",
        "parser_status": f"parser_status_{judge_ids[0]}",
        "measurement_status": f"measurement_status_{judge_ids[0]}",
    })
    for judge_id in judge_ids[1:]:
        frame = judge_frames[judge_id].rename(columns={
            "label": f"label_{judge_id}",
            "abstain": f"abstain_{judge_id}",
            "parser_status": f"parser_status_{judge_id}",
            "measurement_status": f"measurement_status_{judge_id}",
        })
        merged = merged.merge(frame, on=["blind_item_id", "construct"], how="inner", validate="one_to_one")
    if len(merged) != expected_rows:
        fail("judge labels cannot be aligned one-to-one")
    label_columns = [f"label_{judge_id}" for judge_id in judge_ids]
    validity_columns = [f"measurement_status_{judge_id}" for judge_id in judge_ids]
    merged["measurement_comparable"] = (merged[validity_columns] == "VALID_SYNTHETIC_RECORD").all(axis=1)
    merged["all_judges_same_label"] = pd.NA
    comparable = merged["measurement_comparable"]
    merged.loc[comparable, "all_judges_same_label"] = (
        merged.loc[comparable, label_columns].nunique(axis=1) == 1
    )
    merged["disagreement_status"] = "NOT_COMPARABLE_INVALID_MEASUREMENT"
    merged.loc[comparable & (merged["all_judges_same_label"] == True), "disagreement_status"] = "AGREE"
    merged.loc[comparable & (merged["all_judges_same_label"] == False), "disagreement_status"] = "DISAGREE"
    disagreement_path = args.outdir / "blinded_disagreement_map.csv"
    merged.to_csv(disagreement_path, index=False)

    checksum_rows = [
        {"artifact": "config_file", "path": str(args.config), "sha256": config_file_hash},
        {"artifact": "prompt", "path": str(args.prompt), "sha256": prompt_hash},
        {"artifact": "blinded_packet", "path": str(args.packet), "sha256": sha256(args.packet)},
        {"artifact": "manifest", "path": str(manifest_path), "sha256": sha256(manifest_path)},
        {"artifact": "blinded_disagreement_map", "path": str(disagreement_path), "sha256": sha256(disagreement_path)},
    ]
    for manifest in manifests:
        checksum_rows.extend([
            {"artifact": f"{manifest['judge_id']}_labels", "path": manifest["labels_path"], "sha256": manifest["labels_sha256"]},
            {"artifact": f"{manifest['judge_id']}_raw", "path": manifest["raw_path"], "sha256": manifest["raw_sha256"]},
        ])
    checksums_path = args.outdir / "synthetic_panel_checksums.csv"
    pd.DataFrame(checksum_rows).to_csv(checksums_path, index=False)

    summary = {
        "status": "FROZEN_BLINDED_SYNTHETIC_PANEL_OUTPUTS",
        "condition_labels_exposed": False,
        "packet_rows": len(packet),
        "constructs": constructs,
        "expected_labels_per_judge": expected_rows,
        "judge_ids": judge_ids,
        "panel_config_canonical_json_sha256": config_hash,
        "panel_config_file_sha256": config_file_hash,
        "packet_sha256": sha256(args.packet),
        "prompt_sha256": prompt_hash,
        "manifest_sha256": sha256(manifest_path),
        "checksums_sha256": sha256(checksums_path),
        "disagreement_map_sha256": sha256(disagreement_path),
        "interpretation_boundary": "No condition-level analysis, consensus collapse, or human-equivalence claim is authorized.",
    }
    (args.outdir / "SYNTHETIC_PANEL_OUTPUT_FREEZE.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.outdir / "SYNTHETIC_PANEL_OUTPUT_FREEZE.md").write_text(
        "# Blinded synthetic panel output freeze\n\n"
        f"Status: `{summary['status']}`\n\n"
        f"- Condition labels exposed: `{summary['condition_labels_exposed']}`\n"
        f"- Frozen packet rows: {summary['packet_rows']}\n"
        f"- Constructs per judge: {len(constructs)}\n"
        f"- Expected labels per judge: {expected_rows}\n"
        f"- Panel config file SHA-256: `{config_file_hash}`\n"
        f"- Panel config canonical-JSON SHA-256: `{config_hash}`\n"
        f"- Prompt SHA-256: `{prompt_hash}`\n"
        f"- Interpretation boundary: {summary['interpretation_boundary']}\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
