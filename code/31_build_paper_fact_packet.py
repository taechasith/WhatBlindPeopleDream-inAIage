"""Build anonymous paper facts and LaTeX macros from a frozen results receipt.

This post-results utility is deliberately downstream of RESULTS_FREEZE.  It
does not estimate effects, select findings, generate prose, or inspect a
condition mapping.  It verifies the freeze receipt and its ledger before
copying ledger-backed result rows into a machine-readable fact packet and a
numeric LaTeX macro file.  The output intentionally contains hashes and
anonymous result-family names rather than local paths or author metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import uuid
from pathlib import Path
from typing import Any

import pandas as pd


EXPECTED_TABLES = {
    "RQ2",
    "RQ3",
    "RQ4",
    "RQ5",
    "RQ4_profiles",
    "RQ4_association_status",
}

ROOT = Path(__file__).resolve().parents[1]

# The public analysis runner writes these exact canonical artifacts.  Refusing
# arbitrary ledger paths prevents a self-consistent but redirected ledger from
# injecting an unrelated table into a review-side fact packet.
CANONICAL_TABLE_PATHS = {
    "RQ2": ROOT / "results" / "post_freeze_analysis_v1" / "RQ2_results.csv",
    "RQ3": ROOT / "results" / "post_freeze_analysis_v1" / "RQ3_results.csv",
    "RQ5": ROOT / "results" / "post_freeze_analysis_v1" / "RQ5_results.csv",
    "RQ4": ROOT / "results" / "representational_space_v1" / "RQ4_results.csv",
    "RQ4_profiles": ROOT / "results" / "representational_space_v1" / "RQ4_space_profiles.csv",
    "RQ4_association_status": ROOT / "results" / "representational_space_v1" / "RQ4_association_status.csv",
}

UPSTREAM_RECEIPTS = {
    "coded_data_freeze_sha256": (
        ROOT / "results" / "coded_data_freeze" / "CODED_DATA_FREEZE.json",
        "CODED_DATA_FROZEN_PUBLIC_DATA_ONLY",
    ),
    "post_freeze_analysis_manifest_sha256": (
        ROOT / "results" / "post_freeze_analysis_v1" / "ANALYSIS_MANIFEST.json",
        "RQ2_RQ3_RQ5_COMPLETE_PUBLIC_DATA_ONLY",
    ),
    "rq4_manifest_sha256": (
        ROOT / "results" / "representational_space_v1" / "RQ4_MANIFEST.json",
        "RQ4_COMPLETE_DISTRIBUTIONAL_PUBLIC_DATA_ONLY",
    ),
}

PAPER_COLUMNS = {
    "RQ2": [
        "judge_id", "construct", "measurement_status", "contrast", "n_paired_items",
        "paired_coverage", "effect", "ci_low", "ci_high", "permutation_p",
        "analysis_status", "primary_family", "fdr_q", "analysis_role",
    ],
    "RQ3": [
        "metric", "contrast", "measurement_status", "claim_boundary", "n_paired_items",
        "paired_coverage", "effect", "ci_low", "ci_high", "permutation_p",
        "analysis_status", "fdr_q",
    ],
    "RQ4": [
        "space_a", "space_b", "n_a", "n_b", "jensen_shannon_divergence",
        "cosine_similarity", "hellinger_distance", "n_categories", "js_ci_low",
        "js_ci_high", "analysis_status", "interpretation_boundary",
    ],
    "RQ5": [
        "judge_id", "construct", "measurement_status", "contrast", "n_paired_items",
        "paired_coverage", "effect", "ci_low", "ci_high", "permutation_p",
        "analysis_status", "primary_family", "fdr_q", "analysis_role",
        "output_change_direction",
    ],
    "RQ4_profiles": [
        "space", "category", "n_text_units", "proportion_expressed", "measurement_status",
        "claim_boundary",
    ],
    "RQ4_association_status": ["analysis", "status", "reason"],
}

REQUIRED_COLUMNS = {
    "RQ2": {
        "judge_id", "construct", "measurement_status", "contrast",
        "n_paired_items", "paired_coverage", "effect", "ci_low", "ci_high",
        "permutation_p", "fdr_q", "analysis_role",
    },
    "RQ3": {
        "metric", "contrast", "measurement_status", "claim_boundary",
        "n_paired_items", "paired_coverage", "effect", "ci_low", "ci_high",
        "permutation_p", "fdr_q", "analysis_status",
    },
    "RQ4": {
        "space_a", "space_b", "n_a", "n_b", "jensen_shannon_divergence",
        "cosine_similarity", "hellinger_distance", "n_categories", "js_ci_low",
        "js_ci_high", "analysis_status",
    },
    "RQ5": {
        "judge_id", "construct", "measurement_status", "contrast",
        "n_paired_items", "paired_coverage", "effect", "ci_low", "ci_high",
        "permutation_p", "fdr_q", "analysis_role", "output_change_direction",
    },
    "RQ4_profiles": {
        "space", "category", "n_text_units", "proportion_expressed", "measurement_status",
    },
    "RQ4_association_status": {"analysis", "status", "reason"},
}

NUMERIC_MACRO_FIELDS = {
    "RQ2": ("n_paired_items", "paired_coverage", "effect", "ci_low", "ci_high", "permutation_p", "fdr_q"),
    "RQ3": ("n_paired_items", "paired_coverage", "effect", "ci_low", "ci_high", "permutation_p", "fdr_q"),
    "RQ4": ("n_a", "n_b", "jensen_shannon_divergence", "cosine_similarity", "hellinger_distance", "n_categories", "js_ci_low", "js_ci_high"),
    "RQ5": ("n_paired_items", "paired_coverage", "effect", "ci_low", "ci_high", "permutation_p", "fdr_q"),
    "RQ4_profiles": ("n_text_units", "proportion_expressed"),
    "RQ4_association_status": (),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"PAPER_FACT_PACKET_FAILED: {message}")


def read_json(path: Path, expected_status: str) -> dict[str, Any]:
    if not path.is_file():
        fail(f"required receipt unavailable: {path.name}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != expected_status:
        fail(f"unexpected receipt status for {path.name}: {payload.get('status')!r}")
    return payload


def require_columns(frame: pd.DataFrame, columns: set[str], label: str) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        fail(f"{label} schema is incomplete: {', '.join(sorted(missing))}")


def normalise(value: Any) -> Any:
    """Convert pandas/numpy values to JSON-safe values without changing facts."""
    if value is None or pd.isna(value):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if hasattr(value, "item"):
        return normalise(value.item())
    return str(value)


def latex_number(value: Any) -> str:
    value = normalise(value)
    if value is None:
        return r"\PaperNotEstimable"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return format(value, ".10g")
    try:
        numeric = float(str(value))
    except (TypeError, ValueError):
        return r"\PaperNotEstimable"
    return format(numeric, ".10g") if math.isfinite(numeric) else r"\PaperNotEstimable"


def macro_family(name: str) -> str:
    return {
        "RQ2": "RQTwo",
        "RQ3": "RQThree",
        "RQ4": "RQFour",
        "RQ5": "RQFive",
        "RQ4_profiles": "RQFourProfile",
        "RQ4_association_status": "RQFourAssociation",
    }[name]


def macro_field(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


def validate_results_freeze(results_freeze: Path) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Path]]:
    freeze = read_json(results_freeze, "RESULTS_FROZEN_PUBLIC_DATA_ONLY")
    if freeze.get("new_human_data_collected") is not False:
        fail("results freeze does not document zero new human data collection")
    if freeze.get("condition_unblinded_once") is not True:
        fail("results freeze does not document the authorized single unblinding")
    for hash_field, (receipt_path, receipt_status) in UPSTREAM_RECEIPTS.items():
        upstream = read_json(receipt_path, receipt_status)
        if freeze.get(hash_field) != sha256(receipt_path):
            fail(f"RESULTS_FREEZE does not reconcile upstream receipt: {hash_field}")
        if upstream.get("new_human_data_collected") is not False:
            fail(f"upstream receipt does not document public-data-only scope: {receipt_path.name}")
    expected_analysis_ledger = ROOT / "results" / "post_freeze_analysis_v1" / "ANALYSIS_CHECKSUMS.csv"
    if not expected_analysis_ledger.is_file() or freeze.get("analysis_ledger_sha256") != sha256(expected_analysis_ledger):
        fail("RESULTS_FREEZE does not reconcile the post-freeze analysis ledger")
    expected_freeze_script = ROOT / "code" / "29_freeze_public_data_results.py"
    expected_figure_script = ROOT / "code" / "30_generate_public_data_figures.py"
    if not expected_freeze_script.is_file() or freeze.get("results_freeze_script_sha256") != sha256(expected_freeze_script):
        fail("RESULTS_FREEZE does not reconcile the committed results-freeze script")
    if not expected_figure_script.is_file() or freeze.get("figure_script_sha256") != sha256(expected_figure_script):
        fail("RESULTS_FREEZE does not reconcile the committed figure script")
    ledger_path = results_freeze.parent / "RESULTS_LEDGER.csv"
    expected_ledger_hash = str(freeze.get("results_ledger_sha256", ""))
    if not ledger_path.is_file() or sha256(ledger_path) != expected_ledger_hash:
        fail("results ledger is unavailable or does not match RESULTS_FREEZE")
    ledger = pd.read_csv(ledger_path, dtype=str, keep_default_na=False)
    require_columns(ledger, {"result_family", "path", "sha256", "rows"}, "results ledger")
    if ledger.result_family.duplicated().any() or set(ledger.result_family) != EXPECTED_TABLES:
        fail("results ledger does not cover exactly the expected frozen result tables")
    table_receipt = freeze.get("tables")
    if not isinstance(table_receipt, dict) or set(table_receipt) != EXPECTED_TABLES:
        fail("RESULTS_FREEZE table receipt does not cover exactly the expected result tables")
    table_paths: dict[str, Path] = {}
    for row in ledger.to_dict("records"):
        family = str(row["result_family"])
        table_path = Path(str(row["path"])).resolve()
        canonical_path = CANONICAL_TABLE_PATHS[family].resolve()
        if table_path != canonical_path:
            fail(f"results ledger path is not the canonical frozen artifact: {family}")
        expected_hash = str(row["sha256"])
        try:
            expected_rows = int(str(row["rows"]))
        except ValueError as exc:
            raise ValueError(f"PAPER_FACT_PACKET_FAILED: invalid frozen row count for {family}") from exc
        if not table_path.is_file() or sha256(table_path) != expected_hash:
            fail(f"frozen result table is unavailable or changed: {family}")
        frame = pd.read_csv(table_path)
        if len(frame) != expected_rows:
            fail(f"frozen result table row count changed: {family}")
        receipt = table_receipt[family]
        if not isinstance(receipt, dict) or str(receipt.get("sha256", "")) != expected_hash or int(receipt.get("rows", -1)) != expected_rows:
            fail(f"RESULTS_FREEZE table receipt does not reconcile: {family}")
        require_columns(frame, REQUIRED_COLUMNS[family], family)
        unexpected = set(frame.columns).difference(PAPER_COLUMNS[family])
        missing_output = set(PAPER_COLUMNS[family]).difference(frame.columns)
        if unexpected or missing_output:
            parts = []
            if unexpected:
                parts.append(f"unexpected columns: {', '.join(sorted(unexpected))}")
            if missing_output:
                parts.append(f"missing canonical columns: {', '.join(sorted(missing_output))}")
            fail(f"{family} cannot enter the anonymous fact packet ({'; '.join(parts)})")
        table_paths[family] = table_path
    return freeze, ledger, table_paths


def build_fact_rows(table_paths: dict[str, Path]) -> tuple[list[dict[str, Any]], list[str]]:
    facts: list[dict[str, Any]] = []
    latex_lines = [
        "% Generated only by code/31_build_paper_fact_packet.py after RESULTS_FREEZE.",
        "% Numeric macros are traceable via paper_fact_packet.csv and paper_fact_packet.json.",
        "% Do not edit this file by hand; regenerate from the immutable results ledger.",
        r"\providecommand{\PaperNotEstimable}{\texttt{NOT\_ESTIMABLE}}",
        r"\newcommand{\PaperFactPacketVersion}{1}",
    ]
    for family in sorted(table_paths):
        frame = pd.read_csv(table_paths[family]).loc[:, PAPER_COLUMNS[family]]
        source_hash = sha256(table_paths[family])
        family_macro = macro_family(family)
        latex_lines.append(rf"\newcommand{{\Paper{family_macro}FactCount}}{{{len(frame)}}}")
        for ordinal, record in enumerate(frame.to_dict("records"), start=1):
            fact_id = f"{family}_{ordinal:04d}"
            fact = {
                "fact_id": fact_id,
                "result_family": family,
                "source_file": table_paths[family].name,
                "source_sha256": source_hash,
                "source_data_row": ordinal,
                "values": {key: normalise(value) for key, value in record.items()},
            }
            facts.append(fact)
            base = f"Paper{family_macro}F{ordinal:04d}"
            for field in NUMERIC_MACRO_FIELDS[family]:
                latex_lines.append(rf"\newcommand{{\{base}{macro_field(field)}}}{{{latex_number(record.get(field))}}}")
    return facts, latex_lines


def write_csv(facts: list[dict[str, Any]], path: Path) -> None:
    rows: list[dict[str, Any]] = []
    for fact in facts:
        row = {
            "fact_id": fact["fact_id"],
            "result_family": fact["result_family"],
            "source_file": fact["source_file"],
            "source_sha256": fact["source_sha256"],
            "source_data_row": fact["source_data_row"],
        }
        row.update(fact["values"])
        rows.append(row)
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite an existing paper fact packet")
    freeze, ledger, table_paths = validate_results_freeze(args.results_freeze)
    facts, latex_lines = build_fact_rows(table_paths)
    temp_outdir = args.outdir.parent / f".{args.outdir.name}.tmp-{uuid.uuid4().hex}"
    temp_outdir.mkdir(parents=True, exist_ok=False)
    packet_path = temp_outdir / "paper_fact_packet.json"
    csv_path = temp_outdir / "paper_fact_packet.csv"
    macros_path = temp_outdir / "results_macros.tex"
    packet = {
        "status": "PAPER_FACT_PACKET_FROM_RESULTS_FREEZE",
        "source_results_freeze_sha256": sha256(args.results_freeze),
        "source_results_ledger_sha256": sha256(args.results_freeze.parent / "RESULTS_LEDGER.csv"),
        "results_freeze_status": freeze["status"],
        "interpretation_boundary": freeze.get("interpretation_boundary"),
        "new_human_data_collected": False,
        "fact_count": len(facts),
        "frozen_table_summary": [
            {
                "result_family": str(row.result_family),
                "source_file": table_paths[str(row.result_family)].name,
                "sha256": str(row.sha256),
                "rows": int(str(row.rows)),
            }
            for row in ledger.itertuples(index=False)
        ],
        "facts": facts,
    }
    packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(facts, csv_path)
    macros_path.write_text("\n".join(latex_lines) + "\n", encoding="utf-8")
    manifest_path = temp_outdir / "PAPER_FACT_PACKET_MANIFEST.json"
    manifest = {
        "status": "PAPER_FACT_PACKET_FROZEN_FROM_RESULTS_FREEZE",
        "source_results_freeze_sha256": sha256(args.results_freeze),
        "source_results_ledger_sha256": sha256(args.results_freeze.parent / "RESULTS_LEDGER.csv"),
        "script_sha256": sha256(Path(__file__).resolve()),
        "fact_count": len(facts),
        "artifacts": {
            packet_path.name: sha256(packet_path),
            csv_path.name: sha256(csv_path),
            macros_path.name: sha256(macros_path),
        },
        "anonymity_note": "This packet contains result-family identifiers, table basenames, and hashes only; it must not be supplemented with author-identifying metadata.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Directory rename is atomic on this filesystem when the target does not
    # exist. A failed run leaves a uniquely named temporary directory rather
    # than poisoning the requested immutable output path.
    temp_outdir.replace(args.outdir)
    print(json.dumps({"status": manifest["status"], "facts": len(facts)}, sort_keys=True))


if __name__ == "__main__":
    main()
