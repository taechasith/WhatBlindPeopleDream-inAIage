# Study 1 power analysis

**Status:** `NONEMPIRICAL_PLANNING_SIMULATION_COMPLETE`
**Not an outcome analysis; no participant data exist.**

## Decision

The pre-ethics allocation configuration is **208 anonymous slots** (13 complete
four-condition-by-four-stimulus counterbalance blocks). It is powered for the
predefined minimum scientifically interesting target-versus-decoy odds ratio of
1.50 under the assumptions below, but is explicitly not powered to 80% for the
smaller 1.35 sensitivity scenario. This is a design decision, not evidence that
the target effect exists or has that magnitude.

## Authoritative simulation

`code/power_study1.R` was run on 2026-10-05 with:

```powershell
$env:R_LIBS_USER = 'C:/Users/HP OMEN/Documents/R/win-library/4.6'
& 'C:/Program Files/R/R-4.6.1/bin/Rscript.exe' code/power_study1.R --reps 1000 --slots 208 --workers 4
```

The output model is a binomial participant-random-intercept GLMM with the
primary AI-condition-averaged target-versus-decoy coefficient; condition,
period, order, and the four-level stimulus block are fixed effects. It does not
use the Study 0 Jensen--Shannon result as an effect-size estimate. Environment
details are in `results/power_r_sessioninfo.txt`.

| Scenario | Decoy incorporation probability | Target OR | Participant RE SD | Stimulus-generation SD | Missing report rate | Dropout rate | Mean effective participants | Simulations | Estimated power | Monte Carlo SE |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Small sensitivity | 0.04 | 1.35 | 0.65 | 0.25 | 0.20 | 0.10 | 193.15 | 1,000 | 0.669 | 0.0149 |
| Minimum scientific interest | 0.04 | 1.50 | 0.65 | 0.25 | 0.20 | 0.10 | 192.81 | 1,000 | 0.891 | 0.0099 |
| Plausible sensitivity | 0.04 | 2.00 | 0.65 | 0.25 | 0.20 | 0.10 | 192.86 | 1,000 | 1.000 | 0.0000 |

Each simulated participant has four sessions, including two AI sessions (DAI
and SAI). Each retained AI session contributes eight delivered target and eight
matched-decoy semantic-unit rows. The nominal pre-missingness primary unit-row
count is 6,656. All values are assumptions or simulation outputs, not observed
incorporation rates.

## Assumption rationale and limitations

- The 4% decoy rate and random-effect SDs are conservative planning values, not
  imported from Study 0 or from a blind-dream prevalence estimate.
- The OR=1.50 threshold is the minimum effect chosen for the prospective
  target-specific incorporation question; it is not a clinically validated
  threshold.
- The simulation treats the four source stimuli as fixed blocks in the primary
  model because a random effect with only four levels is unstable. A
  random-stimulus formulation is sensitivity-only if estimable.
- Clustered semantic units are handled with a participant random intercept in
  the primary model and a participant-cluster bootstrap in analysis. A
  report-level aggregation is also prespecified as a robustness check.
- The DAI-versus-SAI interaction, DAI-versus-HUM package comparison, ANC
  context comparison, and subgroup analyses are not individually powered
  confirmatory endpoints.

## Before recruitment

Repeat this exact simulation only if an ethics-required protocol amendment
changes the primary model, allocation structure, target/decoy unit count,
missing-data plan, or recruitment target. Preserve the prior result and log the
amendment; never tune the plan after viewing Study 1 outcomes.
