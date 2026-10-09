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


def bootstrap_profiles(matrix: np.ndarray, repetitions: int, rng: np.random.Generator) -> np.ndarray:
    """Ordinary text-unit bootstrap, sampled once per space and reused by pairs."""
    profiles = np.empty((repetitions, matrix.shape[1]), dtype=float)
    for index in range(repetitions):
        sampled = matrix[rng.integers(0, matrix.shape[0], matrix.shape[0])]
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
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite immutable representational-space results")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    freeze = json.loads(args.coded_data_freeze.read_text(encoding="utf-8"))
    analysis = json.loads((args.post_freeze_analysis / "ANALYSIS_MANIFEST.json").read_text(encoding="utf-8"))
    if freeze.get("status") != "CODED_DATA_FROZEN_PUBLIC_DATA_ONLY" or analysis.get("status") != "RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY":
        fail("coded-data freeze and authorized post-freeze analysis are required")
    for source in (args.dreams, args.intent, args.captions, args.outputs):
        if not source.is_file():
            fail(f"required source unavailable: {source}")
    codebook = runpy.run_path(str(ROOT / config["representational_space"]["lexical_codebook_script"]))
    rules: dict[str, str] = codebook["RULES"]
    label = codebook["label"]
    applicable_rules = [rule for rule in rules if rule not in {"task_relevance", "intent_match", "unsupported_information", "nightmare"}]

    dreams = pd.read_csv(args.dreams, dtype=str, keep_default_na=False)
    intent = pd.read_csv(args.intent, dtype=str, keep_default_na=False)
    captions = pd.read_csv(args.captions, dtype=str, keep_default_na=False)
    outputs = pd.read_csv(args.outputs, dtype=str, keep_default_na=False)
    if not {"dream_text"}.issubset(dreams.columns) or not {"source_type", "input_text"}.issubset(intent.columns) or not {"caption_text"}.issubset(captions.columns) or not {"condition", "output_text"}.issubset(outputs.columns):
        fail("source schema is incomplete")
    spaces: dict[str, list[dict[str, object]]] = {
        "DREAM": [label(text, "DREAM") for text in dreams.dream_text if text],
        "BLV_USER_QUESTION": [label(text, "BLV_USER_QUESTION") for text in intent.loc[intent.source_type == "BLV_USER_QUESTION", "input_text"] if text],
        "HUMAN_CAPTION": [label(text, "AI_DESCRIPTION") for text in captions.caption_text if text],
    }
    condition_space = {"generic": "AI_GENERIC", "intent_steered": "AI_INTENT_STEERED", "accessibility_steered": "AI_ACCESSIBILITY_STEERED"}
    if set(outputs.condition) != set(condition_space):
        fail("output condition set differs from frozen intervention design")
    for condition, space in condition_space.items():
        spaces[space] = [label(text, "AI_DESCRIPTION") for text in outputs.loc[outputs.condition == condition, "output_text"] if text]
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
    }
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
    manifest = {"status": "RQ4_COMPLETE_DISTRIBUTIONAL_PUBLIC_DATA_ONLY", "condition_unblinded_once": True, "new_human_data_collected": False, "lexical_codebook_sha256": sha256(ROOT / config["representational_space"]["lexical_codebook_script"]), "spaces": {name: len(rows) for name, rows in spaces.items()}, "categories": applicable_rules, "interpretation_boundary": "Text distributions only; no inference about cognition, lived experience, preference, or causal transfer."}
    (args.outdir / "RQ4_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, sort_keys=True))


if __name__ == "__main__":
    main()
