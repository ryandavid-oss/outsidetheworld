# SUPER FRGMNTS // Wound Laser Ground Impact v1

**Status:** Implemented for the isolated Seam Hunter boss trial

## Runtime contract

- Runtime sheet: `Images/Game/Super-Frgmnts/wound-laser-ground-impact-sheet-v1.png`
- Sheet: **384 × 288 px**, transparent RGBA
- Layout: **4 columns × 3 rows**, 12 chronological frames
- Frame: **96 × 96 px**
- Runtime render: **192 × 192 px**
- Frame time: **65 ms**
- Authored baseline: **y = 93** inside each source frame
- Trigger: first visible/damaging laser frame
- Position: locked diagonal-laser deck endpoint
- Gameplay: cosmetic only; no damage, collision, or lingering hazard

## Sources and reviews

- Generated source:
  `Raw/wound-laser-ground-impact-source-v1.png`
- Transparent source:
  `Raw/wound-laser-ground-impact-alpha-v1.png`
- Sheet review:
  `Reviews/wound-laser-ground-impact-sheet-review-v1.png`
- Animated review:
  `Reviews/wound-laser-ground-impact-preview-v1.gif`

The built-in image-generation workflow produced the 12-frame effect on a flat
green field. The build removes the field, downsizes each source cell with
nearest-neighbor sampling, centers the visible pixels, and anchors every frame
to the shared baseline.

Final prompt:

> Production sprite sheet for a 2D pixel-art boss laser ground-impact effect;
> exactly 12 chronological frames in an exact 4 × 3 grid. Frames 1–2 contact,
> 3–5 splash, 6–8 peak plasma crown and sparks, 9–12 fading scar and embers.
> Flat #00ff00 chroma background; crisp dark Metroidvania pixel art;
> red, white, pink, and crimson; no character, environment, text, or watermark.

Regenerate:

```sh
python3 tools/build_super_frgmnts_wound_laser_impact.py
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```
