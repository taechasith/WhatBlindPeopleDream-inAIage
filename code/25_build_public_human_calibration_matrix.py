"""Build a metadata-only receipt for public human-calibration sources.

This is a pre-unblinding provenance check.  It validates only the public
calibration matrix, source registers, the local public-reference build
manifest, byte hashes, and CSV headers.  It never reads outcome rows,
condition mappings, model outputs, human-coder files, or annotation packets.

The resulting CSV is a source-readiness receipt, not a calibration result.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "PUBLIC_HUMAN_CALIBRATION_MATRIX.csv"
TIER_MATRIX_PATH = ROOT / "CONSTRUCT_MEASUREMENT_TIER_MATRIX.csv"
SOURCE_GATE_PATH = ROOT / "data" / "PUBLIC_DATA_SOURCE_GATE.csv"
DATA_MANIFEST_PATH = ROOT / "data" / "MANIFEST.csv"
CHECKSUMS_PATH = ROOT / "data" / "CHECKSUMS.csv"
REFERENCE_MANIFEST_PATH = ROOT / "data" / "public_reference" / "processed" / "build_manifest.json"
RESULT_PATH = ROOT / "results" / "public_human_calibration_matrix.csv"

RUN_SCOPE = "PUBLIC_METADATA_ONLY_NO_OUTPUT_OR_LABEL_ANALYSIS"
ARTIFACT_SCHEMA_VERSION = "1.0"

MATRIX_FIELDS = (
    "construct",
    "measurement_layer",
    "public_dataset",
    "human_label_type",
    "population",
    "same_task_or_cross_domain",
    "same_item_or_different_item",
    "measurement_overlap",
    "validation_strength",
    "limitations",
    "availability_status",
    "planned_role",
)
TIER_MATRIX_FIELDS = (
    "construct",
    "measurement_layer",
    "prospective_tier",
    "proposed_measurement_status",
    "bounded_operationalization",
    "public_human_calibration",
    "claim_boundary",
)
SOURCE_GATE_FIELDS = (
    "dataset_id",
    "role",
    "official_source",
    "version_or_revision",
    "license_or_terms",
    "access_checked_2026_10_06",
    "status",
    "allowed_current_use",
    "reason_or_next_gate",
)
DATA_MANIFEST_FIELDS = (
    "dataset_id",
    "version_or_commit",
    "access_date",
    "source_url",
    "license_or_terms",
    "raw_path",
    "processing_path",
    "status",
    "notes",
)
CHECKSUM_FIELDS = ("dataset_id", "path", "algorithm", "checksum", "access_date")
CAPTION_FIELDS = (
    "data_status",
    "source",
    "split",
    "image_id",
    "image_filename",
    "caption_id",
    "caption_text",
    "is_precanned",
    "text_detected",
    "image_text_detected",
)
KAPUR_FIELDS = (
    "data_status",
    "source",
    "comparison_set",
    "context",
    "img_id",
    "hypothesis",
    "hypothesis_avg_overall_blv_rating",
    "hypothesis_avg_overall_sighted_rating",
    "reference_count",
    "hypothesis_length",
    "avg_reference_length",
    "max_reference_length",
    "min_reference_length",
    "Bleu_1",
    "Bleu_2",
    "Bleu_3",
    "Bleu_4",
    "METEOR",
    "ROUGE_L",
    "Spice",
)

EXPECTED_REFERENCE_INPUTS = {
    "data/vizwiz_captions/processed/annotations_source/annotations/val.json",
    "data/kapur/raw/reference-based-bias/datasets/context_sensitive.xlsx",
    "data/kapur/raw/reference-based-bias/datasets/different_context.xlsx",
}


@dataclass(frozen=True)
class SourceSpec:
    """The public provenance records that are permitted for one matrix source."""

    source_gate_id: str | None
    data_manifest_id: str | None
    derived_path: str | None
    derived_header: tuple[str, ...] | None
    estimation_status: str
    boundary: str


SOURCE_SPECS: dict[str, SourceSpec] = {
    "none": SourceSpec(
        source_gate_id=None,
        data_manifest_id=None,
        derived_path=None,
        derived_header=None,
        estimation_status="NOT_APPLICABLE_DIRECT_TEXT_PROPERTY",
        boundary=(
            "No released human source is required for a direct text-property measurement. "
            "This is not evidence of human experience, preference, truth, safety, or harm."
        ),
    ),
    "VizWiz VQA": SourceSpec(
        source_gate_id="VIZWIZ_VQA",
        data_manifest_id="VIZWIZ_VQA",
        derived_path=None,
        derived_header=None,
        estimation_status="NOT_ESTIMATED_PRE_UNBLINDING",
        boundary=(
            "Released answers and answerability are source references only here; "
            "this receipt performs no output join, correctness claim, or condition comparison."
        ),
    ),
    "VizWiz Captions": SourceSpec(
        source_gate_id="VIZWIZ_CAPTIONS",
        data_manifest_id="VIZWIZ_CAPTIONS",
        derived_path="data/public_reference/processed/vizwiz_captions_val.csv",
        derived_header=CAPTION_FIELDS,
        estimation_status="NOT_ESTIMATED_PRE_UNBLINDING",
        boundary=(
            "Multiple captions are public human references, not independent replicates, "
            "universal ground truth, BLV preference, or current-output ratings."
        ),
    ),
    "Kapur--Kreiss released data": SourceSpec(
        source_gate_id="KAPUR_KREISS_2024",
        data_manifest_id="KAPUR_KREISS_2024",
        derived_path="data/public_reference/processed/kapur_preference_ratings.csv",
        derived_header=KAPUR_FIELDS,
        estimation_status="NOT_ESTIMATED_PRE_UNBLINDING",
        boundary=(
            "Released aggregate comparison records are external construct evidence only; "
            "this receipt performs no metric association or condition analysis."
        ),
    ),
    "GuideDog Gold": SourceSpec(
        source_gate_id="GUIDEDOG",
        data_manifest_id="GUIDEDOG",
        derived_path=None,
        derived_header=None,
        estimation_status="NOT_ESTIMABLE_ACCESS_UNAVAILABLE",
        boundary=(
            "No lawful authorized local access is documented. Do not bypass the gate, scrape, "
            "substitute synthetic labels, or report a GuideDog calibration result. A prospective "
            "source-and-method amendment is required before any future use."
        ),
    ),
    "Be My AI / Xie et al. released corpus": SourceSpec(
        source_gate_id="XIE_CHI25_LMM",
        data_manifest_id="XIE_CHI25_LMM",
        derived_path=None,
        derived_header=None,
        estimation_status="NOT_ESTIMABLE_DESCRIPTIVE_ONLY",
        boundary=(
            "The released corpus is ecological/descriptive context only. It is not a gold-label, "
            "same-item, prevalence, preference, or calibration-estimate source."
        ),
    ),
    "DreamBank blind series": SourceSpec(
        source_gate_id=None,
        data_manifest_id="DREAMBANK",
        derived_path=None,
        derived_header=None,
        estimation_status="NOT_ESTIMABLE_HISTORICAL_REFERENCE_ONLY",
        boundary=(
            "Human-authored dream reports are historical representational-space context, not a "
            "validation source for AI labels, cognition, preference, or intervention effects."
        ),
    ),
}


class Audit:
    """Collect machine-readable pass/fail checks without inspecting source semantics."""

    def __init__(self) -> None:
        self.checks: dict[str, str] = {}
        self.failures: list[str] = []

    def record(self, name: str, passed: bool, detail: str) -> bool:
        self.checks[name] = "PASS" if passed else "FAIL"
        if not passed:
            self.failures.append(f"{name}: {detail}")
        return passed

    def status(self, *check_names: str) -> str:
        return "PASS" if all(self.checks.get(name) == "PASS" for name in check_names) else "FAIL"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def optional_sha256(path: Path, audit: Audit, check_name: str) -> str:
    if not audit.record(check_name, path.is_file(), f"missing file: {display_path(path)}"):
        return "MISSING"
    try:
        return sha256_file(path)
    except OSError as error:
        audit.record(f"{check_name}_readable", False, f"cannot hash {display_path(path)}: {error}")
        return "UNREADABLE"


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_csv_table(
    path: Path, expected_fields: tuple[str, ...], audit: Audit, label: str
) -> list[dict[str, str]]:
    if not audit.record(f"{label}_exists", path.is_file(), f"missing file: {display_path(path)}"):
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            observed_fields = tuple(reader.fieldnames or ())
            audit.record(
                f"{label}_schema",
                observed_fields == expected_fields,
                f"unexpected header in {display_path(path)}",
            )
            rows = list(reader)
    except (OSError, csv.Error, UnicodeError) as error:
        audit.record(f"{label}_readable", False, f"cannot read {display_path(path)}: {error}")
        return []

    audit.record(f"{label}_nonempty", bool(rows), f"no rows in {display_path(path)}")
    for row_number, row in enumerate(rows, start=2):
        complete = all((row.get(field) or "").strip() for field in expected_fields)
        audit.record(
            f"{label}_row_{row_number}_complete",
            complete,
            f"blank required metadata field in {display_path(path)} row {row_number}",
        )
    return rows


def read_csv_header(path: Path, audit: Audit, check_name: str) -> tuple[str, ...]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as source:
            header = tuple(next(csv.reader(source), []))
    except (OSError, csv.Error, UnicodeError) as error:
        audit.record(check_name, False, f"cannot read header in {display_path(path)}: {error}")
        return ()
    audit.record(check_name, bool(header), f"missing header in {display_path(path)}")
    return header


def index_by_dataset_id(
    rows: list[dict[str, str]], audit: Audit, label: str
) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        dataset_id = (row.get("dataset_id") or "").strip()
        unique = bool(dataset_id) and dataset_id not in result
        audit.record(f"{label}_id_{dataset_id or 'BLANK'}_unique", unique, "missing or duplicate dataset_id")
        if unique:
            result[dataset_id] = row
    return result


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def normalise_manifest_path(value: str) -> str:
    return PurePosixPath(value.replace("\\", "/")).as_posix()


def public_manifest_path(
    value: str, allowed_roots: tuple[Path, ...], audit: Audit, check_name: str
) -> Path | None:
    normalised = normalise_manifest_path(value)
    relative = PurePosixPath(normalised)
    candidate = (ROOT / Path(*relative.parts)).resolve()
    safe = (
        not relative.is_absolute()
        and ".." not in relative.parts
        and any(is_within(candidate, root) for root in allowed_roots)
    )
    audit.record(check_name, safe, f"manifest path is outside the public allowlist: {value}")
    return candidate if safe else None


def valid_digest(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(char in "0123456789abcdef" for char in value.lower())


def validate_reference_manifest(
    audit: Audit, checksums: dict[str, dict[str, str]]
) -> tuple[dict[str, dict[str, str]], str]:
    manifest_hash = optional_sha256(REFERENCE_MANIFEST_PATH, audit, "reference_manifest_exists")
    if manifest_hash in {"MISSING", "UNREADABLE"}:
        return {}, manifest_hash
    try:
        payload = json.loads(REFERENCE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.record("reference_manifest_json", False, f"invalid JSON: {error}")
        return {}, manifest_hash

    expected_keys = {"data_status", "inputs", "outputs", "output_files"}
    audit.record(
        "reference_manifest_schema",
        isinstance(payload, dict) and set(payload) == expected_keys,
        "unexpected public-reference build-manifest keys",
    )
    if not isinstance(payload, dict):
        return {}, manifest_hash
    audit.record(
        "reference_manifest_data_status",
        payload.get("data_status") == "RELEASED_SOURCE_DERIVED_LOCAL_ONLY",
        "public-reference manifest does not declare local-only released-source status",
    )
    inputs = payload.get("inputs")
    outputs = payload.get("outputs")
    output_files = payload.get("output_files")
    audit.record("reference_manifest_inputs_type", isinstance(inputs, dict), "inputs must be an object")
    audit.record("reference_manifest_outputs_type", isinstance(outputs, dict), "outputs must be an object")
    audit.record("reference_manifest_output_files_type", isinstance(output_files, dict), "output_files must be an object")
    if not isinstance(inputs, dict) or not isinstance(outputs, dict) or not isinstance(output_files, dict):
        return {}, manifest_hash

    normalised_inputs = {normalise_manifest_path(str(path)): digest for path, digest in inputs.items()}
    audit.record(
        "reference_manifest_input_coverage",
        set(normalised_inputs) == EXPECTED_REFERENCE_INPUTS,
        "unexpected public-reference input set",
    )
    input_roots = (ROOT / "data" / "vizwiz_captions", ROOT / "data" / "kapur")
    for relative_path, expected_hash in normalised_inputs.items():
        path_token = relative_path.replace("/", "_").replace(".", "_")
        audit.record(
            f"reference_input_{path_token}_digest_format",
            valid_digest(expected_hash),
            f"invalid SHA-256 in build manifest for {relative_path}",
        )
        source_path = public_manifest_path(
            relative_path, input_roots, audit, f"reference_input_{path_token}_allowlisted"
        )
        if source_path is None:
            continue
        observed_hash = optional_sha256(source_path, audit, f"reference_input_{path_token}_exists")
        if observed_hash not in {"MISSING", "UNREADABLE"}:
            audit.record(
                f"reference_input_{path_token}_hash",
                observed_hash == str(expected_hash).lower(),
                f"input hash mismatch for {relative_path}",
            )
        checksum_row = checksums.get(relative_path)
        if checksum_row:
            audit.record(
                f"reference_input_{path_token}_checksum_register",
                checksum_row.get("checksum", "").lower() == str(expected_hash).lower(),
                f"checksum register disagrees with build manifest for {relative_path}",
            )

    expected_outputs = {
        "data/public_reference/processed/vizwiz_captions_val.csv": CAPTION_FIELDS,
        "data/public_reference/processed/kapur_preference_ratings.csv": KAPUR_FIELDS,
    }
    normalised_outputs = {normalise_manifest_path(str(path)): digest for path, digest in output_files.items()}
    audit.record(
        "reference_manifest_output_coverage",
        set(normalised_outputs) == set(expected_outputs),
        "unexpected public-reference output set",
    )
    required_output_metadata = {
        "vizwiz_captions_val_rows",
        "vizwiz_captions_val_unique_images",
        "kapur_preference_rows",
        "kapur_comparison_sets",
    }
    audit.record(
        "reference_manifest_output_metadata_schema",
        set(outputs) == required_output_metadata,
        "unexpected public-reference output-metadata keys",
    )

    details: dict[str, dict[str, str]] = {}
    output_root = ROOT / "data" / "public_reference" / "processed"
    for relative_path, expected_header in expected_outputs.items():
        path_token = relative_path.replace("/", "_").replace(".", "_")
        expected_hash = normalised_outputs.get(relative_path, "MISSING")
        audit.record(
            f"reference_output_{path_token}_digest_format",
            valid_digest(expected_hash),
            f"invalid SHA-256 in build manifest for {relative_path}",
        )
        output_path = public_manifest_path(
            relative_path, (output_root,), audit, f"reference_output_{path_token}_allowlisted"
        )
        observed_hash = "MISSING"
        if output_path is not None:
            observed_hash = optional_sha256(output_path, audit, f"reference_output_{path_token}_exists")
            if observed_hash not in {"MISSING", "UNREADABLE"}:
                audit.record(
                    f"reference_output_{path_token}_hash",
                    observed_hash == str(expected_hash).lower(),
                    f"derived-file hash mismatch for {relative_path}",
                )
                observed_header = read_csv_header(
                    output_path, audit, f"reference_output_{path_token}_header_present"
                )
                audit.record(
                    f"reference_output_{path_token}_schema",
                    observed_header == expected_header,
                    f"unexpected derived-file header for {relative_path}",
                )
        details[relative_path] = {
            "expected_sha256": str(expected_hash),
            "observed_sha256": observed_hash,
            "status": audit.status(
                f"reference_output_{path_token}_allowlisted",
                f"reference_output_{path_token}_exists",
                f"reference_output_{path_token}_hash",
                f"reference_output_{path_token}_header_present",
                f"reference_output_{path_token}_schema",
            ),
        }
    return details, manifest_hash


def source_status(
    spec: SourceSpec, audit: Audit, derived_details: dict[str, dict[str, str]]
) -> str:
    checks = ["matrix_schema", "source_gate_schema", "data_manifest_schema", "checksums_schema"]
    if spec.source_gate_id:
        checks.append(f"source_gate_id_{spec.source_gate_id}_unique")
    if spec.data_manifest_id:
        checks.append(f"data_manifest_id_{spec.data_manifest_id}_unique")
    if spec.derived_path:
        details = derived_details.get(spec.derived_path)
        if not details or details["status"] != "PASS":
            return "FAIL"
        checks.extend(("reference_manifest_schema", "reference_manifest_data_status"))
    return audit.status(*checks)


def require_matrix_policy_guards(
    rows: list[dict[str, str]], tier_rows: list[dict[str, str]], audit: Audit
) -> None:
    """Validate one row per active construct/layer plus named context rows.

    This validates metadata and prospective scope only. It never reads a model
    output, a condition map, or a label value.
    """
    observed_sources = {row.get("public_dataset", "").strip() for row in rows}
    audit.record(
        "matrix_sources_known",
        observed_sources.issubset(set(SOURCE_SPECS)),
        "matrix contains a public_dataset outside the frozen calibration-source catalog",
    )
    required_pairs = {
        (row.get("construct", "").strip(), row.get("measurement_layer", "").strip())
        for row in tier_rows
    }
    observed_pairs = {
        (row.get("construct", "").strip(), row.get("measurement_layer", "").strip())
        for row in rows
        if row.get("measurement_layer", "").strip() != "external_validation_context"
    }
    audit.record(
        "matrix_construct_layer_coverage",
        observed_pairs == required_pairs,
        "matrix must have exactly one non-context row for each construct/layer in the tier matrix",
    )
    pairs = [
        (row.get("construct", "").strip(), row.get("measurement_layer", "").strip())
        for row in rows
    ]
    audit.record("matrix_construct_layer_unique", len(pairs) == len(set(pairs)), "duplicate construct/layer matrix row")
    context_rows = [row for row in rows if row.get("measurement_layer", "").strip() == "external_validation_context"]
    audit.record(
        "matrix_context_rows_known",
        all(row.get("construct", "").strip() and row.get("public_dataset", "").strip() in SOURCE_SPECS for row in context_rows),
        "external validation context rows require a nonblank construct and known source",
    )
    guide_dog_rows = [row for row in rows if row.get("public_dataset") == "GuideDog Gold"]
    audit.record(
        "guidedog_matrix_access_guard",
        len(guide_dog_rows) == 1 and guide_dog_rows[0].get("availability_status") == "ACCESS_UNAVAILABLE",
        "GuideDog must remain ACCESS_UNAVAILABLE in the pre-unblinding matrix",
    )


def write_receipt(
    matrix_rows: list[dict[str, str]],
    gate_index: dict[str, dict[str, str]],
    manifest_index: dict[str, dict[str, str]],
    derived_details: dict[str, dict[str, str]],
    hashes: dict[str, str],
    audit: Audit,
) -> None:
    fieldnames = (
        "artifact_schema_version",
        "run_scope",
        "matrix_sha256",
        "tier_matrix_sha256",
        "source_gate_sha256",
        "data_manifest_sha256",
        "reference_build_manifest_sha256",
        "matrix_row_number",
        "construct",
        "measurement_layer",
        "public_dataset",
        "matrix_availability_status",
        "planned_role",
        "source_gate_dataset_id",
        "source_gate_status",
        "data_manifest_dataset_id",
        "data_manifest_status",
        "derived_reference_path",
        "derived_reference_status",
        "derived_reference_expected_sha256",
        "derived_reference_observed_sha256",
        "estimation_status",
        "boundary",
        "provenance_validation_status",
    )
    output_rows: list[dict[str, str]] = []
    for row_number, matrix_row in enumerate(matrix_rows, start=2):
        public_dataset = matrix_row.get("public_dataset", "").strip()
        spec = SOURCE_SPECS.get(public_dataset)
        if spec is None:
            output_rows.append(
                {
                    "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                    "run_scope": RUN_SCOPE,
                    "matrix_sha256": hashes["matrix"],
                    "tier_matrix_sha256": hashes["tier_matrix"],
                    "source_gate_sha256": hashes["source_gate"],
                    "data_manifest_sha256": hashes["data_manifest"],
                    "reference_build_manifest_sha256": hashes["reference_manifest"],
                    "matrix_row_number": str(row_number),
                    "construct": matrix_row.get("construct", ""),
                    "measurement_layer": matrix_row.get("measurement_layer", ""),
                    "public_dataset": public_dataset,
                    "matrix_availability_status": matrix_row.get("availability_status", ""),
                    "planned_role": matrix_row.get("planned_role", ""),
                    "source_gate_dataset_id": "UNKNOWN_MATRIX_SOURCE",
                    "source_gate_status": "NOT_RESOLVED",
                    "data_manifest_dataset_id": "UNKNOWN_MATRIX_SOURCE",
                    "data_manifest_status": "NOT_RESOLVED",
                    "derived_reference_path": "NOT_RESOLVED",
                    "derived_reference_status": "NOT_RESOLVED",
                    "derived_reference_expected_sha256": "NOT_RESOLVED",
                    "derived_reference_observed_sha256": "NOT_RESOLVED",
                    "estimation_status": "NOT_ESTIMABLE_UNKNOWN_SOURCE",
                    "boundary": "Matrix source is not in the frozen public-source catalog.",
                    "provenance_validation_status": "FAIL",
                }
            )
            continue

        gate_row = gate_index.get(spec.source_gate_id or "")
        manifest_row = manifest_index.get(spec.data_manifest_id or "")
        if spec.derived_path:
            derived = derived_details.get(
                spec.derived_path,
                {
                    "expected_sha256": "MISSING",
                    "observed_sha256": "MISSING",
                    "status": "FAIL",
                },
            )
            derived_path = spec.derived_path
        else:
            derived = {"expected_sha256": "NOT_REQUIRED", "observed_sha256": "NOT_REQUIRED", "status": "NOT_REQUIRED"}
            derived_path = "NOT_REQUIRED_FOR_THIS_SOURCE_ROLE"
        output_rows.append(
            {
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION,
                "run_scope": RUN_SCOPE,
                "matrix_sha256": hashes["matrix"],
                "tier_matrix_sha256": hashes["tier_matrix"],
                "source_gate_sha256": hashes["source_gate"],
                "data_manifest_sha256": hashes["data_manifest"],
                "reference_build_manifest_sha256": hashes["reference_manifest"],
                "matrix_row_number": str(row_number),
                "construct": matrix_row.get("construct", ""),
                "measurement_layer": matrix_row.get("measurement_layer", ""),
                "public_dataset": public_dataset,
                "matrix_availability_status": matrix_row.get("availability_status", ""),
                "planned_role": matrix_row.get("planned_role", ""),
                "source_gate_dataset_id": spec.source_gate_id or "NOT_APPLICABLE",
                "source_gate_status": gate_row.get("status", "NOT_APPLICABLE") if gate_row else "NOT_APPLICABLE",
                "data_manifest_dataset_id": spec.data_manifest_id or "NOT_APPLICABLE",
                "data_manifest_status": manifest_row.get("status", "NOT_APPLICABLE") if manifest_row else "NOT_APPLICABLE",
                "derived_reference_path": derived_path,
                "derived_reference_status": derived["status"],
                "derived_reference_expected_sha256": derived["expected_sha256"],
                "derived_reference_observed_sha256": derived["observed_sha256"],
                "estimation_status": spec.estimation_status,
                "boundary": spec.boundary,
                "provenance_validation_status": source_status(spec, audit, derived_details),
            }
        )

    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = RESULT_PATH.with_suffix(".tmp")
    with temporary_path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    temporary_path.replace(RESULT_PATH)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate public metadata and provenance without rewriting the receipt",
    )
    args = parser.parse_args()
    audit = Audit()

    matrix_rows = read_csv_table(MATRIX_PATH, MATRIX_FIELDS, audit, "matrix")
    tier_rows = read_csv_table(TIER_MATRIX_PATH, TIER_MATRIX_FIELDS, audit, "tier_matrix")
    require_matrix_policy_guards(matrix_rows, tier_rows, audit)
    gate_rows = read_csv_table(SOURCE_GATE_PATH, SOURCE_GATE_FIELDS, audit, "source_gate")
    data_manifest_rows = read_csv_table(DATA_MANIFEST_PATH, DATA_MANIFEST_FIELDS, audit, "data_manifest")
    checksum_rows = read_csv_table(CHECKSUMS_PATH, CHECKSUM_FIELDS, audit, "checksums")
    gate_index = index_by_dataset_id(gate_rows, audit, "source_gate")
    data_manifest_index = index_by_dataset_id(data_manifest_rows, audit, "data_manifest")
    checksums_index = {
        normalise_manifest_path(row["path"]): row
        for row in checksum_rows
        if row.get("path") and row.get("checksum")
    }
    audit.record(
        "checksums_unique_paths",
        len(checksums_index) == len(checksum_rows),
        "missing or duplicate checksum path",
    )

    for public_dataset, spec in SOURCE_SPECS.items():
        if spec.source_gate_id:
            audit.record(
                f"source_gate_required_{spec.source_gate_id}",
                spec.source_gate_id in gate_index,
                f"source gate lacks required {spec.source_gate_id} record for {public_dataset}",
            )
        if spec.data_manifest_id:
            audit.record(
                f"data_manifest_required_{spec.data_manifest_id}",
                spec.data_manifest_id in data_manifest_index,
                f"data manifest lacks required {spec.data_manifest_id} record for {public_dataset}",
            )

    guide_dog_gate = gate_index.get("GUIDEDOG", {})
    audit.record(
        "guidedog_source_gate_status",
        guide_dog_gate.get("status") == "ACCESS_REQUIRES_HF_TOKEN",
        "GuideDog source gate must remain ACCESS_REQUIRES_HF_TOKEN",
    )
    xie_gate = gate_index.get("XIE_CHI25_LMM", {})
    audit.record(
        "xie_source_gate_status",
        xie_gate.get("status") == "LOCAL_TEXT_RESTRICTED",
        "Xie / Be My AI source gate must remain LOCAL_TEXT_RESTRICTED",
    )

    derived_details, reference_manifest_hash = validate_reference_manifest(audit, checksums_index)
    hashes = {
        "matrix": optional_sha256(MATRIX_PATH, audit, "matrix_hashable"),
        "tier_matrix": optional_sha256(TIER_MATRIX_PATH, audit, "tier_matrix_hashable"),
        "source_gate": optional_sha256(SOURCE_GATE_PATH, audit, "source_gate_hashable"),
        "data_manifest": optional_sha256(DATA_MANIFEST_PATH, audit, "data_manifest_hashable"),
        "reference_manifest": reference_manifest_hash,
    }

    if not args.check:
        write_receipt(
            matrix_rows,
            gate_index,
            data_manifest_index,
            derived_details,
            hashes,
            audit,
        )

    if audit.failures:
        for failure in audit.failures:
            print(f"FAIL\t{failure}")
        if not args.check:
            print(f"WROTE_STATUS_RECEIPT\t{display_path(RESULT_PATH)}")
        return 1
    print("PASS\tpublic human-calibration schema and provenance only")
    if not args.check:
        print(f"WROTE_STATUS_RECEIPT\t{display_path(RESULT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
