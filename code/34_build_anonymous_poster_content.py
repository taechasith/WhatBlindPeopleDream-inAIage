"""Build a deterministic anonymous A0 poster-content plan after RESULTS_FREEZE.

This post-results utility resolves only predeclared semantic keys against the
immutable paper fact packet.  It does not read raw outputs, the private
condition mapping, or any source table.  It never ranks or selects facts using
effect estimates, confidence intervals, p values, FDR values, directions, or
apparent favorability.

The resulting ``POSTER_CONTENT.json`` is the sole content input expected by
``code/31_generate_anonymous_a0_poster.py``.  Its factual display is bounded:
figures carry frozen estimates while the text retains measurement status,
analysis status, public-human-reference boundaries, and causal limitations.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import uuid
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "config" / "poster_content_policy_v1.json"
EXPECTED_RESULTS_STATUS = "RESULTS_FROZEN_PUBLIC_DATA_ONLY"
EXPECTED_PACKET_STATUS = "PAPER_FACT_PACKET_FROM_RESULTS_FREEZE"
EXPECTED_PACKET_MANIFEST_STATUS = "PAPER_FACT_PACKET_FROZEN_FROM_RESULTS_FREEZE"
EXPECTED_FAMILIES = ("RQ2", "RQ3", "RQ4", "RQ5")
# The fact packet also retains two RQ4 provenance-only families.  They are not
# selectable poster result blocks, but must be accepted when verifying the
# complete immutable packet generated from RESULTS_FREEZE.
PACKET_FACT_FAMILIES = EXPECTED_FAMILIES + ("RQ4_profiles", "RQ4_association_status")

# These terms cannot appear in a selection rule.  Result values may be shown
# only in the frozen figures; this content planner selects semantic anchors
# before looking at any estimate-like field.
FORBIDDEN_SELECTION_TERMS = {
    "effect", "effect_size", "ci", "ci_low", "ci_high", "p", "p_value",
    "permutation_p", "fdr", "fdr_q", "significance", "significant", "direction",
    "output_change_direction", "largest", "smallest", "rank", "ranking",
    "favorable", "favourable", "absolute_effect",
}

PENDING_TEXT = re.compile(r"\b(?:tbd|todo|placeholder|results[ -]?pending|replace[_ -]?with)\b", re.IGNORECASE)
REVIEW_ID_PATTERNS = (
    re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:https?://|www\.|mailto:|github\.com|orcid\.org)\b", re.IGNORECASE),
    re.compile(r"\b(?:affiliation|corresponding author|contact author|university|utcc|creativelab)\b", re.IGNORECASE),
    re.compile(r"\b(?:taechasith|kangkhuntod|natch|prawatwong)\b", re.IGNORECASE),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"POSTER_CONTENT_PLAN_FAILED: {message}")


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        fail(f"required {label} is unavailable: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot parse {label}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{label} must be a JSON object")
    return payload


def clean_text(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str):
        fail(f"{label} must be text")
    text = " ".join(value.split())
    if not text or len(text) > maximum:
        fail(f"{label} is empty or exceeds its {maximum}-character budget")
    if PENDING_TEXT.search(text):
        fail(f"{label} contains a pending or placeholder marker")
    for pattern in REVIEW_ID_PATTERNS:
        if pattern.search(text):
            fail(f"{label} contains author-identifying, affiliation, contact, or external-link text")
    return text


def clean_text_list(value: object, label: str, *, minimum: int, maximum: int, item_limit: int) -> list[str]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        fail(f"{label} must have between {minimum} and {maximum} entries")
    result = [clean_text(item, f"{label}[{index}]", item_limit) for index, item in enumerate(value)]
    if len(set(result)) != len(result):
        fail(f"{label} contains duplicate text")
    return result


def require_packet(results_freeze: Path, fact_packet_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    results = load_json(results_freeze, "RESULTS_FREEZE")
    if results.get("status") != EXPECTED_RESULTS_STATUS:
        fail("RESULTS_FREEZE is not a frozen public-data receipt")
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
    if packet.get("status") != EXPECTED_PACKET_STATUS or manifest.get("status") != EXPECTED_PACKET_MANIFEST_STATUS:
        fail("paper fact packet or its manifest has an unexpected status")
    results_hash = sha256(results_freeze)
    if packet.get("source_results_freeze_sha256") != results_hash or manifest.get("source_results_freeze_sha256") != results_hash:
        fail("paper fact packet is not tied to the supplied RESULTS_FREEZE")
    for artifact, label in ((packet_path, "fact packet"), (csv_path, "fact CSV"), (macros_path, "numeric macro file")):
        if not artifact.is_file() or manifest.get("artifacts", {}).get(artifact.name) != sha256(artifact):
            fail(f"{label} is missing or differs from its immutable packet manifest")

    raw_facts = packet.get("facts")
    if not isinstance(raw_facts, list) or not raw_facts or packet.get("fact_count") != len(raw_facts):
        fail("paper fact packet has no reconcilable facts")
    facts: dict[str, dict[str, Any]] = {}
    for fact in raw_facts:
        if not isinstance(fact, dict):
            fail("paper fact packet contains a malformed fact")
        fact_id = fact.get("fact_id")
        family = fact.get("result_family")
        values = fact.get("values")
        if not isinstance(fact_id, str) or not re.fullmatch(
            r"(?:RQ[2345]|RQ4_profiles|RQ4_association_status)_\d{4}", fact_id
        ):
            fail("paper fact packet contains an invalid fact ID")
        if family not in PACKET_FACT_FAMILIES or fact_id in facts or not isinstance(values, dict):
            fail("paper fact packet contains duplicate or malformed fact provenance")
        facts[fact_id] = fact
    return results, packet, manifest, facts


def require_figure_manifest(figures_dir: Path, required_figures: list[str]) -> Path:
    manifest_path = figures_dir / "FIGURE_MANIFEST.csv"
    if not figures_dir.is_dir() or not manifest_path.is_file():
        fail("final figure directory or FIGURE_MANIFEST.csv is unavailable")
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or set(rows[0]) != {"artifact", "sha256", "alt_text"}:
        fail("FIGURE_MANIFEST.csv has an unexpected schema")
    manifest = {str(row["artifact"]): row for row in rows}
    if len(manifest) != len(rows):
        fail("FIGURE_MANIFEST.csv contains duplicate artifacts")
    for artifact in required_figures:
        row = manifest.get(artifact)
        image = figures_dir / artifact
        alt = image.with_suffix(".alt.txt")
        if row is None or not image.is_file() or str(row.get("sha256", "")) != sha256(image):
            fail(f"required final figure differs from its manifest: {artifact}")
        if not alt.is_file() or not alt.read_text(encoding="utf-8").strip():
            fail(f"required final figure lacks alt text: {artifact}")
    return manifest_path


def validate_policy(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema_version") != 1 or payload.get("status") != "FROZEN_PRE_RESULTS_POSTER_CONTENT_POLICY":
        fail("poster-content policy has an unexpected schema version or status")
    if payload.get("review_stage") != "ANONYMOUS_REVIEW":
        fail("poster-content policy is not configured for anonymous review")
    normalized: dict[str, Any] = {
        "policy_id": clean_text(payload.get("policy_id"), "policy_id", 120),
        "selection_principle": clean_text(payload.get("selection_principle"), "selection_principle", 500),
        "title": clean_text(payload.get("title"), "title", 190),
        "subtitle": clean_text(payload.get("subtitle"), "subtitle", 280),
        "sample_summary_template": clean_text(payload.get("sample_summary_template"), "sample_summary_template", 220),
        "methods": clean_text_list(payload.get("methods"), "methods", minimum=2, maximum=5, item_limit=240),
        "implications": clean_text_list(payload.get("implications"), "implications", minimum=1, maximum=4, item_limit=260),
        "limitations": clean_text_list(payload.get("limitations"), "limitations", minimum=2, maximum=5, item_limit=260),
        "ethics_note": clean_text(payload.get("ethics_note"), "ethics_note", 300),
        "discussion_points": clean_text_list(payload.get("discussion_points"), "discussion_points", minimum=2, maximum=5, item_limit=230),
    }
    design = payload.get("design_anchor")
    if not isinstance(design, dict):
        fail("poster-content policy lacks a fixed design_anchor")
    try:
        locked_items = int(design.get("locked_items"))
        prompt_conditions = int(design.get("prompt_conditions"))
        frozen_judge_count = int(design.get("frozen_judge_count"))
    except (TypeError, ValueError) as exc:
        raise ValueError("POSTER_CONTENT_PLAN_FAILED: design_anchor must contain integer counts") from exc
    if locked_items <= 0 or prompt_conditions < 2 or frozen_judge_count < 2:
        fail("design_anchor has invalid locked-item, condition, or judge counts")
    for placeholder in ("{locked_items}", "{prompt_conditions}", "{frozen_judge_count}"):
        if placeholder not in normalized["sample_summary_template"]:
            fail(f"sample_summary_template must include {placeholder}")
    normalized["design_anchor"] = {
        "locked_items": locked_items,
        "prompt_conditions": prompt_conditions,
        "frozen_judge_count": frozen_judge_count,
    }
    policy_keys = set(payload)
    forbidden_top = policy_keys.intersection(FORBIDDEN_SELECTION_TERMS)
    if forbidden_top:
        fail(f"policy illegally exposes result-driven selection fields: {', '.join(sorted(forbidden_top))}")

    blocks = payload.get("selection_blocks")
    if not isinstance(blocks, list) or len(blocks) != len(EXPECTED_FAMILIES):
        fail("policy must have exactly one selection block for each RQ2--RQ5 family")
    if {block.get("family") for block in blocks if isinstance(block, dict)} != set(EXPECTED_FAMILIES):
        fail("policy omits or duplicates a research-question family")
    for block in blocks:
        if not isinstance(block, dict):
            fail("selection block must be an object")
        forbidden = set(block).intersection(FORBIDDEN_SELECTION_TERMS)
        if forbidden:
            fail(f"selection block illegally uses result-driven fields: {', '.join(sorted(forbidden))}")
        block["rationale"] = clean_text(block.get("rationale"), f"{block.get('family', 'unknown')} rationale", 360)
    normalized["selection_blocks"] = blocks

    required_figures = payload.get("required_figures")
    if not isinstance(required_figures, list) or len(required_figures) != 5:
        fail("policy must list the five required anonymous A0 figures")
    if any(not isinstance(artifact, str) or not artifact.endswith(".svg") for artifact in required_figures) or len(set(required_figures)) != len(required_figures):
        fail("policy required_figures must be unique SVG artifact names")
    normalized["required_figures"] = list(required_figures)
    return normalized


def fact_value(fact: dict[str, Any], field: str) -> str:
    return str(dict(fact["values"]).get(field, ""))


def select_exact(candidates: list[dict[str, Any]], description: str) -> dict[str, Any]:
    if len(candidates) != 1:
        fail(f"semantic selector requires exactly one {description}; found {len(candidates)}")
    return candidates[0]


def select_block(facts: dict[str, dict[str, Any]], block: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Resolve semantic keys without accessing estimate, p, CI, FDR, or direction fields."""
    family = str(block["family"])
    candidates = [fact for fact in facts.values() if fact["result_family"] == family]
    selection_type = block.get("selection_type")
    selected: list[dict[str, Any]] = []
    traces: list[dict[str, str]] = []
    if selection_type == "paired_judge_construct":
        constructs = block.get("constructs")
        judges = block.get("judges")
        contrast = block.get("contrast")
        if not isinstance(constructs, list) or not isinstance(judges, list) or not isinstance(contrast, str):
            fail(f"{family} paired-judge selector is malformed")
        if len(set(constructs)) != len(constructs) or len(set(judges)) != len(judges) or len(judges) < 2:
            fail(f"{family} paired-judge selector must list unique constructs and at least two judges")
        for construct in constructs:
            if not isinstance(construct, str) or not construct:
                fail(f"{family} paired-judge selector has an invalid construct")
            for judge in judges:
                match = [
                    fact for fact in candidates
                    if fact_value(fact, "construct") == construct
                    and fact_value(fact, "contrast") == contrast
                    and fact_value(fact, "judge_id") == judge
                ]
                selected.append(select_exact(match, f"{family} construct={construct}; contrast={contrast}; judge={judge}"))
                traces.append({"family": family, "selection_type": str(selection_type), "semantic_key": f"construct={construct}; contrast={contrast}; judge={judge}"})
    elif selection_type == "reference_metric":
        metrics = block.get("metrics")
        contrast = block.get("contrast")
        if not isinstance(metrics, list) or not isinstance(contrast, str) or len(set(metrics)) != len(metrics):
            fail(f"{family} reference-metric selector is malformed")
        for metric in metrics:
            match = [fact for fact in candidates if fact_value(fact, "metric") == metric and fact_value(fact, "contrast") == contrast]
            selected.append(select_exact(match, f"{family} metric={metric}; contrast={contrast}"))
            traces.append({"family": family, "selection_type": str(selection_type), "semantic_key": f"metric={metric}; contrast={contrast}"})
    elif selection_type == "unordered_space_pair":
        pairs = block.get("space_pairs")
        if not isinstance(pairs, list):
            fail(f"{family} space-pair selector is malformed")
        for pair in pairs:
            if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(value, str) and value for value in pair):
                fail(f"{family} has an invalid space-pair selector")
            key = frozenset(pair)
            if len(key) != 2:
                fail(f"{family} space-pair selector repeats a space")
            match = [fact for fact in candidates if frozenset((fact_value(fact, "space_a"), fact_value(fact, "space_b"))) == key]
            selected.append(select_exact(match, f"{family} space_pair={'|'.join(sorted(key))}"))
            traces.append({"family": family, "selection_type": str(selection_type), "semantic_key": f"space_pair={'|'.join(pair)}"})
    else:
        fail(f"{family} has an unsupported semantic selector")
    if len({str(fact["fact_id"]) for fact in selected}) != len(selected):
        fail(f"{family} semantic selector selected a fact more than once")
    for trace, fact in zip(traces, selected):
        trace.update({
            "fact_id": str(fact["fact_id"]),
            "candidate_count": "1",
            "source_sha256": str(fact.get("source_sha256", "")),
            "source_data_row": str(fact.get("source_data_row", "")),
            "measurement_status": fact_value(fact, "measurement_status"),
            "analysis_status": fact_value(fact, "analysis_status"),
        })
    return selected, traces


