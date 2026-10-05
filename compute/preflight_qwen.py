"""Non-analytic CUDA preflight for the pinned Qwen candidate.

This script creates its own synthetic image; it never opens VizWiz or any
research corpus. It exercises each already-frozen prompt condition only for
loadability, deterministic generation, parsing, and memory/runtime logging.
"""
from __future__ import annotations

import hashlib
import json
import platform
import random
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageDraw
from qwen_vl_utils import process_vision_info
from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration


ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "compute" / "model_cache" / "Qwen2.5-VL-3B-Instruct"
PROMPTS = {
    "generic": ROOT / "prompts_public" / "GENERIC_v1.txt",
    "intent_steered": ROOT / "prompts_public" / "INTENT_STEERED_v1.txt",
    "accessibility_steered": ROOT / "prompts_public" / "ACCESSIBILITY_STEERED_v1.txt",
}
REVISION = "66285546d2b821cf421d4f5eb2576359d3770cd3"
SEED = 20261006
MIN_PIXELS = 256 * 28 * 28
MAX_PIXELS = 640 * 28 * 28
MAX_NEW_TOKENS = 128


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_synthetic_image(path: Path) -> None:
    image = Image.new("RGB", (560, 420), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 80, 230, 330), fill="royalblue")
    draw.ellipse((320, 140, 470, 290), fill="orange")
    draw.text((40, 30), "SYNTHETIC TEST", fill="black")
    image.save(path)


def main() -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for this preflight.")
    if not MODEL_DIR.is_dir():
        raise FileNotFoundError(f"Missing pinned model directory: {MODEL_DIR}")
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    image_path = ROOT / "compute" / "preflight_synthetic.png"
    build_synthetic_image(image_path)
    prompt_text = {condition: path.read_text(encoding="utf-8").strip() for condition, path in PROMPTS.items()}
    prompt_text["intent_steered"] = prompt_text["intent_steered"].format(blv_question="What color is the rectangle?")
    prompt_text["accessibility_steered"] = prompt_text["accessibility_steered"].format(blv_question="What color is the rectangle?")
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    start_load = time.perf_counter()
    processor = AutoProcessor.from_pretrained(MODEL_DIR, min_pixels=MIN_PIXELS, max_pixels=MAX_PIXELS)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_DIR, torch_dtype=torch.float16, low_cpu_mem_usage=True
    ).to("cuda").eval()
    load_seconds = time.perf_counter() - start_load
    records = []
    for condition, prompt in prompt_text.items():
        messages = [{"role": "user", "content": [{"type": "image", "image": str(image_path)}, {"type": "text", "text": prompt}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = processor(text=[text], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to("cuda")
        started = time.perf_counter()
        with torch.inference_mode():
            generated = model.generate(**inputs, do_sample=False, max_new_tokens=MAX_NEW_TOKENS, use_cache=True)
        runtime = time.perf_counter() - started
        trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, generated)]
        output = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()
        if not output:
            raise RuntimeError(f"Empty output in {condition} preflight.")
        records.append({"condition": condition, "output_text": output, "runtime_seconds": runtime})
    result = {
        "status": "TECHNICAL_PREFLIGHT_ONLY_NOT_STUDY_DATA",
        "model_id": "Qwen/Qwen2.5-VL-3B-Instruct",
        "revision": REVISION,
        "dtype": "float16",
        "quantization": "none",
        "device": torch.cuda.get_device_name(0),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "processor_class": type(processor).__name__,
        "model_class": type(model).__name__,
        "image_policy": {"min_pixels": MIN_PIXELS, "max_pixels": MAX_PIXELS},
        "generation": {"do_sample": False, "max_new_tokens": MAX_NEW_TOKENS, "seed": SEED},
        "prompt_sha256": {condition: sha256(path) for condition, path in PROMPTS.items()},
        "synthetic_image_sha256": sha256(image_path),
        "load_seconds": load_seconds,
        "peak_vram_bytes": torch.cuda.max_memory_allocated(),
        "records": records,
        "os": platform.platform(),
    }
    (ROOT / "compute" / "preflight_qwen_result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "records"}, sort_keys=True))


if __name__ == "__main__":
    main()
