"""Freeze the blinded public-data computational measurement dataset.

This gate may run only after the frozen synthetic panel, blind technical
robustness checks, construct-strength decisions, and public-human calibration
receipt all exist.  It byte-commits (but never parses) the private condition
map so that the later single authorized analysis cannot substitute another
mapping.  Its role is provenance closure, not statistical analysis.
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
DEFAULT_MAPPING_COMMITMENT = ROOT / "annotation_public" / "private" / "blinding_map_primary_v1.csv"
DEFAULT_OUTPUT_MANIFEST = ROOT / "data" / "model_outputs" / "OUTPUT_MANIFEST.csv"
DEFAULT_OUTPUT_CHECKSUMS = ROOT / "data" / "model_outputs" / "CHECKSUMS.csv"
DEFAULT_OUTPUTS = ROOT / "data" / "model_outputs" / "validated" / "primary_model_outputs.csv"
DEFAULT_ANALYSIS_CONFIG = ROOT / "config" / "post_freeze_analysis_v1.json"
DEFAULT_ANALYSIS_SCRIPT = ROOT / "code" / "27_run_post_freeze_public_analysis.py"
DEFAULT_RQ4_SCRIPT = ROOT / "code" / "28_run_representational_space_analysis.py"
DEFAULT_RESULTS_FREEZE_SCRIPT = ROOT / "code" / "29_freeze_public_data_results.py"
DEFAULT_FIGURE_SCRIPT = ROOT / "code" / "30_generate_public_data_figures.py"
DEFAULT_SAMPLE = ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv"
DEFAULT_CAPTIONS = ROOT / "data" / "public_reference" / "processed" / "vizwiz_captions_val.csv"
DEFAULT_DREAMS = ROOT / "data" / "dreambank" / "processed" / "dream_reports.csv"
DEFAULT_INTENT = ROOT / "data" / "ai_sensory" / "processed" / "corpus_items.csv"
DEFAULT_LEXICAL_CODEBOOK = ROOT / "code" / "04_apply_codebook.py"
DEFAULT_BLINDED_PACKET = ROOT / "annotation_public" / "private" / "blinded_packet_primary_v1.csv"


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


def require_hash(receipt: dict[str, Any], field: str, path: Path, context: str) -> None:
    """Fail closed when a receipt's committed source no longer matches bytes."""
    expected = receipt.get(field)
    if not expected:
        fail(f"{context} does not commit {field}")
    actual = sha256(path)
    if actual != expected:
        fail(f"{context} hash mismatch for {path.name}")


