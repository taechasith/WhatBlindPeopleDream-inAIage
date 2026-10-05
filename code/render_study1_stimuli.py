"""Rasterize original Study 1 SVG prototypes deterministically for local VLM use.

Rendered images are controlled local stimulus assets. They remain under
``private/`` and are never included in the anonymous-review exporter.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BROWSER = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
SOURCE_IMAGES = {
    "S01": ROOT / "stimuli" / "S01_courtyard_v2.svg",
    "S02": ROOT / "stimuli" / "S02_workshop_v2.svg",
    "S03": ROOT / "stimuli" / "S03_station_v2.svg",
    "S04": ROOT / "stimuli" / "S04_garden_v2.svg",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "private" / "study1_rendered_stimuli")
    parser.add_argument("--browser", type=Path, default=DEFAULT_BROWSER)
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=800)
    args = parser.parse_args()
    if not args.browser.exists():
        raise FileNotFoundError(f"Headless browser not found: {args.browser}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    with tempfile.TemporaryDirectory(prefix="study1_stimulus_render_") as profile:
        for stimulus_id, source in SOURCE_IMAGES.items():
            if not source.exists():
                raise FileNotFoundError(source)
            output = args.output_dir / f"{stimulus_id}.png"
            command = [
                str(args.browser),
                "--headless=new",
                "--disable-gpu",
                "--hide-scrollbars",
                f"--user-data-dir={profile}",
                f"--window-size={args.width},{args.height}",
                f"--screenshot={output}",
                source.resolve().as_uri(),
            ]
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
            if not output.exists() or output.stat().st_size == 0:
                raise RuntimeError(f"Browser did not produce {output}")
            manifest_rows.append({
                "stimulus_id": stimulus_id,
                "source_svg": source.relative_to(ROOT).as_posix(),
                "source_svg_sha256": sha256(source),
                "rendered_png": output.name,
                "rendered_png_sha256": sha256(output),
                "render_width_px": args.width,
                "render_height_px": args.height,
                "rendering_status": "LOCAL_NONHUMAN_NOT_FOR_REVIEW_EXPORT",
            })
    manifest = args.output_dir / "render_manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"Rendered {len(manifest_rows)} local images and wrote {manifest}")


if __name__ == "__main__":
    main()
