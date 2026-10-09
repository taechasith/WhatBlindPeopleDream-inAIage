"""Create a distribution-ready v1.1 coder package without regenerating its data.

The script copies the original frozen 600-row subset and coding sheets byte for
byte, then adds hash-pinned rubric, return, attestation, and assignment material.
It never opens the condition mapping or interprets output text.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLES = ("coder_a", "coder_b", "coder_c")
BASE_ARTIFACTS = ("blinded_human_validation_subset_v1.csv", *(f"{role}/coding_sheet.csv" for role in ROLES))
MATERIALS = (
    "CODER_INSTRUCTIONS_v1_1.md",
    "CODER_TRAINING_NONANALYTIC_v1_1.md",
    "adjudication_protocol_v1_1.md",
    "HUMAN_CODER_RETURN_PROTOCOL_v1_1.md",
    "HUMAN_CODER_INDEPENDENCE_ATTESTATION_TEMPLATE_v1_1.csv",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_checksums(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["artifact"]: row["sha256"] for row in csv.DictReader(handle)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-package", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        raise FileExistsError(f"Refuse to overwrite existing package: {args.outdir}")
    base_hashes = read_checksums(args.base_package / "CHECKSUMS.csv")
    for artifact in BASE_ARTIFACTS:
        source = args.base_package / artifact
        if not source.is_file() or base_hashes.get(artifact) != sha256(source):
            raise ValueError(f"Base frozen artifact fails checksum: {artifact}")
    args.outdir.mkdir(parents=True)
    for artifact in BASE_ARTIFACTS:
        destination = args.outdir / artifact
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(args.base_package / artifact, destination)
        if sha256(destination) != base_hashes[artifact]:
            raise RuntimeError(f"Byte-copy verification failed: {artifact}")
    packet_hash = sha256(args.outdir / "blinded_human_validation_subset_v1.csv")
    for role in ROLES:
        folder = args.outdir / role
        for material in MATERIALS:
            shutil.copy2(ROOT / "annotation_public" / material, folder / material)
        shutil.copy2(ROOT / "PUBLIC_INTERVENTION_CODEBOOK_v1_1.md", folder / "PUBLIC_INTERVENTION_CODEBOOK_v1_1.md")
        receipt = {
            "packet_id": "human_validation_v1_1",
            "coder_role": role,
            "coder_id": role.upper(),
            "packet_sha256": packet_hash,
            "distributed_coding_sheet_sha256": sha256(folder / "coding_sheet.csv"),
            "instructions_sha256": sha256(folder / "CODER_INSTRUCTIONS_v1_1.md"),
            "training_sha256": sha256(folder / "CODER_TRAINING_NONANALYTIC_v1_1.md"),
            "adjudication_protocol_sha256": sha256(folder / "adjudication_protocol_v1_1.md"),
            "codebook_sha256": sha256(folder / "PUBLIC_INTERVENTION_CODEBOOK_v1_1.md"),
            "return_protocol_sha256": sha256(folder / "HUMAN_CODER_RETURN_PROTOCOL_v1_1.md"),
            "blinding_statement": "No condition, prompt, model, source-image, hypothesis-direction, synthetic-label, or other-coder labels were distributed.",
        }
        with (folder / "assignment_receipt.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(receipt))
            writer.writeheader()
            writer.writerow(receipt)
    manifest = {
        "status": "DISTRIBUTION_READY_BLINDED_HUMAN_CODER_PACKET",
        "packet_id": "human_validation_v1_1",
        "base_packet": str(args.base_package),
        "subset_data_changed": False,
        "base_subset_sha256": base_hashes["blinded_human_validation_subset_v1.csv"],
        "subset_sha256": packet_hash,
        "coder_sheet_sha256": {role: sha256(args.outdir / role / "coding_sheet.csv") for role in ROLES},
        "material_change": "Hash-pinned codebook, attestation, return protocol, and assignment receipt; corrected malformed quotes and return-file instruction only.",
        "condition_labels_exposed": False,
    }
    (args.outdir / "PACKET_RELEASE_MANIFEST_v1_1.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksum_rows = []
    for path in sorted(args.outdir.rglob("*")):
        if path.is_file() and path.name != "CHECKSUMS.csv":
            checksum_rows.append({"artifact": str(path.relative_to(args.outdir)).replace("\\", "/"), "sha256": sha256(path)})
    with (args.outdir / "CHECKSUMS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("artifact", "sha256"))
        writer.writeheader()
        writer.writerows(checksum_rows)
    print(json.dumps({"packet_id": manifest["packet_id"], "rows": 600, "base_subset_sha256": manifest["base_subset_sha256"], "subset_sha256": packet_hash}, sort_keys=True))


if __name__ == "__main__":
    main()
