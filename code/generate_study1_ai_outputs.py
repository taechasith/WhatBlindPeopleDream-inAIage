"""Generate deterministic *candidate* DAI scripts from local Study 1 stimuli.

This is a non-human pre-collection utility. It never contacts participants and
does not turn a model output into an approved exposure script: every candidate
must fail closed pending the separate grounding and accessibility audits.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "HuggingFaceTB/SmolVLM2-2.2B-Instruct"
MODEL_REVISION = "482adb537c021c86670beed01cd58990d01e72e4"
DEFAULT_MODEL_DIR = ROOT / "private" / "study1_smolvlm2_cache"
DEFAULT_RENDER_DIR = ROOT / "private" / "study1_rendered_stimuli"
DEFAULT_OUTPUT_DIR = ROOT / "private" / "study1_model_candidates"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


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
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--max-new-tokens", type=int, default=130)
    args = parser.parse_args()
    if not args.model_dir.exists() or not (args.model_dir / "config.json").exists():
        raise FileNotFoundError("Pinned local model artifact is missing or incomplete.")
    if not args.prompt.exists():
        raise FileNotFoundError(args.prompt)
    images = {f"S{number:02d}": args.render_dir / f"S{number:02d}.png" for number in range(1, 5)}
    missing_images = [str(path) for path in images.values() if not path.exists()]
    if missing_images:
        raise FileNotFoundError(f"Missing rendered stimulus image(s): {missing_images}")

    import torch
    from transformers import AutoModelForImageTextToText, AutoProcessor

    if args.device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("--device cuda requested but CUDA is unavailable in this environment.")
    device = torch.device(args.device)
    processor = AutoProcessor.from_pretrained(args.model_dir, local_files_only=True)
    model = AutoModelForImageTextToText.from_pretrained(
        args.model_dir,
        local_files_only=True,
        torch_dtype=torch.float32 if device.type == "cpu" else torch.float16,
        low_cpu_mem_usage=True,
    ).to(device)
    model.eval()

    prompt = args.prompt.read_text(encoding="utf-8").strip()
    prompt_hash = sha256_bytes(prompt.encode("utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for stimulus_id, image_path in images.items():
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "path": str(image_path.resolve())},
                {"type": "text", "text": prompt},
            ],
        }]
        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs = {name: value.to(device) for name, value in inputs.items()}
        with torch.inference_mode():
            generated = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=args.max_new_tokens,
                use_cache=True,
            )
        prompt_length = inputs["input_ids"].shape[1]
        text = processor.batch_decode(generated[:, prompt_length:], skip_special_tokens=True)[0].strip()
        rows.append({
            "data_status": "NONHUMAN_MODEL_CANDIDATE_NOT_APPROVED_FOR_EXPOSURE",
            "stimulus_id": stimulus_id,
            "condition": "DAI",
            "model_id": MODEL_ID,
            "model_revision": MODEL_REVISION,
            "model_local_config_sha256": sha256_file(args.model_dir / "config.json"),
            "input_png_sha256": sha256_file(image_path),
            "prompt_sha256": prompt_hash,
            "decoding": "do_sample=false;temperature=not_applicable;top_p=not_applicable;max_new_tokens=" + str(args.max_new_tokens),
            "runtime_device": str(device),
            "runtime_torch": torch.__version__,
            "runtime_transformers": __import__("transformers").__version__,
            "runtime_python": platform.python_version(),
            "output_text": text,
            "output_word_count": word_count(text),
            "candidate_status": "PENDING_GROUNDING_AND_INDEPENDENT_REVIEW",
        })
    output_path = args.output_dir / "dai_model_candidate_outputs.csv"
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "data_status": "NONHUMAN_MODEL_CANDIDATE_NOT_APPROVED_FOR_EXPOSURE",
        "model_id": MODEL_ID,
        "model_revision": MODEL_REVISION,
        "model_dir": str(args.model_dir),
        "prompt": str(args.prompt),
        "prompt_sha256": prompt_hash,
        "device": str(device),
        "outputs": output_path.name,
        "no_participant_data": True,
    }
    (args.output_dir / "generation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} non-human candidate descriptions to {output_path}")


if __name__ == "__main__":
    main()
