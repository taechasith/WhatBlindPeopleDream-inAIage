"""Generate an anonymous, audited bibliography only after RESULTS_FREEZE.

This publication-control utility deliberately does not read result tables,
condition mappings, model outputs, or participant material.  It turns a
prospectively selected citation list plus a local, audited metadata snapshot
into three immutable artifacts:

* ``audited_references.bib``;
* ``REFERENCE_TRACEABILITY.csv``; and
* ``FINAL_REFERENCE_AUDIT.json``.

The tool is intentionally fail-closed.  It does not contact a mutable remote
metadata service at render time, infer missing author/title/venue data, or
silently convert protocols and preprints into completed empirical evidence.
It should be run after ``RESULTS_FREEZE`` but before anonymous manuscript
rendering.  The resulting JSON implements the interface consumed by
``32_render_anonymous_chi_manuscript.py``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RESULTS_STATUS = "RESULTS_FROZEN_PUBLIC_DATA_ONLY"
EXPECTED_RESULTS_FAMILIES = {
    "RQ2", "RQ3", "RQ4", "RQ5", "RQ4_profiles", "RQ4_association_status",
}
DOI_AUDIT_COLUMNS = {
    "paper_id", "doi", "doi_resolution_source", "title_verified",
    "year_verified", "venue_verified", "peer_review_status", "classification",
    "verification_date", "status", "notes",
}
METADATA_COLUMNS = {
    "paper_id", "entry_type", "author", "title", "year", "container_title",
    "volume", "issue", "pages", "publisher", "metadata_source",
    "metadata_verification_date", "metadata_notes",
}
TRACE_COLUMNS = (
    "citation_key", "paper_id", "doi", "doi_audit_status", "classification",
    "claim_use", "evidence_boundary",
)
ALLOWED_ENTRY_TYPES = {"article", "inproceedings", "misc"}
CLASSIFICATION_TO_ENTRY_TYPE = {
    "journal_article": "article",
    "systematic_review": "article",
    "protocol": "article",
    "conference_article": "inproceedings",
    "workshop_article": "inproceedings",
    "preprint": "misc",
}
ALLOWED_CLAIM_USES = {
    "background_context",
    "comparison_context",
    "dataset_context",
    "external_validation_context",
    "future_work_context",
    "methodological_context",
    "theoretical_context",
}
KEY_RE = re.compile(r"[A-Za-z][A-Za-z0-9:_-]*\Z")
YEAR_RE = re.compile(r"(?:19|20)\d{2}\Z")
DOI_RE = re.compile(r"10\.\d{4,9}/\S+\Z", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\b(?:todo|tbd|replace|placeholder|unknown|not[ _-]?reported)\b", re.IGNORECASE)
MOJIBAKE_RE = re.compile(r"(?:\ufffd|â€|Ã[\x80-\xbf])")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"AUDITED_REFERENCE_GENERATION_FAILED: {message}")


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        fail(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {label}: {exc}")
    if not isinstance(value, dict):
        fail(f"{label} must be a JSON object")
    return value


def read_csv(path: Path, required_columns: set[str], label: str) -> list[dict[str, str]]:
    if not path.is_file():
        fail(f"missing {label}: {path}")
    try:
        with path.open("r", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
            columns = set(reader.fieldnames or [])
    except (OSError, csv.Error) as exc:
        fail(f"cannot read {label}: {exc}")
    if not rows:
        fail(f"{label} has no rows")
    missing = required_columns.difference(columns)
    if missing:
        fail(f"{label} lacks required columns: {', '.join(sorted(missing))}")
    return [{str(key): "" if value is None else str(value) for key, value in row.items()} for row in rows]


def clean_text(value: object, label: str, *, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        fail(f"{label} must be text")
    text = " ".join(value.split())
    if not text and not allow_empty:
        fail(f"{label} is empty")
    if "\x00" in text or PLACEHOLDER_RE.search(text) or MOJIBAKE_RE.search(text):
        fail(f"{label} is missing, placeholder-like, or contains undecoded metadata")
    if text.count("{") != text.count("}"):
        fail(f"{label} has unbalanced braces")
    return text


def normalise_doi(value: str, label: str) -> str:
    doi = clean_text(value, label).removeprefix("https://doi.org/").removeprefix("http://doi.org/").lower()
    if not DOI_RE.fullmatch(doi):
        fail(f"{label} is not a DOI")
    return doi


def validate_results_freeze(path: Path) -> dict[str, Any]:
    freeze = read_json(path, "RESULTS_FREEZE")
    if freeze.get("status") != EXPECTED_RESULTS_STATUS:
        fail("RESULTS_FREEZE has an incomplete or unsupported status")
    if freeze.get("new_human_data_collected") is not False:
        fail("RESULTS_FREEZE does not attest to zero new human data collection")
    if freeze.get("condition_unblinded_once") is not True:
        fail("RESULTS_FREEZE does not attest to the authorized single unblinding")
    expected_ledger = str(freeze.get("results_ledger_sha256", ""))
    ledger_path = path.parent / "RESULTS_LEDGER.csv"
    if not expected_ledger or not ledger_path.is_file() or sha256(ledger_path) != expected_ledger:
        fail("RESULTS_FREEZE does not reconcile its RESULTS_LEDGER.csv")
    rows = read_csv(ledger_path, {"result_family", "path", "sha256", "rows"}, "results ledger")
    families = {row["result_family"] for row in rows}
    if families != EXPECTED_RESULTS_FAMILIES or len(families) != len(rows):
        fail("results ledger does not cover exactly the canonical public-data result families")
    for row in rows:
        artifact = Path(row["path"])
        if not artifact.is_absolute():
            artifact = ROOT / artifact
        if not artifact.is_file() or sha256(artifact) != row["sha256"]:
            fail(f"results ledger artifact is absent or hash-mismatched: {row['result_family']}")
        try:
            if int(row["rows"]) < 0:
                raise ValueError
        except ValueError:
            fail(f"results ledger has an invalid row count for {row['result_family']}")
    return freeze


def require_unique(rows: list[dict[str, str]], field: str, label: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        key = clean_text(row.get(field, ""), f"{label}.{field}")
        if key in indexed:
            fail(f"{label} has a duplicate {field}: {key}")
        indexed[key] = row
    return indexed


def load_selection(path: Path, expected_results_sha256: str) -> list[dict[str, str]]:
    selection = read_json(path, "citation selection")
    if selection.get("schema_version") != 1 or selection.get("review_stage") != "ANONYMOUS_REVIEW":
        fail("citation selection must declare schema_version 1 and ANONYMOUS_REVIEW")
    if selection.get("results_freeze_sha256") != expected_results_sha256:
        fail("citation selection is not tied to the supplied RESULTS_FREEZE")
    raw = selection.get("citations")
    if not isinstance(raw, list) or not raw:
        fail("citation selection must contain at least one citation")
    citations: list[dict[str, str]] = []
    keys: set[str] = set()
    papers: set[str] = set()
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            fail(f"citation selection entry {index} must be an object")
        key = clean_text(item.get("citation_key"), f"citation {index}.citation_key")
        if not KEY_RE.fullmatch(key) or key in keys:
            fail(f"citation {index} has an invalid or duplicate citation_key")
        paper_id = clean_text(item.get("paper_id"), f"citation {index}.paper_id")
        if paper_id in papers:
            fail("cite each audited paper at most once; combine claim uses in its boundary")
        claim_use = clean_text(item.get("claim_use"), f"citation {index}.claim_use")
        if claim_use not in ALLOWED_CLAIM_USES:
            fail(f"citation {index} uses unsupported claim_use: {claim_use}")
        boundary = clean_text(item.get("evidence_boundary"), f"citation {index}.evidence_boundary")
        keys.add(key)
        papers.add(paper_id)
        citations.append({
            "citation_key": key,
            "paper_id": paper_id,
            "claim_use": claim_use,
            "evidence_boundary": boundary,
        })
    return citations


def required_boundary(classification: str, boundary: str, claim_use: str) -> None:
    lowered = boundary.lower()
    if classification == "protocol":
        if "protocol" not in lowered or "not" not in lowered or "completed" not in lowered:
            fail("protocol citations require a boundary stating that they are protocol-only, not completed outcome evidence")
        if claim_use not in {"background_context", "future_work_context", "methodological_context"}:
            fail("protocol citations cannot be used as empirical/dataset/external-validation evidence")
    if classification == "preprint":
        if "preprint" not in lowered or "not" not in lowered or "peer" not in lowered:
            fail("preprint citations require a boundary stating that they are a preprint and not peer-reviewed")
    if classification == "workshop_article" and "workshop" not in lowered:
        fail("workshop citations require a boundary identifying workshop status")
    if classification == "systematic_review" and "review" not in lowered:
        fail("systematic-review citations require a boundary identifying review-level evidence")


def bibtex_field(name: str, value: str) -> str:
    value = clean_text(value, f"BibTeX field {name}")
    # A literal at-sign at the start of a metadata value can start an injected
    # BibTeX entry in permissive parsers.  Titles may contain other punctuation.
    if value.startswith("@"):
        fail(f"BibTeX field {name} has an unsafe leading at-sign")
    return f"  {name} = {{{value}}},"


def build_bibtex_entry(key: str, audit: dict[str, str], metadata: dict[str, str]) -> str:
    classification = audit["classification"]
    expected_type = CLASSIFICATION_TO_ENTRY_TYPE.get(classification)
    if expected_type is None:
        fail(f"unsupported DOI-audit classification: {classification}")
    entry_type = clean_text(metadata.get("entry_type", ""), f"metadata[{audit['paper_id']}].entry_type").lower()
    if entry_type not in ALLOWED_ENTRY_TYPES or entry_type != expected_type:
        fail(f"metadata entry_type for {audit['paper_id']} must be {expected_type}, not {entry_type!r}")
    author = clean_text(metadata.get("author", ""), f"metadata[{audit['paper_id']}].author")
    if " and " not in author and "," not in author:
        fail(f"metadata author list for {audit['paper_id']} is not BibTeX-formatted")
    if re.search(r"\bet\s+al\.?\b", author, re.IGNORECASE):
        fail(f"metadata author list for {audit['paper_id']} is abbreviated; provide the audited full list")
    title = clean_text(metadata.get("title", ""), f"metadata[{audit['paper_id']}].title")
    year = clean_text(metadata.get("year", ""), f"metadata[{audit['paper_id']}].year")
    if not YEAR_RE.fullmatch(year):
        fail(f"metadata year for {audit['paper_id']} is invalid")
    container = clean_text(metadata.get("container_title", ""), f"metadata[{audit['paper_id']}].container_title", allow_empty=entry_type == "misc")
    source = clean_text(metadata.get("metadata_source", ""), f"metadata[{audit['paper_id']}].metadata_source")
    if source not in {"Crossref", "DataCite", "Crossref_and_DataCite"}:
        fail(f"metadata source for {audit['paper_id']} is unsupported: {source}")
    verified = clean_text(metadata.get("metadata_verification_date", ""), f"metadata[{audit['paper_id']}].metadata_verification_date")
    if not re.fullmatch(r"20\d{2}-\d{2}-\d{2}", verified):
        fail(f"metadata verification date for {audit['paper_id']} is invalid")
    doi = normalise_doi(audit["doi"], f"doi_audit[{audit['paper_id']}].doi")
    fields = [
        bibtex_field("author", author),
        bibtex_field("title", title),
        bibtex_field("year", year),
    ]
    if entry_type == "article":
        fields.append(bibtex_field("journal", container))
    elif entry_type == "inproceedings":
        fields.append(bibtex_field("booktitle", container))
    else:
        fields.append(bibtex_field("howpublished", "Preprint"))
        fields.append(bibtex_field("archivePrefix", "arXiv"))
        arxiv = doi.removeprefix("10.48550/arxiv.")
        if arxiv == doi:
            fail(f"preprint {audit['paper_id']} lacks a supported arXiv DOI form")
        fields.append(bibtex_field("eprint", arxiv))
    for field in ("volume", "issue", "pages", "publisher"):
        value = clean_text(metadata.get(field, ""), f"metadata[{audit['paper_id']}].{field}", allow_empty=True)
        if value:
            fields.append(bibtex_field(field, value))
    fields.extend((
        bibtex_field("doi", doi),
        bibtex_field("url", f"https://doi.org/{doi}"),
    ))
    return "\n".join([f"@{entry_type}{{{key},", *fields, "}", ""])


def write_csv(path: Path, rows: list[dict[str, str]], columns: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, required=True)
    parser.add_argument("--doi-audit", type=Path, default=ROOT / "refs" / "doi_audit.csv")
    parser.add_argument("--metadata", type=Path, default=ROOT / "refs" / "audited_reference_metadata.csv")
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        parser.error("--outdir must not already exist; reference-audit artifacts are immutable")

    results = validate_results_freeze(args.results_freeze)
    result_hash = sha256(args.results_freeze)
    audit_rows = read_csv(args.doi_audit, DOI_AUDIT_COLUMNS, "DOI audit")
    audit_by_id = require_unique(audit_rows, "paper_id", "DOI audit")
    if len({normalise_doi(row["doi"], f"DOI audit doi for {row['paper_id']}") for row in audit_rows}) != len(audit_rows):
        fail("DOI audit contains duplicate DOI records")
    metadata_rows = read_csv(args.metadata, METADATA_COLUMNS, "audited reference metadata")
    metadata_by_id = require_unique(metadata_rows, "paper_id", "audited reference metadata")
    citations = load_selection(args.selection, result_hash)

    trace_rows: list[dict[str, str]] = []
    bib_entries: list[str] = []
    audit_citations: list[dict[str, str]] = []
    for citation in citations:
        paper_id = citation["paper_id"]
        audit = audit_by_id.get(paper_id)
        metadata = metadata_by_id.get(paper_id)
        if audit is None:
            fail(f"selected citation refers to an unknown DOI-audit paper_id: {paper_id}")
        if metadata is None:
            fail(f"selected citation has no audited metadata record: {paper_id}")
        if audit.get("status") != "PASS":
            fail(f"selected citation is not DOI-audit PASS: {paper_id}")
        if any(audit.get(field) != "yes" for field in ("title_verified", "year_verified", "venue_verified")):
            fail(f"selected citation has incomplete title/year/venue verification: {paper_id}")
        classification = clean_text(audit.get("classification", ""), f"DOI audit classification for {paper_id}")
        required_boundary(classification, citation["evidence_boundary"], citation["claim_use"])
        bib_entries.append(build_bibtex_entry(citation["citation_key"], audit, metadata))
        trace_rows.append({
            "citation_key": citation["citation_key"],
            "paper_id": paper_id,
            "doi": normalise_doi(audit["doi"], f"DOI audit doi for {paper_id}"),
            "doi_audit_status": audit["status"],
            "classification": classification,
            "claim_use": citation["claim_use"],
            "evidence_boundary": citation["evidence_boundary"],
        })
        audit_citations.append({
            "key": citation["citation_key"],
            "paper_id": paper_id,
            "doi": normalise_doi(audit["doi"], f"DOI audit doi for {paper_id}"),
            "classification": classification,
            "peer_review_status": clean_text(audit.get("peer_review_status", ""), f"DOI audit peer review status for {paper_id}"),
            "claim_use": citation["claim_use"],
            "evidence_boundary": citation["evidence_boundary"],
            "verification_status": "PASS",
        })

    temp = args.outdir.parent / f".{args.outdir.name}.tmp-{uuid.uuid4().hex}"
    try:
        temp.mkdir(parents=True, exist_ok=False)
        bibliography = temp / "audited_references.bib"
        bibliography.write_text("% Generated only from refs/doi_audit.csv and audited_reference_metadata.csv.\n% Do not edit manually; regenerate after RESULTS_FREEZE.\n\n" + "\n".join(bib_entries), encoding="utf-8")
        traceability = temp / "REFERENCE_TRACEABILITY.csv"
        write_csv(traceability, trace_rows, TRACE_COLUMNS)
        selected_metadata = temp / "AUDITED_METADATA_USED.csv"
        selected_rows = [metadata_by_id[row["paper_id"]] for row in trace_rows]
        write_csv(selected_metadata, selected_rows, tuple(sorted(METADATA_COLUMNS)))
        checksums = temp / "CHECKSUMS.csv"
        checksum_rows = [
            {"artifact": path.name, "sha256": sha256(path)}
            for path in (bibliography, traceability, selected_metadata)
        ]
        write_csv(checksums, checksum_rows, ("artifact", "sha256"))
        final_audit = {
            "status": "REFERENCE_AUDIT_CLEAN_ANONYMOUS",
            "schema_version": 1,
            "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "scope": "post-results anonymous bibliography audit; no result estimation or interpretation",
            "results_freeze_sha256": result_hash,
            "results_freeze_status": results["status"],
            "doi_audit_sha256": sha256(args.doi_audit),
            "metadata_sha256": sha256(args.metadata),
            "selection_sha256": sha256(args.selection),
            "bibliography_sha256": sha256(bibliography),
            "reference_traceability_sha256": sha256(traceability),
            "metadata_used_sha256": sha256(selected_metadata),
            "checksums_sha256": sha256(checksums),
            "generator_script_sha256": sha256(Path(__file__).resolve()),
            "citation_count": len(audit_citations),
            "citations": audit_citations,
            "boundaries": [
                "Citation records are bibliographically audited; they do not expand the evidentiary scope of a source.",
                "Protocols are not completed outcome evidence; preprints are not peer-reviewed evidence.",
                "This audit does not make model-derived measurement into human judgment or lived experience.",
            ],
        }
        audit_path = temp / "FINAL_REFERENCE_AUDIT.json"
        audit_path.write_text(json.dumps(final_audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        readme = temp / "README.md"
        readme.write_text(
            "# Frozen anonymous reference-audit artifacts\n\n"
            "This directory was generated after the cited `RESULTS_FREEZE`. It contains only selected, DOI-audit-PASS citations and their external evidence boundaries. "
            "It contains no result table or condition mapping. Use `audited_references.bib` and `FINAL_REFERENCE_AUDIT.json` as paired immutable inputs to the anonymous manuscript renderer.\n",
            encoding="utf-8",
        )
        temp.replace(args.outdir)
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    print(json.dumps({"status": "REFERENCE_AUDIT_CLEAN_ANONYMOUS", "citations": len(audit_citations), "outdir": str(args.outdir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
