# The Shard Foundry // Level Design Contract v1

**Status:** Episode 01 easy-to-medium balance candidate
**Runtime:** [`super_frgmnts.html`](../../../super_frgmnts.html)
**Population manifest:** [`episode-01-early-beta-v1.json`](episode-01-early-beta-v1.json)

This contract governs the critical path, encounter order, recovery economy, and
hazard placement for the first underground level. It supplements
[`UNIFIED-LEVEL-ONE-PLAN.md`](../UNIFIED-LEVEL-ONE-PLAN.md); when balancing
Episode 01, use the coordinates and acceptance rules here.

## Player experience target

The level should feel readable on the first attempt and satisfying on the
second. Difficulty comes from recognizing a verb and executing it cleanly, not
from surprise contact, narrow blind jumps, or overlapping threats.

The critical-path rhythm is:

**teach → confirm → combine → recover → breathe → final exam**

Target completion bands:

- first clear: 6:00–7:30;
- practiced clear: 4:30–6:00;
- eight-minute clock: pressure without requiring speedrun routing;
- expected damage: zero to two hits;
- expected deaths: zero for an experienced platform player, no more than one
  for a new player who understands the controls.

## Non-negotiable fairness rules

1. No hostile patrol, projectile, or active hazard begins inside a room link,
   mandatory landing, stabilizer interaction radius, or pickup collection radius.
2. A new mechanic appears alone before it is combined with another demand.
3. Every mandatory landing shows its full top surface before takeoff.
4. Primary runtime landings remain at least 170 pixels wide. The smallest
   painted connector is 127 pixels wide and is never paired with contact
   damage.
5. Baseline-required rises remain at or below 128 pixels. The first stabilizer and
   its powered freight lift are completed without jet-assist; the module is
   then guaranteed on the upper return before Deepworks or any route that
   needs the secondary boost.
6. Moving platforms do not carry enemies or mandatory pickups.
7. The electrified catwalk is safe for 2.35 seconds of every 3.6-second cycle,
   is live for 1.25 seconds, and grants 0.28 seconds of landing grace.
8. Damage knockback must send Aryn toward a stable surface, not into a repeated
   damage loop.
9. Recovery hearts appear after challenge beats. They never sit on ordinary
   spawns or room-transition lines.
10. Deepworks contains no enemies or contact hazards. Its challenge is the
    committed drop and readable jet-assisted return.
11. The heavy-rifle Vesperite obstruction is a physical containment cage on
    the deck, not a full-height energy wall. Upper traversal may continue, but
    the Uplink objective remains locked until three direct rifle hits clear it.
12. The Uplink Gate opens only when twelve Vesperite Fragments, two
    stabilizers, and the mandatory Vesperite lock are complete.
13. A major power-up has at least 240 pixels of route separation from another
    collectible and a safe acquisition apron before the next hostile lane.
14. Runtime platforms use the unified 16-bit industrial module; zone color is
    a restrained navigation accent, not a different material per room.
15. Every critical-path beat should strengthen at least one of the platformer
    pillars: **challenge, recovery, discovery, and exploration**.
16. Horizontal background silhouettes must tell the truth about collision.
    The repeated false junction at local `y = 600`, between the collision-backed
    ledges ending at `x = 646` and beginning at `x = 976`, is painted into
    cavern negative space. Only the real runtime platform may span that gap.

## Seven-seam portal system

Every boundary between the eight horizontal plates uses the same full-height
concrete-and-steel divider, paired side-profile door assemblies, a `128 × 24`
collision bridge at the local deck height, and foreground-concrete occlusion.
The steel housing remains permanently visible; only its translucent pressure
membrane retracts. This covers the repeated and mirrored background joins
without exposing an art seam and gives every area crossing the same
disappear-and-emerge spatial language.

| Boundary | Transition | Floor | Portal rule |
| --- | --- | ---: | --- |
| `WIDTH × 1` | Foundry Intake → Breathing Chamber | Upper `y = 338` | Cyan; always available and proximity-open |
| `WIDTH × 2` | Foundry → Refinery | Upper `y = 338` | Red until the Foundry stabilizer; green and proximity-open afterward |
| `WIDTH × 3` | Compression Line → Pressure Exchange | Middle `y = 600` | Cyan; always available and proximity-open |
| `WIDTH × 4` | Refinery → Biolab | Middle `y = 600` | Cyan; always available and proximity-open |
| `WIDTH × 5` | Culture Vats → Specimen Stabilizer | Upper `y = 338` | Cyan; always available and proximity-open |
| `WIDTH × 6` | Biolab → Uplink | Lower catwalk `y = 1508` | Red until the Biolab stabilizer; green and proximity-open afterward |
| `WIDTH × 7` | Signal Spine → Uplink Gate plate | Middle `y = 600` | Cyan; always available and proximity-open |

