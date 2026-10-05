# Study 1 power analysis plan

## Status

`code/power_study1.R` is the authoritative simulation specification for the
preregistered logistic mixed-effects model. It was executed locally with R 4.6.1
and lme4. The current R grid contains 40--120 participants with 50 repetitions;
its result must be expanded and re-run after the ethics-approved protocol locks
the final model, stimuli, and missingness assumptions.

`code/power_study1.py` was also executed as a fast, transparent planning proxy using
participant-level paired rate contrasts. It simulates participant random
intercepts and session-level missing reports, but it is not a replacement for the
R mixed-model simulation. Its CSV outputs are planning scenarios—not empirical
findings and not a sample-size authorization.

## Assumptions

No effect was derived from Study 0's Jensen--Shannon divergence. Scenarios use a
4% false-source foil-unit base rate, participant random-intercept SD 0.65, two
AI nights/participant, eight target and eight foil units/night, 20% missing
dream-report rate, 10% potential attrition, and 1,000 repetitions. The
scientifically meaningful scenario is target-vs-foil odds ratio 1.5; conservative
and moderate scenarios use 2.0 and 3.0 respectively. These are deliberately
assumed planning values, not estimates.

## Executed outputs and precision

`results/power_scenarios.csv` and `results/power_curve.csv` are the R GLMM
simulation output. The first completed 50-repetition diagnostic run gave primary
power 0.34/0.42/0.54/0.58/0.62 for the OR=1.5 scenario at 40/60/80/100/120;
this low-precision diagnostic shows that 120 is not adequate for the smallest
planning scenario. A separate 1,000-repetition Python proxy at N=200 returned
0.944 for OR=1.5 and 1.000 for OR=2.0; it is a planning cross-check, not the
authoritative GLMM estimate. These are planning simulations, not clinical or
empirical claims.

## Decision boundary

The provisional design target is **200 enrolled participants** (50 complete
Latin-square blocks), anticipating about 180 completing all sessions under the
10% attrition planning assumption. This target preserves a margin above the
smallest-effect proxy, but is not an empirical claim. Before recruitment, rerun
the expanded R GLMM simulation with at least 1,000 repetitions, inspect
convergence, and either retain or increase the target; the R model controls if
it disagrees materially with the proxy.
