"""Compare public textual representational spaces after authorized unblinding.

The script applies the frozen lexical CSO candidate extractor identically to
DreamSpace, IntentSpace, HumanSpace, and each AI prompt condition. It reports
only distributional text-profile distances. It cannot measure cognition,
dream experience, BLV preference, or causal transfer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import runpy
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"REPRESENTATIONAL_SPACE_ANALYSIS_FAILED: {message}")


def committed_sources(
    freeze_path: Path,
    freeze: dict[str, object],
    recovery: dict[str, object] | None = None,
) -> dict[str, tuple[Path, str]]:
    ledger = freeze_path.parent / "CODED_DATA_CHECKSUMS.csv"
    if not ledger.is_file() or freeze.get("coded_data_checksums_sha256") != sha256(ledger):
        fail("coded-data checksum ledger is missing or changed")
    rows = pd.read_csv(ledger, dtype=str, keep_default_na=False)
    if not {"artifact", "path", "sha256"}.issubset(rows.columns) or rows.artifact.duplicated().any():
        fail("coded-data checksum ledger schema is incomplete")
    sources: dict[str, tuple[Path, str]] = {}
    for row in rows.to_dict("records"):
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
            fail(f"committed source is absent or changed: {row['artifact']}")
        sources[str(row["artifact"])] = (path, actual if permitted_recovery else expected)
    for name, expected in dict(freeze.get("source_checksums", {})).items():
        permitted_recovery = (
            recovery is not None
            and name == "analysis_script"
            and str(expected) == str(recovery["original_analysis_script_sha256"])
            and sources.get(name, (None, None))[1] == str(recovery["replacement_analysis_script_sha256"])
        )
        if name not in sources or (sources[name][1] != str(expected) and not permitted_recovery):
            fail(f"coded-data freeze source commitment is incomplete or inconsistent: {name}")
    return sources


def verify_technical_recovery(analysis: dict[str, object], freeze_path: Path) -> dict[str, object] | None:
    receipt_path = analysis.get("unblinding_technical_recovery_receipt")
    if receipt_path in (None, ""):
        return None
    path = Path(str(receipt_path))
    if not path.is_file():
        fail("post-freeze analysis names an unavailable technical recovery receipt")
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("status") == "UNBLINDING_TECHNICAL_RECOVERY_AUTHORIZED":
        # This receipt documents map-access recovery but intentionally has no
        # replacement script hash. The downstream hash-bound receipt supplies
        # that separate provenance link.
        return None
    if record.get("status") != "TECHNICAL_RECOVERY_AUTHORIZED_PRE_RESULT_ONLY":
        fail("technical recovery receipt has an invalid status")
    if record.get("condition_effects_estimated_before_recovery") is not False:
        fail("technical recovery receipt does not establish a pre-result failure")
    if record.get("original_coded_data_freeze_sha256") != sha256(freeze_path):
        fail("technical recovery receipt does not match coded-data freeze")
    return record


def verify_downstream_recovery(path: Path | None, freeze_path: Path) -> dict[str, object] | None:
    if path is None:
        return None
    if not path.is_file():
        fail("downstream technical recovery receipt is unavailable")
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("status") != "DOWNSTREAM_TECHNICAL_RECOVERY_AUTHORIZED_PRE_RQ4_ONLY":
        fail("downstream technical recovery receipt has an invalid status")
    if record.get("coded_data_freeze_sha256") != sha256(freeze_path):
        fail("downstream technical recovery receipt does not match coded-data freeze")
    if record.get("condition_effects_reinterpreted_before_recovery") is not False:
        fail("downstream technical recovery receipt does not establish the permitted recovery boundary")
    return record


def require_committed(sources: dict[str, tuple[Path, str]], name: str, path: Path) -> None:
    if name not in sources or path.resolve() != sources[name][0].resolve() or sha256(path) != sources[name][1]:
        fail(f"source does not match coded-data commitment: {name}")


def verify_post_analysis_receipt(directory: Path, manifest: dict[str, object]) -> None:
    checksums_path = directory / "ANALYSIS_CHECKSUMS.csv"
    if not checksums_path.is_file() or manifest.get("analysis_checksums_sha256") != sha256(checksums_path):
        fail("post-freeze analysis checksum ledger is missing or changed")
    checksums = pd.read_csv(checksums_path, dtype=str, keep_default_na=False)
    if not {"artifact", "sha256"}.issubset(checksums.columns) or checksums.artifact.duplicated().any():
        fail("post-freeze analysis checksum ledger schema is incomplete")
    expected = {"RQ2_results": directory / "RQ2_results.csv", "RQ3_results": directory / "RQ3_results.csv", "RQ5_results": directory / "RQ5_results.csv"}
    for artifact, path in expected.items():
        row = checksums.loc[checksums.artifact == artifact]
        if len(row) != 1 or not path.is_file() or str(row.iloc[0].sha256) != sha256(path):
            fail(f"post-freeze result is absent or changed: {artifact}")
    completion = Path(str(manifest.get("unblinding_completion_receipt", "")))
    if not completion.is_file():
        fail("authorized unblinding completion receipt is unavailable")
    completed = json.loads(completion.read_text(encoding="utf-8"))
    if completed.get("status") != "UNBLINDING_COMPLETED_PUBLIC_DATA_ONLY":
        fail("authorized unblinding completion receipt has an unexpected status")
    ledger = Path(str(manifest.get("unblinding_ledger", "")))
    if not ledger.is_file() or completed.get("started_ledger_sha256") != sha256(ledger):
        fail("authorized unblinding completion receipt is not linked to its start ledger")
    if completed.get("analysis_checksums_sha256") != sha256(checksums_path):
        fail("authorized unblinding completion receipt is not linked to analysis checksums")
    if Path(str(completed.get("analysis_directory", ""))).resolve() != directory.resolve():
        fail("authorized unblinding completion receipt names a different analysis directory")
    for shorthand, artifact in (("RQ2", "RQ2_results"), ("RQ3", "RQ3_results"), ("RQ5", "RQ5_results")):
        result_row = checksums.loc[checksums.artifact == artifact]
        if completed.get("result_sha256", {}).get(shorthand) != str(result_row.iloc[0].sha256):
            fail(f"authorized unblinding completion receipt is not linked to {artifact}")


def profile(rows: list[dict[str, object]], rules: list[str]) -> np.ndarray:
    if not rows:
        return np.full(len(rules), np.nan)
    values = []
    for rule in rules:
        applicable = [int(row[rule]) for row in rows if row[rule] != ""]
        values.append(float(np.mean(applicable)) if applicable else np.nan)
    return np.array(values, dtype=float)


def distances(first: np.ndarray, second: np.ndarray) -> dict[str, float]:
    mask = np.isfinite(first) & np.isfinite(second)
    first, second = first[mask], second[mask]
    if len(first) == 0 or first.sum() == 0 or second.sum() == 0:
        return {"jensen_shannon_divergence": np.nan, "cosine_similarity": np.nan, "hellinger_distance": np.nan, "n_categories": int(len(first))}
    first, second = first / first.sum(), second / second.sum()
    midpoint = (first + second) / 2
    kl = lambda left, right: float(np.sum(np.where(left > 0, left * np.log2(left / right), 0.0)))
    cosine = float(np.dot(first, second) / (np.linalg.norm(first) * np.linalg.norm(second)))
    hellinger = float(np.sqrt(np.sum((np.sqrt(first) - np.sqrt(second)) ** 2)) / math.sqrt(2))
    return {"jensen_shannon_divergence": float((kl(first, midpoint) + kl(second, midpoint)) / 2), "cosine_similarity": cosine, "hellinger_distance": hellinger, "n_categories": int(len(first))}


def row_matrix(rows: list[dict[str, object]], rules: list[str]) -> np.ndarray:
    """Represent fixed lexical labels as a text-unit-by-category matrix."""
    return np.array(
        [[np.nan if row[rule] == "" else float(row[rule]) for rule in rules] for row in rows],
        dtype=float,
    )


def bootstrap_profiles(
    matrix: np.ndarray,
    repetitions: int,
    rng: np.random.Generator,
    fixed_indices: np.ndarray | None = None,
) -> np.ndarray:
    """Bootstrap profiles, optionally using a shared item-level resample matrix."""
    profiles = np.empty((repetitions, matrix.shape[1]), dtype=float)
    if fixed_indices is not None and fixed_indices.shape != (repetitions, matrix.shape[0]):
        fail("paired bootstrap index shape does not match the frozen AI item design")
    for index in range(repetitions):
        draw = fixed_indices[index] if fixed_indices is not None else rng.integers(0, matrix.shape[0], matrix.shape[0])
        sampled = matrix[draw]
        profiles[index] = np.nanmean(sampled, axis=0)
    return profiles


def bootstrap_js(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """Compute paired replicate JSD values from precomputed space bootstraps."""
    mask = np.isfinite(first) & np.isfinite(second)
    first = np.where(mask, first, 0.0)
    second = np.where(mask, second, 0.0)
    first_totals, second_totals = first.sum(axis=1), second.sum(axis=1)
    usable = (first_totals > 0) & (second_totals > 0)
    values = np.full(len(first), np.nan)
    if not usable.any():
        return values
    left = first[usable] / first_totals[usable, None]
    right = second[usable] / second_totals[usable, None]
    midpoint = (left + right) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        left_kl = np.where(left > 0, left * np.log2(left / midpoint), 0.0).sum(axis=1)
        right_kl = np.where(right > 0, right * np.log2(right / midpoint), 0.0).sum(axis=1)
    values[usable] = (left_kl + right_kl) / 2
    return values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "post_freeze_analysis_v1.json")
    parser.add_argument("--coded-data-freeze", type=Path, required=True)
    parser.add_argument("--post-freeze-analysis", type=Path, required=True)
    parser.add_argument("--dreams", type=Path, default=ROOT / "data" / "dreambank" / "processed" / "dream_reports.csv")
    parser.add_argument("--intent", type=Path, default=ROOT / "data" / "ai_sensory" / "processed" / "corpus_items.csv")
    parser.add_argument("--captions", type=Path, default=ROOT / "data" / "public_reference" / "processed" / "vizwiz_captions_val.csv")
    parser.add_argument("--outputs", type=Path, default=ROOT / "data" / "model_outputs" / "validated" / "primary_model_outputs.csv")
    parser.add_argument("--downstream-recovery", type=Path, default=None)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite immutable representational-space results")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    freeze = json.loads(args.coded_data_freeze.read_text(encoding="utf-8"))
    analysis = json.loads((args.post_freeze_analysis / "ANALYSIS_MANIFEST.json").read_text(encoding="utf-8"))
    if freeze.get("status") != "CODED_DATA_FROZEN_PUBLIC_DATA_ONLY" or analysis.get("status") != "RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY":
        fail("coded-data freeze and authorized post-freeze analysis are required")
    if analysis.get("condition_unblinded_once") is not True or analysis.get("frozen_coded_data_status") != freeze.get("status"):
        fail("post-freeze analysis receipt does not document the one authorized unblinding")
    recovery = verify_technical_recovery(analysis, args.coded_data_freeze)
    downstream = verify_downstream_recovery(args.downstream_recovery, args.coded_data_freeze)
    if downstream is not None:
        replacements = downstream.get("replacements", {})
        recovery = {"original_analysis_script_sha256": replacements["analysis_script"]["original_sha256"], "replacement_analysis_script_sha256": replacements["analysis_script"]["replacement_sha256"]}
    sources = committed_sources(args.coded_data_freeze, freeze, recovery)
    if downstream is not None:
        replacement = downstream["replacements"].get("rq4_script", {})
        expected = sources["rq4_script"][1]
        actual = sha256(Path(__file__).resolve())
        if replacement.get("original_sha256") != expected or replacement.get("replacement_sha256") != actual:
            fail("downstream recovery does not authorize this RQ4 script")
        sources["rq4_script"] = (Path(__file__).resolve(), actual)
    for name, path in {
        "analysis_config": args.config,
        "rq4_script": Path(__file__).resolve(),
        "dreams": args.dreams,
        "intent_corpus": args.intent,
        "captions": args.captions,
        "primary_outputs": args.outputs,
        "lexical_codebook": ROOT / config["representational_space"]["lexical_codebook_script"],
    }.items():
        require_committed(sources, name, path)
    verify_post_analysis_receipt(args.post_freeze_analysis, analysis)
    for source in (args.dreams, args.intent, args.captions, args.outputs):
        if not source.is_file():
            fail(f"required source unavailable: {source}")
    codebook_path = ROOT / config["representational_space"]["lexical_codebook_script"]
    codebook = runpy.run_path(str(codebook_path))
    rules: dict[str, str] = codebook["RULES"]
    label = codebook["label"]
    applicable_rules = [rule for rule in rules if rule not in {"task_relevance", "intent_match", "unsupported_information", "nightmare"}]

    dreams = pd.read_csv(args.dreams, dtype=str, keep_default_na=False)
    intent = pd.read_csv(args.intent, dtype=str, keep_default_na=False)
    captions = pd.read_csv(args.captions, dtype=str, keep_default_na=False)
    outputs = pd.read_csv(args.outputs, dtype=str, keep_default_na=False)
    if not {"dream_text"}.issubset(dreams.columns) or not {"source_type", "input_text"}.issubset(intent.columns) or not {"caption_text"}.issubset(captions.columns) or not {"sample_row_id", "condition", "output_text"}.issubset(outputs.columns):
        fail("source schema is incomplete")
    spaces: dict[str, list[dict[str, object]]] = {
        "DREAM": [label(text, "DREAM") for text in dreams.dream_text if text],
        "BLV_USER_QUESTION": [label(text, "BLV_USER_QUESTION") for text in intent.loc[intent.source_type == "BLV_USER_QUESTION", "input_text"] if text],
        "HUMAN_CAPTION": [label(text, "AI_DESCRIPTION") for text in captions.caption_text if text],
    }
    condition_space = {"generic": "AI_GENERIC", "intent_steered": "AI_INTENT_STEERED", "accessibility_steered": "AI_ACCESSIBILITY_STEERED"}
    if set(outputs.condition) != set(condition_space):
        fail("output condition set differs from frozen intervention design")
    if outputs.duplicated(["sample_row_id", "condition"]).any():
        fail("frozen AI outputs contain duplicate item-condition records")
    expected_items = int(config["design"]["expected_items"])
    ai_item_ids: set[str] | None = None
    for condition, space in condition_space.items():
        condition_rows = outputs.loc[outputs.condition == condition, ["sample_row_id", "output_text"]].copy()
        if len(condition_rows) != expected_items or (condition_rows.output_text == "").any():
            fail(f"frozen AI output coverage is incomplete for {condition}")
        condition_rows = condition_rows.sort_values("sample_row_id", key=lambda value: value.astype(str)).reset_index(drop=True)
        current_ids = set(condition_rows.sample_row_id.astype(str))
        if ai_item_ids is None:
            ai_item_ids = current_ids
        elif current_ids != ai_item_ids:
            fail("AI conditions do not cover the same frozen item identifiers")
        spaces[space] = [label(text, "AI_DESCRIPTION") for text in condition_rows.output_text]
    if any(len(rows) == 0 for rows in spaces.values()):
        fail("one or more spaces have no available text rows")

    profiles = {space: profile(rows, applicable_rules) for space, rows in spaces.items()}
    matrices = {space: row_matrix(rows, applicable_rules) for space, rows in spaces.items()}
    profile_rows = []
    for space, values in profiles.items():
        for category, value in zip(applicable_rules, values):
            profile_rows.append({"space": space, "category": category, "n_text_units": len(spaces[space]), "proportion_expressed": value, "measurement_status": "COMPUTATIONAL_SECONDARY_LEXICAL_PROFILE", "claim_boundary": "Expressed textual vocabulary only; not sensation, cognition, preference, or image-grounded truth."})
    rng = np.random.default_rng(int(config["inference"]["seed"]))
    bootstrap_repetitions = int(config["representational_space"]["bootstrap_repetitions"])
    bootstrap_space_profiles = {
        space: bootstrap_profiles(matrix, bootstrap_repetitions, rng)
        for space, matrix in matrices.items()
        if not space.startswith("AI_")
    }
    ai_spaces = ["AI_GENERIC", "AI_INTENT_STEERED", "AI_ACCESSIBILITY_STEERED"]
    ai_matrix_sizes = {matrices[space].shape[0] for space in ai_spaces}
    if ai_matrix_sizes != {expected_items}:
        fail("AI condition matrices do not retain the frozen paired item count")
    paired_ai_indices = rng.integers(0, expected_items, size=(bootstrap_repetitions, expected_items))
    for space in ai_spaces:
        bootstrap_space_profiles[space] = bootstrap_profiles(
            matrices[space], bootstrap_repetitions, rng, fixed_indices=paired_ai_indices
        )
    comparisons = []
    for left, right in combinations(spaces, 2):
        metrics = distances(profiles[left], profiles[right])
        estimates = bootstrap_js(bootstrap_space_profiles[left], bootstrap_space_profiles[right])
        estimates = estimates[np.isfinite(estimates)]
        ci_low = float(np.quantile(estimates, 0.025)) if len(estimates) else np.nan
        ci_high = float(np.quantile(estimates, 0.975)) if len(estimates) else np.nan
        comparisons.append({"space_a": left, "space_b": right, "n_a": len(spaces[left]), "n_b": len(spaces[right]), **metrics, "js_ci_low": ci_low, "js_ci_high": ci_high, "analysis_status": "DISTRIBUTIONAL_TEXT_PROFILE_ONLY", "interpretation_boundary": "Distributional resemblance is not cognitive equivalence, dream transfer, or accessibility usefulness."})
    association = pd.DataFrame([{
        "analysis": "DreamSpace distance versus human-reference alignment",
        "status": config["representational_space"]["association_test"],
        "reason": "Three AI condition profiles do not support a stable association estimate.",
    }])
    args.outdir.mkdir(parents=True, exist_ok=False)
    pd.DataFrame(profile_rows).to_csv(args.outdir / "RQ4_space_profiles.csv", index=False)
    pd.DataFrame(comparisons).to_csv(args.outdir / "RQ4_results.csv", index=False)
    association.to_csv(args.outdir / "RQ4_association_status.csv", index=False)
    manifest = {
        "status": "RQ4_COMPLETE_DISTRIBUTIONAL_PUBLIC_DATA_ONLY",
        "condition_unblinded_once": True,
        "new_human_data_collected": False,
        "coded_data_freeze_sha256": sha256(args.coded_data_freeze),
        "post_freeze_analysis_manifest_sha256": sha256(args.post_freeze_analysis / "ANALYSIS_MANIFEST.json"),
        "lexical_codebook_sha256": sha256(codebook_path),
        "rq4_script_sha256": sha256(Path(__file__).resolve()),
        "paired_ai_bootstrap": "Shared sample_row_id bootstrap draws were used for every AI-condition comparison.",
        "spaces": {name: len(rows) for name, rows in spaces.items()},
        "categories": applicable_rules,
        "interpretation_boundary": "Text distributions only; no inference about cognition, lived experience, preference, or causal transfer.",
    }
    (args.outdir / "RQ4_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
