"""Run the predeclared public-data analysis after the coded-data freeze.

This is the only analysis utility in this version that accepts the private
condition mapping. It fail-closes unless the public-data computational
measurement gate is frozen. It reports synthetic judges separately and treats
released human answers/captions as bounded reference material only.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
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


def paired_statistics(frame: pd.DataFrame, numerator: str, denominator: str, value: str, seed: int, bootstrap: int, permutations: int) -> dict[str, object]:
    pivot = frame.pivot(index="sample_row_id", columns="condition", values=value)
    if numerator not in pivot or denominator not in pivot:
        return {"n_paired_items": 0, "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "permutation_p": np.nan, "analysis_status": "NOT_ESTIMABLE_MISSING_PAIRED_VALUES"}
    paired = pivot[[numerator, denominator]].dropna()
    if paired.empty:
        return {"n_paired_items": 0, "effect": np.nan, "ci_low": np.nan, "ci_high": np.nan, "permutation_p": np.nan, "analysis_status": "NOT_ESTIMABLE_NO_PAIRED_VALUES"}
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
        "analysis_status": "ESTIMATED_PAIRED_CLUSTER_BOOTSTRAP_AND_SIGN_FLIP",
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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "post_freeze_analysis_v1.json")
    parser.add_argument("--coded-data-freeze", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--outputs", type=Path, default=ROOT / "data" / "model_outputs" / "validated" / "primary_model_outputs.csv")
    parser.add_argument("--sample", type=Path, default=ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv")
    parser.add_argument("--panel-dir", type=Path, required=True)
    parser.add_argument("--construct-strength", type=Path, required=True)
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
    if outputs.duplicated(["sample_row_id", "model_id", "condition"]).any() or len(outputs) != len(mapping):
        fail("validated output table does not match the frozen primary design")
    unblinded = mapping.merge(outputs[["sample_row_id", "model_id", "condition", "output_text"]], on=["sample_row_id", "model_id", "condition"], how="inner", validate="one_to_one")
    if len(unblinded) != len(mapping):
        fail("mapping/output join has missing or unmatched frozen rows")
    unblinded = unblinded.merge(sample[["sample_row_id", "image_filename", "answerable", "human_answer_mode"]], on="sample_row_id", how="inner", validate="many_to_one")
    if len(unblinded) != len(mapping):
        fail("frozen sample join is incomplete")

    caption_groups = captions.groupby("image_filename", observed=True)["caption_text"].apply(list).to_dict()
    unblinded["human_answer_mode_string_coverage"] = unblinded.apply(parsed_answer_mode_covered, axis=1)
    unblinded["human_caption_max_token_f1"] = unblinded.apply(lambda row: max_token_f1(row.output_text, caption_groups.get(row.image_filename, [])), axis=1)

    panel_files = sorted(args.panel_dir.glob("*_labels.csv"))
    if not panel_files:
        fail("no frozen synthetic-panel label files found")
    label_tables: list[pd.DataFrame] = []
    for path in panel_files:
        labels = pd.read_csv(path, dtype=str, keep_default_na=False)
        required = {"blind_item_id", "judge_id", "construct", "label", "abstain", "parser_status"}
        if not required.issubset(labels.columns):
            fail(f"synthetic label schema incomplete: {path.name}")
        label_tables.append(labels[list(required)].copy())
    labels = pd.concat(label_tables, ignore_index=True)
    labels["eligible_binary"] = (labels.parser_status == config["measurement"]["synthetic_label_eligibility"]["parser_status"]) & (labels.abstain.str.casefold() == "false") & labels.label.isin(config["measurement"]["synthetic_label_eligibility"]["label_values"])
    labels["value"] = pd.to_numeric(labels.label.where(labels.eligible_binary), errors="coerce")
    labels = labels.merge(unblinded[["blind_item_id", "sample_row_id", "model_id", "condition"]], on="blind_item_id", how="inner", validate="many_to_one")
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
            stats = paired_statistics(group.loc[group.eligible_binary], contrast["numerator"], contrast["denominator"], "value", int(inference["seed"]) + contrast_index, int(inference["bootstrap_repetitions"]), int(inference["permutation_repetitions"]))
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
    rq5 = rq2.copy()
    rq5["output_change_direction"] = np.where(rq5.effect > 0, "NUMERATOR_ADDED_RELATIVE_TO_DENOMINATOR", np.where(rq5.effect < 0, "NUMERATOR_OMITTED_RELATIVE_TO_DENOMINATOR", "NO_ESTIMATED_DIFFERENCE"))

    rq3_rows: list[dict[str, object]] = []
    for metric_index, metric in enumerate(config["measurement"]["human_reference_metrics"]):
        for contrast_index, contrast in enumerate(contrasts):
            stats = paired_statistics(unblinded, contrast["numerator"], contrast["denominator"], metric, int(inference["seed"]) + 100 + metric_index * 10 + contrast_index, int(inference["bootstrap_repetitions"]), int(inference["permutation_repetitions"]))
            rq3_rows.append({"metric": metric, "contrast": contrast["id"], "measurement_status": "PUBLIC_HUMAN_BENCHMARKED", "claim_boundary": config["measurement"]["human_reference_boundary"], **stats})
    rq3 = pd.DataFrame(rq3_rows)
    rq3["fdr_q"] = benjamini_hochberg(rq3.permutation_p)

    args.outdir.mkdir(parents=True, exist_ok=False)
    rq2.to_csv(args.outdir / "RQ2_results.csv", index=False)
    rq3.to_csv(args.outdir / "RQ3_results.csv", index=False)
    rq5.to_csv(args.outdir / "RQ5_results.csv", index=False)
    unblinded[["sample_row_id", "model_id", "condition", "human_answer_mode_string_coverage", "human_caption_max_token_f1"]].to_csv(args.outdir / "private_human_reference_metrics.csv", index=False)
    pd.DataFrame({"artifact": ["config", "coded_data_freeze", "mapping", "outputs", "sample", "captions", "construct_strength"], "sha256": [sha256(args.config), sha256(args.coded_data_freeze), sha256(args.mapping), sha256(args.outputs), sha256(args.sample), sha256(args.captions), sha256(args.construct_strength)]}).to_csv(args.outdir / "ANALYSIS_CHECKSUMS.csv", index=False)
    manifest = {
        "status": "RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY",
        "condition_unblinded_once": True,
        "new_human_data_collected": False,
        "alt_test_current_study": "NOT_APPLICABLE_TO_CURRENT_DESIGN",
        "frozen_coded_data_status": freeze["status"],
        "primary_outputs": len(unblinded),
        "synthetic_label_rows": len(labels),
        "judges": sorted(labels.judge_id.unique().tolist()),
        "analysis_boundary": "VLM-output effects and bounded human-reference alignment only; no human-equivalence or lived-experience inference.",
    }
    (args.outdir / "ANALYSIS_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
