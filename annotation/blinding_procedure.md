# Study 1 blinded coding procedure

**Status:** non-deployed procedure for BD-AI-CHI27-Study1-v2.0. No real Study 1 participant data or coder labels exist. This procedure is activated only after ethics authorization, approved data-management controls, and a locked allocation/codebook version.

## Separation of roles

| Role | May access | Must not access |
|---|---|---|
| Data steward | consent-compatible study ID, session timing, condition/allocation, stimulus, delivery log, raw report/transcript, target/decoy mapping | coder decisions before lock except for file validation |
| Independent coder | blinded report ID, approved transcript, blinded unit ID, randomly relabeled Set A/Set B, codebook, coding template | participant identity, condition, order, stimulus, source, target/decoy truth, hypothesis direction, delivery transcript |
| Adjudicator | blinded discordant/undecidable cases, code definitions, anonymized rationales | allocation, source, participant identity, coder identity, hypothesis direction |
| Analyst | locked coding files, approved de-identified analysis data, predeclared model code | contact key; condition/allocation during independent coding and adjudication |
| Coordinator | enrollment/consent route and allocation assignment as approved | independent coding decisions and adjudication details before analysis lock |

One person may not combine roles when doing so would reveal both allocation and coder decisions. If staffing makes a separation impossible, pause the affected workflow and document the limitation before unblinding.

## Packet construction

1. The restricted data steward creates a random blind_report_id unrelated to participant, session, condition, or stimulus IDs.
2. The steward removes or redacts direct identifiers and unneeded third-party information from the coder-facing transcript under the approved privacy plan. The original protected record remains unchanged.
3. For each eligible report, the steward creates unit_blind_id values and assembles the delivered-unit set and matched decoy-unit set.
4. The steward randomly assigns the labels Set A and Set B independently for each report. The target/decoy key is stored separately from the coder packet.
5. The steward exports one coder packet per coder using annotation/coder_template.csv. Packets contain no condition, source, stimulus, sequence, or delivery fields.
6. The steward verifies that no filename, metadata field, file path, comment, hidden spreadsheet column, or transcript header reveals allocation information.

The packet must preserve report eligibility evidence and timing-status fields without revealing the underlying condition. A coder may mark a record ineligible only under codebook rules; the data steward later resolves administrative eligibility fields without altering coder labels.

## Coding and file control

Coders independently complete their own files. They must not share labels, rationales, screenshots, or real report excerpts with another coder outside the approved secure workflow. They return files to the restricted location specified by the approved data-management plan.

The data steward validates schema, duplicate keys, code range, missing required fields, and file hashes. Validation must not modify the submitted coder file. After both independent files are locked:

1. calculate the preregistered reliability measures on independent labels;
2. preserve original independent files read-only;
3. send only allowable discordant or code-9 cases to the blinded adjudicator;
4. retain adjudication in a new file with rationale, date, and codebook version; and
5. join target/decoy truth, condition, and allocation data only after coding and adjudication are locked.

## Blinding checks and deviations

Before each coding batch, the data steward completes a checklist confirming that:

- packet columns match the approved template;
- Set A/Set B labels are balanced and target/decoy mapping is absent;
- no condition/source/stimulus/order data are present;
- file names and metadata are de-identified;
- coder and adjudicator access permissions are separated; and
- the packet is associated with the correct codebook version.

If a coder is accidentally unblinded, receives a corrupted packet, recognizes a participant, or sees an allocation clue, stop coding that packet. Preserve the event record, notify the approved study lead, and apply the preregistered deviation/sensitivity rule. Do not silently relabel or replace the original record.

## Limits

Blinding reduces expectancy bias in semantic coding; it does not make dream reports objectively complete or establish that a target caused a dream. The primary outcome remains reported target-specific incorporation under the defined coding rules.
