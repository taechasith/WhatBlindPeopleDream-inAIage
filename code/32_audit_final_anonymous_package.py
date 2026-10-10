"""Audit a completed anonymous CHI package after RESULTS_FREEZE.

This is a post-results publication-control tool.  It does not calculate,
select, rank, or interpret study findings.  It verifies only the provenance,
traceability, anonymity, accessibility, reference, and reproducibility claims
needed before an anonymous review package is delivered.

The tool intentionally fails closed.  It must be run against a *new* output
directory after the manuscript and poster have been built.  Its report lists
artifact paths and audit decisions, but deliberately does not copy model output
text or result values into the audit report.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FIGURES = (
    "figure_1_reciprocal_cognitive_sensing_loop.svg",
    "figure_2_prompt_condition_effects.svg",
    "figure_3_human_reference_alignment.svg",
    "figure_4_representational_space_distances.svg",
    "figure_5_largest_output_property_changes.svg",
)
REQUIRED_REPRODUCTION_FILES = (
    "REPRODUCTION.md",
    "REPRODUCTION_STATUS.md",
    "DATA_SHARING_PLAN_FINAL.md",
    "data/MANIFEST.csv",
    "data/LICENSES.md",
    "data/CHECKSUMS.csv",
    "MODEL_OUTPUT_FREEZE.md",
    "compute/MODEL_FREEZE.md",
    "AI_USE_LOG.md",
)
CLAIM_COLUMNS = {
    "claim_id",
    "delivery",
    "location",
    "fact_id",
    "source_column",
    "reported_value",
    "rounding_decimals",
    "claim_type",
    "measurement_status",
    "claim_boundary",
}
REFERENCE_COLUMNS = {
    "citation_key",
    "paper_id",
    "doi",
    "doi_audit_status",
    "classification",
    "claim_use",
    "evidence_boundary",
}
PAGE_ACCOUNTING_COLUMNS = {
    "main_pages_excluding_references",
    "reference_pages",
    "total_pdf_pages",
    "call_checked_date",
    "call_url",
}
ALLOWED_MEASUREMENT_STATUSES = {
    "COMPUTATIONAL_PRIMARY",
    "PUBLIC_HUMAN_BENCHMARKED",
    "COMPUTATIONAL_SECONDARY",
    "MODEL_DERIVED_EXPLORATORY",
    "MEASUREMENT_UNSTABLE",
}

# These are intentionally narrow forbidden *claims*.  The negative-context
# rule below permits an explicit limitation such as "does not show that AI
# changes dreams" while retaining it in the report as a useful boundary check.
CAUSAL_PATTERNS = (
    ("AI_CHANGES_DREAMS", re.compile(r"\b(?:ai|artificial intelligence|llm|vlm|model)\b.{0,50}\b(?:changes?|alters?|rewires?|programs?)\b.{0,70}\b(?:blind\s+)?dreams?\b", re.IGNORECASE | re.DOTALL)),
    ("AI_CHANGES_COGNITION", re.compile(r"\b(?:ai|artificial intelligence|llm|vlm|model)\b.{0,50}\b(?:changes?|alters?|rewires?|programs?)\b.{0,70}\b(?:blind\s+)?(?:cognition|brains?|visual cortex|neural organization|neural representation)\b", re.IGNORECASE | re.DOTALL)),
    ("AI_BLIND_COGNITION_EQUIVALENCE", re.compile(r"\b(?:ai|the model|vlm|llm)\b.{0,45}\b(?:thinks?|reproduces?|models?|understands?)\b.{0,40}\b(?:like|as)\b.{0,40}\b(?:blind (?:people|dreamers|cognition)|blindness)\b", re.IGNORECASE | re.DOTALL)),
    ("SYNTHETIC_JUDGE_HUMAN_EQUIVALENCE", re.compile(r"\b(?:synthetic (?:judge|annotator|evaluator)|llm (?:judge|annotator|evaluator))\b.{0,60}\b(?:is|are|acts? as|replaces?|substitutes? for)\b.{0,55}\b(?:human|blind (?:person|people|user|users)|blv (?:person|people|user|users))\b", re.IGNORECASE | re.DOTALL)),
)
NEGATION_CONTEXT = re.compile(
    r"\b(?:does not|do not|did not|cannot|can not|not establish|not show|not demonstrate|not prove|unproven|untested|outside (?:the )?scope|no evidence)\b",
    re.IGNORECASE,
)
AUTHOR_COMMANDS = re.compile(
    r"\\(?:author|affiliation|email|thanks|authornote|orcid|acknowledg(?:e)?ments?)\b",
    re.IGNORECASE,
)
GENERIC_IDENTITY_PATTERNS = (
    ("EMAIL", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
    ("PERSONAL_OR_REPOSITORY_LINK", re.compile(r"\b(?:github\.com|gitlab\.com|bitbucket\.org|orcid\.org|mailto:)\b", re.IGNORECASE)),
    ("AFFILIATION_LANGUAGE", re.compile(r"\b(?:university|college|school of|faculty of|department of|corresponding author|contact author)\b", re.IGNORECASE)),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing {label}: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {label}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def text_files(directory: Path, suffixes: tuple[str, ...]) -> Iterable[Path]:
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in suffixes:
            yield path


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def compact(value: str, maximum: int = 180) -> str:
    value = " ".join(value.split())
    return value if len(value) <= maximum else value[: maximum - 3] + "..."


@dataclass
class Audit:
    records: list[dict[str, str]] = field(default_factory=list)

    def add(self, severity: str, check: str, status: str, detail: str, path: Path | None = None) -> None:
        self.records.append({
            "severity": severity,
            "check": check,
            "status": status,
            "path": "" if path is None else str(path),
            "detail": detail,
        })

    def pass_(self, check: str, detail: str, path: Path | None = None) -> None:
        self.add("PASS", check, "PASS", detail, path)

    def warn(self, check: str, detail: str, path: Path | None = None) -> None:
        self.add("WARNING", check, "REVIEW", detail, path)

    def fail(self, check: str, detail: str, path: Path | None = None) -> None:
        self.add("ERROR", check, "FAIL", detail, path)

    @property
    def errors(self) -> int:
        return sum(row["severity"] == "ERROR" for row in self.records)

    @property
    def warnings(self) -> int:
        return sum(row["severity"] == "WARNING" for row in self.records)


def load_private_patterns(path: Path) -> list[re.Pattern[str]]:
    if not path.is_file():
        raise ValueError("identity pattern file is required for the final anonymity audit")
    raw = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not raw:
        raise ValueError("identity pattern file contains no active patterns")
    patterns: list[re.Pattern[str]] = []
    for value in raw:
        try:
            patterns.append(re.compile(value, re.IGNORECASE))
        except re.error as exc:
            raise ValueError(f"invalid private identity pattern {value!r}: {exc}") from exc
    return patterns


def audit_results_provenance(audit: Audit, results_freeze: Path) -> dict[str, Path]:
    try:
        freeze = read_json(results_freeze, "RESULTS_FREEZE")
    except ValueError as exc:
        audit.fail("RESULTS_FREEZE", str(exc), results_freeze)
        return {}
    if freeze.get("status") != "RESULTS_FROZEN_PUBLIC_DATA_ONLY":
        audit.fail("RESULTS_FREEZE", "unexpected or incomplete freeze status", results_freeze)
    else:
        audit.pass_("RESULTS_FREEZE", "public-data results freeze status is present", results_freeze)
    if freeze.get("new_human_data_collected") is not False:
        audit.fail("PUBLIC_DATA_SCOPE", "freeze does not attest to zero new human data collection", results_freeze)
    else:
        audit.pass_("PUBLIC_DATA_SCOPE", "freeze attests to zero new human data collection", results_freeze)
    if freeze.get("condition_unblinded_once") is not True:
        audit.fail("UNBLINDING_PROVENANCE", "freeze does not attest to the authorized one-time unblinding", results_freeze)
    else:
        audit.pass_("UNBLINDING_PROVENANCE", "freeze attests to the authorized one-time unblinding", results_freeze)

    ledger_path = results_freeze.parent / "RESULTS_LEDGER.csv"
    expected = str(freeze.get("results_ledger_sha256", ""))
    if not ledger_path.is_file() or not expected or sha256(ledger_path) != expected:
        audit.fail("RESULTS_LEDGER", "results ledger is absent or does not match RESULTS_FREEZE", ledger_path)
        return {}
    try:
        with ledger_path.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, csv.Error) as exc:
        audit.fail("RESULTS_LEDGER", f"cannot parse results ledger: {exc}", ledger_path)
        return {}
    required = {"result_family", "path", "sha256", "rows"}
    if not rows or set(rows[0]) != required:
        audit.fail("RESULTS_LEDGER", "unexpected results-ledger schema", ledger_path)
        return {}
    artifacts: dict[str, Path] = {}
    for row in rows:
        family = row["result_family"]
        artifact = Path(row["path"])
        if not artifact.is_absolute():
            artifact = ROOT / artifact
        artifact = artifact.resolve()
        if family in artifacts or not artifact.is_file() or sha256(artifact) != row["sha256"]:
            audit.fail("RESULTS_LEDGER", f"frozen artifact cannot be reconciled for {family}", artifact)
            continue
        try:
            expected_rows = int(row["rows"])
            with artifact.open("r", encoding="utf-8", newline="") as stream:
                observed_rows = sum(1 for _ in csv.reader(stream)) - 1
            if observed_rows != expected_rows:
                audit.fail("RESULTS_LEDGER", f"row count changed for {family}", artifact)
                continue
        except (OSError, ValueError, csv.Error) as exc:
            audit.fail("RESULTS_LEDGER", f"cannot validate row count for {family}: {exc}", artifact)
            continue
        artifacts[family] = artifact
    if artifacts and len(artifacts) == len(rows):
        audit.pass_("RESULTS_LEDGER", f"{len(artifacts)} frozen result artifacts reconcile to the ledger", ledger_path)
    return artifacts


def audit_fact_packet(audit: Audit, results_freeze: Path, fact_packet_dir: Path) -> dict[str, dict[str, str]]:
    manifest_path = fact_packet_dir / "PAPER_FACT_PACKET_MANIFEST.json"
    facts_path = fact_packet_dir / "paper_fact_packet.csv"
    try:
        manifest = read_json(manifest_path, "paper fact-packet manifest")
    except ValueError as exc:
        audit.fail("FACT_PACKET", str(exc), manifest_path)
        return {}
    if manifest.get("status") != "PAPER_FACT_PACKET_FROZEN_FROM_RESULTS_FREEZE":
        audit.fail("FACT_PACKET", "unexpected fact-packet status", manifest_path)
    if manifest.get("source_results_freeze_sha256") != sha256(results_freeze):
        audit.fail("FACT_PACKET", "fact packet is not tied to this RESULTS_FREEZE", manifest_path)
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict) or artifacts.get(facts_path.name) != (sha256(facts_path) if facts_path.is_file() else ""):
        audit.fail("FACT_PACKET", "paper fact-packet CSV is absent or hash-mismatched", facts_path)
        return {}
    try:
        with facts_path.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, csv.Error) as exc:
        audit.fail("FACT_PACKET", f"cannot parse fact packet: {exc}", facts_path)
        return {}
    if not rows or "fact_id" not in rows[0]:
        audit.fail("FACT_PACKET", "fact packet has no fact_id column", facts_path)
        return {}
    facts = {str(row["fact_id"]): row for row in rows}
    if len(facts) != len(rows):
        audit.fail("FACT_PACKET", "fact packet contains duplicate fact IDs", facts_path)
        return {}
    audit.pass_("FACT_PACKET", f"{len(facts)} ledger-backed fact rows are available", fact_packet_dir)
    return facts


def numeric_equal(source: str, reported: str, decimals: str) -> bool:
    if decimals.strip().upper() == "EXACT":
        return source.strip() == reported.strip()
    try:
        places = int(decimals)
        source_value = float(source)
        reported_value = float(reported)
    except (TypeError, ValueError):
        return False
    if places < 0 or not math.isfinite(source_value) or not math.isfinite(reported_value):
        return False
    tolerance = 0.5000001 * 10 ** (-places)
    return abs(round(source_value, places) - reported_value) <= tolerance


def audit_claim_traceability(
    audit: Audit,
    claim_ledger: Path,
    fact_rows: dict[str, dict[str, str]],
    manuscript_dir: Path,
    poster_content: Path,
) -> None:
    try:
        with claim_ledger.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, csv.Error) as exc:
        audit.fail("NUMERIC_TRACEABILITY", f"cannot parse claim traceability ledger: {exc}", claim_ledger)
        return
    if not rows or set(rows[0]) != CLAIM_COLUMNS:
        audit.fail("NUMERIC_TRACEABILITY", "claim ledger schema is not exact; use the required template", claim_ledger)
        return
    missing = [column for row in rows for column in CLAIM_COLUMNS if not str(row.get(column, "")).strip()]
    if missing:
        audit.fail("NUMERIC_TRACEABILITY", "claim ledger contains blank required fields", claim_ledger)
        return
    claim_ids = {row["claim_id"] for row in rows}
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in text_files(manuscript_dir, (".tex",)))
    poster_payload = ""
    if poster_content.is_file():
        poster_payload = poster_content.read_text(encoding="utf-8")
    else:
        audit.fail("NUMERIC_TRACEABILITY", "poster content JSON is missing", poster_content)
    marker_counts = {claim_id: len(re.findall(rf"CLAIM-ID:\s*{re.escape(claim_id)}\b", source_text)) for claim_id in claim_ids}
    for claim_id, count in marker_counts.items():
        paper_claim = any(row["claim_id"] == claim_id and row["delivery"].strip().lower() == "paper" for row in rows)
        if paper_claim and count != 1:
            audit.fail("NUMERIC_TRACEABILITY", f"paper claim {claim_id} must have exactly one CLAIM-ID marker; observed {count}", manuscript_dir)
    try:
        poster_json = json.loads(poster_payload) if poster_payload else {}
    except json.JSONDecodeError:
        poster_json = {}
        audit.fail("NUMERIC_TRACEABILITY", "poster content JSON is invalid", poster_content)
    poster_trace_ids = set(str(item) for item in poster_json.get("result_trace_ids", []) if isinstance(item, str))

    checked = 0
    for row in rows:
        delivery = row["delivery"].strip().lower()
        if delivery not in {"paper", "poster"}:
            audit.fail("NUMERIC_TRACEABILITY", f"claim {row['claim_id']} has invalid delivery {row['delivery']!r}", claim_ledger)
            continue
        if row["measurement_status"] not in ALLOWED_MEASUREMENT_STATUSES:
            audit.fail("NUMERIC_TRACEABILITY", f"claim {row['claim_id']} has an unknown measurement status", claim_ledger)
            continue
        if row["measurement_status"] == "MEASUREMENT_UNSTABLE":
            audit.fail("NUMERIC_TRACEABILITY", f"claim {row['claim_id']} cannot report a measurement-unstable construct as a result", claim_ledger)
            continue
        fact = fact_rows.get(row["fact_id"])
        if fact is None:
            audit.fail("NUMERIC_TRACEABILITY", f"unknown fact ID {row['fact_id']!r} for claim {row['claim_id']}", claim_ledger)
            continue
        column = row["source_column"]
        if column not in fact:
            audit.fail("NUMERIC_TRACEABILITY", f"fact {row['fact_id']} has no source column {column!r}", claim_ledger)
            continue
        if not numeric_equal(str(fact[column]), row["reported_value"], row["rounding_decimals"]):
            audit.fail("NUMERIC_TRACEABILITY", f"reported numeric value does not reconcile for claim {row['claim_id']}", claim_ledger)
            continue
        if delivery == "poster" and row["fact_id"] not in poster_trace_ids:
            audit.fail("NUMERIC_TRACEABILITY", f"poster fact {row['fact_id']} is not listed in poster result_trace_ids", poster_content)
            continue
        checked += 1
    if checked == len(rows) and not any(record["check"] == "NUMERIC_TRACEABILITY" and record["severity"] == "ERROR" for record in audit.records):
        audit.pass_("NUMERIC_TRACEABILITY", f"{checked} claimed numeric assertions reconcile to frozen fact IDs", claim_ledger)


def audit_identity_and_language(
    audit: Audit,
    manuscript_dir: Path,
    poster_content: Path,
    private_patterns: list[re.Pattern[str]],
) -> None:
    if not manuscript_dir.is_dir():
        audit.fail("MANUSCRIPT_SOURCE", "anonymous manuscript source directory is missing", manuscript_dir)
        return
    source_paths = list(text_files(manuscript_dir, (".tex", ".md", ".json", ".csv")))
    if not source_paths:
        audit.fail("MANUSCRIPT_SOURCE", "anonymous manuscript source has no auditable text files", manuscript_dir)
        return
    for path in source_paths:
        text = path.read_text(encoding="utf-8")
        # Reference metadata names are legitimate citations rather than author
        # metadata, so identity scans intentionally exclude bibliography files.
        if path.suffix.lower() != ".bib":
            for label, pattern in GENERIC_IDENTITY_PATTERNS:
                match = pattern.search(text)
                if match:
                    audit.fail("ANONYMITY_SOURCE", f"{label} at line {line_number(text, match.start())}: {compact(match.group(0))}", path)
            for pattern in private_patterns:
                match = pattern.search(text)
                if match:
                    audit.fail("ANONYMITY_SOURCE", f"private identity pattern at line {line_number(text, match.start())}", path)
        if path.suffix.lower() == ".tex":
            command = AUTHOR_COMMANDS.search(text)
            if command:
                audit.fail("ANONYMITY_SOURCE", f"author/affiliation command at line {line_number(text, command.start())}: {command.group(0)}", path)
            for label, pattern in CAUSAL_PATTERNS:
                for match in pattern.finditer(text):
                    context = text[max(0, match.start() - 180): match.end()]
                    detail = f"{label} at line {line_number(text, match.start())}: {compact(match.group(0))}"
                    if NEGATION_CONTEXT.search(context):
                        audit.warn("CAUSAL_BOUNDARY", f"negated/limited claim retained for review: {detail}", path)
                    else:
                        audit.fail("FORBIDDEN_CAUSAL_CLAIM", detail, path)
    if poster_content.is_file():
        text = poster_content.read_text(encoding="utf-8")
        for label, pattern in GENERIC_IDENTITY_PATTERNS:
            match = pattern.search(text)
            if match:
                audit.fail("ANONYMITY_POSTER_CONTENT", f"{label}: {compact(match.group(0))}", poster_content)
        for pattern in private_patterns:
            if pattern.search(text):
                audit.fail("ANONYMITY_POSTER_CONTENT", "private identity pattern found", poster_content)
    else:
        audit.fail("ANONYMITY_POSTER_CONTENT", "poster content JSON is missing", poster_content)
    audit.pass_("MANUSCRIPT_SOURCE", f"scanned {len(source_paths)} anonymous manuscript text files", manuscript_dir)


def audit_figures(audit: Audit, figures_dir: Path, private_patterns: list[re.Pattern[str]]) -> None:
    manifest_path = figures_dir / "FIGURE_MANIFEST.csv"
    if not figures_dir.is_dir() or not manifest_path.is_file():
        audit.fail("FIGURES", "final figures directory or FIGURE_MANIFEST.csv is missing", figures_dir)
        return
    try:
        with manifest_path.open("r", encoding="utf-8", newline="") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, csv.Error) as exc:
        audit.fail("FIGURES", f"cannot parse figure manifest: {exc}", manifest_path)
        return
    if not rows or set(rows[0]) != {"artifact", "sha256", "alt_text"}:
        audit.fail("FIGURES", "figure manifest schema must be artifact,sha256,alt_text", manifest_path)
        return
    indexed = {row["artifact"]: row for row in rows}
    if len(indexed) != len(rows):
        audit.fail("FIGURES", "figure manifest contains duplicate artifact names", manifest_path)
    for artifact in REQUIRED_FIGURES:
        row = indexed.get(artifact)
        figure = figures_dir / artifact
        alt_path = figure.with_suffix(".alt.txt")
        if row is None or not figure.is_file() or sha256(figure) != row["sha256"]:
            audit.fail("FIGURES", f"missing or hash-mismatched final figure {artifact}", figure)
            continue
        if not alt_path.is_file():
            audit.fail("FIGURES", f"missing stand-alone alt text for {artifact}", alt_path)
            continue
        alt_text = alt_path.read_text(encoding="utf-8").strip()
        if len(alt_text) < 40 or alt_text != row["alt_text"].strip():
            audit.fail("FIGURES", f"alt text is absent, too brief, or disagrees with manifest for {artifact}", alt_path)
        svg_text = figure.read_text(encoding="utf-8")
        if re.search(r"(?:href|xlink:href)\s*=\s*['\"](?:https?:|//)|url\(\s*(?:https?:|//)", svg_text, re.IGNORECASE):
            audit.fail("FIGURES", f"external resource link in {artifact}", figure)
        for label, pattern in GENERIC_IDENTITY_PATTERNS:
            if pattern.search(svg_text):
                audit.fail("FIGURES", f"{label} appears in final figure {artifact}", figure)
        for pattern in private_patterns:
            if pattern.search(svg_text):
                audit.fail("FIGURES", f"private identity pattern appears in final figure {artifact}", figure)
    audit.pass_("FIGURES", "all five required final figures have manifest hashes and matching alt text", figures_dir)


def load_pdf(path: Path, label: str, audit: Audit) -> tuple[Any | None, str]:
    if not path.is_file():
        audit.fail(label, "PDF is missing", path)
        return None, ""
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        audit.fail(label, f"pypdf unavailable: {exc}", path)
        return None, ""
    try:
        reader = PdfReader(str(path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:  # pypdf has multiple PDF-specific exception types.
        audit.fail(label, f"cannot read PDF: {exc}", path)
        return None, ""
    if not reader.pages:
        audit.fail(label, "PDF has no pages", path)
    return reader, text


def audit_pdf_metadata(
    audit: Audit,
    path: Path,
    label: str,
    *,
    poster: bool,
    private_patterns: list[re.Pattern[str]],
) -> None:
    reader, extracted = load_pdf(path, label, audit)
    if reader is None:
        return
    metadata = reader.metadata or {}
    author = str(metadata.get("/Author", "")).strip()
    if author and author.lower() != "anonymous":
        audit.fail(label, "PDF /Author metadata is not Anonymous", path)
    elif not author:
        audit.warn(label, "PDF /Author metadata is blank rather than explicit Anonymous", path)
    for key, value in metadata.items():
        value_text = str(value)
        for _, pattern in GENERIC_IDENTITY_PATTERNS:
            if pattern.search(value_text):
                audit.fail(label, f"PDF metadata {key} contains identifying text", path)
        for pattern in private_patterns:
            if pattern.search(value_text):
                audit.fail(label, f"PDF metadata {key} contains a private identity pattern", path)
        for causal_label, pattern in CAUSAL_PATTERNS:
            if pattern.search(value_text):
                audit.fail(label, f"PDF metadata contains forbidden causal claim {causal_label}", path)
    for page_number, page in enumerate(reader.pages, start=1):
        annotations = page.get("/Annots")
        if annotations:
            for annotation in annotations:
                try:
                    target = annotation.get_object().get("/A", {}).get("/URI")
                except Exception:
                    target = None
                if target and poster:
                    audit.fail(label, f"poster PDF has an external-link annotation on page {page_number}", path)
                elif target and re.search(r"(?:github\.com|gitlab\.com|bitbucket\.org|orcid\.org)", str(target), re.IGNORECASE):
                    audit.fail(label, f"PDF includes a potentially identifying repository/profile link on page {page_number}", path)
    for identity_label, pattern in GENERIC_IDENTITY_PATTERNS:
        match = pattern.search(extracted)
        if match:
            audit.fail(label, f"PDF text has {identity_label}: {compact(match.group(0))}", path)
    for pattern in private_patterns:
        if pattern.search(extracted):
            audit.fail(label, "PDF text has a private identity pattern", path)
    if poster:
        page = reader.pages[0] if reader.pages else None
        if len(reader.pages) != 1 or page is None:
            audit.fail(label, "A0 poster must be exactly one PDF page", path)
        else:
            width, height = float(page.mediabox.width), float(page.mediabox.height)
            expected_width, expected_height = 1189 * 72 / 25.4, 841 * 72 / 25.4
            if abs(width - expected_width) > 8 or abs(height - expected_height) > 8:
                audit.fail(label, f"poster PDF is not A0 landscape ({width:.1f} x {height:.1f} pt)", path)
    audit.pass_(label, f"PDF metadata and {len(reader.pages)} page(s) were inspected", path)


def audit_page_accounting(audit: Audit, page_accounting: Path, manuscript_pdf: Path) -> None:
    try:
        payload = read_json(page_accounting, "paper page-accounting record")
    except ValueError as exc:
        audit.fail("PAPER_PAGE_LIMIT", str(exc), page_accounting)
        return
    if set(payload) != PAGE_ACCOUNTING_COLUMNS:
        audit.fail("PAPER_PAGE_LIMIT", "page-accounting JSON must use the required exact keys", page_accounting)
        return
    try:
        main_pages = int(payload["main_pages_excluding_references"])
        reference_pages = int(payload["reference_pages"])
        total = int(payload["total_pdf_pages"])
    except (TypeError, ValueError):
        audit.fail("PAPER_PAGE_LIMIT", "page-accounting values must be integers", page_accounting)
        return
    if main_pages < 1 or reference_pages < 0 or total != main_pages + reference_pages or main_pages > 4:
        audit.fail("PAPER_PAGE_LIMIT", "paper exceeds four pages excluding references or accounting is inconsistent", page_accounting)
        return
    reader, _ = load_pdf(manuscript_pdf, "PAPER_PAGE_LIMIT", audit)
    if reader is not None and len(reader.pages) != total:
        audit.fail("PAPER_PAGE_LIMIT", "page-accounting total differs from manuscript PDF", manuscript_pdf)
        return
    audit.pass_("PAPER_PAGE_LIMIT", f"{main_pages} main page(s) plus {reference_pages} reference page(s) are recorded", page_accounting)


def extract_citations(tex: str) -> set[str]:
    citations: set[str] = set()
    for match in re.finditer(r"\\cite(?:[a-zA-Z*]*)?(?:\[[^\]]*\]){0,2}\{([^}]+)\}", tex):
        citations.update(part.strip() for part in match.group(1).split(",") if part.strip())
    return citations


def extract_bib_keys(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    return set(re.findall(r"^\s*@\w+\s*\{\s*([^,\s]+)", path.read_text(encoding="utf-8"), re.MULTILINE))


def audit_references(audit: Audit, manuscript_dir: Path, reference_traceability: Path, doi_audit: Path) -> None:
    main_tex = manuscript_dir / "main.tex"
    bib = manuscript_dir / "references.bib"
    if not main_tex.is_file() or not bib.is_file():
        audit.fail("REFERENCE_AUDIT", "main.tex or references.bib is missing", manuscript_dir)
        return
    citations = extract_citations(main_tex.read_text(encoding="utf-8"))
    bib_keys = extract_bib_keys(bib)
    if citations.difference(bib_keys):
        audit.fail("REFERENCE_AUDIT", f"cited keys absent from bibliography: {', '.join(sorted(citations.difference(bib_keys)))}", bib)
    try:
        with reference_traceability.open("r", encoding="utf-8", newline="") as stream:
            trace_rows = list(csv.DictReader(stream))
        with doi_audit.open("r", encoding="utf-8", newline="") as stream:
            doi_rows = list(csv.DictReader(stream))
    except (OSError, csv.Error) as exc:
        audit.fail("REFERENCE_AUDIT", f"cannot parse reference evidence: {exc}", reference_traceability)
        return
    if not trace_rows or set(trace_rows[0]) != REFERENCE_COLUMNS:
        audit.fail("REFERENCE_AUDIT", "reference traceability ledger has an unexpected schema", reference_traceability)
        return
    doi_by_id = {row.get("paper_id", ""): row for row in doi_rows}
    trace_by_key = {row["citation_key"]: row for row in trace_rows}
    if len(trace_by_key) != len(trace_rows):
        audit.fail("REFERENCE_AUDIT", "reference traceability ledger has duplicate citation keys", reference_traceability)
    if set(trace_by_key) != citations:
        missing = citations.difference(trace_by_key)
        extra = set(trace_by_key).difference(citations)
        audit.fail("REFERENCE_AUDIT", f"traceability ledger and cited keys differ (missing={sorted(missing)}, extra={sorted(extra)})", reference_traceability)
    for key in citations:
        row = trace_by_key.get(key)
        if row is None:
            continue
        evidence = doi_by_id.get(row["paper_id"])
        if evidence is None:
            audit.fail("REFERENCE_AUDIT", f"citation {key} has an unknown DOI-audit paper_id", reference_traceability)
            continue
        if row["doi"].strip().lower() != str(evidence.get("doi", "")).strip().lower():
            audit.fail("REFERENCE_AUDIT", f"citation {key} DOI does not match DOI audit", reference_traceability)
        if row["doi_audit_status"] != "PASS" or evidence.get("status") != "PASS":
            audit.fail("REFERENCE_AUDIT", f"citation {key} is not DOI-audit PASS", reference_traceability)
    if not any(record["check"] == "REFERENCE_AUDIT" and record["severity"] == "ERROR" for record in audit.records):
        audit.pass_("REFERENCE_AUDIT", f"{len(citations)} cited works reconcile to audited reference records", reference_traceability)


def audit_reproducibility(audit: Audit, results_freeze: Path) -> None:
    missing = [relative for relative in REQUIRED_REPRODUCTION_FILES if not (ROOT / relative).is_file()]
    if missing:
        audit.fail("REPRODUCIBILITY", f"missing required reproducibility/provenance files: {', '.join(missing)}")
    else:
        audit.pass_("REPRODUCIBILITY", f"{len(REQUIRED_REPRODUCTION_FILES)} required provenance/reproduction files exist")
    freeze_parent = results_freeze.parent
    required = (freeze_parent / "RESULTS_LEDGER.csv", ROOT / "data" / "MANIFEST.csv", ROOT / "data" / "LICENSES.md")
    for path in required:
        if not path.is_file():
            audit.fail("REPRODUCIBILITY", "required frozen/provenance artifact is absent", path)
    status = ROOT / "REPRODUCTION_STATUS.md"
    if status.is_file():
        text = status.read_text(encoding="utf-8")
        if "PARTIAL_REPRODUCTION" not in text and "CLEAN_REPRODUCTION_PASSED" not in text:
            audit.warn("REPRODUCIBILITY", "reproduction status has no recognized explicit status label", status)


def write_report(audit: Audit, outdir: Path, arguments: argparse.Namespace) -> None:
    outdir.mkdir(parents=True, exist_ok=False)
    report_csv = outdir / "FINAL_PUBLICATION_AUDIT.csv"
    with report_csv.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("severity", "check", "status", "path", "detail"))
        writer.writeheader()
        writer.writerows(audit.records)
    summary = {
        "status": "FINAL_PUBLICATION_AUDIT_PASS" if audit.errors == 0 else "FINAL_PUBLICATION_AUDIT_FAIL",
        "errors": audit.errors,
        "warnings": audit.warnings,
        "audit_script_sha256": sha256(Path(__file__).resolve()),
        "inputs": {
            key: str(value)
            for key, value in vars(arguments).items()
            if key != "outdir"
        },
        "report_sha256": sha256(report_csv),
        "scope": "post-results anonymous publication audit; no new human data and no result estimation",
    }
    (outdir / "FINAL_PUBLICATION_AUDIT.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = [
        "# Final Anonymous CHI Package Audit",
        "",
        f"**Status:** `{summary['status']}`  ",
        f"**Errors:** {audit.errors}  ",
        f"**Warnings requiring review:** {audit.warnings}",
        "",
        "This report checks publication controls only. It does not estimate or interpret scientific results.",
        "",
        "| Severity | Check | Detail |",
        "| --- | --- | --- |",
    ]
    for row in audit.records:
        escaped_detail = row["detail"].replace("|", "\\|")
        markdown.append(f"| {row['severity']} | {row['check']} | {escaped_detail} |")
    (outdir / "FINAL_PUBLICATION_AUDIT.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, required=True)
    parser.add_argument("--fact-packet-dir", type=Path, required=True)
    parser.add_argument("--claim-ledger", type=Path, required=True)
    parser.add_argument("--manuscript-dir", type=Path, required=True)
    parser.add_argument("--manuscript-pdf", type=Path, required=True)
    parser.add_argument("--page-accounting", type=Path, required=True)
    parser.add_argument("--figures-dir", type=Path, required=True)
    parser.add_argument("--poster-content", type=Path, required=True)
    parser.add_argument("--poster-pdf", type=Path, required=True)
    parser.add_argument("--reference-traceability", type=Path, required=True)
    parser.add_argument("--doi-audit", type=Path, required=True)
    parser.add_argument("--identity-patterns", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        parser.error("--outdir must not already exist; final audit records are immutable")

    audit = Audit()
    try:
        private_patterns = load_private_patterns(args.identity_patterns)
    except ValueError as exc:
        audit.fail("ANONYMITY_SETUP", str(exc), args.identity_patterns)
        private_patterns = []
    artifacts = audit_results_provenance(audit, args.results_freeze)
    facts = audit_fact_packet(audit, args.results_freeze, args.fact_packet_dir)
    audit_claim_traceability(audit, args.claim_ledger, facts, args.manuscript_dir, args.poster_content)
    audit_identity_and_language(audit, args.manuscript_dir, args.poster_content, private_patterns)
    audit_figures(audit, args.figures_dir, private_patterns)
    audit_pdf_metadata(audit, args.manuscript_pdf, "MANUSCRIPT_PDF", poster=False, private_patterns=private_patterns)
    audit_page_accounting(audit, args.page_accounting, args.manuscript_pdf)
    audit_pdf_metadata(audit, args.poster_pdf, "POSTER_PDF", poster=True, private_patterns=private_patterns)
    audit_references(audit, args.manuscript_dir, args.reference_traceability, args.doi_audit)
    audit_reproducibility(audit, args.results_freeze)
    if not artifacts:
        audit.fail("RESULTS_PROVENANCE", "no frozen result artifacts reconciled; publication must remain blocked", args.results_freeze)
    write_report(audit, args.outdir, args)
    print(json.dumps({"status": "PASS" if audit.errors == 0 else "FAIL", "errors": audit.errors, "warnings": audit.warnings}, sort_keys=True))
    return 0 if audit.errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
