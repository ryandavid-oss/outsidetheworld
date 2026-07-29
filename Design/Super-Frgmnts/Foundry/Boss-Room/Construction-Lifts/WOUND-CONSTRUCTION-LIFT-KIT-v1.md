# SUPER FRGMNTS // The Wound Construction Lift Kit

**Status:** Superseded by the approved wide-arena v2 contract

## Runtime contract

The three approved construction platforms keep their existing collision,
motion ranges, speeds, and positions. This kit replaces only their provisional
procedural appearance.

- Left and right fixed elevator towers: **320 × 592 px**
- Left and right moving platforms: **320 × 72 px**
- Vertical cable tile: **8 × 64 px**
- Upper fixed gantry runway: **1,156 × 64 px**
- Upper moving trolley/platform assembly: **300 × 152 px**
- Moving-platform walk surface: **12 px below the platform sprite top**
- Upper-gantry walk surface: **86 px below the assembly sprite top**
- Vertical guide centers: **x = 30** and **x = 290**
- Vertical cable center: **x = 160**
- Upper suspension anchors: **x = 54** and **x = 246**

The two vertical elevators reuse one symmetrical tower and one platform
sprite. The upper gantry uses a distinct trolley/platform assembly because its
suspension length remains fixed while it travels horizontally.

## Visual contract

- The user-supplied platform establishes the dark navy steel, silver edge,
  triangular underframe, central clamp, and restrained amber-light language.
- Fixed architecture is deterministic and dimension-locked rather than
  generated as a complete mechanical scene.
- Wear is localized to rails, braces, and load paths.
- Platforms have clear straight walkable surfaces and no gameplay-blocking
  railings.
- Cables, rails, trolley wheels, guide shoes, brakes, and bottom buffers make
  every visible component read as load-bearing machinery.

## Source and runtime paths

User reference:

`Raw/wound-construction-platform-user-reference-v1.png`

Built-in image-editing chroma source:

`Raw/wound-construction-platform-chroma-source-v1.png`

Clean material source:

`Raw/wound-construction-platform-clean-source-v1.png`

Runtime assets:

- `Images/Game/Super-Frgmnts/wound-construction-lift-tower-runtime-v1.png`
- `Images/Game/Super-Frgmnts/wound-construction-lift-platform-runtime-v1.png`
- `Images/Game/Super-Frgmnts/wound-construction-lift-cable-tile-v1.png`
- `Images/Game/Super-Frgmnts/wound-construction-gantry-runway-runtime-v1.png`
- `Images/Game/Super-Frgmnts/wound-construction-gantry-car-runtime-v1.png`

Reviews:

- `Reviews/wound-construction-lift-kit-review-v1.png`
- `Reviews/wound-construction-lifts-room-review-v1.png`

Regenerate:

```sh
python3 tools/build_super_frgmnts_wound_construction_lifts.py
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```

## Image-editing record

The built-in image-editing workflow was used once to simplify the supplied
platform into a clean chroma-key material source. The result remained too wide
for direct runtime use, so the build script deterministically removes repeated
middle bays, preserves the endcaps and central clamp, and normalizes the final
platforms to exact game dimensions.

Final image-editing prompt:

> Preserve the supplied platform's dark navy steel material, straight slab,
> triangular underframe, amber end lamps, central cable clamp, rivets, and
> restrained wear. Recompose by removing repeated middle sections rather than
> stretching. Use an orthographic side elevation on a flat green chroma-key
> field with no shadow, scenery, text, watermark, characters, railings, tower,
> or cables.
