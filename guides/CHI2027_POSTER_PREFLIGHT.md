# CHI 2027 Poster Preflight

Verified from official CHI/ACM sources on 10 October 2026. This is a submission-readiness note only: no study outcomes or `results/` files were examined.

## What CHI requires at initial submission

- Submit through PCS by **21 January 2027, Anywhere on Earth (AoE)**. The call also lists 18 February notification, 25 February e-rights, 4 March TAPS source submission, and 18 March publication-ready/video deadlines.
- Submit an **anonymous**, single-column ACM Master Article Template extended abstract of **at most four pages excluding references**. For LaTeX, CHI specifies `\documentclass[manuscript,review,anonymous]{acmart}`; submit both the review PDF and source files.
- Submit an **A0 poster** as part of the same submission, plus Key Discussion Points. The poster needs a title, concise research overview, clear illustrations, and a compelling visual design. An appendix (separate file) and supplementary material are optional; neither may contain information essential to understanding the paper.
- Designate **four author review-responsibility slots** in PCS. They must be authors, must bid/update their PCS profiles, and failure to complete assigned reviews results in desk rejection.

## Anonymous-review checklist

- Remove author and institution identities from title/header areas, body text, acknowledgements, figures, external links, and document metadata. Do not merely hide author text with a color change.
- Cite prior/self work normally, in the third person. Do **not** replace citations with "anonymous"; the policy says that is grounds for desk rejection.
- The call says *submissions* must be anonymous. Because the A0 poster is required submission material, keep the review-stage poster free of author names, affiliations, contact details, logos, identifying images, and identifying URLs as well. The call does not provide a separate poster-anonymization exception.
- CHI asks for a short reviewer note describing the applicable human-subjects ethics context. It must be written without revealing institution, location, approval-board identity, grant, partner, or protocol details that identify the authors.

## Other mandatory constraints

- Follow ACM's authorship/AI policy and describe AI use that is directly relevant to research methods, data, code, analyses, or results as required by that policy.
- Follow SIGCHI accessibility guidance for both the manuscript and visual materials.
- Submission metadata is fixed at the deadline for author additions/removals and affiliations. Title changes require chair approval.
- The submission cannot include sensitive, private, or proprietary material that cannot be disclosed at publication.

## If accepted

- Submit publication-ready source to TAPS. The accepted extended abstract must be double-column and remain within **four pages excluding references**; appendices are not allowed, although supplementary material may be uploaded.
- Upload the poster as a PDF for ACM DL publication. At least one author must register and present or the work is withdrawn. On-site posters are A0; CHI provides hanging materials but no printing, power, or AV equipment. Remote presenters must upload a video; on-site video is optional.

## Call ambiguity to resolve before submission

The formal submission details and the preparation section both say **four pages excluding references**, and the accepted-version rule repeats four pages. One review-criterion sentence still refers to a "6-page limit." Treat the repeated four-page requirements as controlling, but request written confirmation from `posters@chi2027.acm.org` before final upload.

## Workspace build readiness (non-outcome inspection)

- No tracked `paper/` directory, ACM template, TeX/BibTeX source, PDF, or standard build file (`Makefile`/`justfile`) was found.
- `tectonic`, `latexmk`, `pdflatex`, `xelatex`, `lualatex`, `biber`, `bibtex`, `pandoc`, `qpdf`, `pdfinfo`, `magick`, and `mutool` were not available on the current command PATH.
- Therefore, a future paper task needs an ACM Primary Article Template plus a reproducible LaTeX/TAPS build path before it can claim a compiled anonymous manuscript or poster.

## Official sources

- [CHI 2027 Posters call](https://chi2027.acm.org/authors/posters/)
- [CHI 2027 publication formats](https://chi2027.acm.org/chi-publication-formats/)
- [CHI 2027 anonymization policy](https://chi2027.acm.org/chi-anonymization-policy/)
- [ACM policy on research involving human participants and subjects](https://www.acm.org/publications/policies/research-involving-human-participants-and-subjects)
