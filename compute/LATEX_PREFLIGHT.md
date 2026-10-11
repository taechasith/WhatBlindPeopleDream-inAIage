# Local ACM LaTeX preflight

`latex_preflight.tex` is a non-analytic technical fixture. It contains no
study data, model output, results, private mapping, or author-identifying
metadata.

On 2026-10-12, the user-scoped MiKTeX installation resolved both:

- `acmart.cls`
- `ACM-Reference-Format.bst`

The fixture compiled successfully with the local `pdflatex` executable using a
sanitized process-local `PATH`. Its generated PDF and logs are retained only
under the ignored `compute/runtime_logs/` directory. The actual manuscript
remains results-gated and must be compiled and visually inspected separately
after `RESULTS_FREEZE`.

The sanitized process path is required because the user's general Windows
`PATH` includes non-directory legacy entries that can make MiKTeX maintenance
tools fail before compilation. This repository does not modify the global
environment; the final controller should use a process-local tool path.
