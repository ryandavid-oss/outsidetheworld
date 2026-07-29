# Seam Hunter Shaft-Sentry Pose v1

## Purpose

This pose communicates that Seam Hunter can see Aryn on the high
construction gantry but cannot reach her. It is a restrained upward watch,
not an attack.

## Runtime contract

- Source: 36-frame, 6 × 6 authored upward-watch sheet.
- Runtime: 16 curated frames in a 5 × 4 atlas.
- Runtime frame: 404 × 458 px.
- Runtime atlas: 2020 × 1832 px RGBA.
- Playback: 76 ms per frame; 1.216-second rise, then hold frame 15.
- Boss render: 396 × 448 px.
- Upward presentation: entirely authored in the sprite; no programmatic body
  tilt.
- Tracking: 110 px horizontal deadzone, 0.20-second facing confirmation, and
  0.28-second exit grace.
- Damage: none.
- Grounding: frames are registered around the planted foot, with a shared
  deck baseline.

### Authored turnaround

- Source: 36-frame, 6 × 6 in-place 180-degree turn.
- Runtime: 19 curated frames in a 5 × 4 atlas.
- Runtime frame: 409 × 458 px.
- Runtime atlas: 2045 × 1832 px RGBA.
- Playback: 45 ms per frame; 0.855 seconds total.
- Boss render: 400 × 448 px.
- Damage: none.
- Direction handling: the source plays forward for a right-to-left turn and
  mirrors around the registered foot for a left-to-right turn.

## Curation

Source frames 0–15 provide a continuous side-view rise from Seam Hunter's
forward hunch into a fully extended upward stare. The feet remain registered
to a single deck root throughout. Frames 16–35 are the return to the lowered
pose and remain outside runtime because the sentry state needs to hold the
highest point of focus until Aryn descends.

The earlier repurposed upward-swipe candidate remains preserved as source
history only. Its pose required an artificial tilt and did not communicate
Seam Hunter's fixation as clearly as the dedicated authored motion.

## Encounter use

The pose is reserved for the hybrid shaft-sentry state when Aryn is above
Seam Hunter on the horizontal construction gantry. He plants, settles into
the upward pose, and tracks Aryn left or right without attacking. The
deadzone and facing confirmation now begin the authored in-place turnaround
instead of flipping the complete pose instantly. Once confirmed, the
0.855-second turn commits through its frontal silhouette and settles into the
mirrored upward watch. Descending during the turn resolves to the nearer
facing and immediately restores pursuit; leaving the gantry while still high
returns him to the existing confusion/search response. Lasers remain
downward-only, so the high gantry continues to provide a reliable perception
break.

The horizontal-gantry reaction is armed independently from vertical-lift
confusion. Riding a lift high enough to break tracking cannot consume the
watch before Aryn transfers onto the gantry. Returning to the main deck rearms
both reactions.