Ordinary cyan portals do not announce themselves and retract in `0.58` seconds,
so they are open before a running Aryn reaches the concrete. Objective locks
retain the deliberate `1.25`-second opening beat. Once Aryn's complete
collision body clears the opposite housing, the pressure membranes reform in
`0.50` seconds for ordinary passages or `0.78` seconds for objective locks.
Returning toward a closing lock safely reverses it. The supplied shimmer cue
marks opening, closing, and safety reversals without replacing the fixed
physical housing. Once fully closed, the proximity sensor remains latched
while Aryn is still inside its radius; it rearms only after she leaves the
radius or deliberately turns back toward the door. A normal exit therefore
produces exactly one opening and one closing cycle.
Enemy annihilation never locks a seam portal, and Vesperite Fragment recovery
remains a final Uplink Gate requirement rather than an intermediate door tax.
The custom Uplink bulkhead remains separate and still requires twelve
fragments, both stabilizers, and the cleared physical Vesperite lock.
The Biolab/Uplink objective lock uses a `636 × 24` collision-backed approach
at `y = 1508`, exactly joining the mirrored Biolab lower catwalk to the Uplink
lower catwalk. Its paired housings alone render 24 pixels above the generic
seam anchor so their feet meet that walking plane; the membrane proximity
threshold, player collision, and tunnel floor remain at `y = 1508` rather
than the lower world ground at `y = 1604`.

## Zone-by-zone critical path

### Foundry // Plates 0–1

**Purpose:** teach the complete movement language and establish the
restore-the-room loop.

#### Plate 0 // Foundry Intake

- Spawn apron is combat-free.
- The first Vesperite Fragment sits on the low, obvious route.
- A recurring three-hit Chitin Sentinel introduces the primary combat grammar
  on a broad deck with retreat space.
- The second fragment leads upward through generous 184–210-pixel platforms.
- The moving bridge has only 110 pixels of horizontal travel and no enemy on
  its landing.
- The Squircle Minion visibly circles the full perimeter of an upper platform
  instead of behaving like a stationary prop.

**Exit state:** player understands the baseline jump and moving-platform
language without bypassing the Breathing Chamber lift.

#### Plate 1 // The Breathing Chamber

- Entry is upper-left and intentionally becomes a downward route.
- One Core Leech occupies the middle-air sightline but not a landing.
- Chitin Sentinel occupies a separate ground lane capped at local
  `x = 760–1100`, leaving the stabilizer apron clear.
- The deck ends at the dormant stabilizer on the right.
- The first recovery heart sits at world `(WIDTH + 1130, 1480)`, after the
  descent encounter and before the lift return.
- Restoring the stabilizer clears the chamber, starts the freight lift, and
  turns the upper Atmosphere Lock green.
- A solid concrete-and-steel divider occupies the right-hand room boundary and
  spans the full world seam from `y = 0–1882`; there is no open cavern gap above
  or below it.
- The side-profile Atmosphere Lock is the divider's one passage. Aryn
  approaches it from the left through the cross-seam catwalk at `y = 338–362`. An original door
  face guards the Foundry side and a mirrored door face guards the Refinery
  side. Both `80 × 206` faces bottom-align at `y = 362` against the `128`-pixel
  divider so no painted seam or floor art remains exposed.
- Both seals are red while offline, turn green when the Foundry stabilizer is
  restored, and retract sideways on approach. A continuous collision floor
  bridges the `44`-pixel gap between the painted catwalks. A single full-height foreground concrete pass
  replaces the former black striped patch and occludes Aryn while she crosses
  inside the wall, so she disappears into one face and emerges from the other
  without a double-composited doorway slice.
- The runtime sizes its backing canvas from the browser's actual displayed
  game area and snaps the camera to that physical-pixel grid. The decorative
  frame no longer changes the canvas content ratio. This prevents Chrome from
  fractionally resampling the concrete divider on a second, distorted grid
  while Aryn runs toward or away from it.
- Jet-assist sits alone beyond the open Atmosphere Lock at world
  `(WIDTH × 2 + 240, 280)`, more than 240 pixels from the nearest collectible.
  It cannot be reached until the stabilizer powers the freight lift and the
  player crosses the restored lock.
- The first stabilizer progressively starts the ventilation rotors across the
  Foundry and Refinery sectors.

**Exit state:** one stabilizer online; player has performed drop, interaction,
lift, and lock crossing before receiving the assisted-return verb.

### Refinery // Plates 2–3

**Purpose:** teach the heavy rifle, lock in route-clearing knowledge, and make
Deepworks meaningful.

#### Plate 2 // Compression Line

- Heavy rifle waits on a safe deck apron at world
  `(WIDTH × 2 + 700, 1518)`.
