# Protocol: Blind Dreams and AI-Mediated Accessibility

**Protocol ID:** BD-AI-CHI27-v1.0  
**Status:** Original v1 freeze retained as historical; active supporting scope amended 2026-10-09<br>
**Freeze date:** 2026-10-05 (Asia/Bangkok)  
**Target:** ACM CHI 2027 Posters, anonymous review version

## Scope and contribution boundary

This public-data study connects (A) blind dream phenomenology, (B) blind and
low-vision (BLV) waking sensory intent, and (C) AI-mediated accessibility text
with one Cognitive Sensing Ontology (CSO). It evaluates alignment among text and
reported sensory distributions, along with implications for agency, epistemic
autonomy, safety, dignity, privacy, and sensory pluralism.

The study does **not** test neural change, cognitive reprogramming, or whether AI
changes dreams. The pathway from repeated AI-mediated exposure to attention,
concept formation, imagery, or dream incorporation is a future longitudinal
hypothesis only.

### Active public-data-only scope (2026-10-09)

Current work is limited to reproducible, blinded computational measurement
using released public data and source-documented public human references. It
does not authorize new participant activity, new human coding, adjudication, an
Alternative Annotator Test (AltTest). Designated automated blinded scripts may
process protected artifacts for technical and robustness audits, but before
`CODED_DATA_FREEZE` they must not expose human-readable label substance, a
private condition mapping, or condition-level inspection, and RQ2--RQ5 are not
authorized. This is a blinding boundary, not a new human-coding or AltTest
requirement in the current scope.

Public-human calibration has a deliberately narrow meaning: a released human
label, rating, or reference may calibrate a named computational measure only at
the source's documented unit, provenance, and permitted use. It is not newly
collected coding and does not establish that a computational measurement is
equivalent to human semantic judgment, user experience, safety, or preference.

`future_human_validation/` is retained as a separate, non-active archive. Its
planned independent coding, adjudication, and AltTest protect possible future
human-study claims, but are not current prerequisites and cannot retroactively
turn a public-data computation into human-validated evidence.

## Historical full-program research questions

The questions below are retained for protocol provenance. They do not authorize
the current scope to run RQ2--RQ5 or to permit human-readable access to blinded
private artifacts.

- **RQ1 (dream sensory construction):** Across evidence-based congenital,
  early-onset, and late-onset blindness groups, how do expressed sensory,
  spatial, emotional, social, and threat-related structures differ in dream
  reports?
- **RQ2 (waking sensory intent):** What sensory and functional information do
  BLV people seek in released questions, image-capture, navigation, and
  description tasks?
- **RQ3 (AI sensory output):** What sensory, spatial, social, identity, safety,
  uncertainty, and agency-related information do released assistive-AI outputs
  provide, omit, overproduce, or label as unsupported where ground truth exists?
- **RQ4 (alignment):** How do blind dream expression, BLV intent, human
  accessibility descriptions, AI descriptions, and human-verified AI guidance
  align or diverge under the CSO?
- **RQ5 (social impact):** Which supported mismatches plausibly affect agency,
  epistemic autonomy, safety, dignity/social meaning, privacy, or sensory
  pluralism?
- **RQ6 (reciprocal programming):** Which human-to-AI grounding and AI-to-human
  information-exposure features are directly observable in released data, and
  which elements require future longitudinal research?

## Data eligibility and exclusions

### Include

1. Formally released, public research datasets or publications with a traceable
   source URL, provenance statement, and documented or verifiable use terms.
2. Dream evidence that reports blindness onset/history explicitly, or whose
   group is explicitly documented by the source. DreamBank records retain the
   source's pseudonymous identifier only.
3. BLV-originating questions, descriptions, preferences, and accessibility
   guidance whose release supports the intended research use.
4. Human descriptions, AI descriptions, and human-verified AI guidance that can
   be connected to a documented source and source type.
5. Literature estimates reported at a clear unit of analysis (participant,
   dream, or study estimate).

### Exclude

1. Newly scraped social-media posts, private content, or individual public posts
   without a released research-dataset context.
2. Records with an unverified license/terms status for reuse; retain an access
   log but do not place their text in the analysis corpus.
3. Dream records whose blindness-onset group must be inferred.
4. Studies that conflate participant prevalence, dream prevalence, and
   study-level percentages without enough information to retain their proper
   estimand.
