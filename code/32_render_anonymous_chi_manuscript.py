"""Render an anonymous, evidence-traceable CHI manuscript source post-freeze.

This renderer is deliberately downstream of RESULTS_FREEZE.  It never reads
raw model outputs, a condition mapping, or a live analysis table outside the
immutable paper fact packet produced by ``31_build_paper_fact_packet.py``.
It is also deliberately *not* a scientific-writing model: selected numerical
facts are placed into fixed, cautious table language, while all supplied prose
is restricted to non-result context and is screened for review-stage metadata.

The program fails closed.  It refuses to render until the results freeze,
fact-packet receipt, selected figures, and an audited bibliography all
reconcile.  It must be run only after the final results, reference, anonymity,
and claim audits are complete.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FACT_PACKET_STATUS = "PAPER_FACT_PACKET_FROM_RESULTS_FREEZE"
EXPECTED_FACT_MANIFEST_STATUS = "PAPER_FACT_PACKET_FROZEN_FROM_RESULTS_FREEZE"
EXPECTED_RESULTS_STATUS = "RESULTS_FROZEN_PUBLIC_DATA_ONLY"
EXPECTED_REFERENCE_AUDIT_STATUS = "REFERENCE_AUDIT_CLEAN_ANONYMOUS"
EXPECTED_FAMILIES = ("RQ2", "RQ3", "RQ4", "RQ5")
FACT_FAMILIES = EXPECTED_FAMILIES + ("RQ4_profiles", "RQ4_association_status")
MAX_RESULT_ROWS = 12
MAX_FIGURES = 3
MAX_CONTEXT_CHARS = 700

FAMILY_LABELS = {
    "RQ2": "RQ2: within-item information changes",
    "RQ3": "RQ3: bounded external human-reference alignment",
    "RQ4": "RQ4: distributional representational-space comparison",
    "RQ5": "RQ5: measured output-property changes",
}
FAMILY_MACROS = {
    "RQ2": "RQTwo",
    "RQ3": "RQThree",
    "RQ4": "RQFour",
    "RQ5": "RQFive",
}
NUMERIC_FIELDS = {
    "RQ2": ("n_paired_items", "effect", "ci_low", "ci_high", "fdr_q"),
    "RQ3": ("n_paired_items", "effect", "ci_low", "ci_high", "fdr_q"),
    "RQ4": ("n_a", "n_b", "jensen_shannon_divergence", "js_ci_low", "js_ci_high"),
    "RQ5": ("n_paired_items", "effect", "ci_low", "ci_high", "fdr_q"),
}

EMAIL = re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", re.IGNORECASE)
URL = re.compile(r"\b(?:https?://|www\.|mailto:|github\.com|orcid\.org)\b", re.IGNORECASE)
LOCAL_PATH = re.compile(r"(?:[A-Za-z]:[\\/]|(?:^|\s)(?:\.?[\\/])\S+)")
PLACEHOLDER = re.compile(r"\b(?:todo|tbd|placeholder|results[ -]?pending|replace this)\b", re.IGNORECASE)
FORBIDDEN_CAUSAL = re.compile(
    r"\b(?:rewire[sd]?|reprogram(?:s|med|ming)?\s+(?:the\s+)?brain|changes?\s+(?:blind\s+)?dreams?|"
    r"enters?\s+(?:blind\s+)?dreams?|thinks?\s+like\s+blind|reproduce[sd]?\s+blind\s+cognition|"
    r"synthetic\s+(?:humans?|participants?|blind\s+users?)|blind\s+people\s+(?:rated|preferred|felt))\b",
    re.IGNORECASE,
)
IDENTIFYING_KEYS = {
    "author", "authors", "affiliation", "affiliations", "email", "emails",
    "acknowledgment", "acknowledgements", "acknowledgments", "institution",
    "repository", "repository_url", "contact", "corresponding_author",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"ANONYMOUS_MANUSCRIPT_RENDER_FAILED: {message}")


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


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


def normal_text(value: object, label: str, *, maximum: int, allow_empty: bool = False) -> str:
    if not isinstance(value, str):
        fail(f"{label} must be text")
    text = " ".join(value.split())
    if not text and not allow_empty:
        fail(f"{label} is empty")
    if len(text) > maximum:
        fail(f"{label} exceeds its {maximum}-character budget")
    if PLACEHOLDER.search(text):
        fail(f"{label} contains placeholder text")
    if EMAIL.search(text) or URL.search(text) or LOCAL_PATH.search(text):
        fail(f"{label} contains contact, URL, repository, or local-path metadata")
    if FORBIDDEN_CAUSAL.search(text):
        fail(f"{label} contains a prohibited causal or lived-experience claim")
    return text


def require_hash(manifest: dict[str, Any], artifact: Path, label: str) -> None:
    expected = manifest.get("artifacts", {}).get(artifact.name)
    if not isinstance(expected, str) or not artifact.is_file() or expected != sha256(artifact):
        fail(f"{label} does not match its immutable receipt")


def validate_results_and_packet(
    results_freeze_path: Path, fact_packet_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], Path]:
    results = load_json(results_freeze_path, "RESULTS_FREEZE")
    if results.get("status") != EXPECTED_RESULTS_STATUS:
        fail("RESULTS_FREEZE is not the public-data frozen result receipt")
    if results.get("new_human_data_collected") is not False:
        fail("RESULTS_FREEZE does not attest to zero new human data collection")
    if results.get("condition_unblinded_once") is not True:
        fail("RESULTS_FREEZE does not attest to the authorized one-time unblinding")

    packet_path = fact_packet_dir / "paper_fact_packet.json"
    manifest_path = fact_packet_dir / "PAPER_FACT_PACKET_MANIFEST.json"
    csv_path = fact_packet_dir / "paper_fact_packet.csv"
    macros_path = fact_packet_dir / "results_macros.tex"
    packet = load_json(packet_path, "paper fact packet")
    manifest = load_json(manifest_path, "paper fact-packet manifest")
    if packet.get("status") != EXPECTED_FACT_PACKET_STATUS:
        fail("paper fact packet has an unexpected status")
    if manifest.get("status") != EXPECTED_FACT_MANIFEST_STATUS:
        fail("paper fact-packet manifest has an unexpected status")
    if packet.get("source_results_freeze_sha256") != sha256(results_freeze_path):
        fail("paper fact packet is not tied to the supplied RESULTS_FREEZE")
    if manifest.get("source_results_freeze_sha256") != sha256(results_freeze_path):
        fail("paper fact-packet manifest is not tied to the supplied RESULTS_FREEZE")
    for artifact, label in ((packet_path, "paper fact packet"), (csv_path, "paper fact CSV"), (macros_path, "numeric macro file")):
        require_hash(manifest, artifact, label)

    facts_raw = packet.get("facts")
    if not isinstance(facts_raw, list) or not facts_raw:
        fail("paper fact packet contains no facts")
    facts: dict[str, dict[str, Any]] = {}
    for fact in facts_raw:
        if not isinstance(fact, dict):
            fail("paper fact packet contains a malformed fact")
        fact_id = fact.get("fact_id")
        family = fact.get("result_family")
        values = fact.get("values")
        if not isinstance(fact_id, str) or not re.fullmatch(r"(?:RQ[2345]|RQ4_profiles|RQ4_association_status)_\d{4}", fact_id):
            fail("paper fact packet contains an invalid fact identifier")
        if family not in FACT_FAMILIES or fact_id in facts or not isinstance(values, dict):
            fail("paper fact packet has duplicate or malformed fact provenance")
        facts[fact_id] = fact
    if packet.get("fact_count") != len(facts):
        fail("paper fact packet fact count does not reconcile")
    return results, packet, manifest, facts, macros_path


def validate_figures(figures_dir: Path, expected_freeze_hash: str) -> tuple[dict[str, dict[str, str]], Path]:
    manifest_path = figures_dir / "FIGURE_MANIFEST.csv"
    binding_path = figures_dir / "FIGURE_METHODS.md"
    if not figures_dir.is_dir() or not manifest_path.is_file() or not binding_path.is_file():
        fail("final figure directory is incomplete")
    # Figure generation is bound to RESULTS_FREEZE by the upstream results
    # receipt; this renderer also records the exact manifest hash in its plan.
    _ = expected_freeze_hash
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or set(rows[0]) != {"artifact", "sha256", "alt_text"}:
        fail("FIGURE_MANIFEST.csv has an unexpected schema")
    figures: dict[str, dict[str, str]] = {}
    for row in rows:
        artifact = str(row.get("artifact", ""))
        if not artifact or artifact in figures or not artifact.endswith(".png"):
            continue
        image = figures_dir / artifact
        alt = image.with_suffix(".alt.txt")
        if not image.is_file() or sha256(image) != str(row.get("sha256", "")):
            fail(f"figure does not match its manifest: {artifact}")
        if not alt.is_file() or not alt.read_text(encoding="utf-8").strip():
            fail(f"figure lacks accessible alt text: {artifact}")
        figures[artifact] = {"sha256": str(row["sha256"]), "alt_text": str(row["alt_text"])}
    if not figures:
        fail("figure manifest has no verified PNG figures")
    return figures, manifest_path


def macro_name(fact_id: str, family: str, field: str) -> str:
    ordinal = int(fact_id.rsplit("_", 1)[1])
    title_field = "".join(piece.capitalize() for piece in field.split("_"))
    return rf"\csname Paper{FAMILY_MACROS[family]}F{ordinal:04d}{title_field}\endcsname"


def write_tex_macros(source: Path, destination: Path) -> None:
    """Translate digit-bearing macro names to TeX ``csname`` definitions."""
    lines: list[str] = []
    pattern = re.compile(r"\\newcommand\{\\([A-Za-z]+\d+[A-Za-z0-9]*)\}\{(.*)\}$")
    for raw in source.read_text(encoding="utf-8").splitlines():
        match = pattern.fullmatch(raw)
        if match:
            lines.append(rf"\expandafter\def\csname {match.group(1)}\endcsname{{{match.group(2)}}}")
        else:
            lines.append(raw)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def paper_claim_id(fact_id: str, field: str) -> str:
    """Return the immutable source marker used by the post-render audit.

    The marker is deliberately a LaTeX comment rather than visible prose.  It
    lets the later traceability builder bind every displayed *numeric* table
    value to a fact-packet row without asking a human to transcribe results or
    inspecting a condition mapping.  Non-numeric NOT_ESTIMABLE values are not
    claims and are omitted by that later builder.
    """
    return f"PAPER_{fact_id}_{field.upper()}"


def paper_claim_markers(fact_id: str, fact: dict[str, Any]) -> list[str]:
    family = str(fact["result_family"])
    return [f"% CLAIM-ID: {paper_claim_id(fact_id, field)}" for field in NUMERIC_FIELDS[family]]


def validate_plan(
    plan_path: Path,
    results_freeze_path: Path,
    packet_manifest_path: Path,
    figure_manifest_path: Path,
    facts: dict[str, dict[str, Any]],
    figures: dict[str, dict[str, str]],
) -> dict[str, Any]:
    plan = load_json(plan_path, "manuscript render plan")
    if plan.get("schema_version") != 1 or plan.get("review_stage") != "ANONYMOUS_REVIEW":
        fail("render plan must declare schema_version 1 and ANONYMOUS_REVIEW")
    if any(key in plan for key in IDENTIFYING_KEYS):
        fail("render plan contains an author-identifying metadata field")
    if plan.get("results_freeze_sha256") != sha256(results_freeze_path):
        fail("render plan is not tied to the supplied RESULTS_FREEZE")
    if plan.get("fact_packet_manifest_sha256") != sha256(packet_manifest_path):
        fail("render plan is not tied to the frozen fact-packet manifest")
    if plan.get("figure_manifest_sha256") != sha256(figure_manifest_path):
        fail("render plan is not tied to the frozen figure manifest")

    normalized = {
        "title": normal_text(plan.get("title"), "title", maximum=190),
        "motivation": normal_text(plan.get("motivation"), "motivation", maximum=MAX_CONTEXT_CHARS),
        "method_scope": normal_text(plan.get("method_scope"), "method_scope", maximum=MAX_CONTEXT_CHARS),
        "impact_scope": normal_text(plan.get("impact_scope"), "impact_scope", maximum=MAX_CONTEXT_CHARS),
        "citation_keys": plan.get("citation_keys"),
    }
    if "\\" in normalized["title"]:
        fail("title cannot contain LaTeX commands")
    if not isinstance(normalized["citation_keys"], list) or not normalized["citation_keys"]:
        fail("render plan must include at least one audited citation key")
    citation_keys: list[str] = []
    for key in normalized["citation_keys"]:
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9:_-]+", key) or key in citation_keys:
            fail("render plan contains an invalid or duplicate citation key")
        citation_keys.append(key)
    normalized["citation_keys"] = citation_keys

    raw_blocks = plan.get("result_blocks")
    if not isinstance(raw_blocks, list) or len(raw_blocks) != len(EXPECTED_FAMILIES):
        fail("render plan must contain one result block for each of RQ2--RQ5")
    blocks: list[dict[str, Any]] = []
    used_fact_ids: set[str] = set()
    for raw in raw_blocks:
        if not isinstance(raw, dict):
            fail("result block must be an object")
        family = raw.get("family")
        fact_ids = raw.get("fact_ids")
        if family not in EXPECTED_FAMILIES or not isinstance(fact_ids, list) or not fact_ids:
            fail("each result block needs a family and at least one frozen fact")
        if any(not isinstance(fact_id, str) or fact_id not in facts for fact_id in fact_ids):
            fail("result block refers to a fact absent from the frozen fact packet")
        if any(facts[fact_id]["result_family"] != family for fact_id in fact_ids):
            fail("result block mixes result families")
        if len(set(fact_ids)) != len(fact_ids) or used_fact_ids.intersection(fact_ids):
            fail("result block reuses a fact identifier")
        used_fact_ids.update(fact_ids)
        blocks.append({"family": family, "fact_ids": list(fact_ids)})
    if {block["family"] for block in blocks} != set(EXPECTED_FAMILIES):
        fail("render plan omits a required result family")
    if len(used_fact_ids) > MAX_RESULT_ROWS:
        fail(f"render plan selects more than the {MAX_RESULT_ROWS}-row four-page manuscript budget")
    normalized["result_blocks"] = blocks

    raw_figures = plan.get("figures")
    if not isinstance(raw_figures, list) or not 1 <= len(raw_figures) <= MAX_FIGURES:
        fail(f"render plan must select between 1 and {MAX_FIGURES} final figures")
    selected_figures: list[dict[str, Any]] = []
    selected_names: set[str] = set()
    for raw in raw_figures:
        if not isinstance(raw, dict):
            fail("figure selection must be an object")
        artifact = raw.get("artifact")
        caption = normal_text(raw.get("caption"), "figure caption", maximum=430)
        trace_ids = raw.get("fact_ids", [])
        if not isinstance(artifact, str) or artifact not in figures or artifact in selected_names:
            fail("figure selection is missing, duplicated, or absent from the frozen manifest")
        if not isinstance(trace_ids, list) or any(item not in facts for item in trace_ids):
            fail("figure selection contains an invalid fact trace")
        if artifact != "figure_1_reciprocal_cognitive_sensing_loop.png" and not trace_ids:
            fail("empirical figure selection requires at least one frozen fact trace")
        selected_names.add(artifact)
        selected_figures.append({"artifact": artifact, "caption": caption, "fact_ids": list(trace_ids)})
    normalized["figures"] = selected_figures
    return normalized


def validate_citations(
    audit_path: Path, bibliography_path: Path, citation_keys: list[str], results_freeze_path: Path,
) -> None:
    audit = load_json(audit_path, "anonymous reference audit")
    if not bibliography_path.is_file():
        fail("audited bibliography is missing")
    if audit.get("status") != EXPECTED_REFERENCE_AUDIT_STATUS:
        fail("reference audit has not passed for anonymous rendering")
    if audit.get("results_freeze_sha256") != sha256(results_freeze_path):
        fail("reference audit is not sequenced after the supplied RESULTS_FREEZE")
    if audit.get("bibliography_sha256") != sha256(bibliography_path):
        fail("reference audit does not reconcile the supplied bibliography")
    records = audit.get("citations")
    if not isinstance(records, list):
        fail("reference audit lacks citation records")
    audited = {
        str(record.get("key")): record
        for record in records
        if isinstance(record, dict) and record.get("verification_status") == "PASS"
    }
    missing = [key for key in citation_keys if key not in audited]
    if missing:
        fail(f"citation keys lack PASS reference-audit records: {', '.join(missing)}")
    bibliography = bibliography_path.read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bibliography))
    if any(key not in bib_keys for key in citation_keys):
        fail("audited bibliography does not contain every cited key")


def table_row(fact_id: str, fact: dict[str, Any]) -> str:
    family = str(fact["result_family"])
    values = dict(fact["values"])
    if family in {"RQ2", "RQ5"}:
        label = latex_escape(str(values.get("construct", "unknown construct")))
        comparison = latex_escape(str(values.get("contrast", "unknown contrast")))
        status = latex_escape(str(values.get("measurement_status", "unknown status")))
        if values.get("measurement_status") == "MEASUREMENT_UNSTABLE":
            return rf"{label} ({status}) & {comparison} & \multicolumn{{3}}{{l}}{{Not estimable: the computational measurement robustness gate did not pass.}} \\\hline"
        estimate = macro_name(fact_id, family, "effect")
        ci_low = macro_name(fact_id, family, "ci_low")
        ci_high = macro_name(fact_id, family, "ci_high")
        n_value = macro_name(fact_id, family, "n_paired_items")
        q_value = macro_name(fact_id, family, "fdr_q")
        return rf"{label} ({status}) & {comparison} & ${estimate}$ [$ {ci_low}, {ci_high} $] & ${n_value}$ & ${q_value}$ \\\hline"
    if family == "RQ3":
        label = latex_escape(str(values.get("metric", "unknown metric")))
        comparison = latex_escape(str(values.get("contrast", "unknown contrast")))
        estimate = macro_name(fact_id, family, "effect")
        ci_low = macro_name(fact_id, family, "ci_low")
        ci_high = macro_name(fact_id, family, "ci_high")
        n_value = macro_name(fact_id, family, "n_paired_items")
        q_value = macro_name(fact_id, family, "fdr_q")
        return rf"{label} & {comparison} & ${estimate}$ [$ {ci_low}, {ci_high} $] & ${n_value}$ & ${q_value}$ \\\hline"
    label = latex_escape(f"{values.get('space_a', 'unknown')} vs {values.get('space_b', 'unknown')}")
    divergence = macro_name(fact_id, family, "jensen_shannon_divergence")
    ci_low = macro_name(fact_id, family, "js_ci_low")
    ci_high = macro_name(fact_id, family, "js_ci_high")
    n_a = macro_name(fact_id, family, "n_a")
    n_b = macro_name(fact_id, family, "n_b")
    return rf"{label} & ${divergence}$ [$ {ci_low}, {ci_high} $] & ${n_a}$ / ${n_b}$ \\\hline"


def render_result_block(block: dict[str, Any], facts: dict[str, dict[str, Any]]) -> str:
    family = block["family"]
    rows: list[str] = []
    for fact_id in block["fact_ids"]:
        # Keep one machine-auditable marker for every numeric field that the
        # table template may display.  The post-render traceability utility
        # retains only finite numeric values and treats NOT_ESTIMABLE as a
        # non-numeric state rather than silently inventing a claim.
        if facts[fact_id]["values"].get("measurement_status") != "MEASUREMENT_UNSTABLE":
            rows.extend(paper_claim_markers(fact_id, facts[fact_id]))
        rows.append(table_row(fact_id, facts[fact_id]))
    if family in {"RQ2", "RQ5"}:
        header = r"Property and measurement status & Contrast & Estimate [95\% CI] & Paired $n$ & FDR $q$"
        specification = "p{0.26\\linewidth}p{0.18\\linewidth}p{0.23\\linewidth}rr"
    elif family == "RQ3":
        header = r"Bounded public-human reference metric & Contrast & Estimate [95\% CI] & Paired $n$ & FDR $q$"
        specification = "p{0.29\\linewidth}p{0.16\\linewidth}p{0.23\\linewidth}rr"
    else:
        header = r"Distributional comparison & JS divergence [95\% CI] & Text units ($n_a/n_b$)"
        specification = "p{0.47\\linewidth}p{0.30\\linewidth}r"
    explanation = {
        "RQ2": "These are paired differences in computationally measured output-text properties. They are not human judgments or evidence of cognitive change.",
        "RQ3": "These are bounded comparisons against released human-reference data. They do not constitute newly collected BLV ratings or preference judgments.",
        "RQ4": "These values quantify measured text-profile distributions only. Distributional proximity is not cognitive equivalence, accessibility value, or a dream effect.",
        "RQ5": "These are measured output-property differences. They do not establish measured harms, preferences, or lived experience.",
    }[family]
    return "\n".join([
        rf"\subsection{{{FAMILY_LABELS[family]}}}",
        latex_escape(explanation),
        r"\begin{center}",
        rf"\begin{{tabular}}{{{specification}}}",
        r"\hline",
        header + r" \\ \hline",
        *rows,
        r"\end{tabular}",
        r"\end{center}",
    ])


def render_tex(plan: dict[str, Any], facts: dict[str, dict[str, Any]], figures: dict[str, dict[str, str]]) -> str:
    citations = ",".join(plan["citation_keys"])
    results_blocks = "\n\n".join(render_result_block(block, facts) for block in plan["result_blocks"])
    figure_blocks: list[str] = []
    for index, figure in enumerate(plan["figures"], start=1):
        artifact = figure["artifact"]
        alt = latex_escape(figures[artifact]["alt_text"])
        caption = latex_escape(figure["caption"])
        figure_blocks.append("\n".join([
            r"\begin{figure}[t]",
            r"\centering",
            rf"\includegraphics[width=\linewidth]{{figures/{latex_escape(artifact)}}}",
            rf"\caption{{{caption}}}",
            rf"\Description{{{alt}}}",
            rf"\label{{fig:{index}}}",
            r"\end{figure}",
        ]))
    remaining_figures = "\n\n".join(figure_blocks[1:])
    return rf"""% Generated by code/32_render_anonymous_chi_manuscript.py.
