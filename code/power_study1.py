"""Synthetic simulation scenarios for Study 1 planning; no empirical effect is used."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
RNG = np.random.default_rng(20261006)


def simulate_power(n_participants: int, foil_probability: float, odds_ratio: float, missing_rate: float, repetitions: int = 1000) -> float:
    # Participant random intercept SD .65 and eight target/foil units per AI
    # session. Analysis is a paired participant-level contrast approximation;
    # final inference is the preregistered logistic mixed model in R.
    target_logit_offset = np.log(odds_ratio)
    intercepts = RNG.normal(0, .65, size=(repetitions, n_participants, 1, 1, 1))
    status = np.array([0, 1])[None, None, None, :, None]
    probability = 1 / (1 + np.exp(-(np.log(foil_probability/(1-foil_probability)) + intercepts + status*target_logit_offset)))
    outcomes = RNG.binomial(1, probability, size=(repetitions, n_participants, 2, 2, 8))
    observed_night = RNG.random((repetitions, n_participants, 2, 1, 1)) >= missing_rate
    numerator = (outcomes * observed_night).sum(axis=(2, 4))
    denominator = observed_night.sum(axis=(2, 3, 4)) * 8
    rates = numerator / np.where(denominator == 0, np.nan, denominator)[:, :, None]
    differences = rates[:, :, 1] - rates[:, :, 0]
    pvalues = ttest_1samp(differences, 0.0, axis=1, alternative="greater", nan_policy="omit").pvalue
    return float(np.mean(pvalues < .05))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    rows = []
    for scenario, foil_probability, odds_ratio in [("minimal_scientific_interest", .04, 1.5), ("conservative", .04, 2.0), ("moderate", .04, 3.0)]:
        for n in [40, 60, 80, 100, 120]:
            power = simulate_power(n, foil_probability, odds_ratio, .20)
            rows.append({"data_status": "SIMULATED_PLANNING_ONLY_NOT_EMPIRICAL", "scenario": scenario, "participants": n, "ai_nights_per_participant": 2, "semantic_units_per_ai_night": 8, "total_nominal_unit_observations": n*2*16, "foil_probability": foil_probability, "target_odds_ratio": odds_ratio, "random_intercept_sd": .65, "missing_dream_report_rate": .20, "dropout_assumption": .10, "simulation_repetitions": 1000, "power": power, "analysis": "paired_participant_rate_contrast_approximation"})
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "power_scenarios.csv", index=False)
    table[["scenario", "participants", "power"]].to_csv(OUT / "power_curve.csv", index=False)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()