5. Records with missing essential text, provenance, or duplicate identifiers.

## Population definitions

- **Congenitally blind:** only where source metadata states blindness at birth or
  equivalent congenital status.
- **Early-onset blind:** only where source supplies an onset age meeting its
  stated early-onset definition; preserve that definition verbatim.
- **Late-onset/acquired blind:** only where source states acquired/late blindness
  or an onset age meeting its stated late-onset definition.
- **Low vision / visually impaired / mixed PVI:** retained as separately labelled
  source populations; never silently pooled with blind groups.
- **Unknown onset:** retained only when otherwise eligible, with group
  `UNKNOWN_ONSET`; excluded from onset-group confirmatory contrasts.

## Units of observation

| Evidence layer | Primary unit | Clustering / denominator rule |
|---|---|---|
| Published dream studies | Reported estimate | Preserve whether participant-, dream-, or study-level; never convert silently. |
| DreamBank | Dream report | Cluster by pseudonymous dreamer and series where available. |
| BLV intent | Question / text item | Cluster by dataset; participant identity is not assumed available. |
| Accessibility descriptions | Description / guidance item | Retain dataset, task, human/AI origin, and gold/silver status. |
| Preference evidence | Released rating/judgment | Preserve rater population and rating unit. |

## Active computational measurement outputs

1. Provenance, coverage, and reproducibility receipts for eligible public-data
   inputs and blinded computational measurement artifacts.
2. Pre-specified computational measurement, robustness, and non-estimability
   summaries that remain blinded and source-bounded.
3. Source-specific public-human calibration summaries only where a released
   human reference is available and its unit, provenance, and comparison target
   are documented.
4. Explicit exclusions and limits showing what the measurement cannot establish,
   including human semantic agreement, participant experience, causal effects,
   and RQ2--RQ5 findings.

## Historical full-program primary outcomes

The outcomes below remain part of the preserved v1 record. They are not active
execution authorization under the public-data-only scope.

1. CSO category prevalence and normalized frequencies for each eligible corpus
   and onset group, with uncertainty at its actual unit of observation.
2. Pairwise distributional alignment of CSO profiles using Jensen-Shannon
   divergence, cosine similarity, Hellinger distance, and category-level
   differences with bootstrapped confidence intervals.
3. AI-versus-human and AI-versus-human-verified differences in task relevance,
   spatial relation, safety, uncertainty, identity inference, and unsupported
   information when the source supports the comparison.
4. Human-to-AI Grounding Score components: intent match, task relevance, spatial
   actionability, safety relevance, uncertainty calibration, and preference
   agreement. Components remain separately reported unless a pre-specified,
   justified composite is feasible.

## Historical secondary and exploratory outcomes

- Dream nightmare/threat, affect, social interaction, locomotion, memory, and
  imagination markers.
- AI-to-Human Sensory Exposure Profile (AHSEP): a descriptive profile of what
  sensory information AI makes available; it is not a cognitive-change score.
- Legacy weighted-mean reproduction of prior aggregate logic, clearly labelled
  exploratory/legacy comparison.
- Vocabulary-sensitive and text-length-controlled variants; data-source,
  language, geography, task, and collection-method strata.
- Any new composite score, model-assisted label, or post-freeze subgroup is
  exploratory unless logged before outcome interpretation in `logs/deviations.md`.

## Hypothesis and inference discipline

This is primarily a descriptive and comparative public-data audit, not a test of
a single directional causal hypothesis. Confirmatory analyses test pre-specified
differences and alignment metrics only when the applicable active scope and
source documentation support them. Current computational measurements are
bounded by the public-human calibration rule above; they neither require new
human coding nor an AltTest, and RQ2--RQ5 remain blocked only until the
current `CODED_DATA_FREEZE` is committed. Statistical similarity is not
cognitive transfer; an observed mismatch is not measured harm; association is
not causation.

## Freeze and amendment rule

No primary outcome, population definition, ontology definition, or analysis
family may change after outcome inspection. A necessary change must be appended
to `logs/deviations.md` with date, original plan, new plan, reason, whether any
relevant result was already seen, and confirmatory/exploratory status.

The 2026-10-09 amendment constrains current execution to the public-data-only
boundary; it preserves rather than silently revises the historical v1 record.
