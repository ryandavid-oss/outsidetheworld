# SUPER FRGMNTS vertical expansion guides

These templates prepare the four current 1672 × 941 background plates for a full additional screen of vertical exploration.

## Package contents

Each room has three 1672 × 1882 PNG files:

- `*-vertical-expansion-canvas.png` — transparent upper half with the original plate preserved pixel-for-pixel in the lower half.
- `*-outpaint-mask-white-edit.png` — white pixels may be generated/inpainted; black pixels protect the source.
- `*-collision-guide.png` — annotated planning image with current collision anchors and suggested upper routes.

The package also includes a contact sheet and `MASTER-OUTPAINT-PROMPT.txt`.

## Coordinate contract

- Composite dimensions: 1672 × 1882
- New upper plate: `y=0–940`
- Original plate begins: `y=941`
- Blend/inpaint zone: `y=941–1120`
- Protected original pixels: `y=1121–1881`
- Existing concrete deck: `y≈1634`
- Existing Deepworks floor: `y≈1856`
- Deepworks drop corridor: `x≈314–1131`
- Shared upper inter-room walkway: `y=740`
- Suggested major gantry bands: `y≈1020`, `600`, and `260`

The collision drawings are proposals, not baked artwork. Their purpose is to keep generated architecture visually compatible with eventual gameplay collision geometry.

## Color legend

- Cyan: current or proposed standard platforms
- Blue: shared inter-room edge links
- Pink: optional platforms intended for a jump-height powerup
- Gold: moving-platform travel corridors and key floor anchors
- Purple dashed line: major gantry band

## Recommended tool workflow

1. Load the vertical expansion canvas as the edit target.
2. Load the white-edit mask if the tool supports masks.
3. Use the matching collision guide as a structural reference.
4. Paste the room-specific paragraph from the master prompt.
5. Generate several variants without changing dimensions.
6. Confirm that the original protected pixels remain unchanged.
7. Test the resulting composite at 100% pixel scale before resizing.

Some tools interpret masks in reverse. If so, invert the mask while preserving the same boundary.

## Rebuild

Run:

```sh
python3 tools/build_super_frgmnts_expansion_guides.py
```

