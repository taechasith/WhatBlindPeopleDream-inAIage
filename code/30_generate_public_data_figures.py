"""Generate accessible, data-driven figures only from frozen public-data results."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fail(message: str) -> None:
    raise ValueError(f"FIGURE_GENERATION_FAILED: {message}")


def save(figure: plt.Figure, stem: str, alt_text: str, outdir: Path, files: list[dict[str, str]]) -> None:
    for extension in ("png", "svg"):
        path = outdir / f"{stem}.{extension}"
        figure.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
        files.append({"artifact": path.name, "sha256": sha256(path), "alt_text": alt_text})
    (outdir / f"{stem}.alt.txt").write_text(alt_text + "\n", encoding="utf-8")
    plt.close(figure)


def require_frozen_table(freeze: dict[str, object], name: str, path: Path) -> None:
    table = dict(freeze.get("tables", {})).get(name)
    if not isinstance(table, dict) or not path.is_file():
        fail(f"results freeze does not commit required table: {name}")
    if str(table.get("sha256")) != sha256(path):
        fail(f"results table differs from the frozen ledger: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-freeze", type=Path, required=True)
    parser.add_argument("--post-freeze-analysis", type=Path, required=True)
    parser.add_argument("--space-analysis", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    if args.outdir.exists():
        fail("refuse to overwrite frozen figure directory")
    freeze = json.loads(args.results_freeze.read_text(encoding="utf-8"))
    if freeze.get("status") != "RESULTS_FROZEN_PUBLIC_DATA_ONLY":
        fail("results are not frozen")
    if freeze.get("figure_script_sha256") != sha256(Path(__file__).resolve()):
        fail("figure-generation script differs from its pre-unblinding commitment")
    rq2_path = args.post_freeze_analysis / "RQ2_results.csv"
    rq3_path = args.post_freeze_analysis / "RQ3_results.csv"
    rq5_path = args.post_freeze_analysis / "RQ5_results.csv"
    rq4_path = args.space_analysis / "RQ4_results.csv"
    for name, path in (("RQ2", rq2_path), ("RQ3", rq3_path), ("RQ5", rq5_path), ("RQ4", rq4_path)):
        require_frozen_table(freeze, name, path)
    rq2 = pd.read_csv(rq2_path)
    rq3 = pd.read_csv(rq3_path)
    rq5 = pd.read_csv(rq5_path)
    rq4 = pd.read_csv(rq4_path)
    for frame, name in ((rq2, "RQ2"), (rq3, "RQ3"), (rq4, "RQ4"), (rq5, "RQ5")):
        if frame.empty:
            fail(f"{name} results table is empty")
    args.outdir.mkdir(parents=True, exist_ok=False)
    files: list[dict[str, str]] = []

    # Figure 1: conceptual architecture, explicitly marking the noncausal boundary.
    figure, axis = plt.subplots(figsize=(12, 4.8))
    axis.set_axis_off()
    nodes = [(0.08, 0.68, "DreamSpace\nhistorical blind dream\nexpression"), (0.36, 0.68, "IntentSpace\nBLV-originating\nquestions"), (0.64, 0.68, "AISpace\nfrozen VLM outputs"), (0.90, 0.68, "Accessible\ninformation\nenvironment")]
    for x, y, label in nodes:
        axis.text(x, y, label, ha="center", va="center", fontsize=11, bbox={"boxstyle": "round,pad=0.5", "facecolor": "white", "edgecolor": "black"})
    for start, end in zip(nodes[1:], nodes[2:]):
        axis.annotate("", xy=(end[0] - 0.08, end[1]), xytext=(start[0] + 0.08, start[1]), arrowprops={"arrowstyle": "->", "lw": 1.5, "color": "black"})
    axis.annotate("compare distributions only", xy=(0.50, 0.52), ha="center", fontsize=10)
    axis.annotate("Hypothesis only: no cognitive or dream effect tested", xy=(0.74, 0.25), xytext=(0.43, 0.25), arrowprops={"arrowstyle": "->", "lw": 1.2, "linestyle": "dashed"}, ha="center", va="center", fontsize=10)
    save(figure, "figure_1_reciprocal_cognitive_sensing_loop", "Conceptual diagram. Historical dream-report expression, BLV-originating questions, frozen VLM outputs, and the accessible information environment are connected. The only causal intervention is user question and accessibility instruction changing VLM output; a dashed arrow explicitly labels cognition or dream change as untested.", args.outdir, files)

    # Figure 2: primary within-item synthetic-measurement effects.
    selected = rq2.loc[rq2.analysis_role == "CONFIRMATORY_COMPUTATIONAL"].copy()
    selected = selected.dropna(subset=["effect", "ci_low", "ci_high"])
    if selected.empty:
        figure, axis = plt.subplots(figsize=(10, 4))
        axis.set_axis_off()
        axis.text(
            0.5,
            0.55,
            "No estimable predeclared confirmatory\ncomputational measurement rows",
            ha="center",
            va="center",
            fontsize=15,
            bbox={"boxstyle": "round,pad=0.6", "facecolor": "white", "edgecolor": "black"},
        )
        axis.text(0.5, 0.25, "The frozen measurement-strength gate prevents plotting unstable or exploratory labels as primary effects.", ha="center", va="center", fontsize=10)
        save(figure, "figure_2_prompt_condition_effects", "A measurement-status figure stating that no estimable predeclared confirmatory computational measurement rows were available. It explicitly does not substitute unstable or exploratory labels.", args.outdir, files)
    else:
        selected["label"] = selected["construct"] + " | " + selected["judge_id"]
        labels = list(dict.fromkeys(selected.label.tolist()))
        figure, axes = plt.subplots(1, 2, figsize=(15, max(5, 0.42 * len(labels) + 2)), sharey=True)
        contrasts = ["intent_minus_generic", "accessibility_minus_intent"]
        for axis, contrast in zip(axes, contrasts):
            current = selected.loc[selected.contrast == contrast].set_index("label").reindex(labels)
            y = np.arange(len(labels))
            axis.axvline(0, color="black", linewidth=0.8)
            axis.errorbar(current.effect, y, xerr=[current.effect - current.ci_low, current.ci_high - current.effect], fmt="o", color="black", capsize=2)
            axis.set_title(contrast.replace("_", " "))
            axis.set_xlabel("Paired difference in label prevalence")
            axis.set_yticks(y, labels if axis is axes[0] else [])
            axis.grid(axis="x", linestyle=":", color="0.65")
        axes[0].invert_yaxis()
        save(figure, "figure_2_prompt_condition_effects", f"Within-item paired label-prevalence differences with 95% bootstrap intervals for {len(selected)} predeclared confirmatory computational judge-construct-contrast records. Zero indicates no estimated difference. Judges remain separate; this is computational measurement, not human judgment.", args.outdir, files)

    # Figure 3: bounded human-reference alignment.
    rq3 = rq3.dropna(subset=["effect", "ci_low", "ci_high"])
    if rq3.empty:
        fail("RQ3 has no estimable rows for the reference-alignment figure")
    figure, axis = plt.subplots(figsize=(10, 5))
    positions = np.arange(len(rq3))
    axis.axhline(0, color="black", linewidth=0.8)
    axis.errorbar(positions, rq3.effect, yerr=[rq3.effect - rq3.ci_low, rq3.ci_high - rq3.effect], fmt="s", color="black", capsize=3)
    axis.set_xticks(positions, [f"{row.metric}\n{row.contrast}" for row in rq3.itertuples()], rotation=20, ha="right")
    axis.set_ylabel("Paired difference in bounded reference alignment")
    axis.grid(axis="y", linestyle=":", color="0.65")
    save(figure, "figure_3_human_reference_alignment", f"Paired differences with 95% bootstrap intervals for {len(rq3)} bounded released-human-reference metrics. These metrics are answer-string coverage and maximum caption token F1; they are not BLV preference, usefulness, or human ratings.", args.outdir, files)

    # Figure 4: key distributional distances to DreamSpace, HumanSpace, and IntentSpace.
    ai_spaces = {"AI_GENERIC", "AI_INTENT_STEERED", "AI_ACCESSIBILITY_STEERED"}
    references = {"DREAM", "BLV_USER_QUESTION", "HUMAN_CAPTION"}
    current = rq4.loc[(rq4.space_a.isin(ai_spaces) & rq4.space_b.isin(references)) | (rq4.space_b.isin(ai_spaces) & rq4.space_a.isin(references))].copy()
    current = current.dropna(subset=["jensen_shannon_divergence", "js_ci_low", "js_ci_high"])
    if current.empty:
        fail("RQ4 has no estimable AI/reference distance rows")
    current["comparison"] = current.space_a + " vs " + current.space_b
    figure, axis = plt.subplots(figsize=(12, max(5, 0.38 * len(current) + 2)))
    y = np.arange(len(current))
    axis.errorbar(current.jensen_shannon_divergence, y, xerr=[current.jensen_shannon_divergence - current.js_ci_low, current.js_ci_high - current.jensen_shannon_divergence], fmt="D", color="black", capsize=2)
    axis.set_yticks(y, current.comparison)
    axis.set_xlabel("Jensen-Shannon divergence (lower = closer text-profile distribution)")
    axis.grid(axis="x", linestyle=":", color="0.65")
    axis.invert_yaxis()
    save(figure, "figure_4_representational_space_distances", f"Jensen-Shannon divergence and 95% bootstrap intervals for {len(current)} comparisons between AI condition text profiles and DreamSpace, IntentSpace, or HumanSpace. Lower distance is only textual distributional resemblance, not cognitive similarity or accessibility value.", args.outdir, files)

    # Figure 5: largest measured additions / omissions, all with construct status shown.
    current = rq5.loc[rq5.analysis_role != "MEASUREMENT_UNSTABLE_NOT_FOR_SUBSTANTIVE_CLAIMS"].copy()
    current = current.dropna(subset=["effect"])
    if current.empty:
        fail("RQ5 has no estimable output-property rows")
    current["absolute_effect"] = current.effect.abs()
    current = current.nlargest(min(12, len(current)), "absolute_effect").copy().sort_values("effect")
    current["label"] = current.construct + " | " + current.contrast + " | " + current.judge_id + " | " + current.analysis_role
    figure, axis = plt.subplots(figsize=(14, max(5, 0.4 * len(current) + 2)))
    colors = ["white" if value < 0 else "0.65" for value in current.effect]
    hatches = ["///" if value < 0 else "" for value in current.effect]
    bars = axis.barh(np.arange(len(current)), current.effect, color=colors, edgecolor="black")
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)
    axis.axvline(0, color="black", linewidth=0.8)
    axis.set_yticks(np.arange(len(current)), current.label)
    axis.set_xlabel("Paired difference in label prevalence")
    axis.grid(axis="x", linestyle=":", color="0.65")
    save(figure, "figure_5_largest_output_property_changes", f"The {len(current)} largest absolute paired changes in computationally measured output properties, with the construct measurement role embedded in each label. Solid gray bars are increases in the numerator condition; hatched white bars are decreases. These are output properties, not measured human harms or preferences.", args.outdir, files)

    pd.DataFrame(files).to_csv(args.outdir / "FIGURE_MANIFEST.csv", index=False)
    (args.outdir / "FIGURE_METHODS.md").write_text("# Figure methods\n\nAll five figures are generated from `RESULTS_FROZEN_PUBLIC_DATA_ONLY`. Exact source-table hashes are in the results freeze and figure manifest. Grayscale, direct text labels, markers, and hatching avoid color-only encoding.\n", encoding="utf-8")
    print(json.dumps({"status": "DATA_DRIVEN_FIGURES_COMPLETE", "figures": len(files) // 2}, sort_keys=True))


if __name__ == "__main__":
    main()
