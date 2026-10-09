"""Apply frozen generic rule anchors to a blinded measurement-audit receipt.

No construct-specific lexicon, model output text, condition label, or private
mapping is read. This validates accounting and schema controls only; it cannot
establish semantic or human validity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def fail(message: str) -> None:
    raise ValueError(f"RULE_ANCHOR_FAILED: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--subset-manifest", type=Path, required=True)
    parser.add_argument("--measurement-audit-dir", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("output directory already exists")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    subset = json.loads(args.subset_manifest.read_text(encoding="utf-8"))
    audit_manifest_path = args.measurement_audit_dir / "AUDIT_MANIFEST.json"
    metrics_path = args.measurement_audit_dir / "blinded_measurement_audit_metrics.csv"
    if not audit_manifest_path.is_file() or not metrics_path.is_file():
        fail("required blinded audit artifacts are unavailable")
    audit_manifest = json.loads(audit_manifest_path.read_text(encoding="utf-8"))
    if config.get("status") != "FROZEN_BLINDED_PUBLIC_DATA_ONLY":
        fail("unexpected configuration status")
    if subset.get("condition_labels_exposed") is not False or audit_manifest.get("condition_labels_exposed") is not False:
        fail("a source artifact records condition exposure")
    if audit_manifest.get("status") != "BLINDED_COMPUTATIONAL_MEASUREMENT_AUDIT_COMPLETE":
        fail("measurement audit is not complete")
    metrics = pd.read_csv(metrics_path)
    required = {"metric_family", "judge_id", "construct"}
    if not required.issubset(metrics.columns):
        fail("audit metrics have incomplete schema")
    quality = metrics.loc[metrics.metric_family == "record_quality"].copy()
    if quality.empty:
        fail("record-quality metrics are absent")
    expected_judges = set(audit_manifest["judges"])
    expected_constructs = set(audit_manifest["constructs"])
    expected_rows = len(expected_judges) * len(expected_constructs) * 3
    if len(quality) != expected_rows:
        fail("record-quality metrics do not cover every judge/construct/set")
    flip = metrics.loc[metrics.metric_family == "label_flip_code_path"]
    if len(flip) != 1 or "control_pass" not in flip.columns or str(flip.iloc[0]["control_pass"]).casefold() != "true":
        fail("deterministic label-flip code-path control did not pass")

    records: list[dict[str, object]] = []
    for construct in sorted(expected_constructs):
        frame = quality.loc[quality.construct == construct]
        complete = len(frame) == len(expected_judges) * 3
        finite_rates = frame[["valid_record_rate", "abstention_rate", "technical_invalid_rate", "span_invalid_rate", "incoherent_rate"]].notna().all().all()
        records.append({
            "construct": construct,
            "anchor_complete_record_accounting": complete,
            "anchor_numeric_quality_fields_present": bool(finite_rates),
            "anchor_label_flip_code_path": True,
            "anchor_construct_specific_lexicon_used": False,
            "anchor_status": "PASS" if complete and finite_rates else "FAIL",
            "boundary": "Generic schema/accounting anchors only; no semantic or human-validity conclusion.",
        })
    args.outdir.mkdir(parents=True, exist_ok=False)
    out = pd.DataFrame(records)
    out.to_csv(args.outdir / "blinded_rule_anchor_summary.csv", index=False)
    manifest = {
        "status": "BLINDED_RULE_ANCHORS_COMPLETE",
        "condition_labels_exposed": False,
        "construct_specific_lexicon_used": False,
        "source_sha256": {"config": sha256(args.config), "subset_manifest": sha256(args.subset_manifest), "audit_metrics": sha256(metrics_path)},
        "interpretation_boundary": "Generic code-path and accounting anchors; not semantic validation or human grounding.",
    }
    (args.outdir / "RULE_ANCHOR_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "condition_labels_exposed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