- The closest Vesperite Fragments remain at least 280 pixels away on the route.
- A second Core Leech patrols the separated upper return lane after the
  Atmosphere Lock, with stable deck beneath it.
- A Kihunter introduces the air lane beyond the acquisition beat.
- The physical Vesperite containment cage begins at local `x = 1280`.
- A Chitin Sentinel occupies the far ground lane beyond the cage. Neither
  hostile overlaps the weapon pickup or rifle firing apron.

**Exit state:** player owns the rifle and has cleared one deliberate
three-shot obstruction.

#### Plate 3 // Pressure Exchange

- Sova patrols local `x = 390–700`; the recurring Chitin Sentinel begins at
  local `x = 1210`. Neither can enter the hazard footprint.
- A 160-pixel thermal purge vent begins at local `x = 900`. Its cycle is
  1.90 seconds dormant, 0.55 seconds of amber shutter warning, and 0.95 seconds
  of visible vertical exhaust. The player waits for the purge, then makes one
  readable jump with stable runway on both sides.
- The only required Deepworks entrance is inside this plate.
- The plate's Vesperite Fragment is below the deck at world
  `(WIDTH × 3 + 920, 1748)`.
- Deepworks has no enemy, no hazard, and a 212-pixel return rise that the
  guaranteed jet-assist can clear.

**Exit state:** player has demonstrated Deepworks entry and return once.

### Biolab // Plates 4–5

**Purpose:** test timing, then combine separated aerial and ground combat
before the second stabilizer.

#### Plate 4 // Culture Vats

- Ember Wasp is guaranteed in the upper-air lane; a Chitin Sentinel owns the
  ground lane. Their patrols do not share a mandatory landing.
- The electrified catwalk is the zone's single timing test.
- The safe phase is longer than the live phase and the first 0.28 seconds
  after landing cannot damage Aryn.
- A recovery heart at world `(WIDTH × 4 + 1340, 970)` rewards the timing beat.
- The credit cache was removed from the normal deck so it cannot distract the
  player during the hazard lesson.

**Exit state:** player has read and crossed the electric cycle.

#### Plate 5 // Specimen Stabilizer

- Seam Hunter owns the early ground lane; Chitin Sentinel guards the later
  approach without entering the stabilizer apron.
- A third Core Leech patrols the early upper lane, separated vertically from
  Seam Hunter and the ground Sentinel.
- The far-right stabilizer apron remains enemy-free.
- The second curated Deepworks entrance is optional.
- A seven-credit cache sits below at world
  `(WIDTH × 5 + 920, floor 1816)`.
- The Biolab stabilizer begins at local `x = 1180`, after the mirrored descent
  rather than at the room entrance.
- Activation reports **Biolab**, authorizes Uplink access, and leaves a clear
  recovery pause before the final zone.
- The second stabilizer starts every remaining Deepworks and Uplink ventilation
  rotor, making the restoration state visible across all later shafts.

**Exit state:** two stabilizers online; player may carry the optional Deepworks
credits.

### Uplink // Plates 6–7

**Purpose:** short, legible final exam followed by a clean exit read.

#### Plate 6 // Signal Spine

- Skree and Chitin Sentinel begin in separated lanes far enough from the zone
  link to be seen before contact.
- The broad deck repeats the rifle-versus-armor test without stacking both
  enemies on one mandatory landing.
- A recovery heart at world `(WIDTH × 6 + 1340, 970)` waits on the upper route
  after the Sentinel.
- The plate contains one low fragment and no environmental hazard.

**Exit state:** player has cleared or consciously bypassed the armored guard
and enters the final plate with a recovery opportunity.

#### Plate 7 // Uplink Gate

- Seam Lurker patrols the underside of the upper catwalk at `y = 362`,
  physically rooted by two visible attachment brackets. It never shares the
  deck hazard footprint.
- A 240-pixel broken arc coupler begins at local `x = 520`. It is recessed
  into the walking surface with explicit end rails rather than resting on the
  deck like loose machinery. Its 1.6-second discharged state and 0.6-second
  warning are followed by a 1.8-second live state. The intended solution is
  the insulated upper transfer, a read-and-run floor crossing, or the earned
  jet-assist. The active discharge is a compact branching cyan-white 16-bit
  sprite rather than a procedural parallel waveform.
- Pale Watcher patrols local `x = 880–1100`, after the coupler but before the
  final approach. Its patrol ends 368 pixels before the Wound-lock membrane,
  preserving a calm recovery runway after the room's last threat.
- The twelfth Vesperite Fragment sits in the left Uplink maintenance alcove at world
  `(WIDTH × 7 + 430, 548)`, 788 pixels before the gate trigger.
- The gate never claims to be open while a stabilizer or the Vesperite lock remains
  incomplete.
