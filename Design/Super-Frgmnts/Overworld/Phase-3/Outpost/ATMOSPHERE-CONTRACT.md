# Veyra overworld atmosphere contract

Status: Beta 2 production progression integrated locally; not yet deployed.

## World-state progression

The Overworld sky is readable game state, not a fixed decorative plate.
Atmospheric stabilizer failure and the infestation both contribute to the
Arrival sky, so restoring machinery improves conditions without falsely
implying that the deeper threat has vanished.

| State | Cause and visual read |
| --- | --- |
| Arrival / `sky=arrival` | Both relays are offline. Dense low storm mass, violet pressure, and a darker horizon make the surface feel atmosphere-starved and infestation-heavy. |
| First relay / `sky=relay-one` | The first break appears in the storm deck and some horizon warmth returns. This is an authored review state for future surface backtracking. |
| Both relays / `sky=stabilized` | Storm opacity and low cloud pressure visibly fall, while the sky remains bruised around Coreworks. This is an authored review state for future surface backtracking. |
| Seam Hunter cleared / `sky=cleared` | The post-Wound surface is warmer and more legible. A localized violet remnant remains over Coreworks because the infestation and Primary Biolab signal are unresolved. |
| Report complete | The broad clearing holds, but the localized remnant persists as the visual bridge to `THE SIGNAL ANSWERED`. |

The production Chapter 01 route exposes Arrival and the post-Wound clearing.
The two relay states are already deterministic for review and later
backtracking; they do not invent an additional surface trip in the current
episode.

## Depth system

- Two generated low-frequency cloud masks create independently moving wispy
  and storm layers with different speed, height, opacity, blend mode, and
  camera parallax. A lightweight volume fallback covers texture-build delay.
- Restoring the stabilizers progressively reduces storm opacity and raises the
  storm deck while adding a restrained warm horizon lift.
- The Coreworks remnant is a localized background-only multiply treatment. It
  never crosses Aryn, the RD-42, dialogue portraits, props, or HUD.
- The sky state is composited at runtime over the approved landscape plates;
  the production art is not swapped, repainted, or contaminated with global
  scanlines.
- A small distant flock crosses the upper sky with independent wing phases.
- Existing foreground dust remains the fastest atmospheric layer.
- The Coreworks volcano keeps the approved plate intact. Runtime treatment is
  limited to a low-opacity orange crater pulse, heat shimmer, sparse warm
  summit motes, and isolated one- or two-pixel seam pulses. Runtime code must
  not redraw or trace the painted fissures.
- Reduced-motion mode freezes cloud drift, wing motion, dust drift, and the camp
  dog's movement cycle without removing any environmental information.

## Music

- Arrival on Veyra uses `Audio/super-frgmnts-overworld-loop.mp3` as its
  dedicated three-minute loop.
- The title and Foundry retain `Audio/super-frgmnts-foundry-loop.mp3`.
- Overworld playback runs slightly below the Foundry mix at 0.29 volume.
- Manual sound state, game pause, tab visibility, window focus, and mobile
  backgrounding all use the existing shared pause-and-resume lifecycle.

## Camp life

- Dras stands at local plate-two X 560, beneath the outpost's left shelter
  rather than in the empty approach.
- **Jane**, Dras's German shepherd camp dog, begins at local plate-two X 810.
  She renders at 85 × 68 pixels beside Dras's 96 × 112 canvas so her
  silhouette remains clearly subordinate to the human scale. Her bright
  collar keeps her readable against the outpost.
- Jane is a lightweight terrain-aware actor rather than a timed decorative
  rail. Her states are idle, wander, sniff, watch, approach, and return home.
  The complete 36-frame gait follows her physical travel direction. The full
  16-frame head-dip cycle plays once across three seconds for a selected sniff
  event, then resolves to the upright idle pose.
- Before first contact, Jane explores only the safe camp side of Dras. After
  first contact, she may travel across the continuous Overworld floor and
  investigate nearby Aryn. A forward ground probe prevents walking off future
  ledges, and her roaming boundary ends before the Coreworks transport.
- Jane remains decorative, non-solid, non-hostile, and unable to interrupt the
  first-contact sequence.

## Landing Flats collision correction

- The unpainted 168-pixel surface at local plate-one X 1376 has been removed.
- Only the continuous desert floor and the approved ship-hull traversal
  surfaces remain solid around the landing craft.

## Dialogue actions

Skip is the secondary left-hand action. Continue is the primary right-hand
action on every dialogue card. The skip confirmation follows the same spatial
grammar: Skip scene on the left, Keep listening on the right.
