# Closest-work audit: public-data intervention scope

**Search/update freeze:** 2026-10-06 (Asia/Bangkok)  
**Decision:** five or more direct comparators are identified before acquiring the
new intervention corpus. This addendum supplements, rather than overwrites,
`CLOSEST_WORK.md`.

| Closest work | What it establishes | What the current study adds, if completed |
| --- | --- | --- |
| VizWiz-VQA (Gurari et al.) | Real image-question pairs originating from blind people, with answerability and crowdsourced answers | A frozen within-item test of what changes when the originating question and accessibility policy are supplied to the same VLM, rather than only benchmark answer accuracy. |
| VizWiz-Captions | Human captions for images originating from blind people | Separates human caption similarity from question-specific alignment; captions are a reference distribution, not an automatic accessibility gold standard. |
| Mohanbabu & Pavel (2024) | Context-sensitive accessible descriptions | Tests prompt-conditioned output changes at scale with actual released BLV questions and a shared sensory/spatial/uncertainty ontology. |
| Kapur & Kreiss (2024) | Generic reference metrics can misrepresent BLV image-description preferences | Uses released preference material as external construct validation, rather than claiming that similarity/divergence itself equals accessibility. |
| Xie et al. (2025) | Real PVI interaction with LMM descriptions exposes intent and context failures | Uses their released material only as ecological context, then tests an observable prompt intervention rather than generalizing from a small shared-description corpus. |
| GuideDog (2026) | Human-verified and VLM-generated BLV guidance, including spatial/depth focus | Treats gold/silver data as a separate external validation layer, conditional on authorized gated access; it does not combine dream expression and BLV-originating question intent. |
| Kang et al. (2023) | Sensory-language differences in blind dream reports | Retains dream expression as a bounded historical reference space and directly tests whether its resemblance to AI text predicts accessibility-alignment measures. |

## Defensible novelty boundary

Do not claim to be first for blind dreams, BLV VQA, image descriptions, prompt
engineering, or accessibility evaluation. The proposed contribution is the
combination of (1) a frozen, pre-specified within-item intervention using actual
BLV-originating question context, (2) external preference/verified-guidance
validation, and (3) a clearly noncausal comparison to blind dream expression.

## Gate outcome

**PASS FOR PUBLIC-DATA ACQUISITION, subject to each source's recorded terms.**
The unresolved GuideDog gate does not block the primary VizWiz intervention; it
blocks only the planned GuideDog gold/silver validation.
