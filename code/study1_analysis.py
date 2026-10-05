"""Validate and dry-run the Study 1 analysis schema.

This program is deliberately safe by default: it accepts only data explicitly
marked synthetic. Passing empirical material requires both an explicit command
line switch and a documented ethics status. Its Bayesian mixed model is a
schema/dry-run check; the preregistered confirmatory GLMM is implemented in
``code/study1_analysis.R``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "synthetic" / "study1_synthetic_unit_data.csv"
SYNTHETIC_STATUS = "SYNTHETIC_ONLY_NOT_EMPIRICAL"
CONDITIONS = {"DAI", "SAI", "HUM", "ANC"}
ORDINAL_CODES = {0, 1, 2, 3, 9}
REQUIRED = {
    "data_status",
    "participant_id",
    "session_id",
    "condition",
    "period",
    "order",
    "stimulus_id",
    "unit_id",
    "target_status",
    "report_eligible",
    "report_status",
    "ordinal_code",
    "primary_binary",
    "delivered_word_count",
}


def _approval_documented() -> bool:
    """Return whether a narrowly defined, authoritative approval is recorded.

    This is a guard against accidentally processing real data during the
    preparation phase. It is not a substitute for checking the actual approval
    letter, protocol version, and institutional requirements.
    """
    status_path = ROOT / "ethics" / "ETHICS_STATUS.md"
    if not status_path.exists():
        return False
    text = status_path.read_text(encoding="utf-8", errors="replace")
    return bool(re.search(r"^Status:\s*(APPROVED|EXEMPT_DETERMINATION|DETERMINED_NOT_HUMAN_SUBJECTS)\b", text, re.MULTILINE))


def _numeric_series(data: pd.DataFrame, column: str) -> pd.Series:
    return pd.to_numeric(data[column], errors="coerce")


def validate(data: pd.DataFrame, allow_real_data: bool = False) -> pd.DataFrame:
    """Validate the locked long-format schema and derive safe numeric fields."""
    missing = REQUIRED - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    data = data.copy()
    statuses = set(data["data_status"].dropna().astype(str))
    if not statuses:
        raise ValueError("data_status is empty.")
    synthetic_only = statuses == {SYNTHETIC_STATUS}
    if not synthetic_only:
        if not allow_real_data:
            raise ValueError("Refusing non-synthetic data without --allow-real-data.")
        if not _approval_documented():
            raise ValueError("Refusing non-synthetic data: authoritative ethics approval is not documented.")
    if not set(data["condition"].dropna()).issubset(CONDITIONS):
        raise ValueError("Unknown condition.")

    for column in ("target_status", "report_eligible"):
        data[column] = _numeric_series(data, column)
        if not set(data[column].dropna().unique()).issubset({0, 1}):
            raise ValueError(f"{column} must contain only 0 or 1.")
    for column in ("period", "order", "delivered_word_count"):
        data[column] = _numeric_series(data, column)
        if data[column].isna().any():
            raise ValueError(f"{column} must be numeric and present.")

    data["ordinal_code"] = _numeric_series(data, "ordinal_code")
    data["primary_binary"] = _numeric_series(data, "primary_binary")
    valid_codes = set(data["ordinal_code"].dropna().unique())
    if not valid_codes.issubset(ORDINAL_CODES):
        raise ValueError("ordinal_code must be 0, 1, 2, 3, 9, or missing for a no-recall/ineligible report.")
    valid_binary = set(data["primary_binary"].dropna().unique())
    if not valid_binary.issubset({0, 1}):
        raise ValueError("primary_binary must be 0, 1, or missing.")

    content_report = data["report_status"].astype(str).eq("ELIGIBLE")
    no_recall = data["report_status"].astype(str).eq("NO_RECALL")
    allowed_status = {"ELIGIBLE", "NO_RECALL", "INELIGIBLE"}
    if not set(data["report_status"].dropna().astype(str)).issubset(allowed_status):
        raise ValueError("report_status must be ELIGIBLE, NO_RECALL, or INELIGIBLE.")
    if (content_report & data["ordinal_code"].isna()).any():
        raise ValueError("ELIGIBLE report rows require an independent/adjudicated ordinal code.")
    if (no_recall & data["primary_binary"].notna()).any():
        raise ValueError("NO_RECALL has missing, never zero, primary outcomes.")
    if ((data["report_eligible"] == 0) & data["primary_binary"].notna()).any():
        raise ValueError("Ineligible report rows cannot have a primary outcome.")

    mapping = {0: 0, 2: 1, 3: 1}
    mapped = data["ordinal_code"].map(mapping)
    must_match = mapped.notna()
    if (data.loc[must_match, "primary_binary"] != mapped.loc[must_match]).any():
        raise ValueError("primary_binary disagrees with the frozen ordinal-code mapping.")
    ambiguous_or_undecidable = data["ordinal_code"].isin([1, 9])
    if data.loc[ambiguous_or_undecidable, "primary_binary"].notna().any():
        raise ValueError("Codes 1 and 9 must be missing from the primary binary outcome.")
    return data


def primary_dataset(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return the locked primary set and transparent row-level exclusion flow."""
    stages = []
    stages.append(("input_unit_rows", len(data)))
    ai = data.loc[data["condition"].isin(["DAI", "SAI"])].copy()
    stages.append(("AI_condition_unit_rows", len(ai)))
    eligible = ai.loc[ai["report_status"].eq("ELIGIBLE") & ai["report_eligible"].eq(1)].copy()
    stages.append(("eligible_report_unit_rows", len(eligible)))
    decidable = eligible.loc[eligible["ordinal_code"].isin([0, 2, 3])].copy()
    stages.append(("primary_decidable_unit_rows", len(decidable)))
    if decidable["primary_binary"].isna().any():
        raise ValueError("Decidable primary rows must contain primary_binary.")
    flow = pd.DataFrame(stages, columns=["stage", "n_unit_rows"])
    return decidable, flow


