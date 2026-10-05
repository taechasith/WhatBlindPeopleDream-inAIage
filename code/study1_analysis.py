"""Validation and synthetic-only dry-run analysis for the frozen Study 1 schema."""
from __future__ import annotations

from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "synthetic" / "study1_synthetic_unit_data.csv"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
REQUIRED = {"data_status", "participant_id", "session_id", "condition", "period", "order", "stimulus_id", "unit_id", "target_status", "report_eligible", "incorporated_binary", "delivered_word_count"}


def validate(data: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if not (data["data_status"] == "SYNTHETIC_ONLY_NOT_EMPIRICAL").all():
        raise ValueError("Dry run accepts synthetic data only.")
    if not set(data["condition"]).issubset({"DAI", "SAI", "HUM", "ANC"}):
        raise ValueError("Unknown condition.")
    eligible = data.query("report_eligible == 1").copy()
    if eligible["incorporated_binary"].isna().any():
        raise ValueError("Eligible synthetic rows require a binary outcome.")
    return eligible


def fit_model(data: pd.DataFrame) -> pd.DataFrame:
    # This dry-run uses a participant-random-intercept logistic model. The final
    # preregistered model adds stimulus/period/order terms in R/lme4; R is absent
    # from this environment, so this is a schema/execution test, not final inference.
    ai = data.query("condition in ['DAI', 'SAI']").copy()
    ai["target_by_sai"] = ai["target_status"] * (ai["condition"] == "SAI").astype(int)
    ai["delivered_word_count_z"] = (ai["delivered_word_count"] - ai["delivered_word_count"].mean()) / ai["delivered_word_count"].std()
    model = BinomialBayesMixedGLM.from_formula(
        "incorporated_binary ~ target_status + C(condition) + target_by_sai",
        {"participant": "0 + C(participant_id)"}, ai,
    )
    fit = model.fit_vb()
    table = pd.DataFrame({"term": model.exog_names, "estimate_log_odds": fit.fe_mean, "sd": fit.fe_sd})
    table["ci95_low"] = table["estimate_log_odds"] - 1.96 * table["sd"]
    table["ci95_high"] = table["estimate_log_odds"] + 1.96 * table["sd"]
    table["odds_ratio"] = np.exp(table["estimate_log_odds"])
    return table


def bootstrap(data: pd.DataFrame, reps: int = 200) -> dict:
    rng = np.random.default_rng(20261005)
    ai = data.query("condition in ['DAI', 'SAI']").copy()
    participants = ai["participant_id"].unique()
    estimates = []
    for _ in range(reps):
        sampled = rng.choice(participants, size=len(participants), replace=True)
        pieces = [ai.loc[ai.participant_id.eq(p)] for p in sampled]
        boot = pd.concat(pieces, ignore_index=True)
        rate = boot.groupby("target_status")["incorporated_binary"].mean()
        estimates.append(float(rate.get(1, np.nan) - rate.get(0, np.nan)))
    return {"repetitions": reps, "target_minus_foil_rate_difference_ci95": [float(np.nanquantile(estimates, .025)), float(np.nanquantile(estimates, .975))]}


def main() -> None:
    raw = pd.read_csv(INPUT)
    data = validate(raw)
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    model_table = fit_model(data)
    model_table.insert(0, "data_status", "SYNTHETIC_ONLY_NOT_EMPIRICAL")
    model_table.to_csv(RESULTS / "study1_synthetic_model_terms.csv", index=False)
    rates = data.query("condition in ['DAI', 'SAI']").groupby("target_status")["incorporated_binary"].agg(["sum", "count", "mean"]).reset_index()
    rates.insert(0, "data_status", "SYNTHETIC_ONLY_NOT_EMPIRICAL")
    rates.to_csv(RESULTS / "study1_synthetic_primary_summary.csv", index=False)
    boot = bootstrap(data)
    (RESULTS / "study1_synthetic_bootstrap.json").write_text(json.dumps({"data_status": "SYNTHETIC_ONLY_NOT_EMPIRICAL", **boot}, indent=2), encoding="utf-8")
    labels = ["Matched foil", "Delivered target"]
    values = [rates.loc[rates.target_status.eq(0), "mean"].iat[0], rates.loc[rates.target_status.eq(1), "mean"].iat[0]]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, values, color=["#666666", "#0066aa"], edgecolor="black")
    ax.set_ylim(0, max(.2, max(values) * 1.3))
    ax.set_ylabel("Synthetic unit incorporation rate")
    ax.set_title("Synthetic-only dry run — not an empirical result")
    for i, value in enumerate(values): ax.text(i, value, f"{value:.3f}", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(FIGURES / "study1_synthetic_primary.png", dpi=180)
    print("Validated", len(data), "eligible synthetic unit rows")
    print(model_table.to_string(index=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"STUDY1_DRYRUN_FAILED: {exc}", file=sys.stderr)
        raise
