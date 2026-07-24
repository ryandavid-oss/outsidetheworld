# SUPER FRGMNTS vertical expansion guides — revision 3

These templates prepare the four 1672 × 941 background plates for one full
additional screen of vertical exploration. Revision 3 derives its coordinate
and movement contracts directly from `super_frgmnts.html`.

## What is authoritative

- The live game canvas is 1672 × 941.
- The original plate is copied into the composite at y=941 without scaling.
- The concrete deck is therefore `941 + 663 = y1604`.
- The Deepworks floor is therefore `941 + 875 = y1816`.
- Normal route steps are 128px. The live jump rises approximately 139.4px at
  the game’s worst permitted 33ms frame interval, leaving about 11.4px of
  margin.

No 900px conversion is used.

## Package contents

Each room has three 1672 × 1882 PNG files:

- `*-vertical-expansion-canvas.png` — transparent upper half with the original
  plate preserved pixel-for-pixel in the lower half.
- `*-outpaint-mask-white-edit.png` — white pixels may be generated or
  inpainted; black pixels protect the source.
- `*-collision-guide.png` — revision-3 planning overlay.

Also included:

- `collision-manifest.json` — machine-readable geometry and live-game values.
- `MASTER-OUTPAINT-PROMPT.txt` — shared and room-specific generation language.
- `super-frgmnts-expansion-guides-contact-sheet.png`.

The deterministic builder and independent verifier live at:

- `tools/build_super_frgmnts_expansion_guides.py`
- `tools/verify_super_frgmnts_expansion_guides.py`

## Coordinate contract

| Item | Composite coordinate |
|---|---:|
| Composite dimensions | 1672 × 1882 |
| New upper plate | y=0–940 |
| Original plate begins | y=941 |
| Blend/inpaint zone | y=941–1120 |
| Protected original pixels | y=1121–1881 |
| Concrete deck | y=1604 |
| Deepworks floor | y=1816 |
| Deepworks playable span | x=258–1124 |
| Deepworks drop entry | x=300–1082 |
| Shared upper room transition | y=580 |

## Movement contract

| Rule | Value |
|---|---:|
| Normal route rise | 128px |
| Future boost-only rise | 192px |
| Maximum planned horizontal gap | 160px |
| Minimum platform width | 144px |
| Collision grid | 16px |
| Vertical grid phase | y ≡ 4 (mod 16) |
| Player collision height | 100px |
| Player drawn sprite height | 112px |

The 192px boost geometry is a future powerup target. It is optional and is not
required to complete either normal ascent route.

## Traversal design

Every room has two independent normal routes from the concrete deck to the top
of the expansion. The routes alternate between wall and inner lanes at 128px
vertical intervals. Their x positions differ by room so the architecture can
vary without changing movement safety.

At y=580, both room-edge anchors align across all rooms. Inner route platforms
and a central cross-link make each anchor reachable from inside its room.

Platforms at or below y=1121 are collision annotations only. They are intended
for runtime platform rendering and must not alter the protected background
pixels.

## Color legend

- White: current runtime collision surface.
- Cyan: proposed structure to include in generated artwork.
- Blue: shared room-transition anchor.
- Pink: optional boost-only geometry.
- Violet hatching: runtime collision annotation; do not generate artwork.
- Gold: moving-platform concept path.

## Recommended generation workflow

1. Use the vertical expansion canvas as the edit target.
2. Use the matching collision guide as a structural reference, not as visual
   style.
3. If the tool supports masks, use the white-edit mask.
4. Apply the shared prompt and matching room paragraph.
5. Reject any result that copies guide labels, grids, colored route lines, or
   interface-like overlays into the artwork.
6. Restore rows 1121–1881 from the original source plate before accepting any
   result.
7. Test the composite at 100% pixel scale before wiring it into the game.

## Rebuild and verify

From the repository root:

```sh
python3 tools/build_super_frgmnts_expansion_guides.py
python3 tools/verify_super_frgmnts_expansion_guides.py
```

The verifier independently rereads the live game, simulates its capped-frame
jump, validates both ascent routes, checks room anchors, and compares every
protected source pixel.
