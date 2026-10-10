"""Create a deterministic anonymous CHI manuscript render plan after RESULTS_FREEZE.

This program is intentionally downstream of RESULTS_FREEZE and the immutable
paper fact packet. It does not inspect raw outputs or choose findings based on
effect size, uncertainty, p values, FDR, direction, or apparent favorability.
Instead, it resolves a predeclared semantic-key policy against fact IDs in the
frozen packet, preserves both frozen judges for every selected judged construct,
and writes an anonymous render plan accepted by
``code/32_render_anonymous_chi_manuscript.py``.

The output is a publication-planning artifact, not a manuscript and not an
analysis. It must be run only after RESULTS_FREEZE, fact-packet creation, and
final figure generation. Citation keys remain subject to the later anonymous
reference audit performed before manuscript rendering.
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
DEFAULT_POLICY = ROOT / "config" / "manuscript_render_plan_policy_v1.json"
EXPECTED_RESULTS_STATUS = "RESULTS_FROZEN_PUBLIC_DATA_ONLY"
EXPECTED_PACKET_STATUS = "PAPER_FACT_PACKET_FROM_RESULTS_FREEZE"
EXPECTED_PACKET_MANIFEST_STATUS = "PAPER_FACT_PACKET_FROZEN_FROM_RESULTS_FREEZE"
EXPECTED_FAMILIES = ("RQ2", "RQ3", "RQ4", "RQ5")
FORBIDDEN_SELECTION_TERMS = {
    "effect", "effect_size", "ci", "ci_low", "ci_high", "p", "p_value",
    "permutation_p", "fdr", "fdr_q", "significance", "significant", "direction",
    "largest", "smallest", "rank", "ranking", "favorable", "favourable",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"MANUSCRIPT_RENDER_PLAN_FAILED: {message}")


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        fail(f"required {label} is unavailable: {path.name}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot parse {label}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{label} must be a JSON object")
    return payload


def require_text(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str):
        fail(f"policy {label} must be text")
    normalized = " ".join(value.split())
    if not normalized or len(normalized) > maximum:
        fail(f"policy {label} is missing or exceeds its character budget")
    if re.search(r"\b(?:todo|tbd|placeholder|replace[_ -]?with)\b", normalized, re.IGNORECASE):
        fail(f"policy {label} contains placeholder text")
    return normalized


def validate_results_and_packet(
    results_freeze_path: Path, fact_packet_dir: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
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
    if packet.get("status") != EXPECTED_PACKET_STATUS:
        fail("paper fact packet has an unexpected status")
    if manifest.get("status") != EXPECTED_PACKET_MANIFEST_STATUS:
        fail("paper fact-packet manifest has an unexpected status")
    freeze_hash = sha256(results_freeze_path)
    if packet.get("source_results_freeze_sha256") != freeze_hash or manifest.get("source_results_freeze_sha256") != freeze_hash:
        fail("paper fact packet is not tied to the supplied RESULTS_FREEZE")
    for artifact, label in ((packet_path, "paper fact packet"), (csv_path, "paper fact CSV"), (macros_path, "numeric macro file")):
        expected = manifest.get("artifacts", {}).get(artifact.name)
        if not isinstance(expected, str) or not artifact.is_file() or expected != sha256(artifact):
            fail(f"{label} does not match its immutable fact-packet manifest")

    raw_facts = packet.get("facts")
    if not isinstance(raw_facts, list) or not raw_facts:
        fail("paper fact packet contains no facts")
    facts: dict[str, dict[str, Any]] = {}
    for fact in raw_facts:
        if not isinstance(fact, dict):
            fail("paper fact packet contains a malformed fact")
        fact_id = fact.get("fact_id")
        family = fact.get("result_family")
        values = fact.get("values")
        if not isinstance(fact_id, str) or not re.fullmatch(r"RQ[2345]_\d{4}", fact_id):
            fail("paper fact packet contains an invalid fact identifier")
        if family not in EXPECTED_FAMILIES or fact_id in facts or not isinstance(values, dict):
            fail("paper fact packet has duplicate or malformed fact provenance")
        facts[fact_id] = fact
    if packet.get("fact_count") != len(facts):
        fail("paper fact packet fact count does not reconcile")
    return results, packet, manifest, facts


def validate_figures(figures_dir: Path) -> tuple[dict[str, dict[str, str]], Path]:
    manifest_path = figures_dir / "FIGURE_MANIFEST.csv"
    methods_path = figures_dir / "FIGURE_METHODS.md"
    if not figures_dir.is_dir() or not manifest_path.is_file() or not methods_path.is_file():
        fail("final figure directory is incomplete")
    with manifest_path.open("r", encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or set(rows[0]) != {"artifact", "sha256", "alt_text"}:
        fail("FIGURE_MANIFEST.csv has an unexpected schema")
    figures: dict[str, dict[str, str]] = {}
    for row in rows:
        artifact = str(row.get("artifact", ""))
        if not artifact.endswith(".png") or artifact in figures:
            continue
        image_path = figures_dir / artifact
        alt_path = image_path.with_suffix(".alt.txt")
        if not image_path.is_file() or sha256(image_path) != str(row.get("sha256", "")):
            fail(f"figure does not match its manifest: {artifact}")
        if not alt_path.is_file() or not alt_path.read_text(encoding="utf-8").strip():
            fail(f"figure lacks accessible alt text: {artifact}")
        figures[artifact] = {"sha256": str(row["sha256"]), "alt_text": str(row["alt_text"])}
    if not figures:
        fail("figure manifest has no verified PNG figures")
    return figures, manifest_path


def validate_policy(policy: dict[str, Any]) -> dict[str, Any]:
    if policy.get("schema_version") != 1 or policy.get("status") != "FROZEN_PRE_RESULTS_SELECTION_POLICY":
        fail("selection policy has an unexpected schema version or status")
    if policy.get("review_stage") != "ANONYMOUS_REVIEW":
        fail("selection policy is not configured for anonymous review")
    budget = policy.get("page_budget")
    if not isinstance(budget, dict):
        fail("selection policy lacks page_budget")
    try:
        max_rows = int(budget.get("max_result_rows"))
        max_figures = int(budget.get("max_figures"))
    except (TypeError, ValueError) as exc:
        raise ValueError("MANUSCRIPT_RENDER_PLAN_FAILED: page budget must use integers") from exc
    if max_rows < 4 or max_figures < 1:
        fail("selection policy has an unusable page budget")
    normalized = {
        "policy_id": require_text(policy.get("policy_id"), "policy_id", 120),
        "page_budget": {"target": require_text(budget.get("target"), "page_budget.target", 120), "max_result_rows": max_rows, "max_figures": max_figures, "selection_principle": require_text(budget.get("selection_principle"), "page_budget.selection_principle", 350)},
        "title": require_text(policy.get("title"), "title", 190),
        "motivation": require_text(policy.get("motivation"), "motivation", 700),
        "method_scope": require_text(policy.get("method_scope"), "method_scope", 700),
        "impact_scope": require_text(policy.get("impact_scope"), "impact_scope", 700),
    }
    citations = policy.get("citation_keys")
    if not isinstance(citations, list) or not citations:
        fail("selection policy lacks citation keys")
    if any(not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9:_-]+", key) for key in citations):
        fail("selection policy has invalid citation keys")
    if len(set(citations)) != len(citations):
        fail("selection policy has duplicate citation keys")
    normalized["citation_keys"] = list(citations)

    blocks = policy.get("selection_blocks")
    if not isinstance(blocks, list) or len(blocks) != len(EXPECTED_FAMILIES):
        fail("selection policy must contain exactly one block for each RQ2--RQ5 family")
    if {block.get("family") for block in blocks if isinstance(block, dict)} != set(EXPECTED_FAMILIES):
        fail("selection policy omits a result family or duplicates a family")
    for block in blocks:
        if not isinstance(block, dict):
            fail("selection policy block must be an object")
        if not isinstance(block.get("rationale"), str) or not " ".join(block["rationale"].split()):
            fail("each selection block needs a rationale")
        forbidden = set(block).intersection(FORBIDDEN_SELECTION_TERMS)
        if forbidden:
            fail(f"selection policy illegally uses result-driven fields: {', '.join(sorted(forbidden))}")
    normalized["selection_blocks"] = blocks

    figures = policy.get("figures")
    if not isinstance(figures, list) or not figures or len(figures) > max_figures:
        fail("selection policy violates its figure budget")
    seen_artifacts: set[str] = set()
    for figure in figures:
        if not isinstance(figure, dict):
            fail("figure rule must be an object")
        artifact = figure.get("artifact")
        families = figure.get("fact_families")
        if not isinstance(artifact, str) or not artifact.endswith(".png") or artifact in seen_artifacts:
            fail("figure rule contains an invalid or duplicate artifact")
        if not isinstance(families, list) or any(family not in EXPECTED_FAMILIES for family in families):
            fail("figure rule has an invalid fact-family trace")
        require_text(figure.get("caption"), "figure caption", 430)
        seen_artifacts.add(artifact)
    normalized["figures"] = figures
    return normalized


def select_exact(candidates: list[dict[str, Any]], descriptor: str) -> dict[str, Any]:
    if len(candidates) != 1:
        fail(f"semantic selection requires exactly one {descriptor}; found {len(candidates)}")
    return candidates[0]


def fact_value(fact: dict[str, Any], field: str) -> str:
    return str(dict(fact["values"]).get(field, ""))


def select_block(facts: dict[str, dict[str, Any]], block: dict[str, Any]) -> tuple[list[str], list[dict[str, str]]]:
    family = str(block["family"])
    source = [fact for fact in facts.values() if fact["result_family"] == family]
    kind = block.get("selection_type")
    selected: list[dict[str, Any]] = []
    traces: list[dict[str, str]] = []
    if kind == "paired_judge_construct":
        constructs = block.get("constructs")
        judges = block.get("judges")
        contrast = block.get("contrast")
        if not isinstance(constructs, list) or not isinstance(judges, list) or not isinstance(contrast, str):
            fail(f"{family} paired-judge selection rule is malformed")
        if len(set(constructs)) != len(constructs) or len(set(judges)) != len(judges) or len(judges) < 2:
            fail(f"{family} must specify unique constructs and at least two preserved judges")
        for construct in constructs:
            if not isinstance(construct, str) or not construct:
                fail(f"{family} has an invalid construct key")
            for judge in judges:
                matched = [
                    fact for fact in source
                    if fact_value(fact, "construct") == construct
                    and fact_value(fact, "contrast") == contrast
                    and fact_value(fact, "judge_id") == judge
                ]
                selected.append(select_exact(matched, f"{family} fact for construct={construct}, contrast={contrast}, judge={judge}"))
                traces.append({"semantic_key": f"construct={construct}; contrast={contrast}; judge={judge}", "selection_type": str(kind)})
    elif kind == "reference_metric":
        metrics = block.get("metrics")
        contrast = block.get("contrast")
        if not isinstance(metrics, list) or not isinstance(contrast, str) or len(set(metrics)) != len(metrics):
            fail(f"{family} reference-metric selection rule is malformed")
        for metric in metrics:
            matched = [fact for fact in source if fact_value(fact, "metric") == metric and fact_value(fact, "contrast") == contrast]
            selected.append(select_exact(matched, f"{family} fact for metric={metric}, contrast={contrast}"))
            traces.append({"semantic_key": f"metric={metric}; contrast={contrast}", "selection_type": str(kind)})
    elif kind == "unordered_space_pair":
        pairs = block.get("space_pairs")
        if not isinstance(pairs, list):
            fail(f"{family} space-pair selection rule is malformed")
        for pair in pairs:
            if not isinstance(pair, list) or len(pair) != 2 or not all(isinstance(value, str) and value for value in pair):
                fail(f"{family} has an invalid space-pair semantic key")
            pair_key = frozenset(pair)
            if len(pair_key) != 2:
                fail(f"{family} space-pair semantic key repeats a space")
            matched = [fact for fact in source if frozenset((fact_value(fact, "space_a"), fact_value(fact, "space_b"))) == pair_key]
            selected.append(select_exact(matched, f"{family} fact for space_pair={'|'.join(sorted(pair_key))}"))
            traces.append({"semantic_key": f"space_pair={'|'.join(pair)}", "selection_type": str(kind)})
    else:
        fail(f"{family} has an unsupported semantic selection type")
    fact_ids = [str(fact["fact_id"]) for fact in selected]
    if len(set(fact_ids)) != len(fact_ids):
        fail(f"{family} semantic policy selected a fact more than once")
    for trace, fact in zip(traces, selected):
        trace.update({
            "family": family,
            "fact_id": str(fact["fact_id"]),
            "candidate_count": "1",
            "source_sha256": str(fact.get("source_sha256", "")),
            "source_data_row": str(fact.get("source_data_row", "")),
        })
    return fact_ids, traces


def make_rationale(
    policy: dict[str, Any], selected_blocks: list[dict[str, Any]], traces: list[dict[str, str]],
    results_hash: str, packet_manifest_hash: str, figure_manifest_hash: str,
) -> str:
    lines = [
        "# Deterministic anonymous manuscript render-plan rationale",
        "",
        "## Status",
        "",
        "This plan was generated only after the immutable public-data RESULTS_FREEZE and paper fact packet were supplied. It is a selection and rendering-plan artifact, not an analysis or a manuscript.",
        "",
        "## Fixed selection rule",
        "",
        policy["page_budget"]["selection_principle"],
        "",
        f"The policy reserves at most {policy['page_budget']['max_result_rows']} displayed result rows and {policy['page_budget']['max_figures']} manuscript figures for the stated four-page target. Every selected judged construct includes both predeclared frozen judges; neither judge is removed because of its estimate or statistical result.",
        "",
        "## Provenance bindings",
        "",
        f"- RESULTS_FREEZE SHA-256: `{results_hash}`",
        f"- paper fact-packet manifest SHA-256: `{packet_manifest_hash}`",
        f"- final figure manifest SHA-256: `{figure_manifest_hash}`",
        f"- selection-policy ID: `{policy['policy_id']}`",
        "",
        "## Semantic selection blocks",
        "",
    ]
    for block in selected_blocks:
        lines.extend([
            f"### {block['family']}",
            "",
            str(block["rationale"]),
            "",
            f"Selected fact IDs: {', '.join(block['fact_ids'])}.",
            "",
        ])
    lines.extend([
        "## Fact-level trace",
        "",
        "The following IDs are resolved solely by the semantic keys below. This trace deliberately excludes estimates, intervals, p values, FDR values, directions, and rankings.",
        "",
        "| Family | Fact ID | Semantic key | Candidate count | Source table hash | Source row |",
        "| --- | --- | --- | ---: | --- | ---: |",
    ])
    for trace in traces:
        lines.append(f"| {trace['family']} | {trace['fact_id']} | {trace['semantic_key']} | {trace['candidate_count']} | `{trace['source_sha256']}` | {trace['source_data_row']} |")
    lines.extend([
        "",
        "## Citation and scope boundary",
        "",
        "The plan names predeclared citation keys only. The later anonymous reference audit must verify every key against the final bibliography before manuscript rendering. The rendered paper must retain the public-data scope: model-derived text measurements are not human judgments, and the study does not test changes in dreams, cognition, neural organization, or lived experience.",
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
        fail("refuse to overwrite an existing immutable render-plan directory")

    _results, _packet, packet_manifest, facts = validate_results_and_packet(args.results_freeze, args.fact_packet_dir)
    figures, figure_manifest_path = validate_figures(args.figures_dir)
    policy = validate_policy(load_json(args.policy, "render-plan selection policy"))

    selected_blocks: list[dict[str, Any]] = []
    traces: list[dict[str, str]] = []
    all_fact_ids: list[str] = []
    for block in policy["selection_blocks"]:
        fact_ids, block_traces = select_block(facts, block)
        selected_blocks.append({"family": str(block["family"]), "fact_ids": fact_ids, "rationale": str(block["rationale"])})
        traces.extend(block_traces)
        all_fact_ids.extend(fact_ids)
    if len(set(all_fact_ids)) != len(all_fact_ids):
        fail("semantic policy selected a fact across more than one result block")
    if len(all_fact_ids) > policy["page_budget"]["max_result_rows"]:
        fail("semantic policy exceeds the predeclared manuscript row budget")

    selected_figures: list[dict[str, Any]] = []
    for figure_rule in policy["figures"]:
        artifact = str(figure_rule["artifact"])
        if artifact not in figures:
            fail(f"predeclared figure is absent from the frozen manifest: {artifact}")
        trace_fact_ids: list[str] = []
        for family in figure_rule["fact_families"]:
            trace_fact_ids.extend(next(block["fact_ids"] for block in selected_blocks if block["family"] == family))
        selected_figures.append({
            "artifact": artifact,
            "caption": require_text(figure_rule["caption"], "figure caption", 430),
            "fact_ids": trace_fact_ids,
        })
    if len(selected_figures) > policy["page_budget"]["max_figures"]:
        fail("selected figures exceed the predeclared manuscript figure budget")

    results_hash = sha256(args.results_freeze)
    packet_manifest_hash = sha256(args.fact_packet_dir / "PAPER_FACT_PACKET_MANIFEST.json")
    figure_manifest_hash = sha256(figure_manifest_path)
    plan = {
        "schema_version": 1,
        "review_stage": "ANONYMOUS_REVIEW",
        "results_freeze_sha256": results_hash,
        "fact_packet_manifest_sha256": packet_manifest_hash,
        "figure_manifest_sha256": figure_manifest_hash,
        "selection_policy_sha256": sha256(args.policy),
        "render_plan_generator_sha256": sha256(Path(__file__).resolve()),
        "selection_basis": "fixed semantic keys only; no effect, uncertainty, p value, FDR, direction, or ranking was used",
        "title": policy["title"],
        "motivation": policy["motivation"],
        "method_scope": policy["method_scope"],
        "impact_scope": policy["impact_scope"],
        "citation_keys": policy["citation_keys"],
        "result_blocks": [{"family": block["family"], "fact_ids": block["fact_ids"]} for block in selected_blocks],
        "figures": selected_figures,
    }
    rationale = make_rationale(policy, selected_blocks, traces, results_hash, packet_manifest_hash, figure_manifest_hash)

    temp = args.outdir.parent / f".{args.outdir.name}.tmp-{uuid.uuid4().hex}"
    temp.mkdir(parents=True, exist_ok=False)
    plan_path = temp / "manuscript_render_plan.json"
    rationale_path = temp / "MANUSCRIPT_RENDER_PLAN_RATIONALE.md"
    trace_path = temp / "RENDER_PLAN_SELECTION_TRACE.csv"
    plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rationale_path.write_text(rationale, encoding="utf-8")
    with trace_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["family", "fact_id", "selection_type", "semantic_key", "candidate_count", "source_sha256", "source_data_row"])
        writer.writeheader()
        writer.writerows(traces)
    manifest = {
        "status": "ANONYMOUS_MANUSCRIPT_RENDER_PLAN_FROZEN_FROM_RESULTS_FREEZE",
        "selection_policy_id": policy["policy_id"],
        "selection_policy_sha256": sha256(args.policy),
        "results_freeze_sha256": results_hash,
        "fact_packet_manifest_sha256": packet_manifest_hash,
        "figure_manifest_sha256": figure_manifest_hash,
        "script_sha256": sha256(Path(__file__).resolve()),
        "new_human_data_collected": False,
        "anonymous_review": True,
        "selection_basis": "fixed semantic keys only; no effect, uncertainty, p value, FDR, direction, or ranking was used",
        "selected_fact_ids": all_fact_ids,
        "selected_figures": [figure["artifact"] for figure in selected_figures],
        "artifacts": {
            plan_path.name: sha256(plan_path),
            rationale_path.name: sha256(rationale_path),
            trace_path.name: sha256(trace_path),
        },
    }
    manifest_path = temp / "MANUSCRIPT_RENDER_PLAN_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(args.outdir)
    print(json.dumps({"status": manifest["status"], "facts": len(all_fact_ids), "figures": len(selected_figures)}, sort_keys=True))


if __name__ == "__main__":
    main()
