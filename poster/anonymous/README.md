# Anonymous A0 Poster Pipeline

This directory contains a review-stage A0 poster renderer for the public-data computational study. It is a source-only scaffold: it has no results, no author metadata, and no build output.

## Hard gate

The renderer refuses to run unless all of the following exist and validate:

- `RESULTS_FROZEN_PUBLIC_DATA_ONLY` in the supplied `RESULTS_FREEZE.json`;
- the final five accessible figure SVGs and their hash manifest;
- an anonymous, claim-audited content JSON tied by hash to both frozen inputs;
- a new output directory, so a completed poster is never silently overwritten.

It does not read raw model outputs, calculate results, or generate factual text. Final prose must be constructed from the results ledger and pass the manuscript claim and anonymity audits first.

## Build after results freeze

Create a content record satisfying [POSTER_CONTENT_SCHEMA.md](POSTER_CONTENT_SCHEMA.md), then run:

```powershell
./compute/run_anonymous_a0_poster.ps1 -ContentJson poster/anonymous/POSTER_CONTENT.json
```

The final renderer uses Inkscape when available, or a tested local Microsoft
Edge headless A0-print fallback when Inkscape is unavailable; both paths pass
through the same `pypdf` metadata, one-page, annotation, and A0-geometry
verification. It produces a one-page A0 landscape SVG and PDF, resets
review-stage PDF metadata to anonymous values, rejects PDF annotations/external
links, and writes an accessibility note plus a manifest with checksums.

Do not add author names, affiliations, acknowledgements, email addresses, personal repositories, institutional logos, or identifiable links to this directory or the content record before anonymous review is complete.