def verify_panel_chain(panel: dict[str, Any], panel_dir: Path, manifest: pd.DataFrame) -> None:
    """Verify freeze receipt -> manifest -> every raw/label artifact chain."""
    manifest_path = panel_dir / "synthetic_panel_manifest.csv"
    checksums_path = panel_dir / "synthetic_panel_checksums.csv"
    disagreement_path = panel_dir / "blinded_disagreement_map.csv"
    require_hash(panel, "manifest_sha256", manifest_path, "panel freeze")
    require_hash(panel, "checksums_sha256", checksums_path, "panel freeze")
    require_hash(panel, "disagreement_map_sha256", disagreement_path, "panel freeze")
    checksums = pd.read_csv(checksums_path, dtype=str, keep_default_na=False)
    if not {"artifact", "path", "sha256"}.issubset(checksums.columns) or checksums.artifact.duplicated().any():
        fail("panel checksum ledger schema is incomplete")
    for artifact, path in {
        "manifest": manifest_path,
        "blinded_disagreement_map": disagreement_path,
    }.items():
        row = checksums.loc[checksums.artifact == artifact]
        if len(row) != 1 or str(row.iloc[0]["sha256"]) != sha256(path):
            fail(f"panel checksum ledger does not match {artifact}")
    # The immutable receipt and its ledgers live in ``synthetic_panel_v1/freeze``
    # while the frozen raw and parsed judge artifacts live alongside that
    # directory in ``synthetic_panel_v1``.  Requiring artifacts to be inside the
    # receipt directory would reject the canonical panel layout that the freeze
    # itself hashed.  Still require the one permitted parent directory; never
    # accept an arbitrary absolute path from the manifest.
    artifact_dir = panel_dir.parent.resolve()
    for row in manifest.to_dict("records"):
        for name, hash_column in (("labels_path", "labels_sha256"), ("raw_path", "raw_sha256")):
            path = Path(str(row[name]))
            if path.resolve().parent != artifact_dir:
                fail(f"panel manifest artifact lies outside the frozen panel directory: {row.get('judge_id')} {name}")
            if not path.is_file() or sha256(path) != str(row[hash_column]):
                fail(f"panel manifest hash mismatch for {row.get('judge_id')} {name}")
            artifact = f"{row['judge_id']}_{'labels' if name == 'labels_path' else 'raw'}"
            ledger_row = checksums.loc[checksums.artifact == artifact]
            if len(ledger_row) != 1 or str(ledger_row.iloc[0]["sha256"]) != sha256(path):
                fail(f"panel checksum ledger does not match {artifact}")


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
    parser.add_argument("--mapping-commitment", type=Path, default=DEFAULT_MAPPING_COMMITMENT,
                        help="Private map byte-hashed only; its contents are not parsed at this blinded gate.")
    parser.add_argument("--primary-output-manifest", type=Path, default=DEFAULT_OUTPUT_MANIFEST)
    parser.add_argument("--primary-output-checksums", type=Path, default=DEFAULT_OUTPUT_CHECKSUMS)
    parser.add_argument("--primary-outputs", type=Path, default=DEFAULT_OUTPUTS)
    parser.add_argument("--analysis-config", type=Path, default=DEFAULT_ANALYSIS_CONFIG)
    parser.add_argument("--analysis-script", type=Path, default=DEFAULT_ANALYSIS_SCRIPT)
    parser.add_argument("--rq4-script", type=Path, default=DEFAULT_RQ4_SCRIPT)
    parser.add_argument("--results-freeze-script", type=Path, default=DEFAULT_RESULTS_FREEZE_SCRIPT)
    parser.add_argument("--figure-script", type=Path, default=DEFAULT_FIGURE_SCRIPT)
    parser.add_argument("--frozen-sample", type=Path, default=DEFAULT_SAMPLE)
    parser.add_argument("--captions", type=Path, default=DEFAULT_CAPTIONS)
    parser.add_argument("--dreams", type=Path, default=DEFAULT_DREAMS)
    parser.add_argument("--intent-corpus", type=Path, default=DEFAULT_INTENT)
    parser.add_argument("--lexical-codebook", type=Path, default=DEFAULT_LEXICAL_CODEBOOK)
    parser.add_argument("--blinded-packet", type=Path, default=DEFAULT_BLINDED_PACKET)
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
        "subset_checksums": args.subset_manifest.parent / "CHECKSUMS.csv",
        "disagreement_map": args.panel_freeze.parent / "blinded_disagreement_map.csv",
        "audit_metrics": args.measurement_audit_dir / "blinded_measurement_audit_metrics.csv",
        "rule_anchor_summary": args.rule_anchor_dir / "blinded_rule_anchor_summary.csv",
        "construct_strength": args.construct_strength_dir / "construct_measurement_strength.csv",
        "tier_matrix": args.tier_matrix,
        "calibration_matrix": args.calibration_matrix,
        "calibration_receipt": args.calibration_receipt,
        "mapping_commitment": args.mapping_commitment,
        "primary_output_manifest": args.primary_output_manifest,
        "primary_output_checksums": args.primary_output_checksums,
        "primary_outputs": args.primary_outputs,
        "analysis_config": args.analysis_config,
        "analysis_script": args.analysis_script,
        "rq4_script": args.rq4_script,
        "results_freeze_script": args.results_freeze_script,
        "figure_script": args.figure_script,
        "frozen_sample": args.frozen_sample,
        "captions": args.captions,
        "dreams": args.dreams,
        "intent_corpus": args.intent_corpus,
        "lexical_codebook": args.lexical_codebook,
        "blinded_packet": args.blinded_packet,
        "coded_data_freeze_script": Path(__file__).resolve(),
    }
    missing = [name for name, path in required_files.items() if not path.is_file()]
    if missing:
        fail(f"required file(s) unavailable: {', '.join(missing)}")

    panel_manifest = pd.read_csv(required_files["panel_manifest"], dtype=str, keep_default_na=False)
    if len(panel_manifest) < 2:
        fail("frozen panel manifest does not include multiple judges")
    if not {
        "judge_id", "label_rows", "distinct_blind_item_ids", "expected_label_rows",
        "labels_path", "labels_sha256", "raw_path", "raw_sha256",
    }.issubset(panel_manifest.columns):
        fail("frozen panel manifest schema is incomplete")
    if panel_manifest.judge_id.duplicated().any():
        fail("frozen panel manifest contains duplicate judge identities")
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
    verify_panel_chain(panel, args.panel_freeze.parent, panel_manifest)

    # Reconcile the nested blinded receipts before accepting the source files
    # they name. This is a provenance check only; it does not expose a
    # condition label or interpret model-output content.
    require_hash(subset["source"], "baseline_freeze_sha256", args.panel_freeze, "subset manifest source")
    require_hash(panel, "packet_sha256", args.blinded_packet, "panel freeze")
    blinded_packet = pd.read_csv(args.blinded_packet, dtype=str, keep_default_na=False)
    if not {"blind_item_id", "output_text"}.issubset(blinded_packet.columns):
        fail("frozen blinded packet schema is incomplete")
    if blinded_packet.blind_item_id.duplicated().any() or len(blinded_packet) != packet_rows:
        fail("frozen blinded packet does not cover the frozen panel exactly")
    if {"condition", "condition_label", "prompt_type", "treatment", "arm"}.intersection(blinded_packet.columns):
        fail("frozen blinded packet contains an unblinding field")
    subset_checksums = pd.read_csv(required_files["subset_checksums"], dtype=str, keep_default_na=False)
    if not {"artifact", "sha256"}.issubset(subset_checksums.columns) or subset_checksums.artifact.duplicated().any():
        fail("robustness-subset checksum ledger schema is incomplete")
    subset_receipt_row = subset_checksums.loc[subset_checksums.artifact == "subset_manifest"]
    if len(subset_receipt_row) != 1 or str(subset_receipt_row.iloc[0]["sha256"]) != sha256(args.subset_manifest):
        fail("robustness-subset checksum ledger does not match subset manifest")
    for artifact, digest in dict(subset.get("artifact_sha256", {})).items():
        row = subset_checksums.loc[subset_checksums.artifact == artifact]
        if len(row) != 1 or str(row.iloc[0]["sha256"]) != str(digest):
            fail(f"robustness-subset checksum ledger does not match {artifact}")
    audit_sources = audit.get("inputs_sha256", {})
    if audit_sources.get("subset_manifest") != sha256(args.subset_manifest):
        fail("measurement-audit subset-manifest hash does not match")
    if audit_sources.get("baseline_freeze") != sha256(args.panel_freeze):
        fail("measurement-audit panel-freeze hash does not match")
    anchor_sources = anchors.get("source_sha256", {})
    if anchor_sources.get("subset_manifest") != sha256(args.subset_manifest):
        fail("rule-anchor subset-manifest hash does not match")
    if anchor_sources.get("audit_metrics") != sha256(required_files["audit_metrics"]):
        fail("rule-anchor audit-metrics hash does not match")
    strength_sources = strength.get("source_sha256", {})
    if strength_sources.get("subset_manifest") != sha256(args.subset_manifest):
        fail("construct-strength subset-manifest hash does not match")
    if strength_sources.get("audit_metrics") != sha256(required_files["audit_metrics"]):
        fail("construct-strength audit-metrics hash does not match")
    if strength_sources.get("rule_anchor_summary") != sha256(required_files["rule_anchor_summary"]):
        fail("construct-strength rule-anchor hash does not match")
    if strength_sources.get("tier_matrix") != sha256(args.tier_matrix):
        fail("construct-strength tier-matrix hash does not match")
    if strength_sources.get("calibration_receipt") != sha256(args.calibration_receipt):
        fail("construct-strength calibration-receipt hash does not match")

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
    if tiers.duplicated(["construct", "measurement_layer"]).any() or construct_strength.duplicated(["construct", "measurement_layer"]).any():
        fail("tier or construct-strength table contains duplicate construct-layer keys")
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

    output_manifest = pd.read_csv(args.primary_output_manifest, dtype=str, keep_default_na=False)
    output_checksums = pd.read_csv(args.primary_output_checksums, dtype=str, keep_default_na=False)
    if not {"artifact", "sha256", "rows", "status"}.issubset(output_manifest.columns):
        fail("primary-output manifest schema is incomplete")
    target = output_manifest.loc[output_manifest["artifact"] == "validated/primary_model_outputs.csv"]
    if len(target) != 1 or str(target.iloc[0]["status"]) != "FROZEN":
        fail("primary-output manifest does not commit one frozen validated output table")
    if int(target.iloc[0]["rows"]) != 3000 or str(target.iloc[0]["sha256"]) != sha256(args.primary_outputs):
        fail("primary-output table does not match its frozen manifest")
    if not {"path", "algorithm", "checksum"}.issubset(output_checksums.columns):
        fail("primary-output checksum schema is incomplete")
    normalized_paths = output_checksums["path"].astype(str).str.replace("/", "\\", regex=False).str.casefold()
    target_path = str(args.primary_outputs.relative_to(ROOT)).replace("/", "\\").casefold()
    output_checksum_target = output_checksums.loc[normalized_paths == target_path]
    if (
        len(output_checksum_target) != 1
        or str(output_checksum_target.iloc[0]["algorithm"]).casefold() != "sha256"
        or str(output_checksum_target.iloc[0]["checksum"]) != sha256(args.primary_outputs)
    ):
        fail("primary-output checksum table does not match validated outputs")

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
        "coded_data_checksums_sha256": sha256(checksums_path),
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
