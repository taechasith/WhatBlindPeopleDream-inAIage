"""Audit frozen blinded synthetic measurements without condition analysis.

This script is an instrument-quality check. It reads only the authorized
blinded packet and frozen/sensitivity label files, never accepts a condition
map, and writes no condition-level result. Baseline artifacts are read-only;
the output directory must be new.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_LABEL_COLUMNS = {
    "blind_item_id", "judge_id", "model_id", "model_revision", "prompt_sha256",
    "panel_config_sha256", "construct", "label", "abstain", "evidence_span",
    "reason_code", "parser_status",
}
FORBIDDEN_PACKET_FIELDS = {"condition", "condition_label", "prompt_type", "treatment", "arm", "model_id"}


def fail(message: str) -> None:
    raise ValueError(f"MEASUREMENT_AUDIT_FAILED: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalise(value: object) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", str(value or "")).casefold()).strip()


def as_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    text = str(value).strip().casefold()
    if text == "true":
        return True
    if text == "false":
        return False
    return None


def load_packet(path: Path) -> pd.DataFrame:
    packet = pd.read_csv(path, dtype=str, keep_default_na=False)
    expected = {"blind_item_id", "blv_question", "output_text"}
    if set(packet.columns) != expected or any(column in FORBIDDEN_PACKET_FIELDS for column in packet.columns):
        fail("packet is not the exact blinded three-column contract")
    if packet.blind_item_id.duplicated().any() or packet.blind_item_id.str.strip().eq("").any():
        fail("packet blind identifiers are missing or duplicate")
    return packet


def expected_judge(config: dict[str, Any], judge_id: str) -> dict[str, Any]:
    match = [judge for judge in config["judges"] if judge["judge_id"] == judge_id]
    if len(match) != 1:
        fail(f"unknown or nonunique frozen judge: {judge_id}")
    return match[0]


def label_file(directory: Path, judge_id: str) -> Path:
    path = directory / f"{judge_id}_labels.csv"
    if not path.is_file():
        fail(f"missing labels for {judge_id}: {path}")
    return path


def audit_one_set(
    set_name: str,
    labels_dir: Path,
    packet: pd.DataFrame,
    judge: dict[str, Any],
    config_hash: str,
    expected_prompt_hash: str | None,
    constructs: list[str],
) -> pd.DataFrame:
    """Return per-record audit state; no condition metadata exists or is used."""
    path = label_file(labels_dir, judge["judge_id"])
    labels = pd.read_csv(path, dtype=str, keep_default_na=False)
    if not REQUIRED_LABEL_COLUMNS.issubset(labels.columns):
        fail(f"{set_name}/{judge['judge_id']} labels have an incomplete schema")
    labels["blind_item_id"] = labels["blind_item_id"].astype(str)
    expected_ids = set(packet.blind_item_id.astype(str))
    expected_rows = len(expected_ids) * len(constructs)
    if len(labels) != expected_rows or set(labels.blind_item_id) != expected_ids:
        fail(f"{set_name}/{judge['judge_id']} does not cover the exact frozen packet")
    if labels.duplicated(["blind_item_id", "construct"]).any() or set(labels.construct) != set(constructs):
        fail(f"{set_name}/{judge['judge_id']} has duplicate or unexpected construct records")
    for field, expected in (("judge_id", judge["judge_id"]), ("model_id", judge["model_id"]),
                            ("model_revision", judge["immutable_revision"]), ("panel_config_sha256", config_hash)):
        if set(labels[field].astype(str)) != {str(expected)}:
            fail(f"{set_name}/{judge['judge_id']} provenance mismatch for {field}")
    if expected_prompt_hash is not None and set(labels.prompt_sha256.astype(str)) != {expected_prompt_hash}:
        fail(f"{set_name}/{judge['judge_id']} prompt hash does not match its frozen instruction")

    packet_text = packet.set_index("blind_item_id")["output_text"].to_dict()
    rows: list[dict[str, object]] = []
    for record in labels.to_dict("records"):
        label = str(record["label"])
        parser_status = str(record["parser_status"])
        abstain = as_bool(record["abstain"])
        span = str(record.get("evidence_span", "") or "")
        reason = str(record.get("reason_code", "") or "").strip()
        valid_parser = parser_status == "PARSED"
        technical_invalid = parser_status.startswith("PARSE_ERROR:")
        span_invalid = parser_status == "EVIDENCE_SPAN_INVALID"
        span_found = bool(normalise(span)) and normalise(span) in normalise(packet_text[str(record["blind_item_id"])])
        coherence = False
        if valid_parser and label == "1":
            coherence = abstain is False and bool(reason) and span_found
        elif valid_parser and label == "0":
            coherence = abstain is False and not normalise(span)
        elif valid_parser and label == "NA":
            coherence = abstain is True and not normalise(span)
        elif technical_invalid or span_invalid:
            coherence = True  # preserved but ineligible below
        state = "VALID"
        if technical_invalid:
            state = "TECHNICAL_INVALID"
        elif span_invalid:
            state = "EVIDENCE_SPAN_INVALID"
        elif not coherence:
            state = "LABEL_ABSTAIN_OR_SPAN_INCOHERENT"
        eligible = state == "VALID"
        rows.append({
            "measurement_set": set_name,
            "blind_item_id": str(record["blind_item_id"]),
            "judge_id": judge["judge_id"],
            "construct": str(record["construct"]),
            "label": label,
            "abstain": abstain,
            "parser_status": parser_status,
            "evidence_span_present": bool(normalise(span)),
            "evidence_span_found_in_output": span_found,
            "reason_code_present": bool(reason),
            "audit_state": state,
            "analysis_eligible": eligible,
        })
    return pd.DataFrame(rows)


def paired_metrics(left: pd.DataFrame, right: pd.DataFrame, name: str) -> list[dict[str, object]]:
    keys = ["blind_item_id", "judge_id", "construct"]
    merged = left.merge(right, on=keys, suffixes=("_left", "_right"), validate="one_to_one")
    result: list[dict[str, object]] = []
    for (judge, construct), frame in merged.groupby(["judge_id", "construct"], sort=True):
        comparable = frame.loc[frame.analysis_eligible_left & frame.analysis_eligible_right].copy()
        determinate = comparable.loc[comparable.label_left.isin(["0", "1"]) & comparable.label_right.isin(["0", "1"])]
        n = len(comparable)
        d = len(determinate)
        binary_agree = (determinate.label_left == determinate.label_right).mean() if d else float("nan")
        binary_flip = ((determinate.label_left != determinate.label_right)).mean() if d else float("nan")
        result.append({
            "metric_family": name,
            "judge_id": judge,
            "construct": construct,
            "n_comparable": n,
            "n_binary_comparable": d,
            "label_consistency": (comparable.label_left == comparable.label_right).mean() if n else float("nan"),
            "binary_agreement": binary_agree,
            "binary_flip_rate": binary_flip,
            "determinate_to_na_rate": ((frame.label_left.isin(["0", "1"])) & (frame.label_right == "NA")).mean(),
            "na_to_determinate_rate": ((frame.label_left == "NA") & (frame.label_right.isin(["0", "1"]))).mean(),
        })
    return result


def cross_judge_metrics(frame: pd.DataFrame, judge_ids: list[str]) -> list[dict[str, object]]:
    first, second = judge_ids
    left = frame.loc[frame.judge_id == first].drop(columns=["judge_id"])
    right = frame.loc[frame.judge_id == second].drop(columns=["judge_id"])
    keys = ["blind_item_id", "construct"]
    merged = left.merge(right, on=keys, suffixes=("_left", "_right"), validate="one_to_one")
    result: list[dict[str, object]] = []
    for construct, group in merged.groupby("construct", sort=True):
        comparable = group.loc[group.analysis_eligible_left & group.analysis_eligible_right]
        determinate = comparable.loc[comparable.label_left.isin(["0", "1"]) & comparable.label_right.isin(["0", "1"])]
        n, d = len(comparable), len(determinate)
        result.append({
            "metric_family": "cross_judge_baseline",
            "judge_id": f"{first}__vs__{second}",
            "construct": construct,
            "n_comparable": n,
            "n_binary_comparable": d,
            "label_consistency": (comparable.label_left == comparable.label_right).mean() if n else float("nan"),
            "binary_agreement": (determinate.label_left == determinate.label_right).mean() if d else float("nan"),
            "binary_flip_rate": (determinate.label_left != determinate.label_right).mean() if d else float("nan"),
            "determinate_to_na_rate": ((group.label_left.isin(["0", "1"])) & (group.label_right == "NA")).mean(),
            "na_to_determinate_rate": ((group.label_left == "NA") & (group.label_right.isin(["0", "1"]))).mean(),
        })
    return result


def aggregate_metrics(audited: pd.DataFrame) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for (set_name, judge, construct), frame in audited.groupby(["measurement_set", "judge_id", "construct"], sort=True):
        positives = frame.label.eq("1")
        valid_positive = positives & frame.analysis_eligible
        output.append({
            "metric_family": "record_quality",
            "measurement_set": set_name,
            "judge_id": judge,
            "construct": construct,
            "n_records": len(frame),
            "valid_record_rate": frame.analysis_eligible.mean(),
            "n_positive_labels": int(positives.sum()),
            "valid_positive_span_rate": valid_positive.sum() / positives.sum() if positives.any() else float("nan"),
            "abstention_rate": frame.label.eq("NA").mean(),
            "technical_invalid_rate": frame.audit_state.eq("TECHNICAL_INVALID").mean(),
            "span_invalid_rate": frame.audit_state.eq("EVIDENCE_SPAN_INVALID").mean(),
            "incoherent_rate": frame.audit_state.eq("LABEL_ABSTAIN_OR_SPAN_INCOHERENT").mean(),
        })
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--subset-manifest", type=Path, required=True)
    parser.add_argument("--baseline-freeze", type=Path, required=True)
    parser.add_argument("--baseline-packet", type=Path, required=True)
    parser.add_argument("--baseline-labels-dir", type=Path, required=True)
    parser.add_argument("--prompt-paraphrase-packet", type=Path, required=True)
    parser.add_argument("--prompt-paraphrase-labels-dir", type=Path, required=True)
    parser.add_argument("--exact-rerun-packet", type=Path, required=True)
    parser.add_argument("--exact-rerun-labels-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("audit output directory already exists")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("status") != "FROZEN_BLINDED_PUBLIC_DATA_ONLY":
        fail("unexpected robustness configuration status")
    panel_path = args.config.resolve().parents[1] / config["baseline_panel"]["panel_config_path"]
    panel = json.loads(panel_path.read_text(encoding="utf-8"))
    canonical_hash = hashlib.sha256((args.config.resolve().parents[1] / config["baseline_panel"]["canonical_prompt_path"]).read_bytes()).hexdigest()
    paraphrase_hash = hashlib.sha256((args.config.resolve().parents[1] / config["prompt_paraphrase"]["prompt_path"]).read_bytes()).hexdigest()
    config_hash = hashlib.sha256(json.dumps(panel, sort_keys=True).encode("utf-8")).hexdigest()
    freeze = json.loads(args.baseline_freeze.read_text(encoding="utf-8"))
    if freeze.get("status") != config["baseline_panel"]["required_freeze_status"] or freeze.get("condition_labels_exposed") is not False:
        fail("baseline freeze does not permit blinded audit")
    subset = json.loads(args.subset_manifest.read_text(encoding="utf-8"))
    if subset.get("status") != "FROZEN_BLINDED_MEASUREMENT_ROBUSTNESS_SUBSETS" or subset.get("condition_labels_exposed") is not False:
        fail("subset manifest does not permit blinded audit")

    baseline = load_packet(args.baseline_packet)
    para_packet = load_packet(args.prompt_paraphrase_packet)
    rerun_packet = load_packet(args.exact_rerun_packet)
    if len(baseline) != 3000 or len(para_packet) != 300 or len(rerun_packet) != 60:
        fail("packet sizes violate the frozen 3000/300/60 design")
    if not set(rerun_packet.blind_item_id).issubset(set(para_packet.blind_item_id)):
        fail("exact rerun IDs are not nested in the prompt-paraphrase IDs")
    if not set(para_packet.blind_item_id).issubset(set(baseline.blind_item_id)):
        fail("prompt-paraphrase IDs are not members of baseline")

    constructs = list(panel["constructs"])
    frames: list[pd.DataFrame] = []
    for judge in panel["judges"]:
        frames.extend([
            audit_one_set("baseline", args.baseline_labels_dir, baseline, judge, config_hash, canonical_hash, constructs),
            audit_one_set("prompt_paraphrase", args.prompt_paraphrase_labels_dir, para_packet, judge, config_hash, paraphrase_hash, constructs),
            audit_one_set("exact_rerun", args.exact_rerun_labels_dir, rerun_packet, judge, config_hash, canonical_hash, constructs),
        ])
    audited = pd.concat(frames, ignore_index=True)
    baseline_audit = audited.loc[audited.measurement_set == "baseline"]
    para_audit = audited.loc[audited.measurement_set == "prompt_paraphrase"]
    rerun_audit = audited.loc[audited.measurement_set == "exact_rerun"]
    baseline_for_para = baseline_audit.loc[baseline_audit.blind_item_id.isin(set(para_packet.blind_item_id))]
    baseline_for_rerun = baseline_audit.loc[baseline_audit.blind_item_id.isin(set(rerun_packet.blind_item_id))]
    metrics = aggregate_metrics(audited)
    metrics.extend(cross_judge_metrics(baseline_audit, [judge["judge_id"] for judge in panel["judges"]]))
    metrics.extend(paired_metrics(baseline_for_para, para_audit, "prompt_paraphrase"))
    metrics.extend(paired_metrics(baseline_for_rerun, rerun_audit, "exact_rerun"))
    # Code-path control, never a substantive output result.
    eligible_binary = baseline_audit.loc[baseline_audit.analysis_eligible & baseline_audit.label.isin(["0", "1"])]
    flip_ok = False
    if not eligible_binary.empty:
        before = int(eligible_binary.label.eq("1").sum())
        flipped = eligible_binary.label.copy()
        flipped.iloc[0] = "0" if flipped.iloc[0] == "1" else "1"
        flip_ok = abs(int(flipped.eq("1").sum()) - before) == 1
    metrics.append({"metric_family": "label_flip_code_path", "judge_id": "ALL", "construct": "ALL", "control_pass": flip_ok})

    args.outdir.mkdir(parents=True, exist_ok=False)
    audited.to_csv(args.outdir / "private_audited_records.csv", index=False)
    pd.DataFrame(metrics).to_csv(args.outdir / "blinded_measurement_audit_metrics.csv", index=False)
    manifest = {
        "status": "BLINDED_COMPUTATIONAL_MEASUREMENT_AUDIT_COMPLETE",
        "condition_labels_exposed": False,
        "baseline_records": int(len(baseline_audit)),
        "prompt_paraphrase_records": int(len(para_audit)),
        "exact_rerun_records": int(len(rerun_audit)),
        "constructs": constructs,
        "judges": [judge["judge_id"] for judge in panel["judges"]],
        "inputs_sha256": {"config": sha256(args.config), "subset_manifest": sha256(args.subset_manifest), "baseline_freeze": sha256(args.baseline_freeze)},
        "interpretation_boundary": "Blinded measurement quality only; no condition-level analysis or human-equivalence claim.",
    }
    (args.outdir / "AUDIT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "condition_labels_exposed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