def status_summary(selected: list[dict[str, Any]], *, include_measurement: bool = True) -> str:
    parts: list[str] = []
    if include_measurement:
        measurement = sorted({fact_value(fact, "measurement_status") for fact in selected if fact_value(fact, "measurement_status")})
        if measurement:
            parts.append("measurement=" + "/".join(measurement))
    analysis = sorted({fact_value(fact, "analysis_status") for fact in selected if fact_value(fact, "analysis_status")})
    if analysis:
        parts.append("analysis=" + "/".join(analysis))
    return "; ".join(parts) or "status=NOT_REPORTED"


def make_findings(blocks: dict[str, list[dict[str, Any]]]) -> list[str]:
    # Resolve the policy-selected families before writing short poster copy.
    # Detailed construct statuses remain in the immutable provenance rationale.
    _rq2 = blocks["RQ2"]
    _rq3 = blocks["RQ3"]
    _rq4 = blocks["RQ4"]
    _rq5 = blocks["RQ5"]
    findings = [
        "RQ2: task-answer and spatial properties were preselected for the intent-versus-generic contrast; Figure 2 reports frozen computational estimates.",
        "RQ3: human-answer and caption overlap quantify bounded external human-reference alignment, not preference or ratings.",
        "RQ4: Dream/intent and human-caption/AI distances compare text profiles only, not cognition or accessibility value.",
        "RQ5: identity and social-intent inference are model-derived output properties, not measured harms or lived experience.",
    ]
    return [clean_text(item, f"generated finding {index}", 260) for index, item in enumerate(findings)]


