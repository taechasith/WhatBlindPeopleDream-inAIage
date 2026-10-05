"""Create a narrow, allowlisted anonymous-review source bundle.

This tool intentionally exports no raw data, executable code, images, PDFs,
Git metadata, or web addresses. It is a mechanical preflight check only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PATTERN_FILE = ROOT / "private" / "anonymous_release_forbidden_patterns.txt"
ALLOWLIST = (
    "README.md",
    "PROTOCOL.md",
    "ANALYSIS_PLAN.md",
    "CODEBOOK_v0.csv",
    "DREAM_INCORPORATION_CODEBOOK_v1.md",
    "STUDY0_STATUS.md",
    "STUDY1_DATA_DICTIONARY.md",
    "STUDY1_WAITING_PERIOD_STATUS.md",
    "CHI_ETHICS_NOTE_ANONYMOUS_DRAFT.md",
    "EVIDENCE_STRENGTH.md",
    "PRISMA.md",
    "DATA_DICTIONARY.md",
    "REPRODUCTION_STATUS.md",
    "AI_USE_LOG.md",
    "ANONYMOUS_RELEASE_POLICY.md",
    "results/sample_flow.csv",
    "results/dream_meta_summary.csv",
    "results/alignment_metrics.csv",
    "results/automated_candidate_distribution.csv",
    "results/robustness.csv",
    "results/limitations.md",
)
GENERIC_FORBIDDEN = (
    r"https?://|www\\.|git@|github\\.com|gitlab\\.com|bitbucket\\.org|"
    r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}|"
    r"\b(?:University|College|School of|Faculty of|Department of)\b"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def forbidden_pattern() -> re.Pattern[str]:
    """Combine generic leak checks with locally held project-specific patterns.

    The project-specific file is deliberately ignored by Git and must never be
    copied into an anonymous package. Requiring it prevents a generic scanner
    from being mistaken for a complete identity audit.
    """
    if not PRIVATE_PATTERN_FILE.is_file():
        raise RuntimeError(
            "Missing private anonymous-release pattern file; create it locally before export."
        )
    private_patterns = [
        line.strip()
        for line in PRIVATE_PATTERN_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not private_patterns:
        raise RuntimeError("Private anonymous-release pattern file has no active patterns.")
    return re.compile("|".join([GENERIC_FORBIDDEN, *private_patterns]), re.IGNORECASE)


def validate() -> list[Path]:
    failures: list[str] = []
    paths: list[Path] = []
    forbidden = forbidden_pattern()
    for relative in ALLOWLIST:
        path = ROOT / relative
        if not path.is_file():
            failures.append(f"MISSING_ALLOWLISTED_FILE\t{relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            failures.append(f"NON_TEXT_ALLOWLISTED_FILE\t{relative}")
            continue
        match = forbidden.search(text)
        if match:
            failures.append(f"FORBIDDEN_CONTENT\t{relative}\t{match.group(0)!r}")
            continue
        paths.append(path)
    if failures:
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    return paths


def output_is_outside_repository(output: Path) -> bool:
    try:
        output.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate without writing files")
    parser.add_argument("--output", type=Path, help="empty directory outside the repository")
    args = parser.parse_args()
    if args.check == (args.output is not None):
        parser.error("provide exactly one of --check or --output")
    paths = validate()
    if args.check:
        print(f"ANONYMOUS_EXPORT_CHECK_PASS\t{len(paths)} files")
        return 0
    output = args.output.resolve()
    if not output_is_outside_repository(output):
        parser.error("--output must be outside the repository")
    if output.exists() and any(output.iterdir()):
        parser.error("--output must not exist or must be empty")
    output.mkdir(parents=True, exist_ok=True)
    manifest = []
    for source in paths:
        relative = source.relative_to(ROOT)
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        manifest.append({"path": relative.as_posix(), "sha256": sha256(source)})
    (output / "ANONYMOUS_RELEASE_MANIFEST.json").write_text(
        json.dumps({"bundle": "anonymous-review-source", "files": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"ANONYMOUS_EXPORT_CREATED\t{output}\t{len(paths)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
