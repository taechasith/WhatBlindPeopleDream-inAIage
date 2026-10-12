"""Run the predeclared public-data analysis after the coded-data freeze.

This is the only analysis utility in this version that accepts the private
condition mapping. It fail-closes unless the public-data computational
measurement gate is frozen. It reports synthetic judges separately and treats
released human answers/captions as bounded reference material only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_UNBLINDING_LEDGER = ROOT / "results" / "UNBLINDING_LEDGER_v1.json"
TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")
UNANSWERABLE_PHRASES = (
    "cannot determine", "can't determine", "can not determine", "unable to determine",
    "cannot tell", "can't tell", "not clear", "unclear", "cannot see", "can't see",
    "not visible", "not enough information", "unable to identify",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"POST_FREEZE_ANALYSIS_FAILED: {message}")


def normalize(text: object) -> str:
    return " ".join(TOKEN_RE.findall(str(text).casefold()))


def token_set(text: object) -> set[str]:
    return set(TOKEN_RE.findall(str(text).casefold()))


def max_token_f1(output: object, references: Iterable[object]) -> float:
    output_tokens = token_set(output)
    if not output_tokens:
        return 0.0
    best = 0.0
    for reference in references:
        reference_tokens = token_set(reference)
        if not reference_tokens:
            continue
        overlap = len(output_tokens & reference_tokens)
        if not overlap:
            continue
        precision = overlap / len(output_tokens)
        recall = overlap / len(reference_tokens)
        best = max(best, 2 * precision * recall / (precision + recall))
    return best


def parsed_answer_mode_covered(row: pd.Series) -> int:
    output = normalize(row.output_text)
    if str(row.answerable) == "0":
        return int(any(phrase in output for phrase in UNANSWERABLE_PHRASES))
    answer = normalize(row.human_answer_mode)
    return int(bool(answer) and answer in output)


def paired_statistics(frame: pd.DataFrame, numerator: str, denominator: str, value: str, seed: int, bootstrap: int, permutations: int, expected_items: int) -> dict[str, object]:
    pivot = frame.pivot(index="sample_row_id", columns="condition", values=value)
    if numerator not in pivot or denominator not in pivot:
        return {"n_paired_items": 0, "paired_coverage": 0.0, "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "permutation_p": np.nan, "analysis_status": "NOT_ESTIMABLE_MISSING_PAIRED_VALUES"}
    paired = pivot[[numerator, denominator]].dropna()
    if paired.empty:
        return {"n_paired_items": 0, "paired_coverage": 0.0, "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "permutation_p": np.nan, "analysis_status": "NOT_ESTIMABLE_NO_PAIRED_VALUES"}
    differences = (paired[numerator].astype(float) - paired[denominator].astype(float)).to_numpy()
    rng = np.random.default_rng(seed)
    n = len(differences)
    indices = rng.integers(0, n, size=(bootstrap, n))
    estimates = differences[indices].mean(axis=1)
    signs = rng.choice(np.array([-1.0, 1.0]), size=(permutations, n))
    null = (signs * differences).mean(axis=1)
    return {
        "n_paired_items": int(n),
        "effect": float(differences.mean()),
        "ci_low": float(np.quantile(estimates, 0.025)),
        "ci_high": float(np.quantile(estimates, 0.975)),
        "permutation_p": float((1 + np.sum(np.abs(null) >= abs(differences.mean()))) / (1 + permutations)),
        "paired_coverage": float(n / expected_items),
        "analysis_status": "ESTIMATED_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP" if n == expected_items else "ESTIMATED_COMPLETE_CASE_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP",
    }


def benjamini_hochberg(values: pd.Series) -> pd.Series:
    result = pd.Series(np.nan, index=values.index, dtype=float)
    usable = values.dropna().sort_values()
    if usable.empty:
        return result
    m = len(usable)
    adjusted = np.minimum.accumulate((usable.to_numpy() * m / np.arange(1, m + 1))[::-1])[::-1]
    result.loc[usable.index] = np.minimum(adjusted, 1.0)
    return result


def require_freeze(path: Path, expected_status: str) -> dict[str, object]:
    if not path.is_file():
        fail(f"missing required receipt: {path}")
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("status") != expected_status:
        fail(f"coded-data receipt does not authorize unblinding: {record.get('status')!r}")
    if record.get("condition_labels_exposed") is not False:
        fail("coded-data receipt records pre-analysis condition exposure")
    if record.get("new_human_data_collected") is not False:
        fail("current study unexpectedly records new human data")
    return record


def load_committed_sources(
    freeze_path: Path,
    freeze: dict[str, object],
    recovery: dict[str, object] | None = None,
) -> dict[str, tuple[Path, str]]:
    """Validate every byte-level source commitment from the blinded freeze."""
    checksum_path = freeze_path.parent / "CODED_DATA_CHECKSUMS.csv"
    if not checksum_path.is_file() or freeze.get("coded_data_checksums_sha256") != sha256(checksum_path):
        fail("coded-data checksum ledger is absent or does not match the freeze receipt")
    checksums = pd.read_csv(checksum_path, dtype=str, keep_default_na=False)
    if not {"artifact", "path", "sha256"}.issubset(checksums.columns) or checksums.artifact.duplicated().any():
        fail("coded-data checksum ledger schema is incomplete")
    committed: dict[str, tuple[Path, str]] = {}
    for row in checksums.to_dict("records"):
        path = Path(str(row["path"]))
        expected = str(row["sha256"])
        actual = sha256(path) if path.is_file() else ""
        permitted_recovery = (
            recovery is not None
            and str(row["artifact"]) == "analysis_script"
            and expected == str(recovery["original_analysis_script_sha256"])
            and actual == str(recovery["replacement_analysis_script_sha256"])
        )
        if not path.is_file() or (actual != expected and not permitted_recovery):
            fail(f"committed source is missing or changed: {row['artifact']}")
        committed[str(row["artifact"])] = (path, actual if permitted_recovery else expected)
    for name, expected in dict(freeze.get("source_checksums", {})).items():
        permitted_recovery = (
            recovery is not None
            and name == "analysis_script"
            and str(expected) == str(recovery["original_analysis_script_sha256"])
            and committed.get(name, (None, None))[1] == str(recovery["replacement_analysis_script_sha256"])
        )
        if name not in committed or (committed[name][1] != str(expected) and not permitted_recovery):
            fail(f"freeze source commitment is incomplete or inconsistent: {name}")
    return committed


def load_technical_recovery(path: Path | None, *, freeze_path: Path, script: Path) -> dict[str, object] | None:
    if path is None:
        return None
    if not path.is_file():
        fail("technical recovery receipt is unavailable")
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("status") != "TECHNICAL_RECOVERY_AUTHORIZED_PRE_RESULT_ONLY":
        fail("technical recovery receipt has an invalid status")
    if record.get("condition_effects_estimated_before_recovery") is not False:
        fail("technical recovery receipt does not establish a pre-result failure")
    if record.get("original_coded_data_freeze_sha256") != sha256(freeze_path):
        fail("technical recovery receipt does not match coded-data freeze")
    if record.get("replacement_analysis_script_sha256") != sha256(script):
        fail("technical recovery receipt does not match current analysis script")
    return record


def require_committed_path(committed: dict[str, tuple[Path, str]], name: str, supplied: Path) -> None:
    if name not in committed:
        fail(f"coded-data freeze lacks commitment for {name}")
    committed_path, committed_hash = committed[name]
    if supplied.resolve() != committed_path.resolve() or sha256(supplied) != committed_hash:
        fail(f"supplied {name} does not match its pre-unblinding commitment")


def create_unblinding_ledger(path: Path, *, freeze_path: Path, mapping: Path, config: Path) -> Path | None:
    """Record initial map access or a hash-bound technical recovery.

    A recovery is permitted only when a prior authorized run wrote its started
    ledger but failed before results/completion existed.  It is deliberately
    explicit because the map will be read again from the same committed bytes;
    it is not represented as a fresh blinded analysis or a second experiment.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    receipt = {
        "status": "UNBLINDING_STARTED_PUBLIC_DATA_ONLY",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "coded_data_freeze_sha256": sha256(freeze_path),
        "mapping_sha256": sha256(mapping),
        "analysis_config_sha256": sha256(config),
        "condition_map_interpretation_authorized": "ONE_PRESPECIFIED_ANALYSIS_RUN",
        "new_human_data_collected": False,
    }
    try:
        with path.open("x", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        return None
    except FileExistsError:
        existing = json.loads(path.read_text(encoding="utf-8"))
        expected = {
            "status": "UNBLINDING_STARTED_PUBLIC_DATA_ONLY",
            "coded_data_freeze_sha256": sha256(freeze_path),
            "mapping_sha256": sha256(mapping),
            "analysis_config_sha256": sha256(config),
        }
        if any(existing.get(key) != value for key, value in expected.items()):
            raise ValueError("POST_FREEZE_ANALYSIS_FAILED: existing unblinding ledger is incompatible with this recovery")
        completion = path.with_name("UNBLINDING_COMPLETED_v1.json")
        recovery = path.with_name("UNBLINDING_TECHNICAL_RECOVERY_v1.json")
        if completion.exists():
            raise ValueError("POST_FREEZE_ANALYSIS_FAILED: completed unblinding cannot be rerun")
        recovery_record = {
            "status": "UNBLINDING_TECHNICAL_RECOVERY_AUTHORIZED",
            "reason": "The initial authorized run failed before result creation during a pre-analysis provenance-path check.",
            "initial_ledger_sha256": sha256(path),
            "coded_data_freeze_sha256": sha256(freeze_path),
            "mapping_sha256": sha256(mapping),
            "analysis_config_sha256": sha256(config),
            "condition_effects_estimated_before_recovery": False,
            "new_human_data_collected": False,
        }
        try:
            with recovery.open("x", encoding="utf-8") as stream:
                json.dump(recovery_record, stream, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
        except FileExistsError:
            prior = json.loads(recovery.read_text(encoding="utf-8"))
            if prior != recovery_record:
                raise ValueError("POST_FREEZE_ANALYSIS_FAILED: existing recovery receipt is incompatible")
        return recovery


def validate_frozen_labels(panel_manifest: pd.DataFrame, mapping_ids: set[str], constructs: set[str], judges: set[str]) -> pd.DataFrame:
    """Load exactly the label artifacts committed by the blinded panel freeze."""
    expected_keys = {(blind_id, construct) for blind_id in mapping_ids for construct in constructs}
    tables: list[pd.DataFrame] = []
    if set(panel_manifest.judge_id.astype(str)) != judges:
        fail("panel manifest judge set differs from coded-data freeze")
    for receipt in panel_manifest.to_dict("records"):
        labels_path = Path(str(receipt["labels_path"]))
        if not labels_path.is_file() or sha256(labels_path) != str(receipt["labels_sha256"]):
            fail(f"frozen label artifact changed: {receipt['judge_id']}")
        labels = pd.read_csv(labels_path, dtype=str, keep_default_na=False)
        required = {"blind_item_id", "judge_id", "construct", "label", "abstain", "parser_status"}
        if not required.issubset(labels.columns) or len(labels) != int(receipt["expected_label_rows"]):
            fail(f"frozen label schema or row count invalid: {receipt['judge_id']}")
        if set(labels.judge_id.astype(str)) != {str(receipt["judge_id"])}:
            fail(f"frozen label judge identity invalid: {receipt['judge_id']}")
        keys = list(zip(labels.blind_item_id.astype(str), labels.construct.astype(str)))
        if len(keys) != len(set(keys)) or set(keys) != expected_keys:
            fail(f"frozen label coverage is incomplete or duplicated: {receipt['judge_id']}")
        tables.append(labels[list(required)].copy())
    combined = pd.concat(tables, ignore_index=True)
    expected_total = len(judges) * len(expected_keys)
    if len(combined) != expected_total:
        fail("combined frozen label coverage is incomplete")
    return combined


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "post_freeze_analysis_v1.json")
    parser.add_argument("--coded-data-freeze", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--outputs", type=Path, default=ROOT / "data" / "model_outputs" / "validated" / "primary_model_outputs.csv")
    parser.add_argument("--sample", type=Path, default=ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv")
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument("--construct-strength", type=Path, required=True)
    parser.add_argument("--technical-recovery", type=Path, default=None,
                        help="Immutable pre-result recovery authorization, if an authorized run failed before result creation.")
    parser.add_argument("--captions", type=Path, default=ROOT / "data" / "public_reference" / "processed" / "vizwiz_captions_val.csv")
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite a frozen post-unblinding analysis directory")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("status") != "FROZEN_PRE_UNBLINDING":
        fail("analysis configuration is not frozen before unblinding")
    freeze = require_freeze(args.coded_data_freeze, config["authorization"]["required_coded_data_status"])
    for source in (args.mapping, args.outputs, args.sample, args.captions, args.construct_strength):
        if not source.is_file():
            fail(f"required input unavailable: {source}")
    recovery = load_technical_recovery(args.technical_recovery, freeze_path=args.coded_data_freeze, script=Path(__file__).resolve())
    committed = load_committed_sources(args.coded_data_freeze, freeze, recovery)
    for name, source in {
        "mapping_commitment": args.mapping,
        "primary_outputs": args.outputs,
        "frozen_sample": args.sample,
        "captions": args.captions,
        "construct_strength": args.construct_strength,
        "analysis_config": args.config,
        "analysis_script": Path(__file__).resolve(),
    }.items():
        require_committed_path(committed, name, source)

    # Validate every non-private source and the canonical frozen-panel location
    # before recording or parsing the condition-bearing map.
    panel_manifest_path, _ = committed["panel_manifest"]
    if args.panel_dir.resolve() != panel_manifest_path.parent.parent.resolve():
        fail("supplied panel directory differs from the frozen panel commitment")

    # The ledger is created only after source-byte commitments and all
    # non-private path checks are verified, but before the condition-bearing map
    # is parsed. A narrowly logged recovery is permitted only for an earlier
    # authorized attempt that failed before any result creation.
    unblinding_ledger = DEFAULT_UNBLINDING_LEDGER
    recovery_receipt = create_unblinding_ledger(unblinding_ledger, freeze_path=args.coded_data_freeze, mapping=args.mapping, config=args.config)
    # Check the private bytes once more immediately before its one authorized parse.
    require_committed_path(committed, "mapping_commitment", args.mapping)

    mapping = pd.read_csv(args.mapping, dtype=str, keep_default_na=False)
    outputs = pd.read_csv(args.outputs, dtype=str, keep_default_na=False)
    sample = pd.read_csv(args.sample, dtype=str, keep_default_na=False)
    captions = pd.read_csv(args.captions, dtype=str, keep_default_na=False)
    strengths = pd.read_csv(args.construct_strength, dtype=str, keep_default_na=False)
    expected_conditions = list(config["design"]["expected_conditions"])
    mapping_required = {"blind_item_id", "sample_row_id", "model_id", "condition"}
    output_required = {"sample_row_id", "model_id", "condition", "output_text"}
    sample_required = {"sample_row_id", "image_filename", "answerable", "human_answer_mode"}
    if not mapping_required.issubset(mapping.columns) or not output_required.issubset(outputs.columns) or not sample_required.issubset(sample.columns):
        fail("unblinding/source table schema is incomplete")
    if mapping.duplicated(["blind_item_id"]).any() or mapping.duplicated(["sample_row_id", "model_id", "condition"]).any():
        fail("private mapping is not one-to-one")
    if len(mapping) != int(config["design"]["expected_primary_outputs"]):
        fail("private mapping does not cover the frozen output design")
    if set(mapping.condition) != set(expected_conditions):
        fail("mapping condition set does not match the frozen plan")
    expected_items = int(config["design"]["expected_items"])
    if mapping.sample_row_id.nunique() != expected_items or len(mapping) != expected_items * len(expected_conditions):
        fail("private mapping does not preserve the frozen repeated-measures item count")
    conditions_by_item = mapping.groupby("sample_row_id", observed=True).condition.agg(lambda values: set(values))
    models_by_item = mapping.groupby("sample_row_id", observed=True).model_id.nunique()
    rows_by_item = mapping.groupby("sample_row_id", observed=True).size()
    if not (conditions_by_item == set(expected_conditions)).all() or not (rows_by_item == len(expected_conditions)).all() or not (models_by_item == 1).all():
        fail("private mapping does not contain exactly one frozen condition and model per item")
    if outputs.duplicated(["sample_row_id", "model_id", "condition"]).any() or len(outputs) != len(mapping):
        fail("validated output table does not match the frozen primary design")
    unblinded = mapping.merge(outputs[["sample_row_id", "model_id", "condition", "output_text"]], on=["sample_row_id", "model_id", "condition"], how="inner", validate="one_to_one")
    if len(unblinded) != len(mapping):
        fail("mapping/output join has missing or unmatched frozen rows")

    packet_path, _ = committed["blinded_packet"]
    blinded_packet = pd.read_csv(packet_path, dtype=str, keep_default_na=False)
    if not {"blind_item_id", "output_text"}.issubset(blinded_packet.columns) or blinded_packet.blind_item_id.duplicated().any():
        fail("frozen blinded packet schema is invalid")
    packet_projection = blinded_packet[["blind_item_id", "output_text"]].copy()
    joined_projection = unblinded[["blind_item_id", "output_text"]].copy()
    verified_packet_join = joined_projection.merge(packet_projection, on="blind_item_id", how="inner", suffixes=("_unblinded", "_packet"), validate="one_to_one")
    if len(verified_packet_join) != len(unblinded) or not (verified_packet_join.output_text_unblinded == verified_packet_join.output_text_packet).all():
        fail("unblinded mapping/output association does not exactly match the frozen blinded packet")
    unblinded = unblinded.merge(sample[["sample_row_id", "image_filename", "answerable", "human_answer_mode"]], on="sample_row_id", how="inner", validate="many_to_one")
    if len(unblinded) != len(mapping):
        fail("frozen sample join is incomplete")

    caption_groups = captions.groupby("image_filename", observed=True)["caption_text"].apply(list).to_dict()
    if not set(unblinded.image_filename).issubset(caption_groups):
        fail("released caption reference does not cover every frozen sample image")
    unblinded["human_answer_mode_string_coverage"] = unblinded.apply(parsed_answer_mode_covered, axis=1)
    unblinded["human_caption_max_token_f1"] = unblinded.apply(lambda row: max_token_f1(row.output_text, caption_groups.get(row.image_filename, [])), axis=1)

    panel_manifest = pd.read_csv(panel_manifest_path, dtype=str, keep_default_na=False)
    panel_receipt_path, _ = committed["panel_freeze"]
    panel_receipt = json.loads(panel_receipt_path.read_text(encoding="utf-8"))
    if set(panel_manifest.judge_id.astype(str)) != set(map(str, panel_receipt["judge_ids"])):
        fail("panel manifest and panel-freeze judge identities disagree")
    labels = validate_frozen_labels(
        panel_manifest,
        set(mapping.blind_item_id.astype(str)),
        set(map(str, panel_receipt["constructs"])),
        set(map(str, panel_receipt["judge_ids"])),
    )
    labels["eligible_binary"] = (labels.parser_status == config["measurement"]["synthetic_label_eligibility"]["parser_status"]) & (labels.abstain.str.casefold() == "false") & labels.label.isin(config["measurement"]["synthetic_label_eligibility"]["label_values"])
    labels["value"] = pd.to_numeric(labels.label.where(labels.eligible_binary), errors="coerce")
    labels = labels.merge(unblinded[["blind_item_id", "sample_row_id", "model_id", "condition"]], on="blind_item_id", how="inner", validate="many_to_one")
    eligibility = (
        labels.groupby(["judge_id", "construct", "condition"], observed=True)
        .agg(n_label_records=("blind_item_id", "size"), n_eligible_binary=("eligible_binary", "sum"))
        .reset_index()
    )
    eligibility["n_noneligible"] = eligibility["n_label_records"] - eligibility["n_eligible_binary"]
    eligibility["eligible_rate"] = eligibility["n_eligible_binary"] / eligibility["n_label_records"]
    panel_constructs = set(labels.construct)
    strength = strengths.loc[strengths.measurement_layer == "synthetic_panel", ["construct", "final_measurement_status", "claim_boundary"]].copy()
    if set(strength.construct) != panel_constructs:
        fail("construct-strength table does not cover frozen panel constructs exactly")
    labels = labels.merge(strength, on="construct", how="left", validate="many_to_one")

    inference = config["inference"]
    contrasts = config["design"]["contrasts"]
    synthetic_rows: list[dict[str, object]] = []
    for (judge_id, construct), group in labels.groupby(["judge_id", "construct"], observed=True):
        status = str(group.final_measurement_status.iloc[0])
        for contrast_index, contrast in enumerate(contrasts):
            stats = paired_statistics(group.loc[group.eligible_binary], contrast["numerator"], contrast["denominator"], "value", int(inference["seed"]) + contrast_index, int(inference["bootstrap_repetitions"]), int(inference["permutation_repetitions"]), int(config["design"]["expected_items"]))
            synthetic_rows.append({"judge_id": judge_id, "construct": construct, "measurement_status": status, "contrast": contrast["id"], **stats})
    rq2 = pd.DataFrame(synthetic_rows)
    primary = set(config["measurement"]["primary_family"])
    rq2["primary_family"] = rq2.construct.isin(primary)
    rq2["fdr_q"] = np.nan
    for (judge, contrast), index in rq2.loc[rq2.primary_family].groupby(["judge_id", "contrast"], observed=True).groups.items():
        rq2.loc[index, "fdr_q"] = benjamini_hochberg(rq2.loc[index, "permutation_p"])
    rq2["analysis_role"] = np.select(
        [rq2.measurement_status.isin(config["reporting"]["confirmatory_statuses"]), rq2.measurement_status.isin(config["reporting"]["secondary_statuses"]), rq2.measurement_status.isin(config["reporting"]["exploratory_statuses"])],
        ["CONFIRMATORY_COMPUTATIONAL", "COMPUTATIONAL_SECONDARY", "MODEL_DERIVED_EXPLORATORY"],
        default="MEASUREMENT_UNSTABLE_NOT_FOR_SUBSTANTIVE_CLAIMS",
    )
    rq2.loc[rq2.analysis_status.astype(str).str.startswith("NOT_ESTIMABLE"), "analysis_role"] = "NOT_ESTIMABLE_NOT_FOR_SUBSTANTIVE_CLAIMS"
    rq5 = rq2.copy()
    rq5["output_change_direction"] = np.select(
        [rq5.effect.isna(), rq5.effect > 0, rq5.effect < 0],
        ["NOT_ESTIMABLE", "NUMERATOR_ADDED_RELATIVE_TO_DENOMINATOR", "NUMERATOR_OMITTED_RELATIVE_TO_DENOMINATOR"],
        default="NO_ESTIMATED_DIFFERENCE",
    )

    rq3_rows: list[dict[str, object]] = []
    for metric_index, metric in enumerate(config["measurement"]["human_reference_metrics"]):
        for contrast_index, contrast in enumerate(contrasts):
            stats = paired_statistics(unblinded, contrast["numerator"], contrast["denominator"], metric, int(inference["seed"]) + 100 + metric_index * 10 + contrast_index, int(inference["bootstrap_repetitions"]), int(inference["permutation_repetitions"]), int(config["design"]["expected_items"]))
            rq3_rows.append({"metric": metric, "contrast": contrast["id"], "measurement_status": "PUBLIC_HUMAN_BENCHMARKED", "claim_boundary": config["measurement"]["human_reference_boundary"], **stats})
    rq3 = pd.DataFrame(rq3_rows)
    rq3["fdr_q"] = benjamini_hochberg(rq3.permutation_p)

    args.outdir.mkdir(parents=True, exist_ok=False)
    rq2.to_csv(args.outdir / "RQ2_results.csv", index=False)
    rq3.to_csv(args.outdir / "RQ3_results.csv", index=False)
    rq5.to_csv(args.outdir / "RQ5_results.csv", index=False)
    eligibility.to_csv(args.outdir / "SYNTHETIC_MEASUREMENT_MISSINGNESS.csv", index=False)
    private_metrics_path = args.outdir / "private_human_reference_metrics.csv"
    unblinded[["sample_row_id", "model_id", "condition", "human_answer_mode_string_coverage", "human_caption_max_token_f1"]].to_csv(private_metrics_path, index=False)
    checksum_artifacts = ["config", "coded_data_freeze", "mapping", "outputs", "sample", "captions", "construct_strength", "unblinding_ledger"]
    checksum_values = [sha256(args.config), sha256(args.coded_data_freeze), sha256(args.mapping), sha256(args.outputs), sha256(args.sample), sha256(args.captions), sha256(args.construct_strength), sha256(unblinding_ledger)]
    if recovery_receipt is not None:
        checksum_artifacts.append("unblinding_technical_recovery")
        checksum_values.append(sha256(recovery_receipt))
    checksum_artifacts += ["RQ2_results", "RQ3_results", "RQ5_results", "measurement_missingness", "private_human_reference_metrics"]
    checksum_values += [sha256(args.outdir / "RQ2_results.csv"), sha256(args.outdir / "RQ3_results.csv"), sha256(args.outdir / "RQ5_results.csv"), sha256(args.outdir / "SYNTHETIC_MEASUREMENT_MISSINGNESS.csv"), sha256(private_metrics_path)]
    analysis_checksums = pd.DataFrame({"artifact": checksum_artifacts, "sha256": checksum_values})
    checksums_path = args.outdir / "ANALYSIS_CHECKSUMS.csv"
    analysis_checksums.to_csv(checksums_path, index=False)
    completion_path = unblinding_ledger.with_name("UNBLINDING_COMPLETED_v1.json")
    completion = {
        "status": "UNBLINDING_COMPLETED_PUBLIC_DATA_ONLY",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "started_ledger_sha256": sha256(unblinding_ledger),
        "analysis_directory": str(args.outdir),
        "analysis_checksums_sha256": sha256(checksums_path),
        "result_sha256": {"RQ2": sha256(args.outdir / "RQ2_results.csv"), "RQ3": sha256(args.outdir / "RQ3_results.csv"), "RQ5": sha256(args.outdir / "RQ5_results.csv")},
    }
    try:
        with completion_path.open("x", encoding="utf-8") as stream:
            json.dump(completion, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError as exc:
        raise ValueError("POST_FREEZE_ANALYSIS_FAILED: an unblinding completion receipt already exists") from exc
    manifest = {
        "status": "RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY",
        "condition_unblinded_once": True,
        "new_human_data_collected": False,
        "alt_test_current_study": "NOT_APPLICABLE_TO_CURRENT_DESIGN",
        "frozen_coded_data_status": freeze["status"],
        "primary_outputs": len(unblinded),
        "synthetic_label_rows": len(labels),
        "judges": sorted(labels.judge_id.unique().tolist()),
        "unblinding_ledger": str(unblinding_ledger),
        "unblinding_technical_recovery_receipt": str(recovery_receipt) if recovery_receipt is not None else None,
        "unblinding_completion_receipt": str(completion_path),
        "analysis_checksums_sha256": sha256(checksums_path),
        "analysis_boundary": "VLM-output effects and bounded human-reference alignment only; no human-equivalence or lived-experience inference.",
    }
    (args.outdir / "ANALYSIS_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