def fit_dry_run_model(data: pd.DataFrame, formula: str) -> pd.DataFrame:
    """Fit a synthetic-only Bayesian participant-random-intercept dry-run model."""
    fit_data = data.copy()
    fit_data["condition"] = pd.Categorical(fit_data["condition"], categories=["DAI", "SAI"])
    model = BinomialBayesMixedGLM.from_formula(
        formula,
        {"participant": "0 + C(participant_id)"},
        fit_data,
    )
    fit = model.fit_vb()
    table = pd.DataFrame({"term": model.exog_names, "estimate_log_odds": fit.fe_mean, "sd": fit.fe_sd})
    table["ci95_low"] = table["estimate_log_odds"] - 1.96 * table["sd"]
    table["ci95_high"] = table["estimate_log_odds"] + 1.96 * table["sd"]
    table["odds_ratio"] = np.exp(table["estimate_log_odds"])
    return table


def clustered_rate_bootstrap(data: pd.DataFrame, repetitions: int = 500, seed: int = 20261005) -> dict:
    """Participant-cluster bootstrap of the target-minus-decoy rate difference."""
    rng = np.random.default_rng(seed)
    participants = data["participant_id"].drop_duplicates().to_numpy()
    estimates: list[float] = []
    for _ in range(repetitions):
        selected = rng.choice(participants, size=len(participants), replace=True)
        boot = pd.concat([data.loc[data["participant_id"].eq(pid)] for pid in selected], ignore_index=True)
        rates = boot.groupby("target_status", observed=True)["primary_binary"].mean()
        estimates.append(float(rates.get(1, np.nan) - rates.get(0, np.nan)))
    return {
        "repetitions": repetitions,
        "seed": seed,
        "target_minus_decoy_rate_difference_ci95": [
            float(np.nanquantile(estimates, 0.025)),
            float(np.nanquantile(estimates, 0.975)),
        ],
    }


