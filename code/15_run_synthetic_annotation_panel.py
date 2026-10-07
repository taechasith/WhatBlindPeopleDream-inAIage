"""Run one frozen text-only synthetic judge on a blinded annotation packet.

This runner never reads condition labels or a condition map. Outputs are
incremental and retain raw response, parsed labels, evidence spans, and parser
status. It is a measurement instrument, not an empirical analysis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


ROOT = Path(__file__).resolve().parents[1]


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def parse_response(raw: str, constructs: list[str]) -> tuple[list[dict[str, object]], str]:
    try:
        # v1.1 is JSON Lines. Retain v1.0 top-level-array support only for
        # non-analytic technical fixtures generated before the schema freeze.
        stripped = raw.strip()
        if stripped.startswith("{") and '"labels"' in stripped:
            start, end = stripped.index("{"), stripped.rindex("}") + 1
            labels = json.loads(stripped[start:end])["labels"]
        else:
            objects = re.findall(r"\{[^{}]*\}", raw, flags=re.DOTALL)
            labels = [json.loads(item) for item in objects]
        if not isinstance(labels, list):
            raise ValueError("labels_not_list")
        by_construct = {entry.get("construct"): entry for entry in labels if isinstance(entry, dict)}
        if set(by_construct) != set(constructs):
            raise ValueError("construct_set_mismatch")
        records: list[dict[str, object]] = []
        for construct in constructs:
            entry = by_construct[construct]
            label = str(entry.get("label", ""))
            abstain = entry.get("abstain")
            span = str(entry.get("evidence_span", "") or "")
            if label not in {"0", "1", "NA"} or not isinstance(abstain, bool):
                raise ValueError("invalid_label_or_abstain")
            parser_status = "PARSED"
            if label == "1" and not span.strip():
                parser_status = "EVIDENCE_SPAN_INVALID"
            records.append({
                "construct": construct,
                "label": label,
                "abstain": abstain,
                "confidence_if_used": entry.get("confidence_if_used"),
                "evidence_span": span,
                "reason_code": str(entry.get("reason_code", "")),
                "parser_status": parser_status,
            })
        return records, "PARSED"
    except Exception as exc:  # Parser outcomes are data, never silently retried.
        return [], f"PARSE_ERROR:{type(exc).__name__}"


def build_prompt(instruction: str, row: pd.Series, constructs: list[str]) -> str:
    return (
        f"{instruction}\n\nRequired constructs: {json.dumps(constructs)}\n\n"
        f"blind_item_id: {row.blind_item_id}\n"
        f"user_question: {row.blv_question}\n"
        f"ai_response: {row.output_text}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--judge-id", required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    judge = next((j for j in config["judges"] if j["judge_id"] == args.judge_id), None)
    if judge is None:
        raise ValueError("Unknown frozen judge ID")
    packet = pd.read_csv(args.packet)
    required = {"blind_item_id", "blv_question", "output_text"}
    if not required.issubset(packet.columns) or any(c in packet.columns for c in ("condition", "model_id")):
        raise ValueError("Packet violates blinded input contract")
    if packet.blind_item_id.duplicated().any():
        raise ValueError("Packet needs unique blind IDs")
    instruction = args.prompt.read_text(encoding="utf-8")
    constructs = list(config["constructs"])
    generation = config["generation"]
    set_seed(int(generation["seed"]))
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for frozen synthetic-panel inference")

    kwargs: dict[str, object] = {"revision": judge["immutable_revision"]}
    if judge["quantization"].startswith("bitsandbytes"):
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
        )
        kwargs["device_map"] = "auto"
    else:
        kwargs["torch_dtype"] = torch.float16
        kwargs["device_map"] = "auto"
    local_dir = ROOT / judge["local_dir"]
    if not local_dir.is_dir():
        raise FileNotFoundError(f"Frozen local judge directory is unavailable: {local_dir}")
    tokenizer = AutoTokenizer.from_pretrained(local_dir, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(local_dir, local_files_only=True, **kwargs).eval()

    args.outdir.mkdir(parents=True, exist_ok=True)
    raw_path = args.outdir / f"{args.judge_id}_raw.jsonl"
    parsed_path = args.outdir / f"{args.judge_id}_labels.csv"
    done: set[str] = set()
    if args.resume and parsed_path.exists():
        prior = pd.read_csv(parsed_path, usecols=["blind_item_id"])
        done = set(prior.blind_item_id.dropna().astype(str))
    prompt_hash = digest_text(instruction)
    config_hash = digest_text(json.dumps(config, sort_keys=True))
    all_records: list[dict[str, object]] = []
    if parsed_path.exists() and args.resume:
        all_records.extend(pd.read_csv(parsed_path).to_dict("records"))

    with raw_path.open("a", encoding="utf-8") as raw_file:
        for row in packet.itertuples(index=False):
            blind_id = str(row.blind_item_id)
            if blind_id in done:
                continue
            row_series = pd.Series(row._asdict())
            prompt = build_prompt(instruction, row_series, constructs)
            messages = [{"role": "user", "content": prompt}]
            rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = tokenizer(rendered, return_tensors="pt").to(model.device)
            started = time.perf_counter()
            with torch.inference_mode():
                generated = model.generate(
                    **inputs, do_sample=False, max_new_tokens=int(generation["max_new_tokens"]),
                    pad_token_id=tokenizer.pad_token_id,
                )
            raw = tokenizer.decode(generated[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            records, status = parse_response(raw, constructs)
            common = {
                "blind_item_id": blind_id,
                "judge_id": judge["judge_id"],
                "model_id": judge["model_id"],
                "model_revision": judge["immutable_revision"],
                "prompt_sha256": prompt_hash,
                "panel_config_sha256": config_hash,
                "runtime_seconds": round(time.perf_counter() - started, 6),
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            raw_file.write(json.dumps({**common, "raw_output": raw, "parse_status": status}, ensure_ascii=False) + "\n")
            raw_file.flush()
            if records:
                all_records.extend([{**common, **record} for record in records])
            else:
                all_records.extend([{**common, "construct": construct, "label": "NA", "abstain": True,
                                     "confidence_if_used": None, "evidence_span": "", "reason_code": "",
                                     "parser_status": status} for construct in constructs])
            pd.DataFrame(all_records).to_csv(parsed_path, index=False)
    print(json.dumps({"judge_id": args.judge_id, "rows_completed": len(set(pd.DataFrame(all_records).blind_item_id))}, sort_keys=True))


if __name__ == "__main__":
    main()