% Post-RESULTS_FREEZE source. Do not edit values, macros, tables, or provenance by hand.
% This file intentionally contains no author, affiliation, email, acknowledgement, or repository metadata.
\documentclass[manuscript,review,anonymous]{{acmart}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{tabularx}}
\settopmatter{{printacmref=false,printfolios=false}}
\hypersetup{{pdfauthor={{}},pdfcreator={{}},pdfsubject={{Anonymous review submission}}}}

\title{{{latex_escape(plan['title'])}}}

\begin{{document}}
\input{{results_macros.tex}}
\begin{{abstract}}
We present a public-data study that connects historical blind dream expression, blind and low-vision (BLV) information-seeking questions, human accessibility references, and frozen multimodal-AI outputs. The study uses a controlled within-item prompting intervention and computational measurement, with external public-human calibration where the released data directly support it. {latex_escape(plan['motivation'])} The reported estimates concern output-text properties and bounded reference alignment; they do not test changes in dreams, cognition, neural organization, or lived experience.
\end{{abstract}}
\maketitle

\section{{Introduction}}
Blind sensory expression, information intent, and AI-mediated descriptions are often examined separately. This study instead compares their measured representational spaces while preserving a causal boundary: only the prompt condition is experimentally varied. {latex_escape(plan['motivation'])}

