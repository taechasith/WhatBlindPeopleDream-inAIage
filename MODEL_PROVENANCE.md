# Study 1 model provenance

**Status:** `SMOLVLM2_REJECTED_AFTER_NONHUMAN_GROUNDING_SCREEN; NO_REPLACEMENT_OUTPUT_AVAILABLE`
**Scope:** non-human pre-collection preparation only

## Rejected reproducible candidate system

| Field | Record |
| --- | --- |
| Model repository | `HuggingFaceTB/SmolVLM2-2.2B-Instruct` |
| Immutable revision | `482adb537c021c86670beed01cd58990d01e72e4` |
| Model task | image-to-text instruction following |
| Terms recorded at acquisition | Apache-2.0 |
| Retrieval date | 2026-10-05, Asia/Bangkok |
| Access route | Public Hugging Face artifact, downloaded locally without an account |
| Artifact location | `private/study1_smolvlm2_cache/` (ignored; never included in review/public releases) |
| Artifact verification | `hf cache verify` reported all 16 repository files checksum-matched; local downloader sidecars are expected extra files |
| Rendered inputs | Original `*_v2.svg` scenes rasterized locally; input hashes are in ignored `private/study1_rendered_stimuli/render_manifest.csv` |
| Default prompt | `prompts/default_ai_prompt.txt`, hashed in generation output |
| Decoding | `do_sample=false`; no temperature/top-p; `max_new_tokens=130` |
| Planned SAI policy | `prompts/steered_ai_system_prompt.txt` and `AI_EXPOSURE_PROTOCOL.md`; no participant interaction has occurred |
| Static-audio candidate | Locally installed `Microsoft Zira Desktop` Windows SAPI voice, rate 0, volume 100; final WAV files and hashes remain pending approved scripts |

## Runtime used for candidate generation

The isolated local `.venv/` is ignored and is not a public reproducibility
claim. It uses Python 3.10, `transformers==4.52.4`, `accelerate==1.3.0`, and
the locally available CPU build of PyTorch 2.2.2. The generation command and
all candidate outputs are kept under `private/`. The project-level analytical
environment remains separately documented in `requirements.txt`.

## Replacement candidate under the same non-human screen

| Field | Record |
| --- | --- |
| Model repository | `Qwen/Qwen2.5-VL-7B-Instruct` |
| Immutable revision | `cc594898137f460bfe9f0759e9844b3ce807cfb5` |
| Terms recorded at acquisition | Apache-2.0 |
| Artifact verification | All 16 remote repository files checksum-matched in the local cache; downloader sidecars are expected local extras |
| Candidate generator | `code/generate_study1_qwen_candidates.py` |
| Status | `NO_CANDIDATE_OUTPUT_WRITTEN`; not selected for exposure |

The replacement is evaluated with the same original rendered scenes, frozen
default prompt, deterministic decoding, word-range screen, marker-coverage
screen, and prohibited-language screen. Its larger parameter count is not a
substitute for passing those checks.

### Candidate-generation attempt history

The first local Qwen attempt was stopped before it wrote any candidate output
after it exposed an unbounded/underutilized CPU-thread configuration. A second,
bounded run from the same immutable artifact and prompt used `cpu_threads=16`
and `max_new_tokens=120`; it too was stopped before writing an output, rather
than leaving a sustained CPU-only job running without an execution window. Both
private stdout/stderr logs are retained as terminated technical attempts, not
screen results. These are pre-output computational settings, not changes to
participant materials, a model-selection result, or a protocol amendment.

An appropriately resourced, deterministic run must produce a complete
candidate-output artifact before the lexical and independent grounding reviews
can occur. No replacement model is frozen and no participant-facing text exists.

## What this does and does not freeze

The pinned model artifact, default prompt, raster-input procedure, and
deterministic decoding were tested for prospective preparation. The candidate
failed the required grounding screen and is not an exposure system. The following
gates remain mandatory for a replacement:

1. Candidate DAI outputs must pass a unit-by-unit grounding audit and an
   independent prohibited-claim review.
2. Final static DAI/HUM/ANC scripts must be duration/lexical-complexity audited
   and rendered through a selected TTS route with audio hashes.
3. The SAI implementation must be tested against the same local model revision,
   fixed prompt, question limit, logging schema, and failure policy.
4. Ethics determination/approval must cover the finalized procedure and
   materials. No human may be exposed before it does.

If a final model artifact, prompt, image, TTS engine, or safety policy changes
after preregistration, collection pauses and the change is logged as a protocol
amendment. Candidate model text is not a study result and must not appear as
empirical evidence in a manuscript or poster. See
`MODEL_CANDIDATE_EVALUATION.md` for the failed screen.
