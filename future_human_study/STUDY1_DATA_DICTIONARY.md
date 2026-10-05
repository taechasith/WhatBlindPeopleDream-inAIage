# Study 1 analysis data dictionary

No actual Study 1 records exist. This dictionary defines the de-identified
analysis schema for use after ethics approval.

| Field | Meaning | Allowed/handling |
|---|---|---|
| participant_id | Random study ID | Kept separate from contact key |
| session_id / period / order | Scheduled visit and counterbalance fields | 1--4; retain deviations |
| condition | DAI, SAI, HUM, ANC | Never supplied to coders |
| stimulus_id | S01--S04 | Never supplied to coders |
| unit_id / target_status | Preregistered unit; delivered target=1 or foil=0 | Undelivered target excluded, not absent |
| report_eligible / report_status / reason | Primary-report validity | `ELIGIBLE`, `NO_RECALL`, or `INELIGIBLE`; no recall is missing outcome, never zero |
| ordinal_code / primary_binary | Blinded code and derived primary indicator | 0/1/2/3/9 per codebook |
| delivery metadata | word count, duration, model hash, TTS | manipulation checks; not primary-model covariates because they may be intervention components |
| delayed reconstruction / ratings | optional secondary outcomes | never collected before sleep; kept separate from primary coding |
| adverse_event / withdrawal | minimum event record | restricted access, per approval |

Raw audio, transcripts, allocation, consent, and contact links must never be
combined in a review-release dataset.