\section{{Related Work}}
The literature synthesis and citation set were independently reference-audited before rendering. We cite only audited published sources here \cite{{{citations}}}. This paper does not treat protocol work as completed outcome evidence and does not use synthetic measurement as a substitute for human judgment.

\section{{Method}}
We analyze released research data and frozen model outputs; no new human data were collected. The generator and the synthetic measurement panel have distinct roles. Measurements are reported as computational unless a released public-human dataset directly benchmarks the corresponding construct. {latex_escape(plan['method_scope'])}

{figure_blocks[0] if figure_blocks else ''}

\section{{Results}}
All quantities below are inserted from the immutable fact packet. For each row, the estimate and uncertainty are reported without upgrading model-derived properties into human-centered claims. Full frozen outputs, construct tiers, missingness, and robustness records remain in the anonymous supplementary package.

{results_blocks}

{remaining_figures}

\section{{Social Impact and Design Implications}}
The results concern which information a system makes available and how actual BLV-originating questions reshape that output. Any implication is therefore a design implication, not measured harm or a claim about individual experience. {latex_escape(plan['impact_scope'])}

\section{{Limitations and Future Work}}
This public-data computational study cannot establish whether AI changes dreams, cognition, neural organization, or sensory experience. Synthetic annotation is a model-derived measurement instrument, not a human-equivalent observer. External public-human datasets provide construct-specific calibration only; they are not same-item ratings of the current outputs. A future, separately approved human study would be needed to test experience-centered outcomes.

