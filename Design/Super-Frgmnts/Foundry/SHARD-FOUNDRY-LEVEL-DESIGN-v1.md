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
   mandatory landing, relay interaction radius, or pickup collection radius.
2. A new mechanic appears alone before it is combined with another demand.
3. Every mandatory landing shows its full top surface before takeoff.
4. Primary runtime landings remain at least 170 pixels wide. The smallest
   painted connector is 127 pixels wide and is never paired with contact
   damage.
5. Baseline-required rises remain at or below 128 pixels. Jet-assist is
   guaranteed before Deepworks and any route that needs the secondary boost.
6. Moving platforms do not carry enemies or mandatory pickups.
7. The electrified catwalk is safe for 2.35 seconds of every 3.6-second cycle,
   is live for 1.25 seconds, and grants 0.28 seconds of landing grace.
8. Damage knockback must send Aryn toward a stable surface, not into a repeated
   damage loop.
9. Recovery hearts appear after challenge beats. They never sit on ordinary
   spawns or room-transition lines.
10. Deepworks contains no enemies or contact hazards. Its challenge is the
    committed drop and readable jet-assisted return.
11. The heavy-rifle Vesperite lock is visibly sealed on every traversal layer
    and cannot be bypassed before three direct rifle hits.
12. The Uplink Gate opens only when twelve Signal Shards, two stabilizers, and
    the mandatory Vesperite lock are complete.

## Zone-by-zone critical path

### Foundry // Plates 0–1

**Purpose:** teach the complete movement language and establish the
restore-the-room loop.

#### Plate 0 // Foundry Intake

- Spawn apron is combat-free.
- The first Signal Shard sits on the low, obvious route.
- The Ridge Skitter teaches firing on a broad deck with retreat space.
- The second shard leads upward through generous 184–210-pixel platforms.
- Jet-assist sits on the mandatory ascent at world `(936, 1170)`.
- The moving bridge has only 110 pixels of horizontal travel and no enemy on
  its landing.
- The Squircle Minion is an optional upper observation encounter, not a
  required landing blocker.

**Exit state:** player owns jet-assist and understands moving platforms.

#### Plate 1 // The Breathing Chamber

- Entry is upper-left and intentionally becomes a downward route.
- Core Leech occupies the middle-air sightline but not a landing.
- Clacker Beetle patrol is capped at local `x = 760–1120`, leaving the relay
  apron clear.
- The deck ends at the dormant stabilizer on the right.
- The first recovery heart sits at world `(WIDTH + 1130, 1480)`, after the
  descent encounter and before the lift return.
- Restoring the relay clears the chamber, starts the freight lift, and opens
  the upper Refinery threshold.

**Exit state:** one relay online; player has performed drop, interaction, lift,
and assisted return.

### Refinery // Plates 2–3

**Purpose:** teach the heavy rifle, lock in route-clearing knowledge, and make
Deepworks meaningful.

#### Plate 2 // Compression Line

- Heavy rifle waits on the deck at world `(WIDTH × 2 + 560, 1518)`.
- A Signal Shard on the same approach pulls the player past the weapon without
  hiding it.
- The Vesperite obstruction begins at local `x = 900`.
- Its boulder and full-height Vesperite lock make the three-hit requirement
  visible on the deck, middle tier, and upper route.
- Spore Wisp and Spring Fragment are vertically separated. Neither overlaps
  the weapon pickup or rifle firing apron.

**Exit state:** player owns the rifle and has cleared one deliberate
three-shot obstruction.

#### Plate 3 // Pressure Exchange

- Vesper Mite patrol is capped at local `x = 420–820`, away from the late-room
  descent landing.
- A 76-pixel thermal vent begins at local `x = 1008`. It is one readable jump
  with clear runway on both sides.
- The only required Deepworks entrance is inside this plate.
- The plate's Signal Shard is below the deck at world
  `(WIDTH × 3 + 920, 1748)`.
- Deepworks has no enemy, no hazard, and a 212-pixel return rise that the
  guaranteed jet-assist can clear.

**Exit state:** player has demonstrated Deepworks entry and return once.

### Biolab // Plates 4–5

**Purpose:** test timing, then combine separated aerial and ground combat
before the second relay.

#### Plate 4 // Culture Vats

- Vesper Flare owns the lower-air lane; Ember Wasp owns the upper-air lane.
  Their patrols do not share a mandatory landing.