- Wound access is drawn directly into a room-specific `1672 × 941` lower-half
  Uplink environment plate at world `y = 941`. The deck, lower-third terrain,
  rock, frost, crystals, pipes, right wall, and narrow side-entry pressure
  opening are one authored image rather than layered gate sprites. Aryn always
  approaches from the left. The blue-violet membrane's visible contact edge
  is local `x = 1468`; the authored wall occlusion begins at local `x = 1580`.
- A small weathered `DANGER / ACTIVE WORK` placard is physically bolted into
  the pipe-and-rock structure above the opening. It remains baked into both
  doorway states as worksite storytelling, never as a floating status label.
- Completing all requirements blends only the doorway interior from locked to
  open over `0.72` seconds with the supplied shimmer cue. Every environment
  pixel outside the membrane remains fixed. The HUD, mission line, and unlock
  announcement communicate requirements so the threshold does not become a
  pasted-on status panel.
- Aryn passes into the authored boundary and is hidden by replaying the
  far-right `92`-pixel environment slice as foreground before the Wound
  descent. The previous freestanding front-facing `444 × 376` frame, isolated
  side-lock sprite, clean concrete slab, and permanent `WOUND ACCESS` label
  are retired. No magical ring, floating rectangle, or dashed barrier is
  permitted.

**Exit state:** clear boss-transition read, no enemy or hazard inside the gate
footprint. Entering the complete gate freezes Foundry state and establishes
the safe-bay checkpoint for The Wound.

## Population and economy

| Category | Count | Placement rule |
| --- | ---: | --- |
| Vesperite Fragments | 12 | Four in Foundry, three in Refinery including one Deepworks fragment, three in Biolab, and two in Uplink |
| Recovery hearts | 3 | After Foundry stabilizer approach, Biolab electric beat, and Uplink armored beat |
| Atmospheric stabilizers | 2 | End of Foundry plate 1 and end of Biolab plate 5 |
| Foundry-level credit caches | 2 | Foundry Intake deck and optional Biolab Deepworks |
| Power-ups | 2 | Jet-assist in Foundry; heavy rifle before Refinery obstruction |
| Required Vesperite locks | 1 | Refinery plate 2, three direct rifle hits |
| Authored floor hazards | 2 | Timed Refinery thermal purge and route-choice Uplink arc coupler |
| Electrified platforms | 1 | Biolab plate 4 |
| Curated Deepworks entrances | 2 | Required fragment route in plate 3; optional cache route in plate 5 |
| Enemies | 18 | Seven recurring Chitin Sentinels plus eleven spaced support enemies across ten active families, including three Core Leeches |

Credits and full annihilation remain optional. Vesperite Fragments, both
stabilizers, and the Vesperite lock are completion requirements. The fragments
retain residual harmonics from the pulse, giving Aryn evidence she can use to
trace it toward its source.

## Encounter grammar

Each encounter must resolve to one of these readable shapes:

- **lane:** one ground enemy, flat retreat space, no hazard;
- **air read:** one airborne enemy with a stable floor beneath it;
- **split tier:** one air enemy and one ground enemy separated by at least one
  full traversal tier;
- **timing:** one hazard, no contact enemy on its landing;
- **guard:** one durable enemy before a reward or transition, never inside it.

No encounter may combine a moving platform, active hazard, projectile shooter,
and contact enemy in the same mandatory landing.

## Playtest acceptance

Promotion requires all of the following:

- a no-damage clear is possible without exploiting enemy despawns;
- no room transition produces damage within the first second;
- no recovery heart is collected by a standard room review spawn;
- the Foundry stabilizer apron and Biolab stabilizer apron stay enemy-free for the full
  patrol cycle;
- the Vesperite obstruction requires three direct rifle hits and the Uplink
  remains unavailable until it is cleared;
- the Deepworks fragment and optional cache can both be recovered and exited
  using keyboard and touch controls;
- the electric platform always shows a full safe phase between live phases and
  never damages during landing grace;
- all twelve fragments remain reachable after taking the intended route;
- desktop and 390 × 844 portrait runs show the next landing, threat, or reward
  before commitment;
- desktop HUD displays separate large stabilizer and Vesperite Fragment counts without
  covering play space; portrait uses the compact mission read;
- two stabilizers plus twelve fragments plus the cleared Vesperite lock open the
  Uplink Gate with no contradictory HUD or accessibility announcement;
- the Uplink Gate carries remaining mission time, score, damage, credits, jet
  assist, seeker tier, and heavy rifle into The Wound;
- the final fragment requires deliberate travel before the Uplink Gate and cannot
  trigger gate contact during its collection;
- defeating Seam Hunter cannot end the run before Wound-touched Vesperite
  recovery; and
- recovery fades to black and returns Aryn to the surface without exposing a
  reload or accepting hidden movement input.
