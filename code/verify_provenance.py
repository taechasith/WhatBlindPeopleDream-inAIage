"""Verify local source-file hashes recorded in data/CHECKSUMS.csv.

This utility never downloads, opens as text, or redistributes source material.
It is useful only after an authorized researcher has acquired local files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKSUMS = ROOT / "data" / "CHECKSUMS.csv"


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm.lower())
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest().upper()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="report absent local source files without returning a failure code",
    )
    args = parser.parse_args()
    failures = 0
    with CHECKSUMS.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    required = {"dataset_id", "path", "algorithm", "checksum", "access_date"}
    if not rows or set(rows[0]) != required:
        raise ValueError("Unexpected data/CHECKSUMS.csv schema")
    for row in rows:
        path = ROOT / row["path"]
        if not path.is_file():
            print(f"MISSING_LOCAL_SOURCE\t{row['dataset_id']}\t{row['path']}")
            failures += 1
            continue
        observed = digest(path, row["algorithm"])
        if observed == row["checksum"].upper():
            print(f"PASS\t{row['dataset_id']}\t{row['path']}")
        else:
            print(f"HASH_MISMATCH\t{row['dataset_id']}\t{row['path']}")
            failures += 1
    return 0 if failures == 0 or args.allow_missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
