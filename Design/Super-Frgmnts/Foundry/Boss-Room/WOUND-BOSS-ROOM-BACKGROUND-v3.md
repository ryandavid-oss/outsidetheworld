# SUPER FRGMNTS // The Wound Wide Boss Arena

**Status:** Approved v3 spatial redesign implemented in the isolated boss trial

## Spatial contract

- Master room: **2,580 × 1,882 px**
- Main combat deck: **y = 1,360**
- Portal arrival bay: **x = 0–250**
- Left construction lift: **x = 250–570**
- Clear combat runway: **x = 570–1,990** (**1,420 px**)
- Right construction lift: **x = 1,990–2,310**
- Wound threshold: **x = 2,310–2,580**
- Seam Hunter patrols inside the clear runway; his visible 448 px walk render
  does not enter either fixed lift tower.
- The desktop camera frames Aryn and the living boss around their shared
  midpoint. After the boss is defeated, normal player-led tracking resumes.
- The room retains exactly three continuously moving construction platforms:
  two vertical lifts and one upper horizontal gantry.
- The portal staging zone is safe until Aryn crosses x = 670 into the combat
  runway or initiates combat by landing a shot.
- Heavy-rifle bolts receive a **1.8-second boss-trial travel window** and are
  culled against the room bounds instead of the current camera. This allows a
  shot to cross the 1,420 px runway without deciding the rifle's final global
  range, damage, or ammunition economy.

The wider room now supports a provisional pursuit-and-elevator trial. Seam
Hunter has **50 hit points**, and rifle impacts damage his full authored body
from either direction. There is no frontal ricochet, face-only requirement,
rear-only requirement, or pass-through/levitation window.

## Provisional pursuit-and-elevator loop

On the main deck, Seam Hunter continuously tracks Aryn. He closes long gaps at
**160 px/s**, transitions through **108 px/s**, and slows to **72 px/s** near
her. Velocity ramps instead of snapping. Aryn must remain behind him for
**0.16 seconds** to earn a turn: Seam Hunter brakes for **0.22 seconds**, flips
once during the **0.7-second** turn, then commits forward for **0.55 seconds**
at up to **126 px/s** before reconsidering. He uses the existing readable sweep
within 310 px. His body remains solid, so Aryn must disengage toward one of the
two construction lifts rather than run through him.

Normal jumping does not fool him. If Aryn reaches at least **190 px** above
the main deck for **0.25 seconds**, Seam Hunter loses her position and enters a
**1.6-second** confusion state. If she remains elevated afterward, he searches
slowly without tracking her live position or attacking. Returning to the deck
restores pursuit and rearms the confusion response for the next elevator
escape. The continually moving lift naturally carries Aryn above the boss's
horizontal rifle line, keeping the shooting advantage brief.

Blind-search reversals are direction-aware: Seam Hunter turns only when he is
moving into a patrol boundary, then travels away from it. Merely remaining
inside the boundary tolerance cannot retrigger the turn every frame.

His five-second laser attack captures Aryn's lower-body position when its
charge begins, clamps that target to a **downward 11.5–35.5°** firing angle,
and commits to the resulting deck impact point. A faint diagonal charge line
telegraphs the locked path. The active beam uses the existing sheet's sampled
red-and-white cross-section as one thick procedural beam, while the creature
holds its final pre-beam red-eye pose so the old horizontal beam is not drawn.
Damage follows the same diagonal segment and visible active frames. The aim
never tracks after commitment, and entering elevator confusion cancels the
laser. At the first damaging frame, a **12-frame, 65 ms-per-frame** cosmetic
plasma impact plays at the locked deck endpoint. It adds no damage or collision.
See
[`Laser-Impact/WOUND-LASER-GROUND-IMPACT-v1.md`](Laser-Impact/WOUND-LASER-GROUND-IMPACT-v1.md).

The boss-trial rifle uses a **0.30-second** firing cycle, up from 0.46 seconds.
This is isolated playtest tuning and does not settle global rifle cadence,
damage, ammunition, or heat. The five-second laser cadence and visible damage
timing remain unchanged.

## Death and encounter release

The lethal rifle hit now begins a dedicated **25-frame, 2.675-second** death
sequence rather than removing Seam Hunter immediately. Attacks, pursuit,
collision, and further damage stop at once, while Aryn retains control and the
three construction platforms continue moving. Frame 13 produces a cosmetic
deck-impact cue. Victory and Wound access wait until frame 24 settles, after
which that final corpse pose remains visible. See
[`Seam-Hunter-Death/SEAM-HUNTER-DEATH-v1.md`](Seam-Hunter-Death/SEAM-HUNTER-DEATH-v1.md).

## Runtime texture contract

The wide master is split into two pixel-identical runtime slices so no shipped
texture exceeds the 2,048 px portability ceiling:

- Left: **1,290 × 1,882 px**
- Right: **1,290 × 1,882 px**

The renderer places the slices at world x = 0 and x = 1,290 with no overlap,
scaling, or decorative seam.

## Asset paths

- Image-generation source:
  `Raw/wound-boss-room-background-master-v3-source.png`
- Exact-size master:
  `Raw/wound-boss-room-background-master-v3.png`
- Runtime left:
  `Images/Game/Super-Frgmnts/foundry-wound-boss-room-background-runtime-v3-left.png`
- Runtime right:
  `Images/Game/Super-Frgmnts/foundry-wound-boss-room-background-runtime-v3-right.png`
- Title artwork:
  `Images/Game/Super-Frgmnts/foundry-wound-boss-room-title-runtime-v3.png`
- Scale review:
  `Reviews/wound-boss-room-scale-review-v3.png`
- Sweep review:
  `Reviews/wound-boss-room-sweep-review-v3.png`
- Construction-room review:
  `Construction-Lifts/Reviews/wound-construction-lifts-room-review-v2.png`

Regenerate and verify:

```sh
python3 tools/build_super_frgmnts_wound_boss_room.py
python3 tools/build_super_frgmnts_wound_construction_lifts.py
python3 tools/verify_super_frgmnts_wound_boss_room.py
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```

## Image-generation record

The built-in image-generation workflow recomposed the approved v2 room as one
wide chamber. The build then establishes the exact deck line and deterministically
splits the master for runtime.

Final prompt:

> Recompose the approved Wound room into one seamless 11:8 landscape chamber,
> preserving its crisp pixel-art materials and restrained palette. Give the
> far-left portal, sparse central boss arena, and far-right raw geological
> Wound distinct territory. Keep a continuous combat deck, machinery-filled
> underdeck, and visually quiet runtime lift zones. Background only: no lifts,
> platforms, characters, boss, player, hazards, text, HUD, logo, or watermark.

## Playable route

`super_frgmnts.html?preview=wound-boss&autostart=1`
