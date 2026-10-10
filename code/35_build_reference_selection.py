"""Freeze an anonymous citation selection after RESULTS_FREEZE without reading results.

This tool deliberately performs a narrower task than the audited-reference
generator.  It binds the predeclared citation policy to the SHA-256 of a
completed ``RESULTS_FREEZE.json`` receipt, validates the selected paper IDs
against local DOI-audit metadata, and writes a selection file that is
compatible with ``33_generate_audited_references.py``.

It never reads result tables, result ledgers, raw model outputs, synthetic
labels, private condition mappings, or numerical result values.  The later
audited-reference generator independently validates the complete results
ledger before it creates a bibliography.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RESULTS_STATUS = "RESULTS_FROZEN_PUBLIC_DATA_ONLY"
EXPECTED_POLICY_STATUS = "FROZEN_PRE_RESULTS_REFERENCE_SELECTION_POLICY"
EXPECTED_MANUSCRIPT_STATUS = "FROZEN_PRE_RESULTS_SELECTION_POLICY"
EXPECTED_REVIEW_STAGE = "ANONYMOUS_REVIEW"
EXPECTED_CITATION_KEYS = (
    "KANG2023",
    "XIE2025",
    "KREISS2022",
    "KAPUR2024",
    "GUIDEDOG2026",
    "PATARANUTAPORN2025",
)
REQUIRED_DOI_COLUMNS = {
    "paper_id",
    "doi",
    "title_verified",
    "year_verified",
    "venue_verified",
    "peer_review_status",
    "classification",
    "status",
}
REQUIRED_METADATA_COLUMNS = {"paper_id", "metadata_source", "metadata_verification_date"}
CHECKSUM_COLUMNS = ("artifact", "sha256")


def fail(message: str) -> None:
    raise ValueError(f"REFERENCE_SELECTION_BINDER_FAILED: {message}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        fail(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {label}: {exc}")
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
        fail(f"{label} contains no records")
    missing = required_columns.difference(columns)
    if missing:
        fail(f"{label} lacks required columns: {', '.join(sorted(missing))}")
    return [{str(key): "" if value is None else str(value) for key, value in row.items()} for row in rows]


def require_unique(rows: list[dict[str, str]], key: str, label: str) -> dict[str, dict[str, str]]:
    indexed: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row.get(key, "").strip()
        if not value:
            fail(f"{label} contains an empty {key}")
        if value in indexed:
            fail(f"{label} contains a duplicate {key}: {value}")
        indexed[value] = row
    return indexed


def require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail(f"{label} must be non-empty text")
    return " ".join(value.split())


def validate_results_receipt(path: Path) -> tuple[dict[str, Any], str]:
    """Read only the RESULTS_FREEZE receipt itself, never its ledger or outputs."""
    freeze = read_json(path, "RESULTS_FREEZE receipt")
    if freeze.get("status") != EXPECTED_RESULTS_STATUS:
        fail("RESULTS_FREEZE receipt has an incomplete or unsupported status")
    if freeze.get("new_human_data_collected") is not False:
        fail("RESULTS_FREEZE receipt does not attest to zero new human data collection")
    if freeze.get("condition_unblinded_once") is not True:
        fail("RESULTS_FREEZE receipt does not attest to the authorized single unblinding")
    return freeze, sha256(path)


def validate_policy(
    policy: dict[str, Any], manuscript_policy: dict[str, Any], audit_by_id: dict[str, dict[str, str]],
    metadata_by_id: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    if policy.get("schema_version") != 1 or policy.get("status") != EXPECTED_POLICY_STATUS:
        fail("reference-selection policy has an unsupported schema or status")
    if policy.get("review_stage") != EXPECTED_REVIEW_STAGE:
        fail("reference-selection policy is not limited to anonymous review")
    if manuscript_policy.get("schema_version") != 1 or manuscript_policy.get("status") != EXPECTED_MANUSCRIPT_STATUS:
        fail("manuscript render policy has an unsupported schema or status")
    manuscript_keys = manuscript_policy.get("citation_keys")
    policy_keys = policy.get("citation_keys")
    if not isinstance(manuscript_keys, list) or not isinstance(policy_keys, list):
        fail("citation-key policies must contain lists")
    if tuple(manuscript_keys) != EXPECTED_CITATION_KEYS:
        fail("manuscript render policy no longer contains the frozen exact citation-key sequence")
    if tuple(policy_keys) != EXPECTED_CITATION_KEYS or tuple(policy_keys) != tuple(manuscript_keys):
        fail("reference-selection policy citation keys differ from the frozen manuscript policy")

    citations_raw = policy.get("citations")
    if not isinstance(citations_raw, list) or len(citations_raw) != len(EXPECTED_CITATION_KEYS):
        fail("reference-selection policy must contain exactly the six frozen citations")

    citations: list[dict[str, str]] = []
    seen_keys: set[str] = set()
    seen_papers: set[str] = set()
    for index, raw in enumerate(citations_raw, start=1):
        if not isinstance(raw, dict):
            fail(f"reference-selection policy citation {index} must be an object")
        citation_key = require_string(raw.get("citation_key"), f"citation {index}.citation_key")
        paper_id = require_string(raw.get("paper_id"), f"citation {index}.paper_id")
        classification = require_string(raw.get("expected_classification"), f"citation {index}.expected_classification")
        claim_use = require_string(raw.get("claim_use"), f"citation {index}.claim_use")
        boundary = require_string(raw.get("evidence_boundary"), f"citation {index}.evidence_boundary")
        if citation_key != EXPECTED_CITATION_KEYS[index - 1] or citation_key in seen_keys:
            fail("reference-selection policy citation-key order or uniqueness differs from the frozen policy")
        if paper_id in seen_papers:
            fail(f"reference-selection policy reuses paper_id: {paper_id}")
        audit = audit_by_id.get(paper_id)
        if audit is None:
            fail(f"selected paper_id has no DOI-audit record: {paper_id}")
        if paper_id not in metadata_by_id:
            fail(f"selected paper_id has no audited metadata record: {paper_id}")
        if audit.get("status") != "PASS":
            fail(f"selected paper_id is not DOI-audit PASS: {paper_id}")
        if any(audit.get(field) != "yes" for field in ("title_verified", "year_verified", "venue_verified")):
            fail(f"selected paper_id lacks complete bibliographic verification: {paper_id}")
        if audit.get("classification") != classification:
            fail(f"selected paper_id classification changed: {paper_id}")
        if paper_id == "KAPUR2024":
            if classification != "workshop_article" or "workshop" not in boundary.lower():
                fail("KAPUR2024 must retain workshop_article classification and an explicit workshop boundary")
        seen_keys.add(citation_key)
        seen_papers.add(paper_id)
        citations.append({
            "citation_key": citation_key,
            "paper_id": paper_id,
            "claim_use": claim_use,
            "evidence_boundary": boundary,
        })
    if tuple(citation["citation_key"] for citation in citations) != EXPECTED_CITATION_KEYS:
        fail("selected citations do not exactly cover the frozen six citation keys")
    return citations


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CHECKSUM_COLUMNS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def atomic_publish(temp: Path, outdir: Path) -> None:
    names = ("reference_selection.json", "reference_selection_manifest.json", "reference_selection_checksums.csv")
    targets = [outdir / name for name in names]
    existing = [target.name for target in targets if target.exists()]
    if existing:
        fail(f"refusing to overwrite immutable selection artifacts: {', '.join(existing)}")
    try:
        for name, target in zip(names, targets, strict=True):
            os.replace(temp / name, target)
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, help="RESULTS_FREEZE receipt; only its JSON receipt is read")
    parser.add_argument("--policy", type=Path, default=ROOT / "config" / "reference_selection_policy_v1.json")
    parser.add_argument("--manuscript-policy", type=Path, default=ROOT / "config" / "manuscript_render_plan_policy_v1.json")
    parser.add_argument("--doi-audit", type=Path, default=ROOT / "refs" / "doi_audit.csv")
    parser.add_argument("--metadata", type=Path, default=ROOT / "refs" / "audited_reference_metadata.csv")
    parser.add_argument("--outdir", type=Path, default=ROOT / "refs")
    parser.add_argument("--check-policy", action="store_true", help="validate frozen citation mapping only; do not read RESULTS_FREEZE or write output")
    args = parser.parse_args()
    if args.check_policy and args.results_freeze is not None:
        parser.error("--check-policy must not be combined with --results-freeze")
    if not args.check_policy and args.results_freeze is None:
        parser.error("--results-freeze is required unless --check-policy is used")
    outdir = args.outdir.resolve()
    refs_root = (ROOT / "refs").resolve()
    if outdir != refs_root:
        parser.error("--outdir must be the canonical refs directory for immutable anonymous selection artifacts")

    policy = read_json(args.policy, "reference-selection policy")
    manuscript_policy = read_json(args.manuscript_policy, "manuscript render policy")
    audit_by_id = require_unique(read_csv(args.doi_audit, REQUIRED_DOI_COLUMNS, "DOI audit"), "paper_id", "DOI audit")
    metadata_by_id = require_unique(read_csv(args.metadata, REQUIRED_METADATA_COLUMNS, "audited metadata"), "paper_id", "audited metadata")
    citations = validate_policy(policy, manuscript_policy, audit_by_id, metadata_by_id)
    if args.check_policy:
        print(json.dumps({"status": "REFERENCE_SELECTION_POLICY_VALID", "citations": len(citations)}, sort_keys=True))
        return 0

    # This is intentionally the only access to the results stage.  Do not add
    # ledger/result-table validation here; code/33 is responsible for that.
    freeze, freeze_hash = validate_results_receipt(args.results_freeze)
    selection = {
        "schema_version": 1,
        "status": "REFERENCE_SELECTION_FROZEN_ANONYMOUS",
        "review_stage": EXPECTED_REVIEW_STAGE,
        "results_freeze_sha256": freeze_hash,
        "citations": citations,
        "selection_policy_id": policy["policy_id"],
        "selection_principle": policy["selection_principle"],
        "results_access_boundary": policy["results_access_boundary"],
    }
    manifest = {
        "schema_version": 1,
        "status": "REFERENCE_SELECTION_FROZEN_ANONYMOUS",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "scope": "predeclared anonymous citation selection only; no result values, result tables, raw outputs, synthetic labels, or condition mappings were read",
        "results_freeze_status": freeze["status"],
        "results_freeze_sha256": freeze_hash,
        "reference_selection_policy_sha256": sha256(args.policy),
        "manuscript_render_policy_sha256": sha256(args.manuscript_policy),
        "doi_audit_sha256": sha256(args.doi_audit),
        "audited_metadata_sha256": sha256(args.metadata),
        "generator_script_sha256": sha256(Path(__file__).resolve()),
        "citation_keys": list(EXPECTED_CITATION_KEYS),
        "citation_count": len(citations),
        "new_human_data_collected": False,
        "condition_unblinded_once": True,
        "alt_test_current_study": "NOT_APPLICABLE_TO_CURRENT_DESIGN",
    }

    temp = outdir / f".reference-selection-{uuid.uuid4().hex}"
    if temp.exists():
        fail("unexpected temporary selection path already exists")
    try:
        temp.mkdir(parents=False, exist_ok=False)
        selection_path = temp / "reference_selection.json"
        manifest_path = temp / "reference_selection_manifest.json"
        selection_path.write_text(json.dumps(selection, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        manifest["reference_selection_sha256"] = sha256(selection_path)
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        write_csv(temp / "reference_selection_checksums.csv", [
            {"artifact": selection_path.name, "sha256": sha256(selection_path)},
            {"artifact": manifest_path.name, "sha256": sha256(manifest_path)},
        ])
        atomic_publish(temp, outdir)
    except Exception:
        shutil.rmtree(temp, ignore_errors=True)
        raise
    print(json.dumps({"status": "REFERENCE_SELECTION_FROZEN_ANONYMOUS", "citations": len(citations), "outdir": str(outdir)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
