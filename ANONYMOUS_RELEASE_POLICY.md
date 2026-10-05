# Anonymous review release policy

## Purpose

This policy governs a narrow anonymous-review bundle, not a public repository
release. It exists because the working tree may contain private metadata,
sensitive source-derived text, local Git configuration, and draft materials
that are inappropriate for anonymous review.

## Never include

- Any Git directory, remote URL, commit history, author/committer metadata, or
  repository link that could identify the research team.
- Names, affiliations, institutional ethics-board names, email addresses,
  account handles, personal web addresses, or author-identifying comments.
- The private directory, the supplied identity-bearing governing brief, or
  author metadata.
- Raw/processed source corpora, coder packets that contain source text, source
  images, participant materials with institution-specific contact fields,
  allocation keys, contact/consent records, or future participant data.
- Web addresses in the anonymous bundle. Bibliographic and data-source records
  belong in separately audited materials, not this strict review export.

## What the allowlisted exporter may include

The exporter copies only predeclared plain-text protocols, codebooks,
non-identifying aggregate outputs, synthetic-status documentation, and
anonymized ethics language. It does not copy source corpora, executable code,
images, PDFs, notebooks, binary files, citations with web addresses, or any
unlisted path.

## Required process

1. Run `python code/export_anonymous_review.py --check`.
2. Resolve every reported forbidden pattern or missing allowlisted file; do not
   suppress a failure by editing the exporter allowlist without review.
   The scanner also requires a locally held, Git-ignored project-specific
   pattern file. Never copy that private pattern file into an archive.
3. Export to an empty directory outside the repository.
4. Inspect every output filename and file content manually. Independently check
   final PDFs, image metadata, document properties, external links, and any
   conference upload form.
5. Do not submit a link to the working repository or any repository whose
   history, remote, ownership, or issue tracker identifies the research team.

Passing the script is a necessary mechanical check, not a guarantee of
anonymity, legal redistributability, accessibility, or conference compliance.
