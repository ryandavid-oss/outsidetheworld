# SUPER FRGMNTS // Seam Hunter Death v1

**Status:** Implemented in the isolated Wound boss trial

## Runtime contract

- Runtime sheet:
  `Images/Game/Super-Frgmnts/enemy-seam-hunter-death-sheet-v1.png`
- Sheet: **1,400 × 1,115 px**, transparent RGBA
- Layout: **5 columns × 5 rows**, 25 chronological frames
- Runtime frame: **280 × 223 px**
- Runtime render: **560 × 446 px**
- Frame time: **107 ms**
- Total sequence: **2.675 seconds**
- Deck-impact cue: frame **13**
- Final corpse: frame **24**, held for **1.4 seconds**

The source contains different transparent bottom margins across the sequence:
eight source pixels in the opening frames, nine at the deck-impact frame, and
one after the body settles. Runtime applies the measured per-frame bottom
padding to the render anchor. This keeps every pose in physical contact with
the y = 1,360 deck instead of visibly levitating above it.

## Gameplay behavior

- The lethal rifle hit begins the death sequence instead of removing the boss.
- Sweep, laser, pursuit, collision, and further rifle damage stop immediately.
- Aryn retains control and all three construction platforms continue moving.
- The boss bar remains during collapse and disappears after the body settles.
- Wound access waits until all 25 frames finish.
- The final pose holds for 1.4 seconds, darkens over 1.05 seconds, and fades
  away over 0.9 seconds.
- Wound-touched Vesperite is revealed at Seam Hunter's captured resting
  position during the final fade.
- The results panel waits for Aryn to recover the specimen deliberately.

## Sources and reviews

- Ludo source:
  `Raw/seam-hunter-death-ludo-source-v1.png`
- Ludo metadata:
  `Raw/seam-hunter-death-ludo-source-v1.json`
- Runtime-sheet review:
  `Reviews/seam-hunter-death-sheet-review-v1.png`
- Animated review:
  `Reviews/seam-hunter-death-preview-v1.gif`

The source is **2,800 × 2,230 px**, which exceeds the project’s portable
texture ceiling. The deterministic build downsizes each full frame by 50%
with nearest-neighbor sampling, producing a runtime sheet whose longest edge
is 1,400 px.

Regenerate and verify:

```sh
python3 tools/build_super_frgmnts_seam_hunter_death.py
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```
