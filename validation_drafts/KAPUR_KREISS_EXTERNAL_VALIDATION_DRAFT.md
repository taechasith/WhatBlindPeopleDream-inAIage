# Draft: Kapur--Kreiss external validation plan

**Status:** design draft only. No model output has been joined to these ratings.

## Purpose

Test whether a pre-specified accessibility-alignment metric tracks existing
released BLV rating differences within the Kapur--Kreiss comparison tasks. This
is construct validation for a metric in that dataset's context; it is not a new
BLV preference study and does not establish that every output condition is
preferred.

## Candidate procedure

1. Use only the locally acquired, version-pinned released rating files.
2. Define metric direction before calculating associations: higher task
   relevance/grounded spatial information and lower unsupported identity/social
   inference are hypothesized to be more aligned, but only if those fields have
   an approved label/reference basis.
3. Reproduce the dataset's comparison unit and estimate rank/correlation or a
   paired discrimination statistic with bootstrap confidence intervals.
4. Run context-sensitive and different-context files separately; never pool
   them as independent BLV participants.
5. Treat any metric fit as external construct evidence restricted to these
   released references and rating population.

## Nonclaims

- No causal claim about prompt condition or user benefit.
- No inference that the ratings represent all blind/low-vision users.
- No substitution of automated metric values for human-coded validity.

## Planned outputs

`results/kapur_kreiss_metric_validation.csv` with dataset, metric, comparison
unit, N, effect/association, bootstrap interval, and `NOT_ESTIMABLE` reasons.
