# Aryn Asset Manifest

Status: pose-choreography review. No runtime cutscene frames have been created and no gameplay code has been changed for this work.

Contact sheet: [aryn-reference-contact-sheet-v1.png](./aryn-reference-contact-sheet-v1.png)

## Canon decision

The `LIVE ARMOR` group is the provisional source of truth because these files currently render Aryn during Episode 01. This is a technical classification, not final creative approval. Rylee should confirm the command-rest image as the definitive hero/ready pose before any new cutscene artwork is built.

New Aryn poses should preserve the live set's 112 × 112 frame, body height, helmet silhouette, cyan visor, blue-violet armor, magenta shoulder plate, pixel density, and right-facing presentation. Do not interpolate from the Builder-era Signal Ranger art when a live armored reference exists.

## Live armored set — provisional canonical candidates

| Asset | Size | Current role | Cutscene reference value |
| --- | ---: | --- | --- |
| `aryn-command-rest-runtime-v1.png` | 112 × 112 | Default gameplay/ready pose | Primary body, helmet, backpack, and proportion anchor |
| `aryn-field-rest-runtime-v1.png` | 112 × 112 | Loaded supporting pose; not selected by the current player-state resolver | Secondary stance comparison only |
| `aryn-run-ludo-runtime-v2.png` | 896 × 112, 8 frames | Live Episode 01 run | Weight transfer, shoulder rotation, and limb construction |
| `aryn-jump-ludo-runtime-v1.png` | 784 × 112, 7 frames | Live jump and landing | Crouch, extension, and recovery poses |
| `aryn-drop-ludo-runtime-v1.png` | 448 × 112, 4 frames | Live drop-through pose | Front-facing body and separated arm reference |
| `aryn-impact-light-ludo-runtime-v1.png` | 672 × 112, 6 frames | Live light-damage reaction | Small torso turn and recovery reference |
| `aryn-impact-heavy-ludo-runtime-v1.png` | 784 × 112, 7 frames | Live heavy-damage reaction | Strong torso turn and lowered stance reference |
| `aryn-death-ludo-runtime-v1.png` | 1344 × 112, 12 frames | Live defeat sequence | Extreme silhouette reference only |
| `aryn-jetpack-ludo-runtime-v1.png` | 1792 × 112, 16 frames | Live Jet Assist sequence | Best existing backpack-energy reference |

All files above live in `Images/Game/Super-Frgmnts/`.

## Supporting references

| Asset | Size | Use | Restriction |
| --- | ---: | --- | --- |
| `aryn-dialogue-portrait-runtime-v3.png` | 512 × 512 | Helmet, visor, shoulder armor, and color hierarchy | Do not copy its high-detail proportions directly into 112-pixel sprites |
| `aryn-armor-change-runtime-v1.png` | 672 × 672, 36 tiles | Armor assembly and suit relationship | Multi-state storyboard; individual tiles are not automatically canonical |
| `aryn-fleet-apparel-walk-sheet-v1.png` | 340 × 580 | Unarmored identity and palette context | Not a source for armored body proportions |

## Archive references

- `aryn-run-ludo-runtime-v1.png` is superseded by run v2.
- The four `aryn-rifle-*-ludo-runtime-v1.png` sheets belong to the retired Heavy Rifle. They may help explain reaching and braced arm positions, but the rifle, grip, and shoulder posture must not leak into the pickup cutscene.
- `aryn-flight-suit-run-runtime-v1.png` and `aryn-flight-suit-jump-runtime-v1.png` depict the alternate flight suit, not the armor worn during the Prism encounter.

## Legacy Builder fallbacks

The files under `Images/Builder/` predate the current Ludo-style armored family:

- `aryn-run-10pose-balanced-gait-sheet.png`
- `signal-ranger-idle-focused-v2.png`
- `signal-ranger-jump-takeoff.png`
- `signal-ranger-jump-airborne.png`
- `signal-ranger-crouch.png`
- `signal-ranger-run-10pose-headlocked-armswing-sheet.png`
- `signal-ranger-run-20frame-headlocked-armswing-sheet.png`
- `signal-ranger-run-20frame-headlocked-armswing.png`
- `signal-ranger-run-balanced-gait.png`

Important implementation note: several of these remain referenced as compatibility/fallback assets in `super_frgmnts.html`. Their technical presence does not make them visual canon for new Episode 01 art. Removing or replacing those references is outside this review pass.

## Proposed Prism pickup pose sequence

This sequence is intentionally limited to five held poses at the existing 112 × 112 scale:

1. Command rest — unchanged canonical start frame.
2. Reach — torso remains anchored; forward arm extends toward the floating Prism Splinter.
3. Grasp — Prism Splinter is held close to the shoulder; hand detail may be implied at this resolution.
4. Attach — Aryn turns slightly and places the module against the PACK; the precise connection is covered by a prismatic flash.
5. Recovery — return to command rest with a brief PACK glow overlay.

The likely reference recipe is command rest + selected run/jump torso pixels + a restrained arm adaptation informed by the archived rifle-draw sequence. Each pose should be drawn from the same base, not generated independently.

## Approval gate before drawing

Confirmed by Rylee:

1. `aryn-command-rest-runtime-v1.png` is the definitive armored hero pose.
2. Aryn remains right-facing throughout the insert.
3. The PACK attachment staging is left to the artist's judgment.

## Pose concept v1

Review files:

- `aryn-prism-install-pose-concept-v1.png` — transparent pose concept
- `aryn-prism-install-pose-concept-v1-chroma.png` — preserved generation source

The five approved-reference beats are ready, reach, grasp, attach, and activated recovery. In the attachment pose, Aryn reaches behind the magenta shoulder and presses the module onto the upper PACK beside the antenna base. A concentrated green-cyan flare hides the exact mechanical connection.

This generated sheet is a choreography reference only. Its figures are larger and more detailed than the live 112 × 112 sprite family and must not be connected to `super_frgmnts.html`. After Rylee approves the movement, each pose must be rebuilt on the Command Rest 112 × 112 grid with the live palette and silhouette.

## Full-screen comic sequence v1

Rylee selected a large comic-panel treatment instead of an in-world 112 × 112 stop-motion sequence. Three review panels now live in `Design/Super-Frgmnts/Aryn/Prism-Cutscene/`:

1. `aryn-prism-comic-panel-01-reach-v1.png` — Aryn reaches toward the hovering Prism Splinter.
2. `aryn-prism-comic-panel-02-install-v1.png` — mechanical close-up of the module seating beside the PACK antenna base.
3. `aryn-prism-comic-panel-03-activate-v1.png` — installed module energizes the PACK and refracts three controlled rays.

All three panels are exactly 1672 × 941, matching the native game canvas. `aryn-prism-comic-sequence-review-v1.png` presents the sequence together for approval.

The panel files remain design assets only. They have not been added to the production asset registry, preloader, progression state, or render loop. Integration requires a separate approval after visual review.
