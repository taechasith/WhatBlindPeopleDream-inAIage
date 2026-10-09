"""Build an anonymous A0 poster only from frozen public-data results and figures.

This is deliberately a post-results renderer.  It does not calculate results,
read model outputs, or fill in scientific claims.  Instead it verifies the
frozen results and figure manifests, then lays out a supplied, ledger-backed
anonymous content record with the final accessible figures.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import wrap
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

# ISO A0 landscape, expressed in PostScript points.  The physical dimensions
# are 1,189 mm by 841 mm; one point is 1/72 inch.
WIDTH_MM = 1189
HEIGHT_MM = 841
WIDTH_PT = WIDTH_MM * 72 / 25.4
HEIGHT_PT = HEIGHT_MM * 72 / 25.4
MARGIN = 95

REQUIRED_FIGURES = (
    "figure_1_reciprocal_cognitive_sensing_loop.svg",
    "figure_2_prompt_condition_effects.svg",
    "figure_3_human_reference_alignment.svg",
    "figure_4_representational_space_distances.svg",
    "figure_5_largest_output_property_changes.svg",
)

# Review-stage material must not provide a route back to authors.  References
# in a poster may use ordinary author-year or DOI text, but this renderer never
# permits live contact, repository, or institutional links.
DISALLOWED_REVIEW_TEXT = (
    re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:https?://|www\.|mailto:|github\.com|orcid\.org)\b", re.IGNORECASE),
    re.compile(r"\b(?:affiliation|corresponding author|contact author)\b", re.IGNORECASE),
)
PENDING_TEXT = re.compile(r"\b(?:tbd|todo|placeholder|results[ -]?pending)\b", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"ANONYMOUS_A0_POSTER_FAILED: {message}")


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        fail(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {label}: {exc}")
    if not isinstance(value, dict):
        fail(f"{label} must be a JSON object")
    return value


def nonempty_text(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str):
        fail(f"{label} must be text")
    text = " ".join(value.split())
    if not text:
        fail(f"{label} is empty")
    if len(text) > maximum:
        fail(f"{label} exceeds its {maximum}-character poster limit")
    if PENDING_TEXT.search(text):
        fail(f"{label} contains a results-pending or placeholder marker")
    for pattern in DISALLOWED_REVIEW_TEXT:
        if pattern.search(text):
            fail(f"{label} contains review-identifying contact or affiliation text")
    return text


def require_text_list(value: object, label: str, *, minimum: int, maximum: int, item_limit: int) -> list[str]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        fail(f"{label} must contain between {minimum} and {maximum} items")
    return [nonempty_text(item, f"{label}[{index}]", item_limit) for index, item in enumerate(value)]


def validate_content(content: dict[str, Any], results_freeze: Path, figure_manifest: Path) -> dict[str, Any]:
    if content.get("schema_version") != 1:
        fail("poster content schema_version must be 1")
    if content.get("review_stage") != "ANONYMOUS_REVIEW":
        fail("poster content must explicitly be ANONYMOUS_REVIEW material")
    if content.get("results_freeze_sha256") != sha256(results_freeze):
        fail("poster content is not tied to the supplied RESULTS_FREEZE")
    if content.get("figure_manifest_sha256") != sha256(figure_manifest):
        fail("poster content is not tied to the supplied figure manifest")

    sections = content.get("sections")
    if not isinstance(sections, dict):
        fail("poster content requires a sections object")
    normalized = {
        "title": nonempty_text(content.get("title"), "title", 190),
        "subtitle": nonempty_text(content.get("subtitle"), "subtitle", 280),
        "sample_summary": nonempty_text(content.get("sample_summary"), "sample_summary", 220),
        "methods": require_text_list(sections.get("methods"), "sections.methods", minimum=2, maximum=5, item_limit=240),
        "findings": require_text_list(sections.get("findings"), "sections.findings", minimum=2, maximum=5, item_limit=260),
        "implications": require_text_list(sections.get("implications"), "sections.implications", minimum=1, maximum=4, item_limit=260),
        "limitations": require_text_list(sections.get("limitations"), "sections.limitations", minimum=2, maximum=5, item_limit=260),
        "ethics_note": nonempty_text(content.get("ethics_note"), "ethics_note", 300),
        "discussion_points": require_text_list(content.get("discussion_points"), "discussion_points", minimum=2, maximum=5, item_limit=230),
    }

    trace_ids = content.get("result_trace_ids")
    if not isinstance(trace_ids, list) or not trace_ids or not all(isinstance(item, str) and item.strip() for item in trace_ids):
        fail("poster content must include non-empty result_trace_ids for claim-audit traceability")
    normalized["result_trace_ids"] = [item.strip() for item in trace_ids]
    return normalized


def validate_frozen_inputs(results_freeze: Path, figures_dir: Path) -> tuple[dict[str, Any], Path, dict[str, dict[str, str]]]:
    freeze = load_json(results_freeze, "RESULTS_FREEZE")
    if freeze.get("status") != "RESULTS_FROZEN_PUBLIC_DATA_ONLY":
        fail("results are not frozen for the public-data study")
    if not bool(freeze.get("condition_unblinded_once")):
        fail("results freeze does not attest to the authorized one-time unblinding")
    if not figures_dir.is_dir():
        fail(f"missing final figure directory: {figures_dir}")
    manifest_path = figures_dir / "FIGURE_MANIFEST.csv"
    if not manifest_path.is_file():
        fail("final figure directory has no FIGURE_MANIFEST.csv")

    rows = manifest_path.read_text(encoding="utf-8").splitlines()
    if not rows or rows[0] != "artifact,sha256,alt_text":
        fail("FIGURE_MANIFEST.csv has an unexpected schema")
    figure_rows: dict[str, dict[str, str]] = {}
    # Figure alt text can contain commas, so parse the manifest with csv rather
    # than splitting the data rows by delimiter.
    import csv
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            artifact = str(row.get("artifact", ""))
            if artifact in figure_rows:
                fail(f"duplicate figure manifest artifact: {artifact}")
            figure_rows[artifact] = {key: str(value) for key, value in row.items()}

    for artifact in REQUIRED_FIGURES:
        row = figure_rows.get(artifact)
        path = figures_dir / artifact
        if row is None or not path.is_file():
            fail(f"required final figure is absent: {artifact}")
        if row.get("sha256") != sha256(path):
            fail(f"figure hash differs from final figure manifest: {artifact}")
        alt_path = path.with_suffix(".alt.txt")
        if not alt_path.is_file() or not alt_path.read_text(encoding="utf-8").strip():
            fail(f"required accessible alt text is absent: {alt_path.name}")
        figure_text = path.read_text(encoding="utf-8")
        if re.search(r"(?:href|xlink:href)\s*=\s*['\"](?:https?:|//)|url\(\s*(?:https?:|//)", figure_text, flags=re.IGNORECASE):
            fail(f"final figure contains an external resource link: {artifact}")
    return freeze, manifest_path, figure_rows


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def wrap_lines(text: str, characters: int) -> list[str]:
    return wrap(text, width=characters, break_long_words=False, break_on_hyphens=False) or [text]


def svg_text_block(x: float, y: float, width: float, text: str, font_size: float, *, weight: str = "normal", fill: str = "#111111", bullet: bool = False, line_gap: float = 1.23, max_lines: int | None = None) -> tuple[str, float]:
    chars = max(12, int(width / (font_size * 0.52)))
    prefix = "• " if bullet else ""
    lines = wrap_lines(prefix + text, chars)
    if max_lines is not None and len(lines) > max_lines:
        fail(f"poster text does not fit allocated layout: {text[:48]!r}")
    tspans = []
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else font_size * line_gap
        tspans.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{escape(line)}</tspan>')
    markup = f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, Helvetica, sans-serif" font-size="{font_size:.1f}" font-weight="{weight}" fill="{fill}">{"".join(tspans)}</text>'
    return markup, y + font_size * (1 + (len(lines) - 1) * line_gap)


def svg_list(x: float, y: float, width: float, items: list[str], font_size: float, *, max_height: float) -> tuple[str, float]:
    blocks: list[str] = []
    current = y
    for item in items:
        block, current = svg_text_block(x, current, width, item, font_size, bullet=True, line_gap=1.22)
        blocks.append(block)
        current += font_size * 0.52
    if current > y + max_height:
        fail("poster section exceeds its allocated A0 layout height")
    return "".join(blocks), current


def panel(x: float, y: float, width: float, height: float, title: str, body: str = "") -> str:
    markup = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" rx="18" fill="#ffffff" stroke="#111111" stroke-width="3"/>']
    heading, _ = svg_text_block(x + 28, y + 50, width - 56, title, 30, weight="bold", max_lines=2)
    markup.append(heading)
    if body:
        paragraph, _ = svg_text_block(x + 28, y + 94, width - 56, body, 19, fill="#303030", max_lines=5)
        markup.append(paragraph)
    return "".join(markup)


def figure_panel(x: float, y: float, width: float, height: float, title: str, figure_path: Path, alt_text: str) -> str:
    encoded = base64.b64encode(figure_path.read_bytes()).decode("ascii")
    markup = [panel(x, y, width, height, title)]
    markup.append(f'<g role="img" aria-label="{escape(alt_text)}"><title>{escape(title)}</title><desc>{escape(alt_text)}</desc>')
    markup.append(f'<image x="{x + 22:.1f}" y="{y + 72:.1f}" width="{width - 44:.1f}" height="{height - 94:.1f}" preserveAspectRatio="xMidYMid meet" href="data:image/svg+xml;base64,{encoded}"/>')
    markup.append("</g>")
    return "".join(markup)


def build_svg(content: dict[str, Any], figures_dir: Path, figure_rows: dict[str, dict[str, str]]) -> str:
    header_height = 450
    main_y = 490
    main_height = 1130
    footer_y = 1660
    footer_height = HEIGHT_PT - footer_y - MARGIN
    left_x, left_w = MARGIN, 810
    center_x, center_w = 935, 1100
    right_x, right_w = 2125, WIDTH_PT - MARGIN - 2125

    svg: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_MM}mm" height="{HEIGHT_MM}mm" viewBox="0 0 {WIDTH_PT:.2f} {HEIGHT_PT:.2f}" role="img" aria-labelledby="poster-title poster-description">',
        "<title id=\"poster-title\">Anonymous CHI 2027 A0 poster</title>",
        "<desc id=\"poster-description\">A grayscale accessible A0 research poster generated only after the public-data results and figures were frozen.</desc>",
        "<metadata>Anonymous review-stage poster. No author, affiliation, contact, repository, or identifier metadata is included.</metadata>",
        f'<rect width="{WIDTH_PT:.2f}" height="{HEIGHT_PT:.2f}" fill="#f7f7f7"/>',
    ]
    title, title_bottom = svg_text_block(MARGIN, 100, WIDTH_PT - 2 * MARGIN, content["title"], 68, weight="bold", max_lines=2)
    svg.append(title)
    subtitle, subtitle_bottom = svg_text_block(MARGIN, title_bottom + 45, WIDTH_PT - 2 * MARGIN, content["subtitle"], 31, fill="#252525", max_lines=2)
    svg.append(subtitle)
    sample, _ = svg_text_block(MARGIN, max(subtitle_bottom + 42, 405), WIDTH_PT - 2 * MARGIN, content["sample_summary"], 24, weight="bold", fill="#252525", max_lines=1)
    svg.append(sample)
    svg.append(f'<line x1="{MARGIN}" y1="{header_height}" x2="{WIDTH_PT - MARGIN}" y2="{header_height}" stroke="#111111" stroke-width="4"/>')

    # Main three-column composition.  The conceptual loop remains prominent,
    # while all numeric claims live inside the frozen result figures/content.
    method_height = 330
    svg.append(panel(left_x, main_y, left_w, method_height, "How we studied sensory mediation"))
    methods, _ = svg_list(left_x + 30, main_y + 105, left_w - 60, content["methods"], 22, max_height=method_height - 125)
    svg.append(methods)
    f1 = figures_dir / REQUIRED_FIGURES[0]
    svg.append(figure_panel(left_x, main_y + method_height + 30, left_w, main_height - method_height - 30, "1. Reciprocal Cognitive Sensing Loop", f1, figure_rows[f1.name]["alt_text"]))

    f2, f3 = (figures_dir / REQUIRED_FIGURES[index] for index in (1, 2))
    svg.append(figure_panel(center_x, main_y, center_w, 555, "2. Within-item prompt-condition effects", f2, figure_rows[f2.name]["alt_text"]))
    svg.append(figure_panel(center_x, main_y + 585, center_w, main_height - 585, "3. Bounded human-reference alignment", f3, figure_rows[f3.name]["alt_text"]))

    f4, f5 = (figures_dir / REQUIRED_FIGURES[index] for index in (3, 4))
    svg.append(figure_panel(right_x, main_y, right_w, 540, "4. Representational-space distances", f4, figure_rows[f4.name]["alt_text"]))
    svg.append(figure_panel(right_x, main_y + 570, right_w, main_height - 570, "5. Largest output-property changes", f5, figure_rows[f5.name]["alt_text"]))

    footer_gap = 25
    footer_width = (WIDTH_PT - 2 * MARGIN - 3 * footer_gap) / 4
    footer_titles = ("Key findings", "Design implications", "Limitations", "Ethics and discussion")
    footer_items = (content["findings"], content["implications"], content["limitations"], [content["ethics_note"], *content["discussion_points"]])
    for index, (heading, items) in enumerate(zip(footer_titles, footer_items)):
        x = MARGIN + index * (footer_width + footer_gap)
        svg.append(panel(x, footer_y, footer_width, footer_height, heading))
        item_size = 20 if index < 3 else 18
        text, _ = svg_list(x + 26, footer_y + 105, footer_width - 52, items, item_size, max_height=footer_height - 132)
        svg.append(text)
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


def render_pdf(svg_path: Path, pdf_path: Path) -> None:
    renderer = shutil.which("inkscape")
    if renderer is None:
        fail("Inkscape is required to produce the required A0 PDF but is not on PATH")
    completed = subprocess.run(
        [renderer, str(svg_path), f"--export-filename={pdf_path}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0 or not pdf_path.is_file():
        fail(f"Inkscape PDF export failed: {completed.stderr.strip() or completed.stdout.strip()}")


def scrub_and_verify_pdf(pdf_path: Path) -> None:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        fail(f"pypdf is required for anonymous PDF metadata verification: {exc}")
    reader = PdfReader(str(pdf_path))
    if len(reader.pages) != 1:
        fail("A0 poster PDF must contain exactly one page")
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata({
        "/Title": "Anonymous CHI 2027 Poster",
        "/Author": "Anonymous",
        "/Subject": "Anonymous review-stage public-data study",
        "/Creator": "Reproducible anonymous A0 poster pipeline",
        "/Producer": "pypdf",
    })
    with pdf_path.open("wb") as stream:
        writer.write(stream)

    checked = PdfReader(str(pdf_path))
    if len(checked.pages) != 1:
        fail("post-scrub PDF no longer has one page")
    media_box = checked.pages[0].mediabox
    width = float(media_box.width)
    height = float(media_box.height)
    if abs(width - WIDTH_PT) > 8 or abs(height - HEIGHT_PT) > 8:
        fail(f"PDF page size is not A0 landscape: {width:.1f} by {height:.1f} pt")
    metadata = checked.metadata or {}
    if str(metadata.get("/Author", "")) != "Anonymous":
        fail("PDF author metadata was not anonymized")
    for page in checked.pages:
        annotations = page.get("/Annots")
        if annotations:
            fail("anonymous review poster must not contain PDF annotations or external links")
    text = "\n".join(page.extract_text() or "" for page in checked.pages)
    for pattern in DISALLOWED_REVIEW_TEXT:
        if pattern.search(text):
            fail("PDF text contains contact, repository, or affiliation material")


def write_accessibility_note(outdir: Path, content: dict[str, Any], figures_dir: Path, figure_rows: dict[str, dict[str, str]]) -> Path:
    lines = [
        "# A0 Poster Accessibility Notes",
        "",
        "The review-stage poster uses grayscale, direct labels, markers, hatching, and text summaries rather than color alone.",
        "It has no author, affiliation, contact, repository, or live-link information.",
        "",
        "## Textual overview",
        "",
        content["title"],
        "",
        content["subtitle"],
        "",
        "## Figure alt text",
        "",
    ]
    for artifact in REQUIRED_FIGURES:
        lines.extend((f"### {artifact}", "", figure_rows[artifact]["alt_text"], ""))
    path = outdir / "A0_POSTER_ACCESSIBILITY.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, required=True)
    parser.add_argument("--figures-dir", type=Path, required=True)
    parser.add_argument("--content-json", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--require-pdf", action="store_true", help="render, scrub, and verify the final A0 PDF using Inkscape and pypdf")
    args = parser.parse_args()

    if args.outdir.exists():
        fail("refuse to overwrite an existing poster directory; create a new immutable build directory")
    freeze, figure_manifest, figure_rows = validate_frozen_inputs(args.results_freeze, args.figures_dir)
    content = validate_content(load_json(args.content_json, "poster content"), args.results_freeze, figure_manifest)
    args.outdir.mkdir(parents=True, exist_ok=False)

    svg_path = args.outdir / "A0_anonymous_poster.svg"
    svg_path.write_text(build_svg(content, args.figures_dir, figure_rows), encoding="utf-8")
    accessibility_path = write_accessibility_note(args.outdir, content, args.figures_dir, figure_rows)
    artifacts = [
        {"artifact": svg_path.name, "sha256": sha256(svg_path), "kind": "A0 landscape SVG"},
        {"artifact": accessibility_path.name, "sha256": sha256(accessibility_path), "kind": "poster accessibility text"},
    ]
    if args.require_pdf:
        pdf_path = args.outdir / "A0_anonymous_poster.pdf"
        render_pdf(svg_path, pdf_path)
        scrub_and_verify_pdf(pdf_path)
        artifacts.append({"artifact": pdf_path.name, "sha256": sha256(pdf_path), "kind": "anonymous A0 landscape PDF"})

    manifest = {
        "status": "ANONYMOUS_A0_POSTER_COMPLETE" if args.require_pdf else "ANONYMOUS_A0_POSTER_SVG_COMPLETE",
        "study_scope": "public-data computational study",
        "results_freeze": str(args.results_freeze),
        "results_freeze_sha256": sha256(args.results_freeze),
        "figure_manifest": str(figure_manifest),
        "figure_manifest_sha256": sha256(figure_manifest),
        "content_json": str(args.content_json),
        "content_json_sha256": sha256(args.content_json),
        "a0_orientation": "landscape",
        "a0_dimensions_mm": {"width": WIDTH_MM, "height": HEIGHT_MM},
        "anonymous_review": True,
        "result_trace_ids": content["result_trace_ids"],
        "artifacts": artifacts,
    }
    manifest_path = args.outdir / "POSTER_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "outdir": str(args.outdir), "artifacts": len(artifacts)}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
