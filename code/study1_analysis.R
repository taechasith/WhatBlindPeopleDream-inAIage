# Study 1 confirmatory-analysis implementation and synthetic dry-run.
# Default invocation accepts only explicitly synthetic fixtures:
#   $env:R_LIBS_USER='C:/Users/HP OMEN/Documents/R/win-library/4.6'
#   & 'C:/Program Files/R/R-4.6.1/bin/Rscript.exe' code/study1_analysis.R --bootstrap 100
#
# Empirical analysis is deliberately refused unless a later ethics gate is
# documented and --allow-real-data is explicitly supplied. This program does
# not recruit, contact, or create participant data.

suppressPackageStartupMessages(library(lme4))

args <- commandArgs(trailingOnly = TRUE)
arg_value <- function(flag, default = NULL) {
  index <- match(flag, args)
  if (is.na(index) || index == length(args)) return(default)
  args[index + 1]
}
has_flag <- function(flag) flag %in% args

root <- normalizePath(file.path(dirname(commandArgs()[grep("--file=", commandArgs())]), ".."), winslash = "/", mustWork = TRUE)
input <- arg_value("--input", file.path(root, "synthetic", "study1_synthetic_unit_data.csv"))
outdir <- arg_value("--output-dir", file.path(root, "results"))
bootstrap_repetitions <- as.integer(arg_value("--bootstrap", "500"))
allow_real_data <- has_flag("--allow-real-data")
synthetic_status <- "SYNTHETIC_ONLY_NOT_EMPIRICAL"
dir.create(outdir, recursive = TRUE, showWarnings = FALSE)

approval_documented <- function() {
  path <- file.path(root, "ethics", "ETHICS_STATUS.md")
  if (!file.exists(path)) return(FALSE)
  any(grepl("^Status:[[:space:]]*(APPROVED|EXEMPT_DETERMINATION|DETERMINED_NOT_HUMAN_SUBJECTS)\\b", readLines(path, warn = FALSE)))
}

required <- c("data_status", "participant_id", "session_id", "condition", "period", "order",
              "stimulus_id", "unit_id", "target_status", "report_eligible", "report_status",
              "ordinal_code", "primary_binary", "delivered_word_count")
data <- read.csv(input, na.strings = c("", "NA"), stringsAsFactors = FALSE, check.names = FALSE)
missing <- setdiff(required, names(data))
if (length(missing)) stop("Missing required columns: ", paste(missing, collapse = ", "))
statuses <- unique(na.omit(as.character(data$data_status)))
if (!length(statuses)) stop("data_status is empty")
is_synthetic <- length(statuses) == 1 && statuses[[1]] == synthetic_status
if (!is_synthetic && !allow_real_data) stop("Refusing non-synthetic data without --allow-real-data")
if (!is_synthetic && !approval_documented()) stop("Refusing non-synthetic data: authoritative ethics approval is not documented")
if (!all(data$condition %in% c("DAI", "SAI", "HUM", "ANC"))) stop("Unknown condition")
if (!all(data$target_status %in% c(0, 1))) stop("target_status must be 0/1")
if (!all(data$report_eligible %in% c(0, 1))) stop("report_eligible must be 0/1")
if (!all(na.omit(data$ordinal_code) %in% c(0, 1, 2, 3, 9))) stop("Invalid ordinal code")
if (!all(na.omit(data$primary_binary) %in% c(0, 1))) stop("Invalid primary binary")
if (!all(data$report_status %in% c("ELIGIBLE", "NO_RECALL", "INELIGIBLE"))) stop("Invalid report_status")

mapped <- rep(NA_real_, nrow(data))
mapped[data$ordinal_code == 0] <- 0
mapped[data$ordinal_code %in% c(2, 3)] <- 1
must_match <- !is.na(mapped)
if (any(data$primary_binary[must_match] != mapped[must_match])) stop("primary_binary disagrees with frozen ordinal-code mapping")
if (any(!is.na(data$primary_binary[data$ordinal_code %in% c(1, 9)]))) stop("Codes 1 and 9 must be missing in primary outcome")
if (any(is.na(data$ordinal_code[data$report_status == "ELIGIBLE"]))) stop("ELIGIBLE reports require ordinal coding")
if (any(!is.na(data$primary_binary[data$report_status == "NO_RECALL"]))) stop("NO_RECALL must be missing, not absent")

flow <- data.frame(
  data_status = statuses[[1]],
  stage = c("input_unit_rows", "AI_condition_unit_rows", "eligible_report_unit_rows", "primary_decidable_unit_rows"),
  n_unit_rows = c(
    nrow(data),
    sum(data$condition %in% c("DAI", "SAI")),
    sum(data$condition %in% c("DAI", "SAI") & data$report_status == "ELIGIBLE" & data$report_eligible == 1),
    sum(data$condition %in% c("DAI", "SAI") & data$report_status == "ELIGIBLE" & data$report_eligible == 1 & data$ordinal_code %in% c(0, 2, 3))
  )
)
write.csv(flow, file.path(outdir, if (is_synthetic) "study1_r_synthetic_exclusion_flow.csv" else "study1_empirical_exclusion_flow.csv"), row.names = FALSE)

