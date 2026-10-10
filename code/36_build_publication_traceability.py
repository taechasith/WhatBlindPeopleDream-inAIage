"""Build immutable claim and page-accounting records after anonymous rendering.

This is a post-RESULTS_FREEZE publication-control utility.  It deliberately
does not estimate, rank, interpret, or select scientific findings, and it
never reads raw model outputs or a condition mapping.  Instead, it binds
already selected, finite numeric fact-packet values to deterministic source
markers emitted by ``32_render_anonymous_chi_manuscript.py`` and to the
poster-content plan.  It also makes a conservative physical-page accounting
record from the compiled manuscript PDF.

The utility is fail-closed:

* a missing or hash-mismatched upstream receipt stops execution;
* non-finite selected values remain non-claims (``NOT_ESTIMABLE``), never
  invented numbers;
* a measurement-unstable selected fact cannot enter the claim ledger; and
* a PDF without a detectable References heading cannot receive a page count.

The output is intended as input to ``32_audit_final_anonymous_package.py``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RESULTS_STATUS = "RESULTS_FROZEN_PUBLIC_DATA_ONLY"
EXPECTED_PACKET_STATUS = "PAPER_FACT_PACKET_FROM_RESULTS_FREEZE"
EXPECTED_PACKET_MANIFEST_STATUS = "PAPER_FACT_PACKET_FROZEN_FROM_RESULTS_FREEZE"
EXPECTED_MANUSCRIPT_STATUS = "ANONYMOUS_CHI_MANUSCRIPT_SOURCE_RENDERED_FROM_RESULTS_FREEZE"
EXPECTED_POSTER_CONTENT_STATUS = "ANONYMOUS_A0_POSTER_CONTENT_FROZEN_FROM_RESULTS_FREEZE"
ALLOWED_MEASUREMENT_STATUSES = {
    "COMPUTATIONAL_PRIMARY",
    "PUBLIC_HUMAN_BENCHMARKED",
    "COMPUTATIONAL_SECONDARY",
    "MODEL_DERIVED_EXPLORATORY",
    "MEASUREMENT_UNSTABLE",
}
NUMERIC_FIELDS = {
    "RQ2": ("n_paired_items", "effect", "ci_low", "ci_high", "fdr_q"),
    "RQ3": ("n_paired_items", "effect", "ci_low", "ci_high", "fdr_q"),
    "RQ4": ("n_a", "n_b", "jensen_shannon_divergence", "js_ci_low", "js_ci_high"),
    "RQ5": ("n_paired_items", "effect", "ci_low", "ci_high", "fdr_q"),
}
CLAIM_COLUMNS = (
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
)
NON_NUMERIC_STATES = {"", "na", "n/a", "nan", "none", "null", "not_estimable", "not estimable"}
REFERENCE_HEADING = re.compile(r"(?mi)^\s*references\s*$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"PUBLICATION_TRACEABILITY_FAILED: {message}")


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


def require_status(payload: dict[str, Any], status: str, label: str) -> None:
    if payload.get("status") != status:
        fail(f"{label} has unexpected status: {payload.get('status')!r}")


def require_artifact(manifest: dict[str, Any], path: Path, label: str) -> None:
    expected = manifest.get("artifacts", {}).get(path.name)
    if not isinstance(expected, str) or not path.is_file() or sha256(path) != expected:
        fail(f"{label} is absent or does not match its immutable manifest")


def load_facts(results_freeze: Path, fact_packet_dir: Path) -> tuple[dict[str, Any], dict[str, dict[str, str]], str]:
    results = read_json(results_freeze, "RESULTS_FREEZE")
    require_status(results, EXPECTED_RESULTS_STATUS, "RESULTS_FREEZE")
    if results.get("new_human_data_collected") is not False:
        fail("RESULTS_FREEZE does not attest to public-data-only scope")
    packet_path = fact_packet_dir / "paper_fact_packet.json"
    csv_path = fact_packet_dir / "paper_fact_packet.csv"
    manifest_path = fact_packet_dir / "PAPER_FACT_PACKET_MANIFEST.json"
    packet = read_json(packet_path, "paper fact packet")
    manifest = read_json(manifest_path, "paper fact-packet manifest")
    require_status(packet, EXPECTED_PACKET_STATUS, "paper fact packet")
    require_status(manifest, EXPECTED_PACKET_MANIFEST_STATUS, "paper fact-packet manifest")
    expected_results_hash = sha256(results_freeze)
    if packet.get("source_results_freeze_sha256") != expected_results_hash or manifest.get("source_results_freeze_sha256") != expected_results_hash:
        fail("paper fact packet is not bound to the supplied RESULTS_FREEZE")
    for path, label in ((packet_path, "paper fact packet"), (csv_path, "paper fact CSV")):
        require_artifact(manifest, path, label)
    with csv_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or "fact_id" not in rows[0]:
        fail("paper fact CSV has no fact identifiers")
    facts = {str(row["fact_id"]): {str(key): "" if value is None else str(value) for key, value in row.items()} for row in rows}
    if len(facts) != len(rows):
        fail("paper fact CSV contains duplicate fact identifiers")
    return results, facts, sha256(manifest_path)


def load_manuscript(manuscript_dir: Path, results_freeze: Path, packet_manifest_hash: str) -> tuple[dict[str, Any], str]:
    manifest_path = manuscript_dir / "MANUSCRIPT_RENDER_MANIFEST.json"
    main_tex = manuscript_dir / "main.tex"
    manifest = read_json(manifest_path, "manuscript render manifest")
    require_status(manifest, EXPECTED_MANUSCRIPT_STATUS, "manuscript render manifest")
    if manifest.get("results_freeze_sha256") != sha256(results_freeze):
        fail("manuscript render is not bound to the supplied RESULTS_FREEZE")
    if manifest.get("fact_packet_manifest_sha256") != packet_manifest_hash:
        fail("manuscript render is not bound to the supplied fact-packet manifest")
    require_artifact(manifest, main_tex, "manuscript main.tex")
    fact_ids = manifest.get("fact_ids_rendered")
    marker_fields = manifest.get("paper_claim_marker_fields")
    if not isinstance(fact_ids, list) or not fact_ids or len(set(fact_ids)) != len(fact_ids):
        fail("manuscript render manifest has invalid rendered fact IDs")
    if not isinstance(marker_fields, dict) or set(marker_fields) != set(fact_ids):
        fail("manuscript render manifest has incomplete claim-marker coverage")
    return manifest, main_tex.read_text(encoding="utf-8")


def load_poster_content(poster_content: Path, results_freeze: Path, packet_manifest_hash: str) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_path = poster_content.parent / "POSTER_CONTENT_MANIFEST.json"
    manifest = read_json(manifest_path, "poster-content manifest")
    content = read_json(poster_content, "poster content")
    require_status(manifest, EXPECTED_POSTER_CONTENT_STATUS, "poster-content manifest")
    if manifest.get("results_freeze_sha256") != sha256(results_freeze):
        fail("poster content is not bound to the supplied RESULTS_FREEZE")
    if manifest.get("fact_packet_manifest_sha256") != packet_manifest_hash:
        fail("poster content is not bound to the supplied fact-packet manifest")
    require_artifact(manifest, poster_content, "poster content")
    trace_ids = content.get("result_trace_ids")
    if not isinstance(trace_ids, list) or not trace_ids or any(not isinstance(value, str) or not value for value in trace_ids):
        fail("poster content has invalid result-trace identifiers")
    if len(set(trace_ids)) != len(trace_ids):
        fail("poster content repeats a result-trace identifier")
    return manifest, content


def measurement_status(fact_id: str, fact: dict[str, str]) -> str:
    family = fact.get("result_family", "")
    raw = fact.get("measurement_status", "").strip()
    # RQ4 is a direct distributional computation whose fact-table schema does
    # not carry a construct-level status column.  Its predeclared status is
    # therefore computational-primary, never a human-experience claim.
    status = raw or ("COMPUTATIONAL_PRIMARY" if family == "RQ4" else "")
    if status not in ALLOWED_MEASUREMENT_STATUSES:
        fail(f"fact {fact_id} has no eligible measurement status")
    if status == "MEASUREMENT_UNSTABLE":
        fail(f"fact {fact_id} is measurement-unstable and cannot support a publication claim")
    return status


def numeric_value(fact_id: str, field: str, value: str) -> str | None:
    raw = value.strip()
    if raw.lower() in NON_NUMERIC_STATES:
        return None
    try:
        parsed = float(raw)
    except ValueError as exc:
        raise ValueError(f"PUBLICATION_TRACEABILITY_FAILED: fact {fact_id} field {field} is not numeric or NOT_ESTIMABLE") from exc
    if not math.isfinite(parsed):
        return None
    return raw


def family_boundary(family: str) -> str:
    return {
        "RQ2": "Computational output-text property under a frozen within-item prompt intervention; not a human judgment, cognitive claim, or lived-experience claim.",
        "RQ3": "Bounded alignment with released human-reference data; not a newly collected BLV rating, preference judgment, usefulness judgment, or lived-experience claim.",
        "RQ4": "Distributional text-profile measurement; not cognitive equivalence, accessibility value, dream incorporation, or an effect on people.",
        "RQ5": "Computational output-property measurement; not measured harm, preference, safety outcome, or lived-experience claim.",
    }[family]


def build_rows(
    facts: dict[str, dict[str, str]], manuscript: dict[str, Any], main_tex: str, poster_content: dict[str, Any],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    skipped: list[dict[str, str]] = []
    rendered_ids = [str(value) for value in manuscript["fact_ids_rendered"]]
    poster_ids = [str(value) for value in poster_content["result_trace_ids"]]
    for delivery, fact_ids in (("paper", rendered_ids), ("poster", poster_ids)):
        for fact_id in fact_ids:
            fact = facts.get(fact_id)
            if fact is None:
                fail(f"{delivery} content refers to a fact absent from the frozen packet: {fact_id}")
            family = fact.get("result_family", "")
            if family not in NUMERIC_FIELDS:
                fail(f"fact {fact_id} has unsupported result family: {family!r}")
            status = measurement_status(fact_id, fact)
            for field in NUMERIC_FIELDS[family]:
                if field not in fact:
                    fail(f"fact {fact_id} is missing expected source column {field}")
                reported = numeric_value(fact_id, field, fact[field])
                if reported is None:
                    skipped.append({"delivery": delivery, "fact_id": fact_id, "source_column": field, "reason": "NOT_ESTIMABLE_OR_NONFINITE"})
                    continue
                claim_id = f"{delivery.upper()}_{fact_id}_{field.upper()}"
                if delivery == "paper":
                    marker = f"CLAIM-ID: {claim_id}"
                    if main_tex.count(marker) != 1:
                        fail(f"manuscript source must contain exactly one marker for {claim_id}; observed {main_tex.count(marker)}")
                    location = f"table_{family}"
                    claim_type = "frozen_numeric_table_value"
                else:
                    location = f"poster_content_trace_{family}"
                    claim_type = "frozen_numeric_figure_value"
                rows.append({
                    "claim_id": claim_id,
                    "delivery": delivery,
                    "location": location,
                    "fact_id": fact_id,
                    "source_column": field,
                    "reported_value": reported,
                    "rounding_decimals": "EXACT",
                    "claim_type": claim_type,
                    "measurement_status": status,
                    "claim_boundary": family_boundary(family),
                })
    if not rows:
        fail("no finite numeric claims were eligible for traceability")
    return rows, skipped


def build_page_accounting(pdf_path: Path) -> dict[str, str | int]:
    if not pdf_path.is_file():
        fail(f"compiled manuscript PDF is missing: {pdf_path}")
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError(f"PUBLICATION_TRACEABILITY_FAILED: pypdf is required for page accounting: {exc}") from exc
    try:
        reader = PdfReader(str(pdf_path))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ValueError(f"PUBLICATION_TRACEABILITY_FAILED: cannot extract text from compiled manuscript PDF: {exc}") from exc
    if not pages:
        fail("compiled manuscript PDF has no pages")
    reference_index = next((index for index, text in enumerate(pages) if REFERENCE_HEADING.search(text)), None)
    if reference_index is None:
        fail("cannot conservatively locate a standalone References heading in the compiled PDF")
    reference_match = REFERENCE_HEADING.search(pages[reference_index])
    assert reference_match is not None
    # A reference section can begin on a fresh physical page or after main text
    # on a shared page.  Count a shared page as main text only when the
    # extracted text before the heading contains substantive content.  Page
    # headers alone are not enough to turn an otherwise reference-only page
    # into an extra main page.  This preserves the call's "excluding
    # references" rule while remaining conservative for genuinely shared pages.
    before_references = pages[reference_index][:reference_match.start()]
    substantive_before_references = re.sub(r"\s+", " ", before_references).strip()
    shared_reference_page = len(substantive_before_references) >= 120
    total = len(pages)
    main_pages = reference_index + (1 if shared_reference_page else 0)
    reference_pages = total - main_pages
    if main_pages > 4:
        fail("compiled manuscript exceeds the four-page main-text limit under conservative page accounting")
    return {
        "main_pages_excluding_references": main_pages,
        "reference_pages": reference_pages,
        "total_pdf_pages": total,
        "call_checked_date": datetime.now(timezone.utc).date().isoformat(),
        "call_url": "https://chi2027.acm.org/authors/posters/",
    }


def write_csv(path: Path, rows: list[dict[str, str]], columns: tuple[str, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, required=True)
    parser.add_argument("--fact-packet-dir", type=Path, required=True)
    parser.add_argument("--manuscript-dir", type=Path, required=True)
    parser.add_argument("--manuscript-pdf", type=Path, required=True)
    parser.add_argument("--poster-content", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite an existing publication-traceability directory")

    results, facts, packet_manifest_hash = load_facts(args.results_freeze, args.fact_packet_dir)
    manuscript, main_tex = load_manuscript(args.manuscript_dir, args.results_freeze, packet_manifest_hash)
    poster_manifest, poster_content = load_poster_content(args.poster_content, args.results_freeze, packet_manifest_hash)
    claim_rows, skipped = build_rows(facts, manuscript, main_tex, poster_content)
    page_accounting = build_page_accounting(args.manuscript_pdf)

    temp = args.outdir.parent / f".{args.outdir.name}.tmp-{uuid.uuid4().hex}"
    temp.mkdir(parents=True, exist_ok=False)
    claims_path = temp / "CLAIM_TRACEABILITY.csv"
    skipped_path = temp / "NON_NUMERIC_CLAIM_EXCLUSIONS.csv"
    accounting_path = temp / "PAGE_ACCOUNTING.json"
    write_csv(claims_path, claim_rows, CLAIM_COLUMNS)
    write_csv(skipped_path, skipped, ("delivery", "fact_id", "source_column", "reason"))
    accounting_path.write_text(json.dumps(page_accounting, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "status": "PUBLICATION_TRACEABILITY_FROZEN_FROM_RENDERED_ARTIFACTS",
        "results_freeze_sha256": sha256(args.results_freeze),
        "fact_packet_manifest_sha256": packet_manifest_hash,
        "manuscript_render_manifest_sha256": sha256(args.manuscript_dir / "MANUSCRIPT_RENDER_MANIFEST.json"),
        "poster_content_manifest_sha256": sha256(args.poster_content.parent / "POSTER_CONTENT_MANIFEST.json"),
        "manuscript_pdf_sha256": sha256(args.manuscript_pdf),
        "script_sha256": sha256(Path(__file__).resolve()),
        "new_human_data_collected": False,
        "claim_count": len(claim_rows),
        "non_numeric_claim_exclusion_count": len(skipped),
        "page_accounting": page_accounting,
        "artifacts": {
            claims_path.name: sha256(claims_path),
            skipped_path.name: sha256(skipped_path),
            accounting_path.name: sha256(accounting_path),
        },
        "boundary": "This ledger binds frozen numeric artifacts only. It does not make computational measurement into human judgment or expand the study's causal scope.",
    }
    manifest_path = temp / "PUBLICATION_TRACEABILITY_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(args.outdir)
    print(json.dumps({"status": manifest["status"], "claims": len(claim_rows), "pages": page_accounting["total_pdf_pages"]}, sort_keys=True))


if __name__ == "__main__":
    main()
