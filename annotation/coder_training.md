# Study 1 coder training protocol

**Status:** preparation only. No coder has been recruited, trained, assigned a real report, or asked to generate labels through this document. It becomes operational only after the applicable ethics determination/approval, approved staffing, and locked blinded coding packet are in place.

## Purpose

This protocol prepares independent human coders to apply DREAM_INCORPORATION_CODEBOOK_v1.md consistently to blinded dream-report units. The role is to evaluate text/audio-transcript evidence, not to infer a participant's sensory history, condition, target scene, or the truth of an AI description.

No LLM, retrieval system, or automated classifier may be treated as a ground-truth coder.

## Required blinding

During training and coding, coders must not receive:

- participant names, contact information, demographic combinations, or onset labels;
- condition, session sequence, period, allocation order, or stimulus identity;
- source identity of the description;
- target/decoy truth or hypothesis direction;
- delivery transcripts, AI prompts, model metadata, or another coder's labels;
- adjudicated decisions before their own independent file is locked.

Coders may receive only the de-identified report, blinded unit ID, randomly relabeled Set A or Set B, codebook version, and the coding fields defined in annotation/coder_template.csv.

## Training materials

Training uses synthetic or otherwise ethics-approved nonparticipant examples only. Training material must be clearly labeled TRAINING_ONLY_NOT_EMPIRICAL and must never enter the Study 1 analysis dataset.

The data steward prepares examples spanning:

- no defensible unit reference (code 0);
- generic or competing-source material (code 1);
- defensible semantic incorporation (code 2);
- exact/unambiguous incorporation (code 3);
- unclear audio/transcript material (code 9);
- spatial relation, sensory transformation, emotional incorporation, novel recombination, and unsupported-inference flags;
- reports that are ineligible, no-recall, or lack verifiable timing.

Examples must not reveal actual target scenes or condition labels. They should include positive and negative examples for relational units, because an object without its required relation is not automatically a match.

## Training workflow

1. The data steward provides the current codebook, this protocol, the adjudication protocol, and synthetic practice packet.
2. Each coder completes the practice packet independently without discussing cases with another coder.
3. The trainer reviews codebook-rule questions using synthetic examples only. Do not change the codebook after viewing real condition-linked outcomes.
4. Each coder signs or otherwise records completion of the approved confidentiality, blinding, and conflict-of-interest requirements.
5. The data steward records codebook version, training material version, date, and completion status in a restricted training log.
6. If a coder identifies an ambiguity, add a prospective clarification with an example to the codebook/deviation record before real coding begins. Do not silently rewrite definitions.

Training agreement is a process check, not a Study 1 result and not a substitute for independent double-coding reliability on real eligible reports.

## Independent coding workflow

For real study records, coders work independently and use the ordinal scale exactly as defined in the codebook:

- 0 = absent;
- 1 = possible/ambiguous;
- 2 = semantic incorporation;
- 3 = exact incorporation;
- 9 = undecidable.

Coders do not decide whether a unit is a true target or decoy. They document the minimum textual evidence and any uncertainty in their rationale field. At least 20% of eligible reports, selected by the data steward using the preregistered stratification procedure, receive independent double coding before adjudication.

## Reliability and adjudication boundary

Independent coder files are locked before reliability calculation. The study reports raw agreement and the prespecified reliability statistics only when estimable; it must report NOT_ESTIMABLE rather than invent a value. The adjudicator receives discordant or undecidable cases only after independent files are preserved and reliability is calculated.

A coder must not adjudicate their own case, view allocation information, or communicate about unresolved real cases with another coder before lock. Any accidental unblinding, missing packet, technical failure, or protocol deviation is logged and evaluated under the preregistered sensitivity rules.