- The electrified catwalk is the zone's single timing test.
- The safe phase is longer than the live phase and the first 0.28 seconds
  after landing cannot damage Aryn.
- A recovery heart at world `(WIDTH × 4 + 1340, 970)` rewards the timing beat.
- The credit cache was removed from the normal deck so it cannot distract the
  player during the hazard lesson.

**Exit state:** player has read and crossed the electric cycle.

#### Plate 5 // Specimen Relay

- Bastion Fragment is the elevated read; Seam Hunter owns the middle deck.
- Seam Hunter patrol is capped at local `x = 480–900`.
- The far-right relay apron remains enemy-free.
- The second curated Deepworks entrance is optional.
- A seven-credit cache sits below at world
  `(WIDTH × 5 + 920, floor 1816)`.
- The Biolab stabilizer begins at local `x = 1180`, after the mirrored descent
  rather than at the room entrance.
- Activation reports **Biolab**, authorizes Uplink access, and leaves a clear
  recovery pause before the final zone.

**Exit state:** two relays online; player may carry the optional Deepworks
credits.

### Uplink // Plates 6–7

**Purpose:** short, legible final exam followed by a clean exit read.

#### Plate 6 // Signal Spine

- Chitin Sentinel begins far enough from the zone link to be seen before
  contact.
- Its broad deck is the primary rifle-versus-armor test.
- A recovery heart at world `(WIDTH × 6 + 1340, 970)` waits on the upper route
  after the Sentinel.
- The plate contains one low shard and no environmental hazard.

**Exit state:** player has cleared or consciously bypassed the armored guard
and enters the final plate with a recovery opportunity.

#### Plate 7 // Uplink Gate

- Spore Wisp remains high and cannot fire while Aryn is in Deepworks.
- A 76-pixel arc leak begins at local `x = 900`.
- Pale Watcher patrol begins beyond the leak at local `x = 1110`, leaving more
  than one player-width of stable recovery runway between the two demands.
- The twelfth Signal Shard sits at the Uplink Gate at world
  `(WIDTH × 7 + 1284, 286)`.
- The gate never claims to be open while a relay or the Vesperite lock remains
  incomplete.

**Exit state:** clear boss-transition read, no enemy or hazard inside the gate
footprint. Entering the complete gate freezes Foundry state and establishes
the safe-bay checkpoint for The Wound.

## Population and economy

| Category | Count | Placement rule |
| --- | ---: | --- |
| Signal Shards | 12 | Four in Foundry, three in Refinery including one Deepworks shard, three in Biolab, and two in Uplink |
| Recovery hearts | 3 | After Foundry relay approach, Biolab electric beat, and Uplink armored beat |
| Atmospheric stabilizers | 2 | End of Foundry plate 1 and end of Biolab plate 5 |
| Foundry-level credit caches | 2 | Foundry Intake deck and optional Biolab Deepworks |
| Power-ups | 2 | Jet-assist in Foundry; heavy rifle before Refinery obstruction |
| Required Vesperite locks | 1 | Refinery plate 2, three direct rifle hits |
| Static contact hazards | 2 | Refinery thermal vent and final Uplink arc leak |
| Electrified platforms | 1 | Biolab plate 4 |
| Curated Deepworks entrances | 2 | Required signal route in plate 3; optional cache route in plate 5 |
| Enemies | 14 | Thirteen catalog families, with the legacy Spore Wisp repeated only at the final Uplink read |

Credits and full annihilation remain optional. Signal Shards, both stabilizers,
and the Vesperite lock are completion requirements.

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
- the Foundry relay apron and Biolab relay apron stay enemy-free for the full
  patrol cycle;
- the Vesperite lock cannot be crossed on the deck, middle tier, or upper tier
  while intact;
- the Deepworks shard and optional cache can both be recovered and exited
  using keyboard and touch controls;
- the electric platform always shows a full safe phase between live phases and
  never damages during landing grace;
- all twelve shards remain reachable after taking the intended route;
- desktop and 390 × 844 portrait runs show the next landing, threat, or reward
  before commitment;
- two relays plus twelve shards plus the cleared Vesperite lock open the
  Uplink Gate with no contradictory HUD or accessibility announcement;
- the Uplink Gate carries remaining mission time, score, damage, credits, jet
  assist, seeker tier, and heavy rifle into The Wound;
- defeating Seam Hunter cannot end the run before Wound-touched Vesperite
  recovery; and
- recovery fades to black and returns Aryn to the surface without exposing a
  reload or accepting hidden movement input.
