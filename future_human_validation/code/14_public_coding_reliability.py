"""Freeze pre-adjudication reliability for the blinded A/B/C human subset.

This fail-closed utility accepts only a completed lock directory produced by
``code/17_lock_human_coder_files.py`` and an opaque, pre-frozen item-cluster
map. It never accesses condition metadata, model-effect results, synthetic
labels, or the private blinding map. It calculates reliability before
adjudication and writes immutable result artifacts to a new output directory.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


FIELDS = (
    "task_answer", "task_relevance", "spatial_relation", "grounded_uncertainty",
    "unsupported_information", "identity_inference", "social_intent_inference",
    "unrequested_visual_detail", "accessibility_grounded_content", "ambiguity",
)
CODERS = ("coder_a", "coder_b", "coder_c")
VISIBLE_COLUMNS = ("blind_item_id", "blv_question", "output_text")
METADATA_COLUMNS = ("coder_id", "coding_date_utc", "notes")
EXPECTED_COLUMNS = (*VISIBLE_COLUMNS, *FIELDS, *METADATA_COLUMNS)
ALLOWED_LABELS = {"0", "1", "NA"}
EXPECTED_ROWS = 600
EXPECTED_CLUSTERS = 200
OUTPUTS_PER_CLUSTER = 3


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fail(message: str) -> None:
    raise ValueError(f"HUMAN_RELIABILITY_FAILED: {message}")


def read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file():
        fail(f"missing file: {path}")
    # Literal NA is the prospectively valid abstention code; blank is invalid.
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def normalize(value: object) -> str:
    value = str(value)
    if value not in ALLOWED_LABELS:
        fail(f"unexpected raw coding value {value!r}; allowed values are 0, 1, NA")
    return value


def read_locked_coder(lock_dir: Path, role: str) -> pd.DataFrame:
    path = lock_dir / f"{role}_locked.csv"
    frame = read_csv(path)
    if list(frame.columns) != list(EXPECTED_COLUMNS):
        fail(f"{role} locked schema/order differs from frozen schema")
    if len(frame) != EXPECTED_ROWS or frame.blind_item_id.duplicated().any():
        fail(f"{role} does not have {EXPECTED_ROWS} unique blinded rows")
    for field in FIELDS:
        frame[field] = frame[field].map(normalize)
    return frame


def verify_lock(lock_dir: Path) -> dict[str, object]:
    completion_path = lock_dir / "LOCK_COMPLETE.json"
    if not completion_path.is_file():
        fail("lock directory lacks LOCK_COMPLETE.json")
    completion = json.loads(completion_path.read_text(encoding="utf-8"))
    if completion.get("status") != "THREE_HUMAN_CODER_FILES_LOCKED_PRE_ADJUDICATION":
        fail("lock completion marker has an unexpected status")
    if completion.get("condition_labels_exposed") is not False:
        fail("lock marker does not preserve condition blinding")
    if completion.get("n_rows") != EXPECTED_ROWS or completion.get("n_coders") != 3:
        fail("lock completion marker has an unexpected sample size")
    manifest = read_csv(lock_dir / "human_coder_lock_manifest.csv")
    required_manifest = {"coder_role", "artifact", "locked_path", "locked_sha256"}
    if not required_manifest.issubset(manifest.columns):
        fail("human lock manifest has incomplete schema")
    for role in CODERS:
        row = manifest.loc[(manifest.coder_role == role) & (manifest.artifact == "raw_return")]
        if len(row) != 1:
            fail(f"human lock manifest lacks a unique raw return for {role}")
        locked_path = lock_dir / str(row.iloc[0].locked_path)
        if not locked_path.is_file() or sha256(locked_path) != str(row.iloc[0].locked_sha256):
            fail(f"locked raw-return checksum mismatch for {role}")
    return completion


def verify_cluster_map(cluster_map: Path, blind_ids: list[str]) -> pd.DataFrame:
    frame = read_csv(cluster_map)
    if list(frame.columns) != ["blind_item_id", "cluster_id"]:
        fail("cluster map schema/order must be blind_item_id,cluster_id")
    if len(frame) != EXPECTED_ROWS or frame.blind_item_id.duplicated().any():
        fail("cluster map must have 600 unique blinded rows")
    if frame.blind_item_id.tolist() != blind_ids:
        fail("cluster map IDs/order differ from locked human files")
    sizes = frame.groupby("cluster_id", sort=False).size()
    if len(sizes) != EXPECTED_CLUSTERS or not (sizes == OUTPUTS_PER_CLUSTER).all():
        fail("cluster map must contain 200 clusters of three rows")
    return frame


def pairwise_metrics(left: pd.Series, right: pd.Series) -> dict[str, object]:
    usable = left.isin({"0", "1"}) & right.isin({"0", "1"})
    left_u, right_u = left[usable], right[usable]
    n = int(usable.sum())
    counts = {
        "n_00": int(((left_u == "0") & (right_u == "0")).sum()),
        "n_01": int(((left_u == "0") & (right_u == "1")).sum()),
        "n_10": int(((left_u == "1") & (right_u == "0")).sum()),
        "n_11": int(((left_u == "1") & (right_u == "1")).sum()),
    }
    if n == 0:
        return {
            **counts,
            "n_complete_pair": 0,
            "n_any_na": int((~usable).sum()),
            "raw_agreement": None,
            "cohens_kappa": None,
            "kappa_status": "NOT_ESTIMABLE_NO_COMPLETE_BINARY_PAIRS",
            "left_prevalence_1": None,
            "right_prevalence_1": None,
        }
    observed = float((left_u == right_u).mean())
    p_left_1 = float((left_u == "1").mean())
    p_right_1 = float((right_u == "1").mean())
    expected = p_left_1 * p_right_1 + (1 - p_left_1) * (1 - p_right_1)
    if np.isclose(expected, 1.0):
        kappa, status = None, "NOT_ESTIMABLE_EXPECTED_AGREEMENT_ONE"
    else:
        kappa, status = (observed - expected) / (1 - expected), "ESTIMABLE"
    return {
        **counts,
        "n_complete_pair": n,
        "n_any_na": int((~usable).sum()),
        "raw_agreement": observed,
        "cohens_kappa": kappa,
        "kappa_status": status,
        "left_prevalence_1": p_left_1,
        "right_prevalence_1": p_right_1,
    }


def krippendorff_alpha_nominal(values: pd.DataFrame) -> dict[str, object]:
    """Nominal alpha with missingness using standard pairable coincidences.

    Rows with fewer than two binary labels contribute to neither observed nor
    expected disagreement. ``NA`` remains missing, not a category or a zero.
    """
    observed_numerator = 0.0
    pairable_values = 0
    pooled_0 = 0
    pooled_1 = 0
    pairable_units = 0
    all_three_binary = 0
    all_three_unanimous = 0
    any_na = 0
    all_na = 0
    for _, row in values.iterrows():
        labels = row.tolist()
        binary = [value for value in labels if value in {"0", "1"}]
        if len(binary) < len(labels):
            any_na += 1
        if not binary:
            all_na += 1
        if len(binary) == 3:
            all_three_binary += 1
            if len(set(binary)) == 1:
                all_three_unanimous += 1
        m = len(binary)
        if m < 2:
            continue
        pairable_units += 1
        n0, n1 = binary.count("0"), binary.count("1")
        # Ordered nominal coincidences standardized by m - 1.
        observed_numerator += (2 * n0 * n1) / (m - 1)
        pairable_values += m
        pooled_0 += n0
        pooled_1 += n1
    if pairable_values < 2:
        alpha, status = None, "NOT_ESTIMABLE_FEWER_THAN_TWO_PAIRABLE_VALUES"
    else:
        observed_disagreement = observed_numerator / pairable_values
        expected_disagreement = (2 * pooled_0 * pooled_1) / (
            pairable_values * (pairable_values - 1)
        )
        if np.isclose(expected_disagreement, 0.0):
            alpha, status = None, "NOT_ESTIMABLE_EXPECTED_DISAGREEMENT_ZERO"
        else:
            alpha, status = 1 - observed_disagreement / expected_disagreement, "ESTIMABLE"
    return {
        "krippendorff_alpha_nominal": alpha,
        "alpha_status": status,
        "n_pairable_units": pairable_units,
        "n_pairable_values": pairable_values,
        "n_all_three_binary": all_three_binary,
        "n_all_three_unanimous": all_three_unanimous,
        "all_three_unanimous_rate": (
            all_three_unanimous / all_three_binary if all_three_binary else None
        ),
        "n_any_na": any_na,
        "n_all_na": all_na,
        "pooled_prevalence_1": (
            pooled_1 / pairable_values if pairable_values else None
        ),
    }


def percentile_ci(values: list[float], confidence_level: float) -> tuple[float | None, float | None, int]:
    finite = np.asarray([value for value in values if value is not None and np.isfinite(value)], dtype=float)
    if len(finite) < 2:
        return None, None, int(len(finite))
    tail = (1 - confidence_level) / 2
    return float(np.quantile(finite, tail)), float(np.quantile(finite, 1 - tail)), int(len(finite))


def cluster_bootstrap_indices(cluster_ids: pd.Series, rng: np.random.Generator) -> list[int]:
    groups = [np.flatnonzero(cluster_ids.to_numpy() == cluster).tolist() for cluster in pd.unique(cluster_ids)]
    selected = rng.integers(0, len(groups), size=len(groups))
    return [index for group_index in selected for index in groups[group_index]]


def bootstrap_pairwise(
    values: pd.DataFrame,
    cluster_ids: pd.Series,
    left_name: str,
    right_name: str,
    reps: int,
    seed: int,
    confidence_level: float,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    agreement_values: list[float] = []
    kappa_values: list[float] = []
    for _ in range(reps):
        indices = cluster_bootstrap_indices(cluster_ids, rng)
        metrics = pairwise_metrics(values.iloc[indices][left_name], values.iloc[indices][right_name])
        if metrics["raw_agreement"] is not None:
            agreement_values.append(float(metrics["raw_agreement"]))
        if metrics["cohens_kappa"] is not None:
            kappa_values.append(float(metrics["cohens_kappa"]))
    agreement_low, agreement_high, agreement_n = percentile_ci(agreement_values, confidence_level)
    kappa_low, kappa_high, kappa_n = percentile_ci(kappa_values, confidence_level)
    return {
        "raw_agreement_ci_low": agreement_low,
        "raw_agreement_ci_high": agreement_high,
        "raw_agreement_bootstrap_estimable_reps": agreement_n,
        "cohens_kappa_ci_low": kappa_low,
        "cohens_kappa_ci_high": kappa_high,
        "cohens_kappa_bootstrap_estimable_reps": kappa_n,
    }


def bootstrap_alpha(
    values: pd.DataFrame,
    cluster_ids: pd.Series,
    reps: int,
    seed: int,
    confidence_level: float,
) -> dict[str, object]:
    rng = np.random.default_rng(seed)
    alpha_values: list[float] = []
    for _ in range(reps):
        indices = cluster_bootstrap_indices(cluster_ids, rng)
        metrics = krippendorff_alpha_nominal(values.iloc[indices])
        if metrics["krippendorff_alpha_nominal"] is not None:
            alpha_values.append(float(metrics["krippendorff_alpha_nominal"]))
    low, high, n = percentile_ci(alpha_values, confidence_level)
    return {
        "krippendorff_alpha_ci_low": low,
        "krippendorff_alpha_ci_high": high,
        "krippendorff_alpha_bootstrap_estimable_reps": n,
    }


def write_checksum_ledger(outdir: Path) -> Path:
    rows = []
    for path in sorted(outdir.iterdir()):
        if path.is_file() and path.name != "reliability_pre_adjudication_checksums.csv":
            rows.append({"artifact": path.name, "sha256": sha256(path)})
    ledger = outdir / "reliability_pre_adjudication_checksums.csv"
    pd.DataFrame(rows).to_csv(ledger, index=False)
    return ledger


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock-dir", type=Path, required=True)
    parser.add_argument("--cluster-map", type=Path, required=True)
    parser.add_argument("--applicability-precheck", type=Path, required=True)
    parser.add_argument("--bootstrap-policy", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--bootstrap-reps", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20261008)
    parser.add_argument("--confidence-level", type=float, default=0.95)
    args = parser.parse_args()

    if args.outdir.exists():
        fail("refuse to overwrite an existing reliability output directory")
    if args.bootstrap_reps != 2000 or args.bootstrap_seed != 20261008 or not np.isclose(args.confidence_level, 0.95):
        fail("bootstrap settings differ from the frozen v1 policy")
    lock_completion = verify_lock(args.lock_dir)
    frames = {role: read_locked_coder(args.lock_dir, role) for role in CODERS}
    reference = frames["coder_a"]
    for role, frame in frames.items():
        if frame.blind_item_id.tolist() != reference.blind_item_id.tolist():
            fail(f"{role} blind IDs/order differ from coder_a in the completed lock")
        if not frame.loc[:, VISIBLE_COLUMNS].equals(reference.loc[:, VISIBLE_COLUMNS]):
            fail(f"{role} visible packet text differs from coder_a in the completed lock")
    clusters = verify_cluster_map(args.cluster_map, reference.blind_item_id.tolist())
    precheck = read_csv(args.applicability_precheck)
    if set(precheck.construct) != set(FIELDS) or precheck.construct.duplicated().any():
        fail("applicability precheck must contain exactly one row per frozen construct")
    if not args.bootstrap_policy.is_file():
        fail("missing frozen bootstrap-policy document")

    pairwise_rows: list[dict[str, object]] = []
    construct_rows: list[dict[str, object]] = []
    missingness_rows: list[dict[str, object]] = []
    for field_index, field in enumerate(FIELDS):
        values = pd.DataFrame({role: frames[role][field] for role in CODERS})
        applicability = precheck.loc[precheck.construct == field].iloc[0].to_dict()
        alpha = krippendorff_alpha_nominal(values)
        alpha_ci = bootstrap_alpha(
            values, clusters.cluster_id, args.bootstrap_reps,
            args.bootstrap_seed + field_index * 1009, args.confidence_level,
        )
        structural = str(applicability["packet_evidence_status"]).startswith("NOT_ESTIMABLE_STRUCTURAL")
        construct_rows.append({
            "construct": field,
            "n_packet": EXPECTED_ROWS,
            "n_coders": len(CODERS),
            **alpha,
            **alpha_ci,
            "packet_evidence_status": applicability["packet_evidence_status"],
            "synthetic_scaling_from_this_packet": applicability["synthetic_scaling_from_this_packet"],
            "reliability_decision": (
                "NOT_ESTIMABLE_STRUCTURAL_NO_REFERENCE" if structural else "THRESHOLD_NOT_PREDEFINED"
            ),
            "confirmatory_use": (
                "BLOCKED_STRUCTURAL_NO_REFERENCE" if structural else "BLOCKED_PENDING_PROSPECTIVE_RULE"
            ),
        })
        for role in CODERS:
            coder_values = values[role]
            binary = coder_values.isin({"0", "1"})
            missingness_rows.append({
                "construct": field,
                "coder_role": role,
                "n_packet": EXPECTED_ROWS,
                "n_label_0": int((coder_values == "0").sum()),
                "n_label_1": int((coder_values == "1").sum()),
                "n_label_na": int((coder_values == "NA").sum()),
                "n_invalid": 0,
                "positive_prevalence_among_binary": (
                    float((coder_values[binary] == "1").mean()) if binary.any() else None
                ),
                "abstention_rate": float((coder_values == "NA").mean()),
                "packet_evidence_status": applicability["packet_evidence_status"],
            })
        for pair_index, (left, right) in enumerate(itertools.combinations(CODERS, 2)):
            metrics = pairwise_metrics(values[left], values[right])
            intervals = bootstrap_pairwise(
                values, clusters.cluster_id, left, right, args.bootstrap_reps,
                args.bootstrap_seed + field_index * 1009 + pair_index + 1,
                args.confidence_level,
            )
            pairwise_rows.append({
                "construct": field,
                "coder_pair": f"{left}__{right}",
                "n_packet": EXPECTED_ROWS,
                **metrics,
                **intervals,
                "packet_evidence_status": applicability["packet_evidence_status"],
                "reliability_decision": (
                    "NOT_ESTIMABLE_STRUCTURAL_NO_REFERENCE" if structural else "THRESHOLD_NOT_PREDEFINED"
                ),
                "confirmatory_use": (
                    "BLOCKED_STRUCTURAL_NO_REFERENCE" if structural else "BLOCKED_PENDING_PROSPECTIVE_RULE"
                ),
            })

    args.outdir.mkdir(parents=True, exist_ok=False)
    paths = {
        "construct": args.outdir / "human_reliability_by_construct.csv",
        "pairwise": args.outdir / "human_pairwise_reliability.csv",
        "missingness": args.outdir / "human_missingness_by_construct.csv",
    }
    pd.DataFrame(construct_rows).to_csv(paths["construct"], index=False)
    pd.DataFrame(pairwise_rows).to_csv(paths["pairwise"], index=False)
    pd.DataFrame(missingness_rows).to_csv(paths["missingness"], index=False)
    report = args.outdir / "HUMAN_RELIABILITY_REPORT.md"
    report.write_text(
        "# Pre-adjudication human reliability report\n\n"
        "Status: `RAW_HUMAN_RELIABILITY_CALCULATED_NO_ADJUDICATION`\n\n"
        f"- Packet rows: {EXPECTED_ROWS}\n"
        f"- Independent locked coders: {len(CODERS)}\n"
        f"- Cluster bootstrap: {args.bootstrap_reps} item-cluster replicates, seed {args.bootstrap_seed}, {args.confidence_level:.0%} percentile intervals.\n"
        "- Reliability decision: `THRESHOLD_NOT_PREDEFINED` for text-packet-applicable constructs; no numerical pass/borderline threshold was frozen before labels.\n"
        "- Structural constructs: see `CONSTRUCT_APPLICABILITY_PRECHECK_v1.csv`; they are not evidence of poor human reliability.\n"
        "- Confirmatory scaling/unblinding remains blocked pending prospective governance, adjudication, same-item validation, and the coded-data freeze.\n",
        encoding="utf-8",
    )
    manifest = {
        "status": "PRE_ADJUDICATION_HUMAN_RELIABILITY_FROZEN",
        "condition_labels_exposed": False,
        "n_rows": EXPECTED_ROWS,
        "n_coders": len(CODERS),
        "bootstrap_reps": args.bootstrap_reps,
        "bootstrap_seed": args.bootstrap_seed,
        "confidence_level": args.confidence_level,
        "bootstrap_unit": "opaque_source_item_cluster",
        "reliability_decision_policy": "THRESHOLD_NOT_PREDEFINED",
        "confirmatory_use_policy": "BLOCKED_PENDING_PROSPECTIVE_RULE",
        "lock_completion_sha256": sha256(args.lock_dir / "LOCK_COMPLETE.json"),
        "cluster_map_sha256": sha256(args.cluster_map),
        "applicability_precheck_sha256": sha256(args.applicability_precheck),
        "bootstrap_policy_sha256": sha256(args.bootstrap_policy),
        "reliability_script_sha256": sha256(Path(__file__).resolve()),
        "python_version": sys.version,
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
    }
    manifest_path = args.outdir / "reliability_pre_adjudication_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_checksum_ledger(args.outdir)
    print(json.dumps({"status": manifest["status"], "outdir": str(args.outdir)}, sort_keys=True))


if __name__ == "__main__":
    main()
