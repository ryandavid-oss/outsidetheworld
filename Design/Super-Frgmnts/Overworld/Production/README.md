# SUPER FRGMNTS // Coreworks Overworld Production Landscape

This directory contains the Phase 2B static landscape production pass for the
original three-plate Coreworks overworld plus the approved Western Signal Flats
runtime extension.

## Outputs

- `overworld-production-master-v1.png` — the continuous 5,016 × 941 panorama.
- `Plates/overworld-landing-flats-v1.png` — Plate 1, 1,672 × 941.
- `Plates/overworld-dras-outpost-v1.png` — Plate 2, 1,672 × 941.
- `Plates/overworld-coreworks-threshold-v1.png` — Plate 3, 1,672 × 941.
- `overworld-production-contact-sheet-v1.png` — three-plate review image.
- `overworld-production-seam-audit-v1.png` — full-height crops around both
  plate seams.
- `Plates/overworld-western-signal-flats-v1.png` — the prepended western
  runtime plate, 1,672 × 941.

The four-plate contact sheet and western-to-landing seam audit are stored in
`../Western-Signal-Flats/Reviews/`. The western source prompt and its dedicated
builder live beside that review package so the original Phase 2B master remains
reproducible without rewriting it.

The unmodified built-in image-generation results are retained in `Raw/`.
`production-prompts-v1.txt` records the complete prompt set.

## Geometry contract

- Each plate is exactly 1,672 × 941.
- The master panorama is exactly 5,016 × 941.
- The walkable ground top is y=744 on every plate.
- Plate seams are x=1,672 and x=3,344.
- A 128-pixel band on each side of a seam receives color harmonization only.
  Geometry is not crossfaded or blurred.

The builder preserves the generated pixel art. It shifts each raw plate
vertically to align the ground, mirrors the hidden bottom tail to fill newly
exposed pixels, applies restrained per-row color correction near the seams,
and then splits the master back into exact plates.

## Scope

These files contain static landscape only. The following remain separate:

- Aryn Sol-Mavi;
- Aryn's ship;
- Dras Ehdre and his personal camp details;
- the galactic-credit terminal;
- the active Coreworks portal;
- moving cloud layers, dust ribbons, volcanic smoke, heat shimmer, lights, and
  cloth animation.

The production landscape is not wired into the live game during Phase 2B.

## Build

From the repository root:

```sh
python3 tools/build_super_frgmnts_overworld_production.py
```

The script validates every dimension, ground shift, output plate, master seam,
and final file before returning success.

To validate and republish the prepended western plate:

```sh
python3 tools/build_super_frgmnts_overworld_western_expansion.py
```
