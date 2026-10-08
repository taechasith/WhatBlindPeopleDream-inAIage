# Ethics and data-use note

**Current status:** active secondary analysis of formally released public
research data. Documented local source acquisition and provenance are recorded
in `data/PUBLIC_DATA_SOURCE_GATE.csv` and `data/MANIFEST.csv`. No new human
subjects activity has been initiated.

## Study boundary

The active CHI-scope study is a secondary analysis of formally released public
research datasets and published evidence plus a deterministic local
image-question-to-model-output intervention. It does not recruit, contact,
intervene with, track, deceive, screen, consent, or collect data from people.
It does not scrape fresh social-media content, even when public. Released
research data are preferred over individual public posts.

## Population sensitivity and mitigations

Dream narratives and BLV-originating accessibility data are human-originating
and may contain sensitive personal, social, medical, location, image, or private
text information. The project will:

- retain only release-supported fields and the minimum text needed for analysis;
- never attempt re-identification or infer diagnosis/blindness onset;
- retain pseudonymous source identifiers only where required for clustering;
- avoid publishing source images and avoid reproducing sensitive dream excerpts;
- use paraphrases or short anonymized excerpts only where scientifically
  necessary and permitted;
- preserve blind, low-vision, congenital, acquired, and mixed populations as
  distinct labels;
- document source consent/release context, terms, and provenance before import;
- remove author-identifying material from every anonymous review artifact.

## License and access gate

Only sources recorded as current-use eligible in
`data/PUBLIC_DATA_SOURCE_GATE.csv` may enter the active study. Raw
content-bearing data stay local and are not distributed by default. Sources
with ambiguous terms, unavailable access, or incompatible research use are
excluded rather than silently substituted. GuideDog remains gated and has not
been downloaded or analyzed; no access control is bypassed.

## Institutional ethics determination

No local ethics/IRB determination has yet been documented. Before external
dissemination or any activity outside the released-data boundary, the research
team must obtain and record the applicable institutional determination (for
example, exempt/not-human-subjects/review-required) from the responsible
research environment. If a determination requires approval before secondary
analysis or independent human annotation, those activities pause at that point.
This record must include date, office, reference number if issued, scope, and
conditions; it must not appear in anonymized review materials if it would reveal
author identity.

## Risk framing

Corpus findings may support a plausible design risk but cannot establish injury,
harm, cognitive change, or causal dream change. Findings will be translated using
the social-impact matrix with explicit evidence strength and uncertainty.
