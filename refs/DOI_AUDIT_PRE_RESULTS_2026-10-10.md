# Pre-results DOI and reference audit

**Audit date:** 2026-10-10 (Asia/Bangkok)
**Scope:** bibliographic metadata and evidence-status audit only.
**Status:** `PASS_WITH_REPAIRS` for the 26 records in `refs/doi_audit.csv`.

## Blinding and scope statement

This audit did not read the private condition mapping, synthetic-label content by
condition, RQ2--RQ5 tables, or any model-output effect. It did not alter a
prompt, sample, model, ontology, output, analysis plan, anonymous manuscript,
or poster. It repairs only auditable citation metadata and evidence-status
language before the public-data results are interpreted.

## Method

For journal and ACM records, title, publication year, venue, and DOI resolution
were cross-checked against the DOI metadata supplied by Crossref and, where
relevant, the publisher, PubMed, PLOS, ScienceDirect, or Oxford Academic.
ACL records were checked against ACL Anthology/DOI metadata. The Gonzalez
Penuela record is registered by DataCite rather than Crossref and was checked
against its arXiv DOI metadata and the official CV4A11y programme.

`PASS` in the CSV means that the bibliographic record resolved and its
classification below is appropriate. It does **not** establish that a dataset is
locally accessible, licensed for redistribution, or suitable as same-item
human ground truth. Those questions remain governed by the source gate and
public-human calibration matrix.

## Repaired records

| ID | Verified record / correction | Correct evidence boundary |
| --- | --- | --- |
| `ORTIZ2011` | Corrected the DOI from `10.1371/journal.pone.0023275` to `10.1371/journal.pone.0023264`: *Recruitment of Occipital Cortex during Sensory Substitution Training Linked to Subjective Experience of Seeing in People with Blindness* (PLOS ONE, 2011). The former DOI resolves to an unrelated rat-neuroscience article. | Mechanistic sensory-substitution context only; it is not evidence about assistive AI, natural-language descriptions, dreams, or a general neural effect. |
| `GONZALEZ2025` | DataCite classifies `10.48550/arXiv.2510.01576` as an arXiv **preprint**. The official CV4A11y programme lists a presentation, but no archival proceedings record was verified. | Closest-work/context citation only. Do not call it a peer-reviewed workshop article or use it to claim priority for BLV-question steering. |
| `NEUROIMAGE2025` | *Long-term visual-to-tactile stimulation induces functional reorganization of thalamic pathways to achieve visual perception* appears in **NeuroImage 325 (2026)**; the online/DOI date is 2025. | Historical future-human-study mechanism context only. Cite the 2026 issue year if cited. |
| `PALMIERI2026` | *Incorporation of complex narratives into dreaming* appears in **SLEEP 49(2) (2026)**; Crossref also exposes a 2025 online date. | Presleep narrative/dream-incorporation method precedent only; not BLV-specific or AI-specific evidence. |
| `ENVISAGE2026` | Added `10.1016/j.patcog.2026.114298`: *ENVISAGE: An image captioning dataset and conformal uncertainty modeling framework to assist visually impaired individuals* (Pattern Recognition, 2026). | Bibliographic inclusion does not override the local data-source gate or establish usable dataset access. |
| `NEUROIMAGE2024` | Added `10.1016/j.neuroimage.2024.120621`: *Visual Mental Imagery and Neural Dynamics of Sensory Substitution in the Blindfolded Subjects* (NeuroImage, 2024). | Blindfolded-sighted mechanism context only; not blind-participant dream or AI-description outcome evidence. |
| `GARG2026` | Corrected the stored full title to *“It's trained by non-disabled people”: Evaluating How Image Quality Affects Product Captioning with Vision-Language Models* (CHI 2026). | Peer-reviewed CHI comparator; no question-steering or dream claim follows from it. |

## Protocol-versus-results classification checks

| Status | Records | Submission rule |
| --- | --- | --- |
| Completed peer-reviewed empirical study | Kang 2023; Meaidi 2014; van der Heijden 2024; Mohanbabu & Pavel 2024; Xie 2025; Karamolegkou et al. 2025; GuideDog 2026; He et al. 2026; SceneScout 2026; Gonzalez Penuela et al. 2026; Garg et al. 2026; Doore et al. 2024; Zur et al. 2024; Pataranutaporn et al. 2025. | State only the result, population, and task the individual source actually reports. None licenses a claim that the current VLM changes cognition or dreams. |
| Peer-reviewed workshop article | Kapur & Kreiss 2024. | Identify its workshop status and use its released preference data only for bounded external validation. It is not same-item annotation of the current outputs. |
| Protocol, not completed outcome study | Vitali et al. / `BLINDREAM2025`. | May motivate future work and describe protocol context; never cite as completed dream/spatial outcome evidence. |
| Systematic review | Ilic et al. 2023. | Synthesis/context only; do not treat review-level evidence as raw participant or dream observations. |
| Methodological precedent, outside current causal scope | Ortiz et al. 2011; Striem-Amit et al. 2012; NeuroImage 2024; NeuroImage 2026; Palmieri et al. 2026. | Maintain the explicit boundary: mechanistic plausibility or method precedent is not evidence that AI changes blind cognition, brains, or dreams. |
| Preprint | Gonzalez Penuela et al. 2025. | Cite only with a preprint label and do not treat it as peer-reviewed archival evidence. |
| Current-study method paper with no current critical-path role | Calderon et al. 2025. | The current study sets `ALT_TEST_CURRENT_STUDY = NOT_APPLICABLE_TO_CURRENT_DESIGN`; retaining the citation does not activate an Alt-Test claim. |

## Verification sources

- [Crossref works API](https://api.crossref.org/) for journal, ACM, ACL-DOI,
  and PNAS bibliographic metadata.
- [DataCite DOI metadata](https://api.datacite.org/dois/10.48550/arXiv.2510.01576)
  and the [official CV4A11y 2025 programme](https://cv4a11y.github.io/ICCV2025/)
  for `GONZALEZ2025`.
- [PLOS record for Ortiz et al.](https://doi.org/10.1371/journal.pone.0023264)
  and the unrelated former DOI
  [10.1371/journal.pone.0023275](https://doi.org/10.1371/journal.pone.0023275).
- [PubMed record for Palmieri et al.](https://pubmed.ncbi.nlm.nih.gov/40973163/)
  and [PubMed record for Ortiz-Teran et al.](https://pubmed.ncbi.nlm.nih.gov/41407217/)
  for issue-year reconciliation.
- [ACL Anthology](https://aclanthology.org/) for ACL venue and workshop/long-paper
  metadata.

## Result

The reference audit is clean after the repairs recorded above. Before drafting
the anonymous paper, generate the actual BibTeX only from these verified
records (and only for sources actually cited), preserve the classifications in
the prose, and rerun the DOI duplicate and anonymity checks.