def report_level_target_minus_decoy(data: pd.DataFrame, repetitions: int, seed: int = 20261005) -> dict:
    """Check a report-level aggregation without treating units as participants.

    This is a prespecified robustness computation for the eventual empirical
    pipeline. In the dry run it merely verifies that grouped rows, missingness,
    and a participant-cluster bootstrap are handled correctly.
    """
    grouped = (
        data.groupby(["participant_id", "session_id", "target_status"], observed=True)["primary_binary"]
        .mean()
        .unstack("target_status")
        .dropna(subset=[0, 1])
        .rename(columns={0: "decoy_rate", 1: "target_rate"})
        .reset_index()
    )
    grouped["difference"] = grouped["target_rate"] - grouped["decoy_rate"]
    if grouped.empty:
        raise ValueError("No complete report-level target/decoy pairs for robustness computation.")
    rng = np.random.default_rng(seed)
    participants = grouped["participant_id"].drop_duplicates().to_numpy()
    estimates: list[float] = []
    for _ in range(repetitions):
        selected = rng.choice(participants, size=len(participants), replace=True)
        sampled = pd.concat(
            [grouped.loc[grouped["participant_id"].eq(pid)] for pid in selected],
            ignore_index=True,
        )
        estimates.append(float(sampled["difference"].mean()))
    return {
        "estimate": float(grouped["difference"].mean()),
        "n_complete_report_pairs": int(len(grouped)),
        "bootstrap_ci95_low": float(np.quantile(estimates, 0.025)),
        "bootstrap_ci95_high": float(np.quantile(estimates, 0.975)),
    }


def ambiguous_as_absent_dataset(data: pd.DataFrame) -> pd.DataFrame:
    """Return the predeclared code-1 sensitivity mapping; code 9 stays missing."""
    sensitivity = data.loc[data["ordinal_code"].isin([0, 1, 2, 3])].copy()
    sensitivity["primary_binary"] = sensitivity["ordinal_code"].isin([2, 3]).astype(int)
    return sensitivity


