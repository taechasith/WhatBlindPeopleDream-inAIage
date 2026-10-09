"""Freeze blinded construct-strength decisions from predeclared technical rules.

This utility never accepts a condition map or model-output table. It consumes
only blinded construct-level quality metrics, generic rule anchors, the frozen
construct-tier matrix, and the public-source readiness receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TIER_MATRIX = ROOT / "CONSTRUCT_MEASUREMENT_TIER_MATRIX.csv"


def fail(message: str) -> None:
    raise ValueError(f"ROBUSTNESS_SUMMARY_FAILED: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def at_least(value: object, threshold: float) -> bool:
    return pd.notna(value) and float(value) >= threshold


def exactly(value: object, expected: float) -> bool:
    return pd.notna(value) and float(value) == expected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--subset-manifest", type=Path, required=True)
    parser.add_argument("--measurement-audit-dir", type=Path, required=True)
    parser.add_argument("--rule-anchor-dir", type=Path, required=True)
    parser.add_argument("--calibration-receipt", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("output directory already exists")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    subset = json.loads(args.subset_manifest.read_text(encoding="utf-8"))
    audit_manifest = json.loads((args.measurement_audit_dir / "AUDIT_MANIFEST.json").read_text(encoding="utf-8"))
    anchors_manifest = json.loads((args.rule_anchor_dir / "RULE_ANCHOR_MANIFEST.json").read_text(encoding="utf-8"))
    if any(record.get("condition_labels_exposed") is not False for record in (subset, audit_manifest, anchors_manifest)):
        fail("a source receipt records condition exposure")
    if audit_manifest.get("status") != "BLINDED_COMPUTATIONAL_MEASUREMENT_AUDIT_COMPLETE" or anchors_manifest.get("status") != "BLINDED_RULE_ANCHORS_COMPLETE":
        fail("required blinded audit or anchor receipt is incomplete")
    tiers = pd.read_csv(TIER_MATRIX, dtype=str, keep_default_na=False)
    metrics = pd.read_csv(args.measurement_audit_dir / "blinded_measurement_audit_metrics.csv")
    anchors = pd.read_csv(args.rule_anchor_dir / "blinded_rule_anchor_summary.csv")
    calibration = pd.read_csv(args.calibration_receipt, dtype=str, keep_default_na=False)
    if not {"construct", "measurement_layer", "prospective_tier", "proposed_measurement_status"}.issubset(tiers.columns):
        fail("construct-tier matrix has incomplete schema")
    if not {"construct", "anchor_status"}.issubset(anchors.columns):
        fail("rule-anchor summary has incomplete schema")
    if "provenance_validation_status" not in calibration.columns:
        fail("public-human calibration receipt has incomplete schema")
    if not (calibration.provenance_validation_status == "PASS").all():
        fail("public-human calibration receipt has failed provenance rows")

    thresholds = config["summary"]
    panel_constructs = set(audit_manifest["constructs"])
    judges = list(audit_manifest["judges"])
    primary_candidates = set(thresholds["primary_candidate_constructs"])
    rows: list[dict[str, object]] = []
    for tier in tiers.to_dict("records"):
        construct = tier["construct"]
        layer = tier["measurement_layer"]
        baseline = metrics.loc[(metrics.metric_family == "record_quality") & (metrics.measurement_set == "baseline") & (metrics.construct == construct)]
        para = metrics.loc[(metrics.metric_family == "prompt_paraphrase") & (metrics.construct == construct)]
        rerun = metrics.loc[(metrics.metric_family == "exact_rerun") & (metrics.construct == construct)]
        cross = metrics.loc[(metrics.metric_family == "cross_judge_baseline") & (metrics.construct == construct)]
        anchor = anchors.loc[anchors.construct == construct]
        audited_panel_construct = layer == "synthetic_panel" and construct in panel_constructs
        quality_pass = False
        primary_rule_pass = False
        reasons: list[str] = []
        if audited_panel_construct:
            if len(baseline) != len(judges):
                reasons.append("INCOMPLETE_BASELINE_JUDGE_COVERAGE")
            else:
                valid = baseline.valid_record_rate.map(lambda value: at_least(value, float(thresholds["minimum_valid_record_rate_per_judge"]))).all()
                spans = baseline.apply(lambda row: int(row.n_positive_labels) >= int(thresholds["minimum_positive_records_per_judge"]) and at_least(row.valid_positive_span_rate, float(thresholds["minimum_valid_positive_span_rate_per_judge"])), axis=1).all()
                quality_pass = bool(valid and spans)
                if not valid:
                    reasons.append("VALID_RECORD_RATE_BELOW_THRESHOLD")
                if not spans:
                    reasons.append("POSITIVE_SPAN_SUPPORT_BELOW_THRESHOLD_OR_TOO_RARE")
            prompt_ok = len(para) == len(judges) and para.apply(lambda row: int(row.n_binary_comparable) >= int(thresholds["minimum_comparable_binary_records"]) and at_least(row.binary_agreement, float(thresholds["minimum_prompt_paraphrase_binary_agreement"])) and (pd.isna(row.binary_flip_rate) or float(row.binary_flip_rate) <= float(thresholds["maximum_binary_flip_rate"])), axis=1).all()
            rerun_ok = len(rerun) == len(judges) and rerun.apply(lambda row: exactly(row.label_consistency, float(thresholds["exact_rerun_label_consistency_required"])), axis=1).all()
            cross_ok = len(cross) == 1 and int(cross.iloc[0].n_binary_comparable) >= int(thresholds["minimum_comparable_binary_records"]) and at_least(cross.iloc[0].binary_agreement, float(thresholds["minimum_cross_judge_binary_agreement"]))
            anchor_ok = len(anchor) == 1 and anchor.iloc[0].anchor_status == "PASS"
            if not prompt_ok:
                reasons.append("PROMPT_PARAPHRASE_STABILITY_INSUFFICIENT")
            if not rerun_ok:
                reasons.append("DETERMINISTIC_RERUN_INCONSISTENT")
            if not cross_ok:
                reasons.append("CROSS_JUDGE_AGREEMENT_INSUFFICIENT")
            if not anchor_ok:
                reasons.append("GENERIC_RULE_ANCHOR_FAILED")
            primary_rule_pass = bool(quality_pass and prompt_ok and rerun_ok and cross_ok and anchor_ok)
        else:
            reasons.append("NOT_AUDITED_BY_SYNTHETIC_PANEL_ROBUSTNESS_PROTOCOL")

        if tier["prospective_tier"] == "TIER_C":
            final_status = "MODEL_DERIVED_EXPLORATORY"
        elif tier["prospective_tier"] == "TIER_B":
            final_status = "PUBLIC_HUMAN_BENCHMARKED" if (not audited_panel_construct or primary_rule_pass or quality_pass) else "MEASUREMENT_UNSTABLE"
        elif tier["proposed_measurement_status"] == "COMPUTATIONAL_PRIMARY":
            final_status = "COMPUTATIONAL_PRIMARY" if primary_rule_pass else "MEASUREMENT_UNSTABLE"
        else:
            final_status = "COMPUTATIONAL_SECONDARY" if (not audited_panel_construct or quality_pass) else "MEASUREMENT_UNSTABLE"
        rows.append({
            "construct": construct,
            "measurement_layer": layer,
            "prospective_tier": tier["prospective_tier"],
            "proposed_measurement_status": tier["proposed_measurement_status"],
            "final_measurement_status": final_status,
            "audited_by_panel_robustness": audited_panel_construct,
            "primary_rule_pass": primary_rule_pass if audited_panel_construct else "NOT_APPLICABLE",
            "decision_reasons": ";".join(reasons) if reasons else "ALL_PREDECLARED_TECHNICAL_RULES_PASSED",
            "condition_labels_exposed": False,
            "claim_boundary": tier["claim_boundary"],
        })
    summary = pd.DataFrame(rows)
    args.outdir.mkdir(parents=True, exist_ok=False)
    summary.to_csv(args.outdir / "construct_measurement_strength.csv", index=False)
    metrics.to_csv(args.outdir / "computational_measurement_robustness.csv", index=False)
    manifest = {
        "status": "BLINDED_CONSTRUCT_MEASUREMENT_STRENGTH_FROZEN",
        "condition_labels_exposed": False,
        "construct_rows": len(summary),
        "status_counts": summary.final_measurement_status.value_counts().to_dict(),
        "source_sha256": {"config": sha256(args.config), "subset_manifest": sha256(args.subset_manifest), "tier_matrix": sha256(TIER_MATRIX), "audit_metrics": sha256(args.measurement_audit_dir / "blinded_measurement_audit_metrics.csv"), "rule_anchor_summary": sha256(args.rule_anchor_dir / "blinded_rule_anchor_summary.csv"), "calibration_receipt": sha256(args.calibration_receipt)},
        "interpretation_boundary": "Blinded construct-strength decision only; no condition effect, mapping exposure, human-equivalence claim, or unblinding authorization.",
    }
    (args.outdir / "CONSTRUCT_STRENGTH_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "condition_labels_exposed": False, "construct_rows": len(summary)}, sort_keys=True))


if __name__ == "__main__":
    main()
