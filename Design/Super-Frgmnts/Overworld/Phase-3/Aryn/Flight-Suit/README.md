# Aryn flight-suit movement

**Status:** Persistent RD-42 movement integrated

The supplied 6 × 6 sheets give Aryn a complete flight-suit run and jump
vocabulary. The run source contains 36 frames at 78 ms each (2.808 seconds).
The jump source contains 36 frames at 71 ms each (2.556 seconds).

## Outputs

- `Raw/aryn-flight-suit-run-source-v1.png` and `.json`: untouched supplied run
  frames with local metadata naming.
- `Raw/aryn-flight-suit-jump-source-v1.png` and `.json`: untouched supplied jump
  frames with local metadata naming.
- `../../../../../../Images/Game/Super-Frgmnts/aryn-flight-suit-run-runtime-v1.png`:
  normalized 6 × 6 runtime atlas with 112 px cells.
- `../../../../../../Images/Game/Super-Frgmnts/aryn-flight-suit-jump-runtime-v1.png`:
  normalized 6 × 6 runtime atlas with 112 px cells.
- `Reviews/aryn-flight-suit-run-preview-v1.gif` and
  `Reviews/aryn-flight-suit-jump-preview-v1.gif`: nearest-neighbor motion
  reviews at 4× runtime scale.
- `Reviews/aryn-flight-suit-run-contact-v1.png` and
  `Reviews/aryn-flight-suit-jump-contact-v1.png`: numbered frame reviews.
- `aryn-flight-suit-movement-v1.json`: source, normalization, cadence, phase,
  and runtime-boundary manifest.

Rebuild the derived files with:

```sh
python3 tools/build_super_frgmnts_aryn_flight_suit.py
```

## Runtime use

In the isolated RD-42 interior, changing out of armor now returns control to
Aryn in her flight suit. Her movement remains unarmored as she walks, runs,
jumps, and lands across the main deck. The resolved flight-suit frame from the
armor-change sequence supplies her standing pose. Returning to the flight/suit
alcove and pressing Down plays the current provisional reverse sequence and
restores field armor.

The source run's authored lead-in and resolve frames remain in the atlas, while
frames 7–32 form the responsive gameplay loop. The jump frames are selected by
takeoff, vertical velocity, and landing state so the sprite follows the real
physics arc instead of imposing the source sheet's full canned duration.

## Current boundary

Aryn must restore field armor before she can use the dorsal hatch or secure the
Core Transit service kit. The new sheets do not include unarmored hatch
traversal, pack attachment, damage, weapon, or keel-service-deck poses. Those
interactions remain intentionally locked rather than silently substituting an
armored sprite.