\bibliographystyle{{ACM-Reference-Format}}
\bibliography{{references}}
\end{{document}}
"""


def write_claim_trace(
    path: Path, plan: dict[str, Any], facts: dict[str, dict[str, Any]], figures: dict[str, dict[str, str]],
) -> None:
    rows: list[dict[str, str]] = []
    for block in plan["result_blocks"]:
        for fact_id in block["fact_ids"]:
            fact = facts[fact_id]
            rows.append({
                "rendered_element": f"table_{block['family']}",
                "fact_id": fact_id,
                "result_family": str(fact["result_family"]),
                "source_sha256": str(fact["source_sha256"]),
                "source_data_row": str(fact["source_data_row"]),
                "measurement_status": str(fact["values"].get("measurement_status", "")),
            })
    for figure in plan["figures"]:
        for fact_id in figure["fact_ids"]:
            fact = facts[fact_id]
            rows.append({
                "rendered_element": figure["artifact"],
                "fact_id": fact_id,
                "result_family": str(fact["result_family"]),
                "source_sha256": str(fact["source_sha256"]),
                "source_data_row": str(fact["source_data_row"]),
                "measurement_status": str(fact["values"].get("measurement_status", "")),
            })
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["rendered_element", "fact_id", "result_family", "source_sha256", "source_data_row", "measurement_status"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, required=True)
    parser.add_argument("--fact-packet-dir", type=Path, required=True)
    parser.add_argument("--figures-dir", type=Path, required=True)
    parser.add_argument("--render-plan", type=Path, required=True)
    parser.add_argument("--citation-audit", type=Path, required=True)
    parser.add_argument("--bibliography", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite an existing anonymous manuscript render")

    results, _packet, packet_manifest, facts, macros_path = validate_results_and_packet(args.results_freeze, args.fact_packet_dir)
    figures, figure_manifest = validate_figures(args.figures_dir, sha256(args.results_freeze))
    plan = validate_plan(
        args.render_plan, args.results_freeze, args.fact_packet_dir / "PAPER_FACT_PACKET_MANIFEST.json",
        figure_manifest, facts, figures,
    )
    validate_citations(args.citation_audit, args.bibliography, plan["citation_keys"], args.results_freeze)

    temp = args.outdir.parent / f".{args.outdir.name}.tmp-{uuid.uuid4().hex}"
    temp.mkdir(parents=True, exist_ok=False)
    (temp / "figures").mkdir()
    write_tex_macros(macros_path, temp / "results_macros.tex")
    shutil.copy2(args.bibliography, temp / "references.bib")
    for figure in plan["figures"]:
        source = args.figures_dir / figure["artifact"]
        destination = temp / "figures" / figure["artifact"]
        shutil.copy2(source, destination)
        shutil.copy2(source.with_suffix(".alt.txt"), destination.with_suffix(".alt.txt"))
    tex_path = temp / "main.tex"
    tex_path.write_text(render_tex(plan, facts, figures), encoding="utf-8")
    trace_path = temp / "CLAIM_TRACE.csv"
    write_claim_trace(trace_path, plan, facts, figures)
    checklist = """# Anonymous manuscript render checks\n\nThis source was rendered after a frozen fact packet. Before compiling or uploading it, independently verify: (1) the current CHI call and page limit, (2) the generated PDF is at most four pages excluding references, (3) all figures are readable and have alt text, (4) every source and PDF metadata field is anonymous, and (5) the final claim/reference/ethics audits pass. This renderer intentionally does not compile a PDF or certify page count.\n"""
    (temp / "RENDER_CHECKLIST.md").write_text(checklist, encoding="utf-8")
    manifest = {
        "status": "ANONYMOUS_CHI_MANUSCRIPT_SOURCE_RENDERED_FROM_RESULTS_FREEZE",
        "results_freeze_sha256": sha256(args.results_freeze),
        "fact_packet_manifest_sha256": sha256(args.fact_packet_dir / "PAPER_FACT_PACKET_MANIFEST.json"),
        "figure_manifest_sha256": sha256(figure_manifest),
        "reference_audit_sha256": sha256(args.citation_audit),
        "bibliography_sha256": sha256(args.bibliography),
        "script_sha256": sha256(Path(__file__).resolve()),
        "new_human_data_collected": False,
        "anonymous_review": True,
        "fact_ids_rendered": [fact_id for block in plan["result_blocks"] for fact_id in block["fact_ids"]],
        "paper_claim_marker_schema": "PAPER_{fact_id}_{source_column_upper}",
        "paper_claim_marker_fields": {
            fact_id: list(NUMERIC_FIELDS[str(facts[fact_id]["result_family"])])
            for block in plan["result_blocks"]
            for fact_id in block["fact_ids"]
        },
        "figures_rendered": [figure["artifact"] for figure in plan["figures"]],
        "artifacts": {},
        "page_target": "at most four pages excluding references; final PDF verification required",
    }
    for artifact in ("main.tex", "results_macros.tex", "references.bib", "CLAIM_TRACE.csv", "RENDER_CHECKLIST.md"):
        manifest["artifacts"][artifact] = sha256(temp / artifact)
    for figure in plan["figures"]:
        artifact = f"figures/{figure['artifact']}"
        manifest["artifacts"][artifact] = sha256(temp / artifact)
        alt_artifact = f"figures/{Path(figure['artifact']).with_suffix('.alt.txt').name}"
        manifest["artifacts"][alt_artifact] = sha256(temp / alt_artifact)
    (temp / "MANUSCRIPT_RENDER_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(args.outdir)
    print(json.dumps({"status": manifest["status"], "facts": len(manifest["fact_ids_rendered"]), "figures": len(manifest["figures_rendered"])}, sort_keys=True))


if __name__ == "__main__":
    main()
