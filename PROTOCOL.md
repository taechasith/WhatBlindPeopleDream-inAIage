# Protocol: Blind Dreams and AI-Mediated Accessibility

**Protocol ID:** BD-AI-CHI27-v1.0  
**Status:** Frozen before data acquisition and outcome inspection  
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

## Research questions

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

## Primary outcomes (confirmatory where data and validation gates permit)

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

## Secondary and exploratory outcomes

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
differences and alignment metrics conditional on the data, licensing, and human
annotation reliability gates. Statistical similarity is not cognitive transfer;
an observed mismatch is not measured harm; association is not causation.

## Freeze and amendment rule

No primary outcome, population definition, ontology definition, or analysis
family may change after outcome inspection. A necessary change must be appended
to `logs/deviations.md` with date, original plan, new plan, reason, whether any
relevant result was already seen, and confirmatory/exploratory status.
