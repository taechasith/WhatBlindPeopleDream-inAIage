"""Make blinded local coding packets from schema-validated real VLM outputs.

The packet includes question and output text because task relevance cannot be
coded without them. It omits source name, image filename, condition, model ID,
and original order. The mapping is a sensitive local file and must not be shared
with coders or placed in a review bundle.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv"


def digest(value: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{value}".encode("utf-8")).hexdigest()[:16]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261006)
    args = parser.parse_args()
    salt = os.environ.get("PUBLIC_CODING_BLIND_SALT")
    if not salt:
        raise RuntimeError("Set the private PUBLIC_CODING_BLIND_SALT environment variable before packet generation.")
    outputs = pd.read_csv(args.outputs)
    sample = pd.read_csv(SAMPLE, usecols=["sample_row_id", "blv_question"])
    required = {"sample_row_id", "model_id", "condition", "output_text"}
    if not required.issubset(outputs.columns) or outputs.duplicated(["sample_row_id", "model_id", "condition"]).any():
        raise ValueError("Outputs must be a unique, schema-validated intervention table.")
    merged = outputs.merge(sample, on="sample_row_id", how="inner", validate="many_to_one")
    if len(merged) != len(outputs):
        raise ValueError("Outputs include item IDs outside the frozen intervention sample.")
    key = merged["sample_row_id"].astype(str) + "|" + merged["model_id"].astype(str) + "|" + merged["condition"].astype(str)
    merged["blind_item_id"] = key.map(lambda value: f"B{digest(value, salt)}")
    if merged["blind_item_id"].duplicated().any():
        raise ValueError("Blinding collision; choose a new private salt.")
    packet = merged[["blind_item_id", "blv_question", "output_text"]].sample(frac=1, random_state=args.seed)
    mapping = merged[["blind_item_id", "sample_row_id", "model_id", "condition"]]
    args.packet.parent.mkdir(parents=True, exist_ok=True)
    args.mapping.parent.mkdir(parents=True, exist_ok=True)
    packet.to_csv(args.packet, index=False)
    mapping.to_csv(args.mapping, index=False)
    print(f"BLINDED_PACKET_CREATED\trows={len(packet)}\tpacket={args.packet}\tmapping={args.mapping}")


if __name__ == "__main__":
    main()
