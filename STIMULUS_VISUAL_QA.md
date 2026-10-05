# Study 1 stimulus visual QA

**Date:** 2026-10-05  
**Scope:** non-human, local design review only  
**Status:** `PARTIAL -- NOT_FOR_EXPOSURE`

## Trigger and decision

The original `S01`--`S04` SVG prototypes were rasterized locally and inspected.
They used abstract shapes that did not visibly support several objects and
relations declared in the marker inventory. They are retained as design history
but rejected for model grounding and participant exposure.

The successor `*_v2.svg` assets are original, non-identifying, neutral-to-mild
affect vector scenes. Local render inspection confirms that each intended scene
contains visible candidate referents for its registered object and spatial
markers. The rendered PNGs, hashes, and rendering parameters are held under
`private/study1_rendered_stimuli/`; those image files are excluded from review
and public releases.

## Checks passed for v2 at the design level

| Set | Candidate visible markers checked locally | Result |
| --- | --- | --- |
| S01 | violin above bench; fountain; umbrella beside fountain; dog under table; lantern; cyclist and gate | Pass as vector-design candidate |
| S02 | open window above toolbox; map; kettle beside plant; bell; stool and spiral stair | Pass as vector-design candidate |
| S03 | traveler; suitcase and cane; clock/exit sign; vending machine/backpack; puddle and platform edge | Pass as vector-design candidate |
| S04 | garden arch/cat; watering can/flowerpot; wind chime/path; wheelbarrow/sign; curving path/gate | Pass as vector-design candidate |

## Still required before exposure

1. Frozen-model output audit against every semantic unit and prohibited-claim
   list.
2. Independent review of final DAI/HUM/ANC scripts for factual grounding,
   accidental decoy leakage, timing, lexical complexity, and social/safety
   overreach.
3. Accessibility/cultural review permitted by the ethics determination.
4. Final TTS render, audio hashes, and playback test.

This review neither establishes model accuracy nor substitutes for a human
accessibility assessment. It produces no participant data and no study result.
