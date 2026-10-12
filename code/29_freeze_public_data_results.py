"""Freeze completed public-data RQ2--RQ5 artifacts before interpretation.

This gate does not recompute effects or generate prose. It checks immutable
receipts and hashes the tables that later figures and the manuscript must cite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path

import numpy as np
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


def require_columns(frame: pd.DataFrame, columns: set[str], name: str) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        fail(f"{name} schema is incomplete: {', '.join(sorted(missing))}")


def load_coded_sources(
    coded_path: Path,
    coded: dict[str, object],
    recovery: dict[str, object] | None = None,
) -> dict[str, tuple[Path, str]]:
    ledger_path = coded_path.parent / "CODED_DATA_CHECKSUMS.csv"
    if not ledger_path.is_file() or coded.get("coded_data_checksums_sha256") != sha256(ledger_path):
        fail("coded-data checksum ledger is unavailable or changed")
    ledger = pd.read_csv(ledger_path, dtype=str, keep_default_na=False)
    require_columns(ledger, {"artifact", "path", "sha256"}, "coded-data checksum ledger")
    if ledger.artifact.duplicated().any():
        fail("coded-data checksum ledger has duplicate artifact names")
    sources: dict[str, tuple[Path, str]] = {}
    for row in ledger.to_dict("records"):
        path = Path(str(row["path"]))
        digest = str(row["sha256"])
        actual = sha256(path) if path.is_file() else ""
        permitted_recovery = (
            recovery is not None
            and str(row["artifact"]) == "analysis_script"
            and digest == str(recovery["original_analysis_script_sha256"])
            and actual == str(recovery["replacement_analysis_script_sha256"])
        )
        if not path.is_file() or (actual != digest and not permitted_recovery):
            fail(f"coded-data committed source is unavailable or changed: {row['artifact']}")
        sources[str(row["artifact"])] = (path, actual if permitted_recovery else digest)
    for name, digest in dict(coded.get("source_checksums", {})).items():
        permitted_recovery = (
            recovery is not None
            and name == "analysis_script"
            and str(digest) == str(recovery["original_analysis_script_sha256"])
            and sources.get(name, (None, None))[1] == str(recovery["replacement_analysis_script_sha256"])
        )
        if name not in sources or (sources[name][1] != str(digest) and not permitted_recovery):
            fail(f"coded-data receipt does not reconcile committed source: {name}")
    return sources


def recovery_from_analysis(manifest: dict[str, object], coded_path: Path) -> dict[str, object] | None:
    value = manifest.get("unblinding_technical_recovery_receipt")
    if value in (None, ""):
        return None
    path = Path(str(value))
    if not path.is_file():
        fail("analysis technical recovery receipt is unavailable")
    record = read_receipt(path, "TECHNICAL_RECOVERY_AUTHORIZED_PRE_RESULT_ONLY")
    if record.get("condition_effects_estimated_before_recovery") is not False:
        fail("analysis recovery receipt does not establish a pre-result failure")
    if record.get("original_coded_data_freeze_sha256") != sha256(coded_path):
        fail("analysis recovery receipt does not match coded-data freeze")
    return record


def downstream_recovery(path: Path | None, coded_path: Path, post_manifest: Path) -> dict[str, object] | None:
    if path is None:
        return None
    if not path.is_file():
        fail("downstream technical recovery receipt is unavailable")
    record = read_receipt(path, "DOWNSTREAM_TECHNICAL_RECOVERY_AUTHORIZED_PRE_RQ4_ONLY")
    if record.get("coded_data_freeze_sha256") != sha256(coded_path) or record.get("post_analysis_manifest_sha256") != sha256(post_manifest):
        fail("downstream technical recovery receipt does not match frozen upstream artifacts")
    if record.get("condition_effects_reinterpreted_before_recovery") is not False:
        fail("downstream technical recovery receipt violates the pre-interpretation boundary")
    return record


def require_analysis_ledger(
    directory: Path,
    manifest: dict[str, object],
    coded_path: Path,
    sources: dict[str, tuple[Path, str]],
) -> pd.DataFrame:
    path = directory / "ANALYSIS_CHECKSUMS.csv"
    if not path.is_file() or manifest.get("analysis_checksums_sha256") != sha256(path):
        fail("post-freeze analysis checksum ledger is unavailable or changed")
    ledger = pd.read_csv(path, dtype=str, keep_default_na=False)
    require_columns(ledger, {"artifact", "sha256"}, "post-freeze analysis checksum ledger")
    if ledger.artifact.duplicated().any():
        fail("post-freeze analysis checksum ledger has duplicate artifact names")
    expected_sources = {
        "config": sources["analysis_config"][1],
        "coded_data_freeze": sha256(coded_path),
        "mapping": sources["mapping_commitment"][1],
        "outputs": sources["primary_outputs"][1],
        "sample": sources["frozen_sample"][1],
        "captions": sources["captions"][1],
        "construct_strength": sources["construct_strength"][1],
    }
    for artifact, digest in expected_sources.items():
        row = ledger.loc[ledger.artifact == artifact]
        if len(row) != 1 or str(row.iloc[0].sha256) != digest:
            fail(f"post-freeze analysis ledger does not match frozen source: {artifact}")
    expected_outputs = {
        "RQ2_results": directory / "RQ2_results.csv",
        "RQ3_results": directory / "RQ3_results.csv",
        "RQ5_results": directory / "RQ5_results.csv",
        "measurement_missingness": directory / "SYNTHETIC_MEASUREMENT_MISSINGNESS.csv",
        "private_human_reference_metrics": directory / "private_human_reference_metrics.csv",
    }
    for artifact, artifact_path in expected_outputs.items():
        row = ledger.loc[ledger.artifact == artifact]
        if len(row) != 1 or not artifact_path.is_file() or str(row.iloc[0].sha256) != sha256(artifact_path):
            fail(f"post-freeze analysis ledger does not match result artifact: {artifact}")
    start_ledger = Path(str(manifest.get("unblinding_ledger", "")))
    completion = Path(str(manifest.get("unblinding_completion_receipt", "")))
    if not start_ledger.is_file() or not completion.is_file():
        fail("authorized unblinding receipts are unavailable")
    started_row = ledger.loc[ledger.artifact == "unblinding_ledger"]
    if len(started_row) != 1 or str(started_row.iloc[0].sha256) != sha256(start_ledger):
        fail("post-freeze analysis ledger is not linked to the unblinding start receipt")
    complete = read_receipt(completion, "UNBLINDING_COMPLETED_PUBLIC_DATA_ONLY")
    if complete.get("started_ledger_sha256") != sha256(start_ledger):
        fail("unblinding completion receipt does not match the start receipt")
    if complete.get("analysis_checksums_sha256") != sha256(path):
        fail("unblinding completion receipt does not match analysis checksums")
    if Path(str(complete.get("analysis_directory", ""))).resolve() != directory.resolve():
        fail("unblinding completion receipt identifies a different analysis directory")
    for short, artifact in (("RQ2", "RQ2_results"), ("RQ3", "RQ3_results"), ("RQ5", "RQ5_results")):
        row = ledger.loc[ledger.artifact == artifact]
        if complete.get("result_sha256", {}).get(short) != str(row.iloc[0].sha256):
            fail(f"unblinding completion receipt does not match {artifact}")
    return ledger


def validate_rq2_rq5(
    rq2: pd.DataFrame,
    rq5: pd.DataFrame,
    config: dict[str, object],
    constructs: set[str],
    judges: set[str],
) -> None:
    common = {
        "judge_id", "construct", "measurement_status", "contrast", "n_paired_items",
        "paired_coverage", "effect", "ci_low", "ci_high", "permutation_p", "fdr_q", "analysis_role",
    }
    require_columns(rq2, common, "RQ2")
    require_columns(rq5, common | {"output_change_direction"}, "RQ5")
    contrasts = {str(item["id"]) for item in config["design"]["contrasts"]}
    expected = {(judge, construct, contrast) for judge in judges for construct in constructs for contrast in contrasts}
    for frame, name in ((rq2, "RQ2"), (rq5, "RQ5")):
        keys = list(zip(frame.judge_id.astype(str), frame.construct.astype(str), frame.contrast.astype(str)))
        if len(keys) != len(set(keys)) or set(keys) != expected:
            fail(f"{name} does not cover exactly the frozen judge-construct-contrast design")
        coverage = pd.to_numeric(frame.paired_coverage, errors="coerce")
        if ((coverage < 0) | (coverage > 1)).fillna(True).any():
            fail(f"{name} has invalid paired coverage")
    key_columns = ["judge_id", "construct", "contrast"]
    merged = rq2.merge(rq5[key_columns + ["effect", "analysis_role"]], on=key_columns, suffixes=("_rq2", "_rq5"), validate="one_to_one")
    if len(merged) != len(rq2) or not np.allclose(
        pd.to_numeric(merged.effect_rq2, errors="coerce"),
        pd.to_numeric(merged.effect_rq5, errors="coerce"),
        equal_nan=True,
    ) or not (merged.analysis_role_rq2.astype(str) == merged.analysis_role_rq5.astype(str)).all():
        fail("RQ5 is not traceably derived from the frozen RQ2 estimates")


def validate_rq3(rq3: pd.DataFrame, config: dict[str, object]) -> None:
    required = {
        "metric", "contrast", "measurement_status", "claim_boundary", "n_paired_items",
        "paired_coverage", "effect", "ci_low", "ci_high", "permutation_p", "fdr_q", "analysis_status",
    }
    require_columns(rq3, required, "RQ3")
    metrics = set(map(str, config["measurement"]["human_reference_metrics"]))
    contrasts = {str(item["id"]) for item in config["design"]["contrasts"]}
    keys = list(zip(rq3.metric.astype(str), rq3.contrast.astype(str)))
    expected = {(metric, contrast) for metric in metrics for contrast in contrasts}
    if len(keys) != len(set(keys)) or set(keys) != expected:
        fail("RQ3 does not cover exactly the frozen metric-contrast design")
    coverage = pd.to_numeric(rq3.paired_coverage, errors="coerce")
    if ((coverage < 0) | (coverage > 1)).fillna(True).any():
        fail("RQ3 has invalid paired coverage")


def validate_rq4(
    rq4: pd.DataFrame,
    profiles: pd.DataFrame,
    association: pd.DataFrame,
    space_manifest: dict[str, object],
    coded_path: Path,
    post_manifest_path: Path,
    sources: dict[str, tuple[Path, str]],
) -> None:
    required = {
        "space_a", "space_b", "n_a", "n_b", "jensen_shannon_divergence",
        "cosine_similarity", "hellinger_distance", "n_categories", "js_ci_low", "js_ci_high", "analysis_status",
    }
    require_columns(rq4, required, "RQ4")
    require_columns(profiles, {"space", "category", "n_text_units", "proportion_expressed", "measurement_status"}, "RQ4 profiles")
    require_columns(association, {"analysis", "status", "reason"}, "RQ4 association status")
    spaces = set(map(str, space_manifest.get("spaces", {}).keys()))
    categories = set(map(str, space_manifest.get("categories", [])))
    expected_pairs = {frozenset(pair) for pair in combinations(spaces, 2)}
    keys = [frozenset((str(row.space_a), str(row.space_b))) for row in rq4.itertuples()]
    if len(keys) != len(set(keys)) or set(keys) != expected_pairs:
        fail("RQ4 does not cover exactly the frozen representational-space comparisons")
    profile_keys = set(zip(profiles.space.astype(str), profiles.category.astype(str)))
    expected_profiles = {(space, category) for space in spaces for category in categories}
    if profiles.duplicated(["space", "category"]).any() or profile_keys != expected_profiles:
        fail("RQ4 profiles do not cover exactly the frozen spaces and lexical categories")
    if space_manifest.get("coded_data_freeze_sha256") != sha256(coded_path):
        fail("RQ4 receipt is not tied to this coded-data freeze")
    if space_manifest.get("post_freeze_analysis_manifest_sha256") != sha256(post_manifest_path):
        fail("RQ4 receipt is not tied to this post-freeze analysis manifest")
    if space_manifest.get("lexical_codebook_sha256") != sources["lexical_codebook"][1]:
        fail("RQ4 receipt is not tied to the frozen lexical codebook")
    if space_manifest.get("rq4_script_sha256") != sources["rq4_script"][1]:
        fail("RQ4 receipt is not tied to the frozen RQ4 script")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coded-data-freeze", type=Path, required=True)
    parser.add_argument("--post-freeze-analysis", type=Path, required=True)
    parser.add_argument("--space-analysis", type=Path, required=True)
    parser.add_argument("--downstream-recovery", type=Path, default=None)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite immutable results freeze")
    coded = read_receipt(args.coded_data_freeze, "CODED_DATA_FROZEN_PUBLIC_DATA_ONLY")
    post_manifest_path = args.post_freeze_analysis / "ANALYSIS_MANIFEST.json"
    post = read_receipt(post_manifest_path, "RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY")
    space = read_receipt(args.space_analysis / "RQ4_MANIFEST.json", "RQ4_COMPLETE_DISTRIBUTIONAL_PUBLIC_DATA_ONLY")
    if post.get("condition_unblinded_once") is not True or post.get("frozen_coded_data_status") != coded.get("status"):
        fail("post-freeze analysis does not document the one authorized unblinding")
    recovery = recovery_from_analysis(post, args.coded_data_freeze)
    downstream = downstream_recovery(args.downstream_recovery, args.coded_data_freeze, post_manifest_path)
    if downstream is not None:
        replacements = downstream.get("replacements", {})
        if replacements.get("analysis_script", {}).get("replacement_sha256") != str(recovery.get("replacement_analysis_script_sha256") if recovery else ""):
            fail("downstream recovery does not chain to the initial analysis recovery")
        recovery = {"original_analysis_script_sha256": replacements["analysis_script"]["original_sha256"], "replacement_analysis_script_sha256": replacements["analysis_script"]["replacement_sha256"]}
    sources = load_coded_sources(args.coded_data_freeze, coded, recovery)
    if downstream is not None:
        replacement = downstream["replacements"].get("results_freeze_script", {})
        expected = sources["results_freeze_script"][1]
        actual = sha256(Path(__file__).resolve())
        if replacement.get("original_sha256") != expected or replacement.get("replacement_sha256") != actual:
            fail("downstream recovery does not authorize this results-freeze script")
        sources["results_freeze_script"] = (Path(__file__).resolve(), actual)
    if Path(__file__).resolve() != sources["results_freeze_script"][0].resolve() or sha256(Path(__file__).resolve()) != sources["results_freeze_script"][1]:
        fail("results-freeze script differs from its pre-unblinding commitment")
    config_path, _ = sources["analysis_config"]
    config = json.loads(config_path.read_text(encoding="utf-8"))
    require_analysis_ledger(args.post_freeze_analysis, post, args.coded_data_freeze, sources)
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
    rq4_profiles = pd.read_csv(required["RQ4_profiles"])
    rq4_association = pd.read_csv(required["RQ4_association_status"])
    if rq2.empty or rq3.empty or rq4.empty or rq5.empty:
        fail("one or more results tables are empty")
    strength_path, _ = sources["construct_strength"]
    strength = pd.read_csv(strength_path, dtype=str, keep_default_na=False)
    require_columns(strength, {"construct", "measurement_layer"}, "construct-strength table")
    constructs = set(strength.loc[strength.measurement_layer == "synthetic_panel", "construct"].astype(str))
    judges = set(map(str, coded.get("frozen_judges", [])))
    if not constructs or not judges:
        fail("coded-data receipt lacks frozen judge or construct commitments")
    validate_rq2_rq5(rq2, rq5, config, constructs, judges)
    validate_rq3(rq3, config)
    validate_rq4(rq4, rq4_profiles, rq4_association, space, args.coded_data_freeze, post_manifest_path, sources)
    args.outdir.mkdir(parents=True, exist_ok=False)
    ledger = pd.DataFrame([
        {"result_family": name, "path": str(path), "sha256": sha256(path), "rows": len(pd.read_csv(path))}
        for name, path in required.items()
    ])
    ledger_path = args.outdir / "RESULTS_LEDGER.csv"
    ledger.to_csv(ledger_path, index=False)
    manifest = {
        "status": "RESULTS_FROZEN_PUBLIC_DATA_ONLY",
        "coded_data_status": coded["status"],
        "condition_unblinded_once": bool(post.get("condition_unblinded_once")),
        "new_human_data_collected": False,
        "alt_test_current_study": "NOT_APPLICABLE_TO_CURRENT_DESIGN",
        "coded_data_freeze_sha256": sha256(args.coded_data_freeze),
        "post_freeze_analysis_manifest_sha256": sha256(post_manifest_path),
        "rq4_manifest_sha256": sha256(args.space_analysis / "RQ4_MANIFEST.json"),
        "analysis_ledger_sha256": sha256(args.post_freeze_analysis / "ANALYSIS_CHECKSUMS.csv"),
        "results_ledger_sha256": sha256(ledger_path),
        "results_freeze_script_sha256": sources["results_freeze_script"][1],
        "figure_script_sha256": sources["figure_script"][1],
        "tables": {name: {"sha256": sha256(path), "rows": len(pd.read_csv(path))} for name, path in required.items()},
        "interpretation_boundary": "Frozen VLM-output and distributional text results only; no human-equivalence, lived-experience, cognitive, dream-causation, or user-benefit claim is authorized.",
    }
    (args.outdir / "RESULTS_FREEZE.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (args.outdir / "RESULTS_FREEZE.md").write_text(
        "# Results freeze: public-data study\n\n"
        "Status: `RESULTS_FROZEN_PUBLIC_DATA_ONLY`\n\n"
        "All listed table hashes are in `RESULTS_LEDGER.csv`. The analysis was performed after the coded-data freeze and one authorized unblinding. Result schemas, paired-design coverage, source ledgers, and RQ4 provenance were validated before this freeze. Results concern model outputs and textual distributions only.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": manifest["status"], "tables": list(required)}, sort_keys=True))


if __name__ == "__main__":
    main()
