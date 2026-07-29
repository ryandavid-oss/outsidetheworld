# SUPER FRGMNTS // The Wound Tall Boss Arena

**Status:** Superseded by the approved wide-arena v3 contract

## Approved encounter contract

- Runtime plate: **1,672 × 1,882 pixels**
- Main combat deck: **y = 1,360**
- Seam Hunter walk render: **448 × 448 pixels**
- Seam Hunter sweep render: **560 × 448 pixels**
- Seam Hunter remains physically grounded on the main deck.
- Per-frame alpha-bound compensation places his visible feet on the deck.
- Aryn can board the construction system with her normal jump.
- The room contains exactly three platforms: a vertical lift on each side and
  one horizontal traveling gantry platform above.
- Fixed guide rails, suspension cables, steel housings, and amber work lights
  make the platforms read as original emergency-construction equipment.
- The implemented modular lift artwork is documented in
  `Construction-Lifts/WOUND-CONSTRUCTION-LIFT-KIT-v1.md`.
- The two vertical lifts move continuously at a slightly reduced speed; they
  never pause or dwell.
- Platforms reposition Aryn; they do not add hazards or a new attack.
- Seam Hunter's glowing eyes and teeth form a compact **104 × 112 px**
  provisional face weak spot that can be damaged from the front.
- Shots entering from behind can damage a broad rear body zone.
- Front shots visibly rebound from his armor without reducing his 20 trial hit
  points unless they intersect the face weak spot.
- Face hits use the ordinary damage flash and particles, a distinct impact
  sound, and a brief cooldown-limited stagger. They do not draw a circular
  weak-spot marker.
- Seam Hunter moves as a deliberate colossus: slow stalking, restrained
  surges, and long readable turns.
- His facing locks when the attack windup begins. The sweep and recovery create
  the primary crossover and rear-punish opportunity.
- A missed sweep adds a short stationary recovery bonus.
- Seam Hunter uses the approved 36-frame laser-eye animation as a secondary
  attack once every **5 seconds**, measured start to start. A melee commitment
  or turn may delay the next use rather than interrupting an existing action.
- The laser sequence runs at the supplied **50 ms per frame** timing:
  frames 0–14 telegraph/charge, frames 15–30 emit the damaging beam, and
  frames 31–35 recover.
- The supplied sheet provides Seam Hunter, his eye charge, and the near-eye
  beam art. The outermost beam column of each active source frame is extended
  to the arena edge, carrying the baked beam's exact centerline, thickness,
  red-pink body, white-hot core, and frame-to-frame flicker through the join.
- Laser damage exists only during visible emission frames 15–30 and can damage
  Aryn at most once per use. Seam Hunter locks his facing for the sequence.
- A successful face hit can interrupt the laser sequence through the existing
  cooldown-limited face stagger.
- While Seam Hunter is active, Aryn keeps the heavy rifle shouldered whenever
  it is selected. Switching to the pack still stows it; selecting the rifle
  again immediately restores the ready pose. The normal Foundry auto-stow
  delay is unchanged.
- High-ground interception begins only after a grace period, travels toward a
  captured position rather than continuously predicting Aryn, and ends after a
  short fixed commitment.
- His behavior vocabulary remains stalk, commit, surge, intercept, turn/guard,
  and reset; no encounter phase or enraged form has been added.
- His damaging sweep remains limited to visible attack frames 14–19.
- Body contact remains safe in this trial.

The collider, sweep footprint, state timing, rifle damage, rifle heat behavior,
and final platform coordinates remain playtest values.

Laser runtime assets:

- Source sheet:
  `Design/Super-Frgmnts/Foundry/Enemies/Tall-Gaunt-Alien/Raw/seam-hunter-laser-eyes-source-v1.png`
- Source metadata:
  `Design/Super-Frgmnts/Foundry/Enemies/Tall-Gaunt-Alien/Raw/seam-hunter-laser-eyes-source-v1.json`
- Runtime sheet:
  `Images/Game/Super-Frgmnts/enemy-tall-gaunt-alien-laser-eyes-sheet-v1.png`
- The runtime sheet horizontally registers every frame to the planted-foot
  anchor in frame 0. The supplied source sheet remains unchanged.
- Animation review:
  `Design/Super-Frgmnts/Foundry/Enemies/Tall-Gaunt-Alien/Reviews/seam-hunter-laser-eyes-preview-v1.gif`

## Asset paths

- Image-generation source:
  `Design/Super-Frgmnts/Foundry/Boss-Room/Raw/wound-boss-room-background-master-v2-source.png`
- Exact-size master:
  `Design/Super-Frgmnts/Foundry/Boss-Room/Raw/wound-boss-room-background-master-v2.png`
- Runtime plate:
  `Images/Game/Super-Frgmnts/foundry-wound-boss-room-background-runtime-v2.png`
- Walk-scale review:
  `Design/Super-Frgmnts/Foundry/Boss-Room/Reviews/wound-boss-room-scale-review-v2.png`
- Sweep-scale review:
  `Design/Super-Frgmnts/Foundry/Boss-Room/Reviews/wound-boss-room-sweep-review-v2.png`

Regenerate and verify:

```sh
python3 tools/build_super_frgmnts_wound_boss_room.py
python3 tools/build_super_frgmnts_seam_hunter_laser.py
python3 tools/verify_super_frgmnts_wound_boss_room.py
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```

## Generation record

The v2 plate was generated with the built-in image-generation workflow. The
approved v1 plate was supplied as the strict style and material reference.

Final prompt:

> Recompose The Wound as a single near-square 7:8 room approximately twice as
> tall. Match the approved plate's crisp hard-edged pixel density, deep navy,
> blue-black, charcoal, muted-purple stone, restrained cyan, magenta, and amber
> palette, portal-housing language, and raw Wound construction. Place a
> continuous heavy-metal combat deck across the width at roughly eighty
> percent height, leaving an enormous open vertical arena and a machinery-filled
> underdeck. Keep the inactive portal low on the far left and extend the dark,
> unlit Wound vertically through the far-right wall. Concentrate detail along
> the side walls, ceiling, Wound construction, and underdeck; keep the center
> sparse for a four-times-player-height boss and runtime platforms. Background
> only: no active portal, baked platforms, characters, boss, player,
> collectibles, hazards, text, HUD, logo, or watermark.

## Playable route

`super_frgmnts.html?preview=wound-boss&autostart=1`
