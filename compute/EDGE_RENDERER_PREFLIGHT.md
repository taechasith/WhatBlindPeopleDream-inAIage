# Edge A0 PDF fallback preflight

This technical fixture is not a study figure and contains no research data.
It verifies the local Microsoft Edge headless fallback used by
`code/31_generate_anonymous_a0_poster.py` when Inkscape is unavailable.

On 2026-10-10, the fixture rendered to one PDF page with a media box of
3370.08 by 2383.92 points (ISO A0 landscape) and passed the renderer's
`pypdf` anonymous-metadata and no-annotation checks. The generated PDF is a
runtime artifact and is intentionally excluded from version control.

The final poster path remains results-gated: it embeds only the generated
anonymous SVG and then re-checks exact A0 geometry and metadata after export.