def verify_content_anonymity(content: dict[str, Any]) -> None:
    strings = [content["title"], content["subtitle"], content["sample_summary"], content["ethics_note"]]
    strings.extend(content["discussion_points"])
    for section in ("methods", "findings", "implications", "limitations"):
        strings.extend(content["sections"][section])
    for index, value in enumerate(strings):
        clean_text(value, f"generated content string {index}", 300)


def write_rationale(
    policy: dict[str, Any], traces: list[dict[str, str]], results_hash: str,
    packet_manifest_hash: str, figure_manifest_hash: str,
) -> str:
    lines = [
        "# Deterministic anonymous A0 poster-content rationale",
        "",
        "## Status",
        "",
        "This plan was generated only after immutable public-data results, a fact packet, and the final figure manifest were supplied. It is a selection-and-content artifact, not an analysis.",
        "",
        "## Fixed selection rule",
        "",
        policy["selection_principle"],
        "",
        "Every judged construct selected by this policy retains both predeclared frozen judges. The selector does not access effect estimates, confidence intervals, p values, FDR values, output-change directions, rankings, or favorability.",
        "",
        "## Provenance bindings",
        "",
        f"- RESULTS_FREEZE SHA-256: `{results_hash}`",
        f"- fact-packet manifest SHA-256: `{packet_manifest_hash}`",
        f"- final figure manifest SHA-256: `{figure_manifest_hash}`",
        f"- policy ID: `{policy['policy_id']}`",
        "",
        "## Fact-level semantic trace",
        "",
        "| Family | Fact ID | Semantic key | Candidate count | Measurement status | Analysis status | Source table hash | Source row |",
        "| --- | --- | --- | ---: | --- | --- | --- | ---: |",
    ]
    for trace in traces:
        lines.append(
            f"| {trace['family']} | {trace['fact_id']} | {trace['semantic_key']} | {trace['candidate_count']} | {trace['measurement_status'] or 'N/A'} | {trace['analysis_status'] or 'N/A'} | `{trace['source_sha256']}` | {trace['source_data_row']} |"
        )
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "The content plan preserves computational measurement and released-human-reference boundaries. It does not claim that synthetic judges are human-equivalent, that released human references are same-item ratings, or that text-profile similarity establishes cognition, dream change, or lived accessibility value.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, required=True)
    parser.add_argument("--fact-packet-dir", type=Path, required=True)
    parser.add_argument("--figures-dir", type=Path, required=True)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite an immutable poster-content directory")

    _results, _packet, packet_manifest, facts = require_packet(args.results_freeze, args.fact_packet_dir)
    policy = validate_policy(load_json(args.policy, "poster-content policy"))
    figure_manifest = require_figure_manifest(args.figures_dir, policy["required_figures"])

    selected_by_family: dict[str, list[dict[str, Any]]] = {}
    traces: list[dict[str, str]] = []
    all_fact_ids: list[str] = []
    for block in policy["selection_blocks"]:
        selected, block_traces = select_block(facts, block)
        family = str(block["family"])
        selected_by_family[family] = selected
        traces.extend(block_traces)
        all_fact_ids.extend(str(fact["fact_id"]) for fact in selected)
    if len(set(all_fact_ids)) != len(all_fact_ids):
        fail("semantic policy selected a fact across more than one research-question block")

    selected_judges = {
        fact_value(fact, "judge_id")
        for family in ("RQ2", "RQ5")
        for fact in selected_by_family[family]
        if fact_value(fact, "judge_id")
    }
    if len(selected_judges) != policy["design_anchor"]["frozen_judge_count"]:
        fail("fixed semantic selection does not retain the policy's complete frozen-judge set")
    sample_summary = clean_text(
        policy["sample_summary_template"].format(**policy["design_anchor"]),
        "generated sample summary",
        220,
    )
    content = {
        "schema_version": 1,
        "review_stage": "ANONYMOUS_REVIEW",
        "results_freeze_sha256": sha256(args.results_freeze),
        "figure_manifest_sha256": sha256(figure_manifest),
        "title": policy["title"],
        "subtitle": policy["subtitle"],
        "sample_summary": sample_summary,
        "sections": {
            "methods": policy["methods"],
            "findings": make_findings(selected_by_family),
            "implications": policy["implications"],
            "limitations": policy["limitations"],
        },
        "ethics_note": policy["ethics_note"],
        "discussion_points": policy["discussion_points"],
        "result_trace_ids": all_fact_ids,
    }
    verify_content_anonymity(content)

    results_hash = sha256(args.results_freeze)
    packet_manifest_hash = sha256(args.fact_packet_dir / "PAPER_FACT_PACKET_MANIFEST.json")
    figure_manifest_hash = sha256(figure_manifest)
    rationale = write_rationale(policy, traces, results_hash, packet_manifest_hash, figure_manifest_hash)

    temp = args.outdir.parent / f".{args.outdir.name}.tmp-{uuid.uuid4().hex}"
    temp.mkdir(parents=True, exist_ok=False)
    content_path = temp / "POSTER_CONTENT.json"
    trace_path = temp / "POSTER_CONTENT_SELECTION_TRACE.csv"
    rationale_path = temp / "POSTER_CONTENT_RATIONALE.md"
    content_path.write_text(json.dumps(content, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with trace_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["family", "fact_id", "selection_type", "semantic_key", "candidate_count", "measurement_status", "analysis_status", "source_sha256", "source_data_row"],
        )
        writer.writeheader()
        writer.writerows(traces)
    rationale_path.write_text(rationale, encoding="utf-8")
    manifest_path = temp / "POSTER_CONTENT_MANIFEST.json"
    manifest = {
        "status": "ANONYMOUS_A0_POSTER_CONTENT_FROZEN_FROM_RESULTS_FREEZE",
        "review_stage": "ANONYMOUS_REVIEW",
        "new_human_data_collected": False,
        "selection_policy_id": policy["policy_id"],
        "selection_policy_sha256": sha256(args.policy),
        "results_freeze_sha256": results_hash,
        "fact_packet_manifest_sha256": packet_manifest_hash,
        "figure_manifest_sha256": figure_manifest_hash,
        "script_sha256": sha256(Path(__file__).resolve()),
        "selection_basis": "fixed semantic keys only; no effect, uncertainty, p value, FDR, direction, or ranking was used",
        "selected_fact_ids": all_fact_ids,
        "design_anchor": policy["design_anchor"],
        "required_figures": policy["required_figures"],
        "artifacts": {
            content_path.name: sha256(content_path),
            trace_path.name: sha256(trace_path),
            rationale_path.name: sha256(rationale_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(args.outdir)
    print(json.dumps({"status": manifest["status"], "facts": len(all_fact_ids), "locked_items": policy["design_anchor"]["locked_items"]}, sort_keys=True))


if __name__ == "__main__":
    main()