primary <- subset(data, condition %in% c("DAI", "SAI") & report_status == "ELIGIBLE" & report_eligible == 1 & ordinal_code %in% c(0, 2, 3))
if (!nrow(primary)) stop("No primary-decidable unit rows")
primary$condition <- factor(primary$condition, levels = c("DAI", "SAI"))
primary$stimulus_id <- factor(primary$stimulus_id)
primary$participant_id <- factor(primary$participant_id)
primary$period <- factor(primary$period)
primary$order <- factor(primary$order)

# Primary estimand: target--decoy contrast averaged over the two AI conditions.
# Stimulus is fixed because the study uses only four source stimuli. The
# target-by-condition interaction is deliberately absent here; it is secondary.
formula_primary <- primary_binary ~ target_status + condition + period + order + stimulus_id + (1 | participant_id)
fit <- glmer(formula_primary, data = primary, family = binomial(), nAGQ = 0,
             control = glmerControl(optimizer = "nloptwrap", calc.derivs = FALSE))
coefs <- as.data.frame(coef(summary(fit)))
coefs$term <- rownames(coefs)
rownames(coefs) <- NULL
p_column <- grep("^Pr\\(", names(coefs), value = TRUE)
if (length(p_column) != 1) stop("Could not identify the model p-value column")
names(coefs)[names(coefs) == p_column] <- "p_value"
ci <- suppressMessages(confint(fit, method = "Wald"))
coefs$ci95_low <- ci[coefs$term, 1]
coefs$ci95_high <- ci[coefs$term, 2]
coefs$odds_ratio <- exp(coefs$Estimate)
coefs$data_status <- statuses[[1]]
coefs <- coefs[, c("data_status", "term", setdiff(names(coefs), c("data_status", "term")))]

new_decoy <- primary
new_target <- primary
new_decoy$target_status <- 0
new_target$target_status <- 1
predicted_difference <- mean(plogis(predict(fit, newdata = new_target, re.form = NA)) - plogis(predict(fit, newdata = new_decoy, re.form = NA)))
target_row <- coefs[coefs$term == "target_status", , drop = FALSE]
estimate <- data.frame(
  data_status = statuses[[1]],
  estimand = "AI_average_target_vs_matched_decoy_odds_ratio",
  estimate_log_odds = target_row$Estimate,
  odds_ratio = target_row$odds_ratio,
  ci95_low_log_odds = target_row$ci95_low,
  ci95_high_log_odds = target_row$ci95_high,
  p_value = target_row$p_value,
  model_based_probability_difference = predicted_difference,
  n_participants = length(unique(primary$participant_id)),
  n_unit_rows = nrow(primary),
  singular_fit = isSingular(fit, tol = 1e-4),
  stringsAsFactors = FALSE
)

# Participant-cluster bootstrap. It estimates interval uncertainty without
# treating semantic units from the same person as independent participants.
bootstrap_once <- function(seed) {
  set.seed(seed)
  ids <- unique(as.character(primary$participant_id))
  selected <- sample(ids, length(ids), replace = TRUE)
  pieces <- lapply(seq_along(selected), function(i) {
    piece <- primary[as.character(primary$participant_id) == selected[[i]], , drop = FALSE]
    piece$participant_boot <- factor(paste0(selected[[i]], "_copy", i))
    piece
  })
  boot <- do.call(rbind, pieces)
  result <- try(suppressMessages(suppressWarnings(glmer(
    primary_binary ~ target_status + condition + period + order + stimulus_id + (1 | participant_boot),
    data = boot, family = binomial(), nAGQ = 0,
    control = glmerControl(optimizer = "nloptwrap", calc.derivs = FALSE)
  ))), silent = TRUE)
  if (inherits(result, "try-error")) return(c(log_odds = NA_real_, odds_ratio = NA_real_))
  beta <- fixef(result)[["target_status"]]
  c(log_odds = beta, odds_ratio = exp(beta))
}
if (bootstrap_repetitions < 20) stop("Use at least 20 bootstrap repetitions")
boot <- t(vapply(seq_len(bootstrap_repetitions), function(i) bootstrap_once(20261005 + i), numeric(2)))
bootstrap <- data.frame(data_status = statuses[[1]], replicate = seq_len(bootstrap_repetitions), boot)
successful <- !is.na(bootstrap$odds_ratio)
bootstrap_summary <- data.frame(
  data_status = statuses[[1]],
  bootstrap_repetitions_requested = bootstrap_repetitions,
  successful_replicates = sum(successful),
  odds_ratio_ci95_low = unname(quantile(bootstrap$odds_ratio[successful], 0.025)),
  odds_ratio_ci95_high = unname(quantile(bootstrap$odds_ratio[successful], 0.975)),
  stringsAsFactors = FALSE
)

prefix <- if (is_synthetic) "study1_r_synthetic" else "study1_empirical"
write.csv(coefs, file.path(outdir, paste0(prefix, "_model_terms.csv")), row.names = FALSE)
write.csv(estimate, file.path(outdir, paste0(prefix, "_primary_estimate.csv")), row.names = FALSE)
write.csv(bootstrap, file.path(outdir, paste0(prefix, "_cluster_bootstrap.csv")), row.names = FALSE)
write.csv(bootstrap_summary, file.path(outdir, paste0(prefix, "_cluster_bootstrap_summary.csv")), row.names = FALSE)
writeLines(capture.output(sessionInfo()), file.path(outdir, paste0(prefix, "_sessioninfo.txt")))
cat("Wrote ", prefix, " outputs; status=", statuses[[1]], "; primary rows=", nrow(primary), "\n", sep = "")
