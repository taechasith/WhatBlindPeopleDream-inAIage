"""Generate deterministic non-human DAI candidates with pinned Qwen2.5-VL.

The utility operates only on original local study scenes. It writes candidate
text under ``private/`` and cannot mark a script approved for exposure.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"
MODEL_REVISION = "cc594898137f460bfe9f0759e9844b3ce807cfb5"
DEFAULT_MODEL_DIR = ROOT / "private" / "study1_qwen25vl7b_cache"
DEFAULT_RENDER_DIR = ROOT / "private" / "study1_rendered_stimuli"
DEFAULT_OUTPUT_DIR = ROOT / "private" / "study1_qwen25vl7b_candidates"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def word_count(text: str) -> int:
    return len([token for token in text.split() if token.strip()])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--render-dir", type=Path, default=DEFAULT_RENDER_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--prompt", type=Path, default=ROOT / "prompts" / "default_ai_prompt.txt")
    parser.add_argument("--max-new-tokens", type=int, default=180)
    parser.add_argument("--max-pixels", type=int, default=401408, help="Image preprocessing cap; must be divisible by 28*28.")
    parser.add_argument(
        "--cpu-threads", type=int, default=min(16, os.cpu_count() or 1),
        help="Bounded local CPU thread count, recorded in the candidate manifest.",
    )
    args = parser.parse_args()
    if args.max_pixels % (28 * 28):
        raise ValueError("max-pixels must be divisible by 784 (28*28).")
    if not (args.model_dir / "config.json").exists():
        raise FileNotFoundError("Pinned Qwen model artifact is missing or incomplete.")
    images = {f"S{number:02d}": args.render_dir / f"S{number:02d}.png" for number in range(1, 5)}
    if any(not path.exists() for path in images.values()):
        raise FileNotFoundError("Run code/render_study1_stimuli.py before generating candidates.")

    import torch
    import transformers
    from PIL import Image
    from transformers import AutoProcessor, Qwen2_5_VLForConditionalGeneration

    prompt = args.prompt.read_text(encoding="utf-8").strip()
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    if args.cpu_threads < 1:
        raise ValueError("cpu-threads must be at least 1.")
    torch.set_num_threads(args.cpu_threads)
    torch.set_num_interop_threads(min(4, args.cpu_threads))
    processor = AutoProcessor.from_pretrained(
        args.model_dir,
        local_files_only=True,
        min_pixels=200704,
        max_pixels=args.max_pixels,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        args.model_dir,
        local_files_only=True,
        torch_dtype=torch.bfloat16,
        low_cpu_mem_usage=True,
    ).to("cpu")
    model.eval()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for stimulus_id, image_path in images.items():
        image = Image.open(image_path).convert("RGB")
        messages = [{"role": "user", "content": [
            {"type": "image", "image": image_path.resolve().as_uri()},
            {"type": "text", "text": prompt},
        ]}]
        chat_text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[chat_text], images=[image], padding=True, return_tensors="pt").to("cpu")
        with torch.inference_mode():
            generated = model.generate(**inputs, do_sample=False, max_new_tokens=args.max_new_tokens)
        trimmed = generated[:, inputs.input_ids.shape[1]:]
        output = processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0].strip()
        rows.append({
            "data_status": "NONHUMAN_MODEL_CANDIDATE_NOT_APPROVED_FOR_EXPOSURE",
            "stimulus_id": stimulus_id,
            "condition": "DAI",
            "model_id": MODEL_ID,
            "model_revision": MODEL_REVISION,
            "model_local_config_sha256": sha256_file(args.model_dir / "config.json"),
            "input_png_sha256": sha256_file(image_path),
            "prompt_sha256": prompt_hash,
            "decoding": f"do_sample=false;temperature=not_applicable;top_p=not_applicable;max_new_tokens={args.max_new_tokens};max_pixels={args.max_pixels}",
            "runtime_device": "cpu",
            "runtime_torch": torch.__version__,
            "runtime_transformers": transformers.__version__,
            "runtime_python": platform.python_version(),
            "runtime_torch_threads": args.cpu_threads,
            "output_text": output,
            "output_word_count": word_count(output),
            "candidate_status": "PENDING_GROUNDING_AND_INDEPENDENT_REVIEW",
        })
    output_path = args.output_dir / "dai_model_candidate_outputs.csv"
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "generation_manifest.json").write_text(json.dumps({
        "data_status": "NONHUMAN_MODEL_CANDIDATE_NOT_APPROVED_FOR_EXPOSURE",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "prompt_sha256": prompt_hash,
        "max_pixels": args.max_pixels,
        "max_new_tokens": args.max_new_tokens,
        "cpu_threads": args.cpu_threads,
        "no_participant_data": True,
    }, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} non-human Qwen candidate descriptions to {output_path}")


if __name__ == "__main__":
    main()
