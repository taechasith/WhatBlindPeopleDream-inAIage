# Study 1 simulation-based power analysis (planning only; no empirical inputs).
# Run with: Rscript code/power_study1.R --reps 1000 --slots 208 --workers 4
suppressPackageStartupMessages({library(lme4); library(parallel)})

args <- commandArgs(trailingOnly = TRUE)
arg_value <- function(flag, default) {
  index <- match(flag, args)
  if (is.na(index) || index == length(args)) return(default)
  as.numeric(args[index + 1])
}
reps <- as.integer(arg_value("--reps", 1000))
slots <- as.integer(arg_value("--slots", 208))
workers <- as.integer(arg_value("--workers", max(1, min(4, detectCores(logical = FALSE) - 1))))
outdir <- "results"
if (slots %% 16 != 0) stop("slots must be a multiple of 16 for exact counterbalance")

conditions <- c("DAI", "SAI", "HUM", "ANC")
stimuli <- c("S01", "S02", "S03", "S04")
williams <- list(c(1,2,4,3), c(2,3,1,4), c(3,4,2,1), c(4,1,3,2))
make_schedule <- function(n) {
  rows <- list(); k <- 0
  for (block in seq_len(n / 16)) for (co in seq_len(4)) for (so in seq_len(4)) {
    k <- k + 1
    rows[[k]] <- data.frame(participant=factor(k), period=1:4,
      condition=conditions[williams[[co]]], stimulus=stimuli[williams[[so]]],
      order=co, stringsAsFactors=FALSE)
  }
  do.call(rbind, rows)
}
schedule <- make_schedule(slots)

simulate_once <- function(scenario) {
  ids <- levels(schedule$participant)
  participant_re <- rnorm(length(ids), 0, scenario$participant_sd)
  stimulus_re <- rnorm(4, 0, scenario$stimulus_sd)
  names(participant_re) <- ids; names(stimulus_re) <- stimuli
  dropout <- rbinom(length(ids), 1, scenario$dropout)
  cutoff <- sample(1:3, length(ids), replace=TRUE)
  names(dropout) <- names(cutoff) <- ids
  ai <- subset(schedule, condition %in% c("DAI", "SAI"))
  ai$available <- rbinom(nrow(ai), 1, 1 - scenario$missing_report) == 1
  ai$available <- ai$available & !(dropout[as.character(ai$participant)] == 1 & ai$period > cutoff[as.character(ai$participant)])
  ai <- subset(ai, available)
  if (nrow(ai) < 20 || length(unique(ai$participant)) < 10) return(c(p=NA_real_, n_effective=0))
  long <- do.call(rbind, lapply(c(0, 1), function(target) {
    eta <- qlogis(scenario$foil_probability) + participant_re[as.character(ai$participant)] +
      stimulus_re[ai$stimulus] + scenario$period_log_odds * (ai$period - 1) +
      log(scenario$target_or) * target
    data.frame(participant=ai$participant, period=ai$period, order=ai$order,
      condition=factor(ai$condition), stimulus=factor(ai$stimulus),
      target_status=target, hits=rbinom(nrow(ai), scenario$units_per_set, plogis(eta)),
      total=scenario$units_per_set)
  }))
  # The primary estimand averages the target--decoy contrast over the two AI
  # conditions.  Do not test the DAI reference-cell coefficient from an
  # interaction model: that would silently change the estimand.  The
  # interaction is a separately preregistered secondary analysis.
  fit <- try(suppressMessages(suppressWarnings(glmer(cbind(hits, total - hits) ~
      target_status + condition + period + order + stimulus +
      (1 | participant), data=long, family=binomial(), nAGQ=0,
      control=glmerControl(optimizer="nloptwrap", calc.derivs=FALSE)))), silent=TRUE)
  if (inherits(fit, "try-error") || !"target_status" %in% rownames(coef(summary(fit)))) return(c(p=NA_real_, n_effective=length(unique(long$participant))))
  c(p=coef(summary(fit))["target_status", "Pr(>|z|)"], n_effective=length(unique(long$participant)))
}

scenarios <- data.frame(
  scenario=c("small_sensitivity", "minimum_scientific_interest", "plausible_sensitivity"),
  foil_probability=c(.04, .04, .04), target_or=c(1.35, 1.50, 2.00),
  participant_sd=c(.65, .65, .65), stimulus_sd=c(.25, .25, .25),
  period_log_odds=c(0, 0, 0), missing_report=c(.20, .20, .20), dropout=c(.10, .10, .10),
  units_per_set=c(8, 8, 8), stringsAsFactors=FALSE)

cluster <- makeCluster(workers)
invisible(clusterEvalQ(cluster, suppressPackageStartupMessages(library(lme4))))
clusterExport(cluster, c("schedule", "simulate_once", "stimuli"), envir=environment())
clusterSetRNGStream(cluster, 20261005)
on.exit(stopCluster(cluster), add=TRUE)

results <- lapply(seq_len(nrow(scenarios)), function(i) {
  scenario <- as.list(scenarios[i,])
  runs <- parLapply(cluster, seq_len(reps), function(ignore, s) simulate_once(s), s=scenario)
  pvalues <- vapply(runs, `[[`, numeric(1), "p")
  effective <- vapply(runs, `[[`, numeric(1), "n_effective")
  successful <- !is.na(pvalues)
  power <- mean(pvalues[successful] < .05)
  data.frame(data_status="SIMULATED_PLANNING_ONLY_NOT_EMPIRICAL", scenario=scenario$scenario,
    enrolled_slots=slots, sessions_per_participant=4, ai_nights_per_participant=2,
    units_per_set=scenario$units_per_set, nominal_unit_rows=slots*2*2*scenario$units_per_set,
    foil_probability=scenario$foil_probability, target_odds_ratio=scenario$target_or,
    participant_random_intercept_sd=scenario$participant_sd, stimulus_generation_sd=scenario$stimulus_sd,
    missing_dream_report_rate=scenario$missing_report, dropout_rate=scenario$dropout,
    mean_effective_participants=mean(effective[successful]), simulation_repetitions=reps,
    successful_model_fits=sum(successful), power=power,
    monte_carlo_se=sqrt(power*(1-power)/sum(successful)), analysis="binomial_glmm_participant_RE_stimulus_fixed", seed=20261005)
})
results <- do.call(rbind, results)
dir.create(outdir, showWarnings=FALSE, recursive=TRUE)
write.csv(results, file.path(outdir, "power_scenarios.csv"), row.names=FALSE)
write.csv(results[, c("scenario", "enrolled_slots", "power", "monte_carlo_se")], file.path(outdir, "power_curve.csv"), row.names=FALSE)
writeLines(capture.output(sessionInfo()), file.path(outdir, "power_r_sessioninfo.txt"))
cat("Wrote power outputs with", reps, "repetitions and", workers, "workers.\n")
