"""Create immutable blind-ID-only subsets for measurement robustness checks.

This pre-measurement utility deliberately ranks only ``blind_item_id`` values.
It neither reads a condition map nor uses question, output, label, construct, or
outcome information to select records.  The resulting packets remain blinded
and are suitable only for the technical prompt-paraphrase and exact-rerun
checks described in ``computational_measurement_robustness_v1.json``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd


FORBIDDEN_FIELDS = {
    "condition",
    "condition_label",
    "prompt_type",
    "generator_condition",
    "treatment",
    "arm",
    "model_id",
    "source_image",
    "original_order",
}


def fail(message: str) -> None:
    raise ValueError(f"ROBUSTNESS_SUBSET_BUILD_FAILED: {message}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def resolve_project_path(config_path: Path, configured_path: str) -> Path:
    candidate = Path(configured_path)
    if candidate.is_absolute():
        return candidate
    return config_path.resolve().parents[1] / candidate


def rank_blind_id(seed: str, blind_item_id: str) -> str:
    """Return the frozen selection rank without consulting any row content."""
    return hashlib.sha256(f"{seed}|{blind_item_id}".encode("utf-8")).hexdigest()


def load_blinded_packet(path: Path, allowed_columns: list[str]) -> pd.DataFrame:
    packet = pd.read_csv(path, dtype=str, keep_default_na=False)
    observed = list(packet.columns)
    if set(observed) != set(allowed_columns) or len(observed) != len(allowed_columns):
        fail("packet must contain exactly the permitted blinded columns")
    if any(column in FORBIDDEN_FIELDS for column in observed):
        fail("packet contains a condition-bearing or otherwise forbidden field")
    if packet["blind_item_id"].str.strip().eq("").any():
        fail("packet contains an empty blind_item_id")
    if packet["blind_item_id"].duplicated().any():
        fail("packet contains duplicate blind_item_id values")
    return packet[allowed_columns].copy()


def validate_baseline_freeze(
    freeze: dict[str, Any],
    packet: pd.DataFrame,
    packet_path: Path,
    panel_config: dict[str, Any],
    config: dict[str, Any],
) -> None:
    baseline = config["baseline_panel"]
    if freeze.get("status") != baseline["required_freeze_status"]:
        fail("baseline freeze status does not authorize blinded robustness selection")
    if freeze.get("condition_labels_exposed") is not False:
        fail("baseline freeze records condition exposure")
    if int(freeze.get("packet_rows", -1)) != len(packet):
        fail("baseline freeze packet-row count does not match supplied packet")
    if freeze.get("packet_sha256") != sha256_file(packet_path):
        fail("baseline freeze packet checksum does not match supplied packet")
    expected_labels = len(packet) * len(panel_config["constructs"])
    if int(freeze.get("expected_labels_per_judge", -1)) != expected_labels:
        fail("baseline freeze expected-label count is inconsistent with panel configuration")
    configured_judges = [judge["judge_id"] for judge in panel_config["judges"]]
    if set(freeze.get("judge_ids", [])) != set(configured_judges):
        fail("baseline freeze judge IDs do not match the frozen panel configuration")
    if freeze.get("panel_config_canonical_json_sha256") != canonical_json_hash(panel_config):
        fail("baseline freeze panel-configuration hash does not match the frozen configuration")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--baseline-freeze", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    if args.outdir.exists():
        fail("output directory already exists; immutable subset receipts cannot be overwritten")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("status") != "FROZEN_BLINDED_PUBLIC_DATA_ONLY":
        fail("robustness configuration is not in the frozen blinded public-data state")
    blinding = config["blinding"]
    if blinding.get("condition_labels_exposed") is not False:
        fail("configuration permits condition-label exposure")
    allowed_columns = list(blinding["permitted_packet_columns"])
    if allowed_columns != ["blind_item_id", "blv_question", "output_text"]:
        fail("unexpected permitted-packet contract")
    packet = load_blinded_packet(args.packet, allowed_columns)

    panel_config_path = resolve_project_path(args.config, config["baseline_panel"]["panel_config_path"])
    if not panel_config_path.is_file():
        fail("frozen synthetic-panel configuration is unavailable")
    panel_config = json.loads(panel_config_path.read_text(encoding="utf-8"))
    if len(packet) != int(config["baseline_panel"]["expected_packet_rows"]):
        fail("supplied packet does not have the frozen expected row count")
    if len(panel_config.get("judges", [])) != int(config["baseline_panel"]["expected_judge_count"]):
        fail("frozen panel has an unexpected judge count")
    if len(panel_config.get("constructs", [])) != int(config["baseline_panel"]["expected_construct_count"]):
        fail("frozen panel has an unexpected construct count")

    if not args.baseline_freeze.is_file():
        fail("baseline synthetic-panel freeze receipt is unavailable")
    baseline_freeze = json.loads(args.baseline_freeze.read_text(encoding="utf-8"))
    validate_baseline_freeze(baseline_freeze, packet, args.packet, panel_config, config)

    selection = config["selection"]
    if selection.get("algorithm") != "sha256_rank_blind_item_id_v1":
        fail("unrecognized frozen selection algorithm")
    prompt_count = int(selection["prompt_paraphrase_subset_rows"])
    rerun_count = int(selection["exact_rerun_subset_rows"])
    if not 0 < rerun_count <= prompt_count <= len(packet):
        fail("frozen subset sizes are invalid for the supplied packet")

    # Selection uses only this identifier list and the frozen seed.  Text is
    # selected afterward solely to build the already-authorized blinded packet.
    ranked_ids = pd.DataFrame({"blind_item_id": packet["blind_item_id"].astype(str)})
    ranked_ids["sha256_rank"] = ranked_ids["blind_item_id"].map(
        lambda value: rank_blind_id(str(selection["selection_seed"]), value)
    )
    ranked_ids = ranked_ids.sort_values(["sha256_rank", "blind_item_id"], kind="mergesort").reset_index(drop=True)
    ranked_ids["selection_rank"] = ranked_ids.index + 1
    prompt_ids = ranked_ids.head(prompt_count)["blind_item_id"].tolist()
    rerun_ids = ranked_ids.head(rerun_count)["blind_item_id"].tolist()
    if not set(rerun_ids).issubset(prompt_ids):
        fail("exact-rerun subset is not nested in prompt-paraphrase subset")

    packet_by_id = packet.set_index("blind_item_id", drop=False)
    prompt_subset = packet_by_id.loc[prompt_ids, allowed_columns].reset_index(drop=True)
    rerun_subset = packet_by_id.loc[rerun_ids, allowed_columns].reset_index(drop=True)
    if prompt_subset["blind_item_id"].tolist() != prompt_ids:
        fail("prompt-paraphrase subset lost frozen rank order")
    if rerun_subset["blind_item_id"].tolist() != rerun_ids:
        fail("exact-rerun subset lost frozen rank order")

    receipt = ranked_ids.head(prompt_count).copy()
    receipt["in_prompt_paraphrase_subset"] = True
    receipt["in_exact_rerun_subset"] = receipt["selection_rank"].le(rerun_count)

    # All validation has completed before creating an immutable output directory.
    args.outdir.mkdir(parents=True, exist_ok=False)
    prompt_path = args.outdir / "prompt_paraphrase_subset_v1.csv"
    rerun_path = args.outdir / "exact_rerun_subset_v1.csv"
    selection_path = args.outdir / "blind_id_selection_receipt_v1.csv"
    prompt_subset.to_csv(prompt_path, index=False)
    rerun_subset.to_csv(rerun_path, index=False)
    receipt.to_csv(selection_path, index=False)

    manifest = {
        "status": "FROZEN_BLINDED_MEASUREMENT_ROBUSTNESS_SUBSETS",
        "condition_labels_exposed": False,
        "selection_algorithm": selection["algorithm"],
        "selection_seed": str(selection["selection_seed"]),
        "selection_input_field": blinding["selection_input_field"],
        "selection_prohibitions": selection["selection_prohibitions"],
        "packet_columns": allowed_columns,
        "prompt_paraphrase_rows": len(prompt_subset),
        "exact_rerun_rows": len(rerun_subset),
        "nested_exact_rerun_in_prompt_paraphrase": True,
        "source": {
            "robustness_config_path": str(args.config),
            "robustness_config_sha256": sha256_file(args.config),
            "baseline_packet_path": str(args.packet),
            "baseline_packet_sha256": sha256_file(args.packet),
            "baseline_freeze_path": str(args.baseline_freeze),
            "baseline_freeze_sha256": sha256_file(args.baseline_freeze),
            "synthetic_panel_config_path": str(panel_config_path),
            "synthetic_panel_config_canonical_json_sha256": canonical_json_hash(panel_config),
        },
        "artifacts": {
            "prompt_paraphrase_subset": prompt_path.name,
            "exact_rerun_subset": rerun_path.name,
            "blind_id_selection_receipt": selection_path.name,
        },
        "artifact_sha256": {
            "prompt_paraphrase_subset": sha256_file(prompt_path),
            "exact_rerun_subset": sha256_file(rerun_path),
            "blind_id_selection_receipt": sha256_file(selection_path),
        },
        "interpretation_boundary": (
            "Selection is blind-ID-only. These subsets authorize technical measurement "
            "robustness checks only; they do not authorize condition analysis, "
            "human-equivalence claims, or unblinding."
        ),
    }
    manifest_path = args.outdir / "COMPUTATIONAL_MEASUREMENT_SUBSET_MANIFEST_v1.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksums = pd.DataFrame(
        [
            {"artifact": "robustness_config", "path": str(args.config), "sha256": sha256_file(args.config)},
            {"artifact": "baseline_packet", "path": str(args.packet), "sha256": sha256_file(args.packet)},
            {"artifact": "baseline_freeze", "path": str(args.baseline_freeze), "sha256": sha256_file(args.baseline_freeze)},
            {"artifact": "synthetic_panel_config", "path": str(panel_config_path), "sha256": sha256_file(panel_config_path)},
            {"artifact": "prompt_paraphrase_subset", "path": prompt_path.name, "sha256": sha256_file(prompt_path)},
            {"artifact": "exact_rerun_subset", "path": rerun_path.name, "sha256": sha256_file(rerun_path)},
            {"artifact": "blind_id_selection_receipt", "path": selection_path.name, "sha256": sha256_file(selection_path)},
            {"artifact": "subset_manifest", "path": manifest_path.name, "sha256": sha256_file(manifest_path)},
        ]
    )
    checksums_path = args.outdir / "CHECKSUMS.csv"
    checksums.to_csv(checksums_path, index=False)
    (args.outdir / "COMPUTATIONAL_MEASUREMENT_SUBSET_MANIFEST_v1.md").write_text(
        "# Blinded computational-measurement robustness subsets\n\n"
        f"Status: `{manifest['status']}`\n\n"
        f"- Condition labels exposed: `{manifest['condition_labels_exposed']}`\n"
        f"- Prompt-paraphrase subset: {len(prompt_subset)} blinded rows\n"
        f"- Exact-rerun subset: {len(rerun_subset)} blinded rows\n"
        "- Selection source: `blind_item_id` only, using the frozen SHA-256 rank rule\n"
        "- Interpretation: technical robustness only; no condition analysis or unblinding.\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "condition_labels_exposed": False,
                "prompt_paraphrase_rows": len(prompt_subset),
                "exact_rerun_rows": len(rerun_subset),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
