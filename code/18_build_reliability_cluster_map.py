"""Build an opaque cluster map for blinded human-reliability bootstrapping.

This pre-label utility reads only ``blind_item_id`` and ``sample_row_id`` from
the private map. It deliberately does not read condition, prompt, model, or
output fields. The resulting map preserves the three-output source-item cluster
needed for a prospective cluster bootstrap while retaining opaque IDs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


EXPECTED_ROWS = 600
EXPECTED_CLUSTERS = 200
OUTPUTS_PER_CLUSTER = 3


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"RELIABILITY_CLUSTER_MAP_FAILED: {message}")


def opaque_cluster_id(sample_row_id: str) -> str:
    return hashlib.sha256(
        f"reliability_cluster_v1:{sample_row_id}".encode("utf-8")
    ).hexdigest()[:24]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subset", type=Path, required=True)
    parser.add_argument("--subset-manifest", type=Path, required=True)
    parser.add_argument("--private-map", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.out.exists() or args.receipt.exists():
        fail("refuse to overwrite an existing frozen map or public receipt")
    subset = pd.read_csv(args.subset, dtype=str, keep_default_na=False)
    if list(subset.columns) != ["blind_item_id", "blv_question", "output_text"]:
        fail("subset must be the exact visible three-column packet")
    if len(subset) != EXPECTED_ROWS or subset.blind_item_id.duplicated().any():
        fail("subset must contain 600 unique blinded IDs")
    manifest = json.loads(args.subset_manifest.read_text(encoding="utf-8"))
    if manifest.get("status") != "FROZEN_BLINDED_HUMAN_VALIDATION_SUBSET":
        fail("subset manifest has an unexpected status")
    if manifest.get("subset_packet_sha256") != sha256(args.subset):
        fail("subset checksum does not match its frozen manifest")

    # The explicit column allowlist protects the blinding boundary. Pandas does
    # not materialize any condition or model metadata from the private map.
    private_map = pd.read_csv(
        args.private_map,
        usecols=["blind_item_id", "sample_row_id"],
        dtype=str,
        keep_default_na=False,
    )
    if private_map.blind_item_id.duplicated().any():
        fail("private map contains duplicate blinded IDs")
    merged = subset[["blind_item_id"]].merge(
        private_map,
        on="blind_item_id",
        how="left",
        validate="one_to_one",
    )
    if merged.sample_row_id.isna().any():
        fail("one or more subset rows are absent from the private map")
    cluster_sizes = merged.groupby("sample_row_id", sort=False).size()
    if len(cluster_sizes) != EXPECTED_CLUSTERS or not (cluster_sizes == OUTPUTS_PER_CLUSTER).all():
        fail("subset is not exactly 200 opaque clusters of three outputs")

    result = merged.assign(cluster_id=merged.sample_row_id.map(opaque_cluster_id))[
        ["blind_item_id", "cluster_id"]
    ]
    if result.cluster_id.nunique() != EXPECTED_CLUSTERS:
        fail("opaque cluster hashing unexpectedly collided")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    receipt = {
        "status": "FROZEN_BLINDED_RELIABILITY_CLUSTER_MAP",
        "condition_labels_exposed": False,
        "private_fields_read": ["blind_item_id", "sample_row_id"],
        "private_fields_not_read": ["condition", "prompt_type", "model_id", "output_text"],
        "subset_rows": len(result),
        "opaque_clusters": int(result.cluster_id.nunique()),
        "outputs_per_cluster": OUTPUTS_PER_CLUSTER,
        "subset_sha256": sha256(args.subset),
        "cluster_map_sha256": sha256(args.out),
        "bootstrap_policy": "annotation_public/RELIABILITY_BOOTSTRAP_POLICY_v1.md",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        "# Blinded reliability-cluster map freeze\n\n"
        "This receipt records a mechanical, label-free cluster map used only for "
        "the precommitted item-cluster bootstrap. It does not contain the map, "
        "conditions, prompts, model identity, output text, or label statistics.\n\n"
        + "\n".join(f"- {key}: `{value}`" for key, value in receipt.items())
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
