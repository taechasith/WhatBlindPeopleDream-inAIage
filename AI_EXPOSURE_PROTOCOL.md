# Study 1 AI exposure protocol

**Status:** prospective non-human implementation candidate; no system has been
exposed to a participant.

The current local VLM candidate status is recorded in `MODEL_PROVENANCE.md`;
no candidate is approved for exposure. The common static-audio candidate is the
locally installed `Microsoft Zira Desktop` SAPI
voice at rate 0 and volume 100, rendered by `code/render_study1_tts.ps1` only
after scripts have passed the recorded audit and the ethics gate. This is not an
approval to expose anyone or to redistribute the voice/audio files.

## Common constraints

- Use only the final licensed original prototype scene supplied to the selected
  system; do not upload participant images or private environments.
- Freeze provider, model snapshot/version, image preprocessing,
  system prompt, user prompt, temperature, top-p, seed where supported, token
  cap, safety filters, response transcript, and TTS engine/voice/rate before
  first exposure.
- If an immutable model snapshot is unavailable or the provider changes the
  selected model during collection, suspend exposure and log a protocol
  deviation; do not silently mix versions.
- Prohibit unsupported identity, demographic, relationship, intent, emotion,
  ownership, or real-world safety claims. Static study scenes are not navigation
  advice.
- Deliver through the same approved TTS engine, voice, rate, volume guidance,
  headphones/speaker policy, and playback controls for DAI/HUM/ANC.

## Default AI (DAI)

The final system receives a frozen scene image and `prompts/default_ai_prompt.txt`.
Its single output must be audited against the scene/semantic-unit manifest.
Target length is 60--85 words. The final audio duration, word count, and content
metrics replace prototype figures in the control audit. Participants may replay
the output only if all non-SAI conditions have an equivalently logged replay
policy; otherwise replay is disabled.

## Participant-steered AI (SAI)

SAI tests a participant-led information interaction package, not a pure text
style effect. The same frozen model and scene are used. Participants may ask up
to six questions over a ten-minute interaction window. Follow-up questions are
allowed only if they remain about the study scene. The model retains current
session conversational context only; it has no cross-session memory. Each answer
has a 45-word cap and is logged with timestamp, prompt, output, delivered
semantic units, and version hash.

Before exposure, staff provide only a neutral accessible explanation that the
participant may ask about objects, spatial relations, action, text, uncertainty,
or what matters to them. They do not list target units or suggest dream content.
Free-form questions are permitted but all transcripts are screened after the
session for protocol compliance and unsupported claims. Question content is a
secondary process measure; it is not excluded for being unusual or unhelpful.

## Human reference (HUM) and active narrative control (ANC)

HUM uses an independently authored, scene-grounded reference script matched to
the final DAI output after the final audit. ANC uses a neutral non-scene script
matched on TTS, approximate duration, neutral framing, and session timing. It
does not claim to control spatial-scene content. Both use a shared quiet period
so the session envelope is 12 minutes.

## Final output audit

Two independent non-participant reviewers must check each final static DAI/HUM/
ANC script against the source scene, semantic inventory, and prohibited-claim
list before exposure. This is a stimulus-quality review, not Study 1 outcome
coding. Disagreements and revisions are versioned. No final output may be called
"AI-generated" until provider/model provenance is completed.
