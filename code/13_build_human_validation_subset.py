"""Create the blinded 600-row human-validation subset without outcome inspection.

Selects 200 locked VizWiz item IDs with a fixed seed, uses only the private
blind-ID-to-item mapping mechanically, includes all three blinded outputs per
selected item, and emits three byte-identical independent-coder packages. It
never reads or writes condition labels into a coder-visible artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ITEMS = 1_000
SELECTED_ITEMS = 200
EXPECTED_ROWS = 600
CODING_COLUMNS = (
    "task_answer", "task_relevance", "spatial_relation",
    "grounded_uncertainty", "unsupported_information", "identity_inference",
    "social_intent_inference", "unrequested_visual_detail",
    "accessibility_grounded_content", "ambiguity",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def arrange_without_adjacent_groups(frame: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Greedy deterministic interleave of three rows per selected source item."""
    rng = np.random.default_rng(seed)
    groups = {
        str(item): group.sample(frac=1, random_state=int(rng.integers(0, 2**31 - 1)))
        for item, group in frame.groupby("sample_row_id", sort=False)
    }
    order = list(groups)
    rng.shuffle(order)
    rows: list[pd.Series] = []
    previous: str | None = None
    while groups:
        candidates = [item for item in order if item in groups and item != previous]
        if not candidates:
            raise RuntimeError("Could not avoid adjacent outputs from one source item.")
        item = candidates[0]
        group = groups[item]
        rows.append(group.iloc[0])
        group = group.iloc[1:]
        if group.empty:
            del groups[item]
        else:
            groups[item] = group
        previous = item
    return pd.DataFrame(rows).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--sample", type=Path, default=ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv")
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261008)
    args = parser.parse_args()

    packet = pd.read_csv(args.packet)
    mapping = pd.read_csv(args.mapping, usecols=["blind_item_id", "sample_row_id"])
    sample = pd.read_csv(args.sample, usecols=["sample_row_id"])
    if len(sample) != EXPECTED_ITEMS or sample.sample_row_id.nunique() != EXPECTED_ITEMS:
        raise ValueError("Expected the locked 1,000-item sample.")
    if packet.blind_item_id.duplicated().any() or mapping.blind_item_id.duplicated().any():
        raise ValueError("Packet and mapping need unique blind IDs.")
    if not {"blind_item_id", "blv_question", "output_text"}.issubset(packet.columns):
        raise ValueError("Unexpected blinded packet schema.")

    rng = np.random.default_rng(args.seed)
    selected_ids = np.sort(rng.choice(sample.sample_row_id.to_numpy(), size=SELECTED_ITEMS, replace=False))
    selected = packet.merge(mapping, on="blind_item_id", how="inner", validate="one_to_one")
    selected = selected.loc[selected.sample_row_id.isin(selected_ids)].copy()
    if len(selected) != EXPECTED_ROWS or not (selected.groupby("sample_row_id").size() == 3).all():
        raise ValueError("Subset must contain exactly three blinded rows for each selected item.")
    selected = arrange_without_adjacent_groups(selected, args.seed + 1)
    if (selected.sample_row_id.shift() == selected.sample_row_id).any():
        raise AssertionError("Adjacent same-item rows remain after shuffle.")

    visible = selected[["blind_item_id", "blv_question", "output_text"]].copy()
    coding = visible.copy()
    for column in CODING_COLUMNS:
        coding[column] = ""
    coding["coder_id"] = ""
    coding["coding_date_utc"] = ""
    coding["notes"] = ""

    args.outdir.mkdir(parents=True, exist_ok=True)
    subset_packet = args.outdir / "blinded_human_validation_subset_v1.csv"
    visible.to_csv(subset_packet, index=False)
    selection_manifest = {
        "status": "FROZEN_BLINDED_HUMAN_VALIDATION_SUBSET",
        "seed": args.seed,
        "selected_locked_items": SELECTED_ITEMS,
        "outputs_per_selected_item": 3,
        "total_rows": EXPECTED_ROWS,
        "condition_labels_exposed": False,
        "same_item_rows_adjacent": False,
        "source_packet_sha256": sha256(args.packet),
        "subset_packet_sha256": sha256(subset_packet),
        "selected_item_ids_sha256": hashlib.sha256(
            ",".join(map(str, selected_ids)).encode("utf-8")
        ).hexdigest(),
    }
    (args.outdir / "human_validation_subset_manifest.json").write_text(
        json.dumps(selection_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for coder in ("coder_a", "coder_b", "coder_c"):
        coder_dir = args.outdir / coder
        coder_dir.mkdir(parents=True, exist_ok=True)
        coding.to_csv(coder_dir / "coding_sheet.csv", index=False)
        for material in ("CODER_INSTRUCTIONS_v1.md", "CODER_TRAINING_NONANALYTIC_v1.md", "adjudication_protocol.md"):
            shutil.copy2(ROOT / "annotation_public" / material, coder_dir / material)
    checksums = pd.DataFrame([
        {"artifact": "blinded_human_validation_subset_v1.csv", "sha256": sha256(subset_packet)},
        {"artifact": "coder_a/coding_sheet.csv", "sha256": sha256(args.outdir / "coder_a" / "coding_sheet.csv")},
        {"artifact": "coder_b/coding_sheet.csv", "sha256": sha256(args.outdir / "coder_b" / "coding_sheet.csv")},
        {"artifact": "coder_c/coding_sheet.csv", "sha256": sha256(args.outdir / "coder_c" / "coding_sheet.csv")},
        *[
            {"artifact": f"{coder}/{material}", "sha256": sha256(args.outdir / coder / material)}
            for coder in ("coder_a", "coder_b", "coder_c")
            for material in ("CODER_INSTRUCTIONS_v1.md", "CODER_TRAINING_NONANALYTIC_v1.md", "adjudication_protocol.md")
        ],
    ])
    if len({checksums.iloc[index].sha256 for index in (1, 2, 3)}) != 1:
        raise AssertionError("Coder packages are not byte-identical.")
    checksums.to_csv(args.outdir / "CHECKSUMS.csv", index=False)
    print(json.dumps(selection_manifest, sort_keys=True))


if __name__ == "__main__":
    main()
