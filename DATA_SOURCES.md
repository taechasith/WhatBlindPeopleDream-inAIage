# Data source register

**Register status:** prospective sources frozen before download or inspection.  
**Rule:** `UNVERIFIED` means no data may enter the corpus until Phase 1/2 source
verification records the access date, license/terms, release context, and exact
retrieval method. An unavailable source is recorded as `ACCESS_UNAVAILABLE`.

| ID | Evidence layer | Source | Intended text unit | Prospective use | License / access status at freeze |
|---|---|---|---|---|---|
| DREAMBANK | Dream | https://dreambank.net/ and https://dreambank.net/grid.cgi | Dream report | Evidence-based blind-series corpus only | CC BY-NC-SA 4.0 reported in governing guide; verify on source before retrieval |
| KANG2023 | Dream | https://doi.org/10.3390/brainsci13101394 | Published estimate / replication anchor | Coding logic and reported evidence | UNVERIFIED |
| MEAIDI2014 | Dream | https://doi.org/10.1016/j.sleep.2013.12.008 | Published estimate | Group-level literature evidence only | UNVERIFIED |
| SENSATIONAL2024 | Dream method | https://doi.org/10.3390/brainsci14060533 | Published method/evidence | Measurement-method limitation | UNVERIFIED |
| BLINDREAM2025 | Dream method | https://doi.org/10.1371/journal.pone.0327521 | Protocol metadata | Context only; never outcome evidence unless completed results are separately verified | UNVERIFIED |
| VIZWIZ_VQA | BLV intent | https://vizwiz.org/tasks-and-datasets/vqa/ | Question text | BLV Intent Vector | UNVERIFIED |
| VIZWIZ_CAPTIONS | Human descriptions | https://vizwiz.org/tasks-and-datasets/image-captioning/ | Caption text | Human comparison layer | UNVERIFIED |
| VIZWIZ_PRIVACY | Privacy | https://vizwiz.org/tasks-and-datasets/vizwiz-priv/ | Released label/text if needed | Privacy subanalysis only | UNVERIFIED |
| XIE2025 | AI accessibility | https://doi.org/10.1145/3706598.3714210; https://github.com/see4vision/chi25_lmm | Released research text | AI-mediated accessibility evidence; no independent social-media scraping | UNVERIFIED |
| MOHANBABU2024 | AI accessibility | https://doi.org/10.1145/3663548.3675658 | Published evidence / released materials if available | Context-aware description comparison | UNVERIFIED |
| KAPURKREISS2024 | Preferences | https://aclanthology.org/2024.nlp4pi-1.26/; https://github.com/rkapur102/reference-based-bias | Preference ratings / text | BLV versus sighted metric-bias validation | UNVERIFIED |
| GUIDEDOG2026 | AI and verified guidance | https://aclanthology.org/2026.acl-long.251/; https://huggingface.co/datasets/kjunh/GuideDog | Guidance/description text | AI versus human-verified comparison | UNVERIFIED |
| ENVISAGE2026 | Accessibility captions | https://doi.org/10.1016/j.patcog.2026.114298; https://github.com/cayl-crypto/envisage_dataset | Caption/annotation text | Spatial and task-relevance comparison | UNVERIFIED |

## Mandatory per-source verification record

Before import, add a row to `data/literature/prisma_log.csv` or a source-specific
manifest recording: access date and URL, version/commit or archive checksum,
license/terms quote or locator, original consent/release context where supplied,
retrieval command, included fields, exclusions, and geographic/language scope.

## Data handling boundary

Raw data remain immutable beneath source-specific `raw/` directories and are
excluded from version control by default. Analysis text is stored independently
of images whenever images are unnecessary. No images, real names, or private
identifiers are copied into anonymous paper/poster/supplementary materials.
