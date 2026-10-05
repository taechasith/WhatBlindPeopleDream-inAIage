"""Run the frozen primary VLM on the locked VizWiz sample with resumable logs.

The script enforces the committed model/prompt/configuration freeze. It writes
one append-only JSON record per attempt and never reruns a successful key on
resume. Generated source-linked text stays in ignored local directories.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "public_intervention" / "processed" / "vizwiz_val_sample_1000.csv"
IMAGE_DIR = ROOT / "data" / "vizwiz" / "processed" / "images_val" / "val"
MODEL_DIR = ROOT / "compute" / "model_cache" / "Qwen2.5-VL-3B-Instruct"
MODEL_MANIFEST = ROOT / "config" / "public_vlm_models.json"
RAW_DIR = ROOT / "data" / "model_outputs" / "raw"
VALIDATED_DIR = ROOT / "data" / "model_outputs" / "validated"
ATTEMPTS = RAW_DIR / "primary_attempts.jsonl"
OUTPUTS = VALIDATED_DIR / "primary_model_outputs.csv"
INFERENCE_LOG = ROOT / "logs" / "inference_manifest.csv"
CHECKPOINT = RAW_DIR / "primary_checkpoint.json"
PROMPTS = {
    "generic": ROOT / "prompts_public" / "GENERIC_v1.txt",
    "intent_steered": ROOT / "prompts_public" / "INTENT_STEERED_v1.txt",
    "accessibility_steered": ROOT / "prompts_public" / "ACCESSIBILITY_STEERED_v1.txt",
}
MODEL_ID = "Qwen2.5-VL-3B-Instruct_FP16_66285546"
REVISION = "66285546d2b821cf421d4f5eb2576359d3770cd3"
SEED = 20261006
MIN_PIXELS = 256 * 28 * 28
MAX_PIXELS = 640 * 28 * 28
MAX_NEW_TOKENS = 128
CONDITIONS = tuple(PROMPTS)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def technical_error(exc: BaseException) -> bool:
    message = f"{type(exc).__name__}: {exc}".lower()
    return any(marker in message for marker in ("out of memory", "cuda", "corrupt", "cannot identify image", "ioerror"))


def append_record(record: dict[str, object]) -> None:
    with ATTEMPTS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()


def successful_keys() -> set[str]:
    if not ATTEMPTS.is_file():
        return set()
    completed: set[str] = set()
    for line in ATTEMPTS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("validator_status") == "VALID_NONEMPTY_UTF8":
                completed.add(str(row["run_key"]))
    return completed


def write_outputs_and_checkpoint() -> None:
    rows = []
    for line in ATTEMPTS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            if row.get("validator_status") == "VALID_NONEMPTY_UTF8":
                rows.append(row)
    keys = ["sample_row_id", "model_id", "condition"]
    frame = pd.DataFrame(rows)
    if len(frame) and frame.duplicated(keys).any():
        raise ValueError("Duplicate successful output key in append-only attempt log.")
    if len(frame):
        ordered = [
            "sample_row_id", "model_id", "condition", "output_text", "model_manifest_sha256",
            "prompt_template_id", "generation_timestamp_utc", "run_id", "run_key", "item_id",
            "image_id", "question_id", "model_revision", "prompt_hash", "prompt_template_sha256",
            "image_hash", "seed", "generation_config_hash", "start_time_utc", "end_time_utc",
            "runtime_seconds", "output_raw", "output_parsed", "validator_status", "error_type", "retry_count",
        ]
        frame[ordered].to_csv(OUTPUTS, index=False)
    runtimes = [float(row["runtime_seconds"]) for row in rows if row.get("runtime_seconds") is not None]
    CHECKPOINT.write_text(json.dumps({
        "status": "INCREMENTAL_PRIMARY_VLM_RUN_NOT_ANALYSIS",
        "completed": len(rows), "expected": 3000, "remaining": 3000 - len(rows),
        "valid_outputs": len(rows), "mean_runtime_seconds": float(np.mean(runtimes)) if runtimes else None,
        "last_checkpoint_utc": utc_now(), "peak_vram_bytes": int(torch.cuda.max_memory_allocated()),
    }, indent=2) + "\n", encoding="utf-8")
    with INFERENCE_LOG.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["model_id", "completed", "expected", "remaining", "valid_outputs", "mean_runtime_seconds", "checkpoint_utc"])
        writer.writeheader()
        writer.writerow({"model_id": MODEL_ID, "completed": len(rows), "expected": 3000, "remaining": 3000-len(rows),
                         "valid_outputs": len(rows), "mean_runtime_seconds": float(np.mean(runtimes)) if runtimes else "", "checkpoint_utc": utc_now()})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=50)
    args = parser.parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("Frozen primary run refuses CPU execution.")
    if not SAMPLE.is_file() or not IMAGE_DIR.is_dir() or not MODEL_DIR.is_dir() or not MODEL_MANIFEST.is_file():
        raise FileNotFoundError("A required frozen source, image directory, model, or model manifest is absent.")
    manifest = json.loads(MODEL_MANIFEST.read_text(encoding="utf-8"))
    record = manifest["models"][0]
    if manifest.get("status") != "FROZEN_PRIMARY_BEFORE_STUDY_INFERENCE" or record.get("model_id") != MODEL_ID or record.get("immutable_revision") != REVISION:
        raise ValueError("Local model manifest does not match the committed primary VLM freeze.")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATED_DIR.mkdir(parents=True, exist_ok=True)
    prompt_templates = {condition: path.read_text(encoding="utf-8").strip() for condition, path in PROMPTS.items()}
    template_hashes = {condition: sha256_file(path) for condition, path in PROMPTS.items()}
    generation = {"do_sample": False, "max_new_tokens": MAX_NEW_TOKENS, "seed": SEED,
                  "min_pixels": MIN_PIXELS, "max_pixels": MAX_PIXELS, "dtype": "float16", "quantization": "none"}
    config_hash = sha256_text(json.dumps(generation, sort_keys=True, separators=(",", ":")))
    manifest_hash = sha256_file(MODEL_MANIFEST)
    sample = pd.read_csv(SAMPLE)
    if len(sample) != 1000 or sample["sample_row_id"].duplicated().any() or sample["image_filename"].duplicated().any():
        raise ValueError("Frozen sample is not the expected 1,000 unique images.")
    if not all((IMAGE_DIR / name).is_file() for name in sample["image_filename"].astype(str)):
        raise FileNotFoundError("At least one locked sample image is absent.")
    existing = successful_keys()
    if existing and not args.resume:
        raise RuntimeError("Existing successful outputs found; use --resume to preserve them.")
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.cuda.manual_seed_all(SEED)
    torch.cuda.empty_cache(); torch.cuda.reset_peak_memory_stats()
    processor = AutoProcessor.from_pretrained(MODEL_DIR, min_pixels=MIN_PIXELS, max_pixels=MAX_PIXELS)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(MODEL_DIR, torch_dtype=torch.float16, low_cpu_mem_usage=True).to("cuda").eval()
    newly_completed = 0
    for row in sample.itertuples(index=False):
        image_path = IMAGE_DIR / str(row.image_filename)
        image_hash = sha256_file(image_path)
        for condition in CONDITIONS:
            run_key = f"{row.sample_row_id}|{MODEL_ID}|{condition}"
            if run_key in existing:
                continue
            prompt = prompt_templates[condition]
            if condition != "generic":
                prompt = prompt.format(blv_question=str(row.blv_question))
            base = {
                "run_id": f"PRIMARY_{sha256_text(run_key)[:16]}", "run_key": run_key,
                "sample_row_id": row.sample_row_id, "item_id": row.sample_row_id, "image_id": row.image_filename,
                "question_id": row.sample_row_id, "condition": condition, "model_id": MODEL_ID,
                "model_revision": REVISION, "prompt_hash": sha256_text(prompt), "prompt_template_id": f"{condition}_v1",
                "prompt_template_sha256": template_hashes[condition], "image_hash": image_hash, "seed": SEED,
                "generation_config_hash": config_hash, "model_manifest_sha256": manifest_hash,
            }
            for attempt in range(2):
                start = utc_now(); started = time.perf_counter()
                try:
                    messages = [{"role": "user", "content": [{"type": "image", "image": str(image_path)}, {"type": "text", "text": prompt}]}]
                    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    image_inputs, video_inputs = process_vision_info(messages)
                    inputs = processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to("cuda")
                    with torch.inference_mode():
                        generated = model.generate(**inputs, do_sample=False, max_new_tokens=MAX_NEW_TOKENS, use_cache=True)
                    trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, generated)]
                    output = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()
                    if not output:
                        raise RuntimeError("parser failure: empty generated output")
                    output.encode("utf-8")
                    complete = {**base, "generation_timestamp_utc": utc_now(), "start_time_utc": start, "end_time_utc": utc_now(),
                                "runtime_seconds": time.perf_counter()-started, "output_raw": output, "output_parsed": output,
                                "output_text": output, "validator_status": "VALID_NONEMPTY_UTF8", "error_type": "", "retry_count": attempt}
                    append_record(complete); existing.add(run_key); newly_completed += 1
                    break
                except Exception as exc:  # logged; only technical errors get one same-config retry
                    failure = {**base, "generation_timestamp_utc": utc_now(), "start_time_utc": start, "end_time_utc": utc_now(),
                               "runtime_seconds": time.perf_counter()-started, "output_raw": "", "output_parsed": "", "output_text": "",
                               "validator_status": "TECHNICAL_FAILURE" if technical_error(exc) else "NONRETRYABLE_FAILURE",
                               "error_type": f"{type(exc).__name__}: {exc}", "retry_count": attempt,
                               "traceback": traceback.format_exc(limit=3)}
                    append_record(failure)
                    if not technical_error(exc) or attempt == 1:
                        break
                    torch.cuda.empty_cache()
            if newly_completed and newly_completed % args.checkpoint_every == 0:
                write_outputs_and_checkpoint()
    write_outputs_and_checkpoint()


if __name__ == "__main__":
    main()
