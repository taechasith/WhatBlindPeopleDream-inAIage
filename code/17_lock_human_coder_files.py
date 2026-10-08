"""Fail-closed, atomic lock for three blinded human-coder return files.

Run this only after three genuine independent coders have completed the frozen
600-row packet and the applicable ethics determination permits annotation. This
tool never accesses a condition map, model-output comparison, synthetic label,
or outcome analysis. It validates and byte-locks raw human returns before any
reliability calculation or adjudication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


FIELDS = (
    "task_answer", "task_relevance", "spatial_relation", "grounded_uncertainty",
    "unsupported_information", "identity_inference", "social_intent_inference",
    "unrequested_visual_detail", "accessibility_grounded_content", "ambiguity",
)
VISIBLE_COLUMNS = ("blind_item_id", "blv_question", "output_text")
METADATA_COLUMNS = ("coder_id", "coding_date_utc", "notes")
EXPECTED_COLUMNS = (*VISIBLE_COLUMNS, *FIELDS, *METADATA_COLUMNS)
ATTESTATION_COLUMNS = (
    "coder_role", "coder_id", "packet_sha256", "distributed_coding_sheet_sha256",
    "instructions_sha256", "training_sha256", "adjudication_protocol_sha256",
    "codebook_sha256", "return_protocol_sha256", "assignment_receipt_sha256",
    "completion_datetime_utc", "independent_work_attested",
    "condition_metadata_not_seen", "synthetic_labels_not_seen",
    "other_coder_labels_not_seen", "no_llm_assistance_attested", "notes",
)
PACKAGE_MATERIALS = (
    ("coding_sheet.csv", None),
    ("CODER_INSTRUCTIONS_v1_1.md", "instructions_sha256"),
    ("CODER_TRAINING_NONANALYTIC_v1_1.md", "training_sha256"),
    ("adjudication_protocol_v1_1.md", "adjudication_protocol_sha256"),
    ("PUBLIC_INTERVENTION_CODEBOOK_v1_1.md", "codebook_sha256"),
    ("HUMAN_CODER_RETURN_PROTOCOL_v1_1.md", "return_protocol_sha256"),
    ("assignment_receipt.csv", "assignment_receipt_sha256"),
    ("HUMAN_CODER_INDEPENDENCE_ATTESTATION_TEMPLATE_v1_1.csv", None),
)
ALLOWED_LABELS = {"0", "1", "NA"}
EXPECTED_ROWS = 600
REQUIRED_TRUE_ATTESTATIONS = (
    "independent_work_attested", "condition_metadata_not_seen",
    "synthetic_labels_not_seen", "other_coder_labels_not_seen",
    "no_llm_assistance_attested",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso8601(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def add_error(errors: list[dict[str, object]], scope: str, code: str, detail: str) -> None:
    errors.append({"scope": scope, "code": code, "detail": detail})


def read_csv(path: Path, errors: list[dict[str, object]], scope: str) -> pd.DataFrame | None:
    if not path.is_file():
        add_error(errors, scope, "FILE_MISSING", str(path))
        return None
    try:
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    except Exception as exc:  # Parser detail is preserved in a technical report.
        add_error(errors, scope, "CSV_UNREADABLE", f"{type(exc).__name__}: {exc}")
        return None


def expected_package_hashes(package_root: Path, errors: list[dict[str, object]]) -> dict[str, str]:
    checksums_path = package_root / "CHECKSUMS.csv"
    checksums = read_csv(checksums_path, errors, "distributed_package_checksums")
    if checksums is None or not {"artifact", "sha256"}.issubset(checksums.columns):
        if checksums is not None:
            add_error(errors, "distributed_package_checksums", "SCHEMA_INVALID", "artifact/sha256 columns required")
        return {}
    values = dict(zip(checksums["artifact"], checksums["sha256"], strict=False))
    required = ["blinded_human_validation_subset_v1.csv", "PACKET_RELEASE_MANIFEST_v1_1.json"]
    for role in ("coder_a", "coder_b", "coder_c"):
        required.extend(f"{role}/{filename}" for filename, _ in PACKAGE_MATERIALS)
    for artifact in required:
        if artifact not in values:
            add_error(errors, "distributed_package_checksums", "ARTIFACT_HASH_MISSING", artifact)
    return values


def validate_distributed_package(package_root: Path, errors: list[dict[str, object]]) -> tuple[pd.DataFrame | None, dict[str, str]]:
    hashes = expected_package_hashes(package_root, errors)
    subset_path = package_root / "blinded_human_validation_subset_v1.csv"
    subset = read_csv(subset_path, errors, "distributed_subset")
    if subset is None:
        return None, hashes
    if list(subset.columns) != list(VISIBLE_COLUMNS):
        add_error(errors, "distributed_subset", "SCHEMA_INVALID", "visible packet schema/order differs")
    if len(subset) != EXPECTED_ROWS:
        add_error(errors, "distributed_subset", "ROW_COUNT_INVALID", f"{len(subset)} != {EXPECTED_ROWS}")
    if "blind_item_id" in subset and subset["blind_item_id"].duplicated().any():
        add_error(errors, "distributed_subset", "DUPLICATE_BLIND_ID", "subset has duplicate blind_item_id")
    expected_hash = hashes.get("blinded_human_validation_subset_v1.csv")
    if expected_hash and sha256(subset_path) != expected_hash:
        add_error(errors, "distributed_subset", "CHECKSUM_MISMATCH", "subset does not match distributed checksum")
    release_manifest = package_root / "PACKET_RELEASE_MANIFEST_v1_1.json"
    release_manifest_hash = hashes.get("PACKET_RELEASE_MANIFEST_v1_1.json")
    if not release_manifest.is_file():
        add_error(errors, "distributed_package", "RELEASE_MANIFEST_MISSING", str(release_manifest))
    elif release_manifest_hash and sha256(release_manifest) != release_manifest_hash:
        add_error(errors, "distributed_package", "RELEASE_MANIFEST_CHECKSUM_MISMATCH", release_manifest.name)
    for role in ("coder_a", "coder_b", "coder_c"):
        for filename, _ in PACKAGE_MATERIALS:
            material = package_root / role / filename
            artifact = f"{role}/{filename}"
            if not material.is_file():
                add_error(errors, role, "DISTRIBUTED_MATERIAL_MISSING", artifact)
                continue
            if hashes.get(artifact) and sha256(material) != hashes[artifact]:
                add_error(errors, role, "DISTRIBUTED_MATERIAL_CHECKSUM_MISMATCH", artifact)
        sheet = package_root / role / "coding_sheet.csv"
        if not sheet.is_file():
            continue
        source_sheet = read_csv(sheet, errors, f"{role}_distributed_sheet")
        if source_sheet is None:
            continue
        if list(source_sheet.columns) != list(EXPECTED_COLUMNS):
            add_error(errors, role, "DISTRIBUTED_SCHEMA_INVALID", "coding-sheet schema/order differs")
        if len(source_sheet) != EXPECTED_ROWS:
            add_error(errors, role, "DISTRIBUTED_ROW_COUNT_INVALID", f"{len(source_sheet)} != {EXPECTED_ROWS}")
        if subset is not None and set(VISIBLE_COLUMNS).issubset(source_sheet.columns):
            if not source_sheet.loc[:, VISIBLE_COLUMNS].equals(subset.loc[:, VISIBLE_COLUMNS]):
                add_error(errors, role, "DISTRIBUTED_SHEET_PACKET_MISMATCH", "visible values/order differ from subset")
    return subset, hashes


def validate_return(
    role: str,
    return_path: Path,
    attestation_path: Path,
    expected_subset: pd.DataFrame | None,
    package_root: Path,
    distributed_hashes: dict[str, str],
    errors: list[dict[str, object]],
) -> tuple[pd.DataFrame | None, dict[str, object] | None, list[dict[str, object]], list[dict[str, object]]]:
    frame = read_csv(return_path, errors, f"{role}_return")
    attestation = read_csv(attestation_path, errors, f"{role}_attestation")
    missingness: list[dict[str, object]] = []
    invalid_report: list[dict[str, object]] = []
    if frame is None:
        return None, None, missingness, invalid_report
    if list(frame.columns) != list(EXPECTED_COLUMNS):
        add_error(errors, role, "RETURN_SCHEMA_INVALID", "columns must exactly match the frozen coding-sheet schema and order")
    if len(frame) != EXPECTED_ROWS:
        add_error(errors, role, "RETURN_ROW_COUNT_INVALID", f"{len(frame)} != {EXPECTED_ROWS}")
    if "blind_item_id" in frame and frame["blind_item_id"].duplicated().any():
        add_error(errors, role, "RETURN_DUPLICATE_BLIND_ID", "duplicate blind_item_id")
    if expected_subset is not None and set(VISIBLE_COLUMNS).issubset(frame.columns):
        if not frame.loc[:, VISIBLE_COLUMNS].equals(expected_subset.loc[:, VISIBLE_COLUMNS]):
            add_error(errors, role, "RETURN_PACKET_MISMATCH", "visible text/IDs/order differ from frozen packet")

    for field in FIELDS:
        if field not in frame.columns:
            continue
        values = frame[field].tolist()
        invalid = sorted({value for value in values if value not in ALLOWED_LABELS})
        invalid_report.append({
            "coder_role": role,
            "construct": field,
            "n_invalid": sum(value not in ALLOWED_LABELS for value in values),
            "invalid_values_json": json.dumps(invalid, ensure_ascii=False),
        })
        if invalid:
            add_error(errors, role, "INVALID_LABEL_VALUE", f"{field}: {invalid[:10]}")
        missingness.append({
            "coder_role": role,
            "construct": field,
            "n_rows": len(values),
            "n_label_0": values.count("0"),
            "n_label_1": values.count("1"),
            "n_label_na": values.count("NA"),
            "n_invalid": sum(value not in ALLOWED_LABELS for value in values),
        })

    coder_id: str | None = None
    if "coder_id" in frame.columns:
        coder_values = sorted({value.strip() for value in frame["coder_id"] if value.strip()})
        if len(coder_values) != 1:
            add_error(errors, role, "CODER_ID_NOT_SINGLETON", json.dumps(coder_values))
        else:
            coder_id = coder_values[0]
    if "coding_date_utc" in frame.columns:
        dates = frame["coding_date_utc"].tolist()
        invalid_dates = [value for value in dates if not value or not parse_iso8601(value)]
        if invalid_dates:
            add_error(errors, role, "CODING_DATE_INVALID", f"{len(invalid_dates)} empty or non-ISO-8601 values")

    attestation_record: dict[str, object] | None = None
    if attestation is not None:
        if list(attestation.columns) != list(ATTESTATION_COLUMNS):
            add_error(errors, role, "ATTESTATION_SCHEMA_INVALID", "attestation columns/order differ from template")
        if len(attestation) != 1:
            add_error(errors, role, "ATTESTATION_ROW_COUNT_INVALID", f"{len(attestation)} != 1")
        elif set(ATTESTATION_COLUMNS).issubset(attestation.columns):
            attestation_record = attestation.iloc[0].to_dict()
            if attestation_record["coder_role"] != role:
                add_error(errors, role, "ATTESTATION_ROLE_MISMATCH", str(attestation_record["coder_role"]))
            if not coder_id or attestation_record["coder_id"].strip() != coder_id:
                add_error(errors, role, "ATTESTATION_CODER_ID_MISMATCH", "attestation coder ID differs from return")
            expected_packet_hash = distributed_hashes.get("blinded_human_validation_subset_v1.csv", "")
            expected_sheet_hash = distributed_hashes.get(f"{role}/coding_sheet.csv", "")
            material_expectations = {
                "packet_sha256": expected_packet_hash,
                "distributed_coding_sheet_sha256": expected_sheet_hash,
                "instructions_sha256": distributed_hashes.get(f"{role}/CODER_INSTRUCTIONS_v1_1.md", ""),
                "training_sha256": distributed_hashes.get(f"{role}/CODER_TRAINING_NONANALYTIC_v1_1.md", ""),
                "adjudication_protocol_sha256": distributed_hashes.get(f"{role}/adjudication_protocol_v1_1.md", ""),
                "codebook_sha256": distributed_hashes.get(f"{role}/PUBLIC_INTERVENTION_CODEBOOK_v1_1.md", ""),
                "return_protocol_sha256": distributed_hashes.get(f"{role}/HUMAN_CODER_RETURN_PROTOCOL_v1_1.md", ""),
                "assignment_receipt_sha256": distributed_hashes.get(f"{role}/assignment_receipt.csv", ""),
            }
            for column, expected_value in material_expectations.items():
                if not expected_value or attestation_record[column] != expected_value:
                    add_error(errors, role, "ATTESTATION_HASH_MISMATCH", column)
            if not parse_iso8601(str(attestation_record["completion_datetime_utc"])):
                add_error(errors, role, "ATTESTATION_COMPLETION_DATE_INVALID", str(attestation_record["completion_datetime_utc"]))
            for column in REQUIRED_TRUE_ATTESTATIONS:
                if str(attestation_record[column]).strip().upper() != "YES":
                    add_error(errors, role, "ATTESTATION_NOT_AFFIRMED", column)
    return frame, attestation_record, missingness, invalid_report


def write_failure_report(path: Path, errors: list[dict[str, object]]) -> None:
    if path.exists():
        raise FileExistsError(f"Refuse to overwrite prior validation/failure report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "HUMAN_CODER_LOCK_VALIDATION_FAILED",
        "condition_labels_exposed": False,
        "generated_at_utc": utc_now(),
        "errors": errors,
        "instruction": "No files were locked. Correct clerical issues through a new derivative while preserving the original return.",
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_checksum_ledger(directory: Path) -> Path:
    rows = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.name != "human_coder_lock_checksums.csv":
            rows.append({"artifact": str(path.relative_to(directory)), "sha256": sha256(path)})
    ledger = directory / "human_coder_lock_checksums.csv"
    pd.DataFrame(rows).to_csv(ledger, index=False)
    return ledger


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--coder-a", type=Path, required=True)
    parser.add_argument("--coder-b", type=Path, required=True)
    parser.add_argument("--coder-c", type=Path, required=True)
    parser.add_argument("--attestation-a", type=Path, required=True)
    parser.add_argument("--attestation-b", type=Path, required=True)
    parser.add_argument("--attestation-c", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--failure-report", type=Path, required=True)
    args = parser.parse_args()

    if args.outdir.exists():
        raise FileExistsError(f"Refuse to overwrite existing lock directory: {args.outdir}")
    errors: list[dict[str, object]] = []
    expected_subset, distributed_hashes = validate_distributed_package(args.package_root, errors)
    roles = {
        "coder_a": (args.coder_a, args.attestation_a),
        "coder_b": (args.coder_b, args.attestation_b),
        "coder_c": (args.coder_c, args.attestation_c),
    }
    returns: dict[str, pd.DataFrame] = {}
    attestations: dict[str, dict[str, object]] = {}
    missingness: list[dict[str, object]] = []
    invalid_values: list[dict[str, object]] = []
    for role, (return_path, attestation_path) in roles.items():
        frame, attestation, role_missingness, role_invalid = validate_return(
            role, return_path, attestation_path, expected_subset, args.package_root,
            distributed_hashes, errors,
        )
        if frame is not None:
            returns[role] = frame
        if attestation is not None:
            attestations[role] = attestation
        missingness.extend(role_missingness)
        invalid_values.extend(role_invalid)

    submitted_hashes = [sha256(path) for path, _ in roles.values() if path.is_file()]
    if len(submitted_hashes) == 3 and len(set(submitted_hashes)) != 3:
        add_error(errors, "returns", "DUPLICATE_SUBMITTED_FILE_HASH", "two or more coder returns are byte-identical")
    submitted_ids = [str(record.get("coder_id", "")) for record in attestations.values()]
    if len(submitted_ids) == 3 and len(set(submitted_ids)) != 3:
        add_error(errors, "attestations", "CODER_IDENTITIES_NOT_DISTINCT", json.dumps(submitted_ids))

    if errors:
        write_failure_report(args.failure_report, errors)
        raise ValueError(
            "HUMAN_CODER_INGESTION_FAILED; no lock directory was created. "
            f"See {args.failure_report} for the validation report."
        )

    temp_dir = args.outdir.with_name(f"{args.outdir.name}.incomplete-{uuid.uuid4().hex}")
    temp_dir.mkdir(parents=True, exist_ok=False)
    source_manifest: list[dict[str, object]] = []
    try:
        for role, (return_path, attestation_path) in roles.items():
            locked_return = temp_dir / f"{role}_locked{return_path.suffix.lower() or '.csv'}"
            locked_attestation = temp_dir / f"{role}_attestation_locked{attestation_path.suffix.lower() or '.csv'}"
            shutil.copy2(return_path, locked_return)
            shutil.copy2(attestation_path, locked_attestation)
            if sha256(return_path) != sha256(locked_return) or sha256(attestation_path) != sha256(locked_attestation):
                raise RuntimeError(f"Byte-copy verification failed for {role}")
            source_manifest.extend([
                {"coder_role": role, "artifact": "raw_return", "source_sha256": sha256(return_path), "locked_path": locked_return.name, "locked_sha256": sha256(locked_return)},
                {"coder_role": role, "artifact": "attestation", "source_sha256": sha256(attestation_path), "locked_path": locked_attestation.name, "locked_sha256": sha256(locked_attestation)},
            ])
        pd.DataFrame(source_manifest).to_csv(temp_dir / "human_coder_lock_manifest.csv", index=False)
        pd.DataFrame(missingness).to_csv(temp_dir / "human_coder_missingness_summary.csv", index=False)
        pd.DataFrame(invalid_values).to_csv(temp_dir / "human_coder_invalid_value_report.csv", index=False)
        validation = {
            "status": "THREE_HUMAN_CODER_FILES_VALIDATED",
            "condition_labels_exposed": False,
            "package_root": str(args.package_root),
            "distributed_subset_sha256": distributed_hashes["blinded_human_validation_subset_v1.csv"],
            "n_rows": EXPECTED_ROWS,
            "n_coders": 3,
            "constructs": list(FIELDS),
            "attestation_status": "THREE_INDEPENDENT_ATTESTATIONS_AFFIRMED",
            "next_step": "Run pre-adjudication reliability from this completed lock only; do not adjudicate first.",
            "python_version": sys.version,
            "pandas_version": pd.__version__,
            "locking_script_sha256": sha256(Path(__file__).resolve()),
        }
        (temp_dir / "human_coder_lock_validation.json").write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        initial_ledger = write_checksum_ledger(temp_dir)
        completion = {
            **validation,
            "status": "THREE_HUMAN_CODER_FILES_LOCKED_PRE_ADJUDICATION",
            "generated_at_utc": utc_now(),
            "lock_manifest_sha256": sha256(temp_dir / "human_coder_lock_manifest.csv"),
            "missingness_sha256": sha256(temp_dir / "human_coder_missingness_summary.csv"),
            "invalid_value_report_sha256": sha256(temp_dir / "human_coder_invalid_value_report.csv"),
            "checksum_ledger_sha256_before_completion_marker": sha256(initial_ledger),
        }
        (temp_dir / "LOCK_COMPLETE.json").write_text(
            json.dumps(completion, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        write_checksum_ledger(temp_dir)
        os.replace(temp_dir, args.outdir)
    except Exception:
        # Deliberately leave the uniquely named incomplete directory for audit;
        # it lacks LOCK_COMPLETE.json and cannot be used by the reliability tool.
        raise
    print(json.dumps({"status": "THREE_HUMAN_CODER_FILES_LOCKED_PRE_ADJUDICATION", "outdir": str(args.outdir)}, sort_keys=True))


if __name__ == "__main__":
    main()
