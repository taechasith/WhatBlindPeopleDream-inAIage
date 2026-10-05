# Study 1 simulation-based power analysis. Requires R >=4.3, lme4, dplyr.
# Scenarios are planning assumptions, not data or estimates from Study 0.
suppressPackageStartupMessages({library(lme4); library(dplyr)})
set.seed(20261006)
simulate_once <- function(n, p_foil, odds_ratio, missing_rate) {
  design <- expand.grid(participant=factor(seq_len(n)), period=1:2,
                        target_status=0:1, unit=1:8)
  participant_re <- rnorm(n, 0, .65)
  design$re <- participant_re[as.integer(design$participant)]
  design$missing_report <- rbinom(nrow(design), 1, missing_rate)
  eta <- qlogis(p_foil) + design$re + log(odds_ratio) * design$target_status
  design$incorporated <- rbinom(nrow(design), 1, plogis(eta))
  dat <- subset(design, missing_report == 0)
  fit <- suppressMessages(suppressWarnings(glmer(incorporated ~ target_status + period +
    (1|participant), data=dat, family=binomial(), nAGQ=0,
    control=glmerControl(optimizer="nloptwrap", calc.derivs=FALSE)))
  )
  coef(summary(fit))["target_status", "Pr(>|z|)"] < .05 &&
    fixef(fit)["target_status"] > 0
}
scenarios <- expand.grid(scenario=c("minimal_scientific_interest","conservative","moderate"),
  participants=c(40,60,80,100,120), stringsAsFactors=FALSE) |>
  mutate(foil_probability=.04, target_odds_ratio=c(1.5,2,3)[match(scenario,
  c("minimal_scientific_interest","conservative","moderate"))],
  random_intercept_sd=.65, missing_dream_report_rate=.20, dropout_assumption=.10,
  simulation_repetitions=50)
results <- scenarios |>
  rowwise() |>
  mutate(power=mean(replicate(simulation_repetitions,
    simulate_once(participants, foil_probability, target_odds_ratio,
    missing_dream_report_rate)))) |>
  ungroup() |>
  mutate(data_status="SIMULATED_PLANNING_ONLY_NOT_EMPIRICAL",
  analysis="logistic_mixed_model", ai_nights_per_participant=2,
  semantic_units_per_ai_night=8,
  total_nominal_unit_observations=participants*2*16)
write.csv(results, "results/power_scenarios.csv", row.names=FALSE)
write.csv(select(results, scenario, participants, power), "results/power_curve.csv", row.names=FALSE)