def write_outputs(data: pd.DataFrame, output_dir: Path, figure_dir: Path, prefix: str, repetitions: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    primary, flow = primary_dataset(data)
    status = data["data_status"].iloc[0]
    flow.insert(0, "data_status", status)
    flow.to_csv(output_dir / f"{prefix}_exclusion_flow.csv", index=False)

    primary_formula = (
        "primary_binary ~ target_status + C(condition) + C(period) + C(order) + C(stimulus_id)"
    )
    model_table = fit_dry_run_model(primary, primary_formula)
    model_table.insert(0, "data_status", status)
    model_table.to_csv(output_dir / f"{prefix}_model_terms.csv", index=False)

    interaction_formula = (
        "primary_binary ~ target_status * C(condition) + C(period) + C(order) + C(stimulus_id)"
    )
    interaction_table = fit_dry_run_model(primary, interaction_formula)
    interaction_table.insert(0, "data_status", status)
    interaction_table.insert(1, "analysis_role", "SECONDARY_TARGET_BY_CONDITION_INTERACTION")
    interaction_table.to_csv(output_dir / f"{prefix}_secondary_interaction_terms.csv", index=False)

    summary = (
        primary.groupby(["condition", "target_status"], observed=True)["primary_binary"]
        .agg(["sum", "count", "mean"])
        .reset_index()
    )
    summary.insert(0, "data_status", status)
    summary.to_csv(output_dir / f"{prefix}_primary_summary.csv", index=False)
    bootstrap = clustered_rate_bootstrap(primary, repetitions=repetitions)
    (output_dir / f"{prefix}_bootstrap.json").write_text(
        json.dumps({"data_status": status, **bootstrap}, indent=2), encoding="utf-8"
    )

    eligible_ai = data.loc[
        data["condition"].isin(["DAI", "SAI"])
        & data["report_status"].eq("ELIGIBLE")
        & data["report_eligible"].eq(1)
    ].copy()
    sensitivity = ambiguous_as_absent_dataset(eligible_ai)
    sensitivity_bootstrap = clustered_rate_bootstrap(sensitivity, repetitions=repetitions)
    report_level = report_level_target_minus_decoy(primary, repetitions=repetitions)
    robustness = pd.DataFrame(
        [
            {
                "data_status": status,
                "analysis": "PRIMARY_UNIT_LEVEL_CODE_2_OR_3",
                "n_unit_rows": len(primary),
                "estimate_type": "target_minus_decoy_rate_bootstrap_ci",
                "estimate": None,
                "ci95_low": sensitivity_bootstrap["target_minus_decoy_rate_difference_ci95"][0],
                "ci95_high": sensitivity_bootstrap["target_minus_decoy_rate_difference_ci95"][1],
                "note": "Primary model is in model_terms; this rate bootstrap is a transparent diagnostic.",
            },
            {
                "data_status": status,
                "analysis": "SENSITIVITY_AMBIGUOUS_CODE_1_AS_ABSENT",
                "n_unit_rows": len(sensitivity),
                "estimate_type": "target_minus_decoy_rate_bootstrap_ci",
                "estimate": None,
                "ci95_low": sensitivity_bootstrap["target_minus_decoy_rate_difference_ci95"][0],
                "ci95_high": sensitivity_bootstrap["target_minus_decoy_rate_difference_ci95"][1],
                "note": "Code 9 remains missing; never convert no recall to absence.",
            },
            {
                "data_status": status,
                "analysis": "ROBUSTNESS_REPORT_LEVEL_TARGET_MINUS_DECOY",
                "n_unit_rows": report_level["n_complete_report_pairs"],
                "estimate_type": "mean_with_participant_cluster_bootstrap_ci",
                "estimate": report_level["estimate"],
                "ci95_low": report_level["bootstrap_ci95_low"],
                "ci95_high": report_level["bootstrap_ci95_high"],
                "note": "One target-minus-decoy rate difference per complete report pair.",
            },
        ]
    )
    # Correct the primary diagnostic row after construction: it uses the frozen
    # primary mapping, whereas the sensitivity row deliberately includes code 1.
    primary_bootstrap = clustered_rate_bootstrap(primary, repetitions=repetitions)
    robustness.loc[0, "ci95_low"] = primary_bootstrap["target_minus_decoy_rate_difference_ci95"][0]
    robustness.loc[0, "ci95_high"] = primary_bootstrap["target_minus_decoy_rate_difference_ci95"][1]
    robustness.to_csv(output_dir / f"{prefix}_robustness.csv", index=False)

    rates = primary.groupby("target_status", observed=True)["primary_binary"].mean()
    labels = ["Matched decoy", "Delivered target"]
    values = [float(rates.get(0, np.nan)), float(rates.get(1, np.nan))]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    ax.bar(labels, values, color=["#d9d9d9", "#4d4d4d"], edgecolor="black", linewidth=1.0)
    ax.set_ylim(0, max(0.20, max(values) * 1.3))
    ax.set_ylabel("Synthetic unit incorporation rate")
    ax.set_title("Synthetic-only Study 1 pipeline dry run; not an empirical result")
    for index, value in enumerate(values):
        ax.text(index, value, f"{value:.3f}", ha="center", va="bottom")
    fig.tight_layout()
    figure_path = figure_dir / f"{prefix}_primary.png"
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)
    (figure_dir / f"{prefix}_primary.alt.txt").write_text(
        "Bar chart labelled synthetic-only dry run, not an empirical result. "
        f"Matched-decoy synthetic incorporation rate: {values[0]:.3f}; "
        f"delivered-target synthetic incorporation rate: {values[1]:.3f}.",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--figure-dir", type=Path, default=ROOT / "figures")
    parser.add_argument("--prefix", default=None)
    parser.add_argument("--bootstrap-repetitions", type=int, default=500)
    parser.add_argument("--allow-real-data", action="store_true")
    args = parser.parse_args()
    if args.bootstrap_repetitions < 20:
        raise ValueError("Use at least 20 bootstrap repetitions for a dry run.")
    raw = pd.read_csv(args.input)
    data = validate(raw, allow_real_data=args.allow_real_data)
    synthetic = set(data["data_status"]) == {SYNTHETIC_STATUS}
    prefix = args.prefix or ("study1_synthetic" if synthetic else "study1_empirical")
    write_outputs(data, args.output_dir, args.figure_dir, prefix, args.bootstrap_repetitions)
    primary, _ = primary_dataset(data)
    print(f"Validated {len(data)} rows; {len(primary)} primary-decidable unit rows; status={data['data_status'].iloc[0]}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STUDY1_ANALYSIS_FAILED: {exc}", file=sys.stderr)
        raise
