# SUPER FRGMNTS // Seam Hunter Encounter Announcement v1

**Status:** Approved presentation implemented in the isolated Wound boss trial

## Trigger and gameplay contract

- Crossing the established combat threshold at **x = 670** starts the
  announcement. Landing a long-range hit before crossing also starts it before
  Seam Hunter can act.
- The complete announcement runs on every fresh attempt and every retry.
- Aryn and Seam Hunter are locked for the announcement.
- The two construction lifts and upper gantry continue moving.
- Environmental atmosphere continues rendering.
- The mission clock is frozen and resumes from the exact same value.
- Gameplay resumes directly into the existing pursuit behavior. Boss health,
  damage, movement, hitboxes, laser cadence, rifle cadence, and arena geometry
  are unchanged.

## Presentation timeline

The full sequence lasts **6.35 seconds**:

1. **0.00 s:** The room darkens, the central blue Wound seam ignites, camera
   push begins, and `wound_ignition` plays.
2. **0.82 s:** `MAIN ENCOUNTER` resolves and the supplied `SEAM HUNTER`
   typography assembles outward from the center with restrained fragments.
   `title_arrival` supplies the impact.
3. **2.02 s:** A cool-blue energy sweep crosses the title while
   `energy_sweep` plays.
4. **2.35 s:** `resonance_tail` carries the completed hold and release.
5. **4.90 s:** The announcement typography, seam, darkness, and camera
   treatment have fully cleared. Seam Hunter remains absent for one short
   beat.
6. **5.05 s:** The dedicated `Subterranean Apex` score starts from its opening
   as Seam Hunter begins materializing into the now-visible room.
7. **6.25 s:** Seam Hunter reaches full opacity.
8. **6.35 s:** His health bar appears and gameplay resumes.

Players who prefer reduced motion retain the complete announcement and sound
timing, but the camera push, fragments, and drifting particles are suppressed.

## Skip and mobile contract

- Keyboard: **Enter** or **numpad Enter**.
- Controller: the standard **Start/Options** button when exposed as Gamepad
  button 9.
- Touch and pointer: the visible **Skip** button.
- The touch target is at least 48 CSS pixels tall on narrow screens and uses
  safe-area insets.
- Movement, firing, jumping, and weapon-switch inputs never skip the
  announcement.
- A held Start input at the trigger cannot skip it; the player must release and
  press again.
- Focus loss pauses presentation audio. Returning to the page restarts the
  short announcement cleanly so visuals and cues cannot drift apart.
- Both paths start the boss score from its opening: natural completion begins
  it with the monster reveal, while skipping begins it immediately.

## Reveal contract

- Seam Hunter and his health bar do not render while the announcement is
  pending.
- Crossing the threshold darkens the room and plays the complete announcement
  while Seam Hunter remains unrendered.
- Seam Hunter begins appearing only after the announcement typography and
  darkness have cleared.
- His combat health bar waits until the announcement clears and control
  returns.
- The mission readout uses `HOSTILE SIGNAL // UNRESOLVED` before the
  announcement and does not expose his name or hit points.
- Wide desktop framing therefore cannot reveal the boss before the cinema.

## Runtime assets

- Title:
  `Images/Game/Super-Frgmnts/seam-hunter-encounter-title-runtime-v1.png`
  (**1,400 × 320 RGBA**)
- Ignition:
  `Audio/super-frgmnts-wound-ignition-v1.wav`
- Title arrival:
  `Audio/super-frgmnts-title-arrival-v1.wav`
- Energy sweep:
  `Audio/super-frgmnts-energy-sweep-v1.wav`
- Resonance tail:
  `Audio/super-frgmnts-resonance-tail-v1.wav`
- Boss score:
  `Audio/super-frgmnts-seam-hunter-boss-v1.m4a`

The four announcement cues are 48 kHz, 16-bit, stereo PCM. The boss score is
48 kHz stereo AAC. Runtime gain provides headroom for the ignition cue.

The supplied originals are preserved in `Raw/`. The SVG is a raster image
embedded in an SVG container rather than editable vector paths, so the
transparent PNG is the canonical runtime title.

## QA

Playable route:

`super_frgmnts.html?preview=wound-boss&autostart=1`

Threshold-review route:

`super_frgmnts.html?preview=wound-boss&autostart=1&qa=intro`

Key canvas telemetry:

- `data-wound-boss-intro`: `pending`, `playing`, `complete`, or `skipped`
- `data-wound-boss-intro-phase`: `empty-room`, `announcement`,
  `boss-reveal`, or `gameplay`
- `data-wound-boss-intro-elapsed`
- `data-wound-boss-intro-cue`
- `data-wound-boss-intro-timer-start`
- `data-wound-boss-intro-timer-end`
- `data-wound-boss-intro-skipped`
- `data-wound-boss-reveal`: `concealed`, `fading`, or `visible`
- `data-wound-boss-reveal-alpha`
- `data-music-scene`
- `data-music-target-volume`

Verify:

```sh
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```
