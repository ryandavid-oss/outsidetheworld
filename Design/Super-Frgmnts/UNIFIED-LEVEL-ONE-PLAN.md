# SUPER FRGMNTS // Unified Level 1 Plan

> Platform baseline: all new systems and promotion reviews follow
> [Native Apple Platform Baseline 2](IOS-PORTABILITY-BASELINE.md). The approved
> level and frozen browser game define migration parity; all new production
> implementation targets native iOS, iPadOS, and macOS.

## Locked world target

- Canonical level: **The Shard Foundry**
- Eight horizontal plates: two each for Foundry, Refinery, Biolab, and Uplink
- World dimensions: 13,376 × 1,882 pixels
- Three traversal layers: upper gantries, main deck, and Deepworks
- Eight-minute level timer
- Uplink Gate at the upper end of the eighth plate
- Down drops through one-way platforms and enters Deepworks
- Deepworks remains jump-exitable

## Current early-beta pass

The current pass assembles the approved systems into one intentionally scoped
Episode 01 run. It establishes:

- room order and dimensions;
- horizontal and vertical camera behavior;
- concrete-deck and Deepworks alignment;
- painted catwalk collision;
- runtime platform placement, thickness, color, and motion;
- complete Arrival-to-Uplink-to-Wound-to-surface reachability;
- desktop and portrait-mobile framing;
- a safe field-calibration lane between Dras's camp and the Coreworks surface
  transport;
- a physical, walkable transport deck whose one-shot energy vortex removes
  Aryn from the surface before the Foundry handoff;
- a shootable credit cache whose coins burst into the world and carry into the
  Foundry scene;
- two atmospheric stabilizers, twelve Vesperite Fragments, recovery hearts,
  and two credit caches;
- a jet-assist pickup, heavy-rifle pickup, and mandatory three-shot Vesperite
  obstruction;
- one cycling electrified platform and representative crawler, flying, and
  armored patrol enemies;
- an eight-minute mission clock and an optional full-annihilation score bonus;
- a state-preserving Uplink checkpoint into the production Seam Hunter
  encounter;
- explicit Wound-touched Vesperite recovery as the completion action; and
- a locked fade-to-black return to the complete Overworld surface.

### Foundry traversal pass

The first two plates are now authored as a deliberate opening sequence rather
than repetitions of the shared provisional route:

- **Foundry Intake** teaches the complete movement language with generous
  staging, a readable upward zigzag, one moving bridge, and aligned painted
  catwalk collision.
- **The Breathing Chamber** is a one-way fall that becomes an ascent when it
  breathes. Aryn enters from the upper-left room link, deliberately descends
  through the dormant chamber, and reaches the atmospheric stabilizer at a
  genuine deck-level dead end.
- Restoration powers two ventilation fans, clears the poisoned haze, energizes
  a full-height freight lift, and opens an upper-right route into Refinery.
- The deck-level Foundry/Refinery boundary is now a sealed service bulkhead. It
  never becomes a shortcut around the restored ascent.
- The cavern-window patch spans the mirrored seam between Foundry Intake and
  The Breathing Chamber. Its concrete sill aligns with the live Foundry deck;
  the view itself remains non-collidable environmental storytelling with
  restrained depth motes and a clearer restored state.

### Atmospheric-control reservation

- The approved stabilizer artwork has matched dormant and active alpha states.
- Both machines render at a reduced **336 × 588 world-pixel** art footprint,
  sunk eight pixels into the deck. Their original **420 × 735** logical
  interaction footprint remains intact, preserving the generous Down-input
  activation zone while keeping the Biolab/Uplink lock visually unobstructed.
- The first Foundry station crossfades through a 2.35-second restart sequence
  when Aryn approaches on the main deck and presses Down.
- The provisional **175 × 100 world-pixel** footprint refers to the embedded
  control interface, not the full environmental machine.
- Reserve one approachable stabilizer station near the conclusion of each
  two-plate zone: Foundry, Refinery, Biolab, and Uplink.
- Each station needs approximately 260 pixels of clear standing width and must
  remain reachable without a power-up.
- The Foundry prototype includes activation feedback, sound, and an
  accessibility announcement. Timer awards remain deferred until the timing
  rule is approved.
- Restoring the Foundry station now produces a room-scale response: conduit
  energy resumes, service lamps illuminate, two ventilation fans restart at
  offset beats, the contaminated haze recedes, and the freight-lift rail fills
  from the deck upward.
- A solid concrete-and-steel divider now spans the full Foundry/Refinery seam
  from ceiling to floor. Its only passage is the side-profile upper
  Foundry/Refinery Atmosphere Lock: the Foundry face is paired with a mirrored
  door face on the Refinery side, and both align to the upper floor bottom.
  Both faces remain red and physically closed until the restart completes.
  They then turn green and retract sideways on Aryn's approach. This updates
  the mission objective to **FREIGHT LIFT ONLINE // REFINERY ABOVE** and
  permits traversal into the third plate only from the upper cross tier. The
  enclosed wall tunnel supplies continuous floor collision and redraws its
  concrete as foreground, hiding Aryn during the crossing.
- This establishes the repeatable two-plate objective cadence:
  **enter zone → learn its traversal → find its stabilizer → restore the
  environment → unlock the next zone**.
- The concrete seam treatment now repeats at all seven boundaries between the
  eight plates. Five ordinary passages use cyan proximity-open seals. The
  `WIDTH × 2` Foundry/Refinery seal requires the Foundry stabilizer, and the
  `WIDTH × 6` Biolab/Uplink seal requires the Biolab stabilizer; both progress
  from red to green. Their floor distribution is upper, upper, middle, middle,
  upper, lower, middle across seams one through seven. Every instance shares
  a local bridged floor; the Biolab/Uplink lock uses a `636 × 24`
  collision-backed approach at lower-catwalk `y = 1508` to join the visible
  routes on both sides. A single full-height foreground concrete pass hides
  Aryn during traversal without double-compositing the doorway slice.
  The canvas backing store now matches the browser's displayed physical-pixel
  grid, the decorative frame sits outside the content box, and the rendered
  camera snaps to that same grid. This removes the second fractional resample
  that made the concrete texture shimmer during horizontal camera movement.
- Each door now separates its permanent steel housing from its pressure
  membrane. Only the membrane retracts; the machinery and indicator remain
  visible as a navigational landmark. After Aryn fully clears the opposite
  housing, the membrane reforms, and a return toward a closing door reverses
  it safely. A dedicated shimmer cue follows each open, close, and reversal.
- At each tunnel elevation, closed-door collision planes meet the visible
  outer membrane edges, 80 pixels beyond the concrete wall faces. Aryn stops
  where her body visibly contacts the bubble instead of overlapping it; away
  from the tunnel elevation, the full-height concrete wall retains its original
  collision plane.
- The pass evaluates traversal against four platformer pillars:
  **challenge, recovery, discovery, and exploration**. Varying the seam height
  makes room transitions part of route comprehension rather than a repeated
  upper-lane convention.
- Enemy annihilation and fragment recovery do not lock intermediate seam
  portals. Those systems remain exploration/reward goals until the custom
  Uplink bulkhead applies its final composite requirement.
- The current timing candidate is a four-minute initial reserve plus two
  minutes per restored stabilizer; this is intentionally not wired into the
  runtime yet.

This remains an early beta at the episode level. Credit values, store prices,
weapon tuning, enemy damage, and later-episode economy remain deliberately
provisional. The first-level platform, encounter, hazard, and recovery
placements now have a bounded balance candidate.

## Easy-to-medium level-design pass

The active shipping candidate is specified in
[`Foundry/SHARD-FOUNDRY-LEVEL-DESIGN-v1.md`](Foundry/SHARD-FOUNDRY-LEVEL-DESIGN-v1.md).
It locks the current critical-path encounter order and fairness rules while
leaving economy values and later-episode combat balance open.

- Foundry teaches movement and guarantees jet-assist beyond the restored
  Atmosphere Lock before any Deepworks entry.
- Refinery teaches the heavy rifle, makes the three-hit Vesperite lock
  non-bypassable, and contains the single required Deepworks fragment.
- Biolab owns the one electrified-platform timing test, places its recovery
  heart afterward, and moves its stabilizer to the end of the mirrored route.
- Uplink embeds the final arc leak into an earlier floor channel, separates it
  from the Pale Watcher, and preserves a 368-pixel recovery runway to a
  side-entry Wound threshold authored directly into the room-specific lower
  Uplink environment plate.
- Deepworks has exactly two curated entrances in this pass: a required,
  enemy-free fragment recovery in Refinery and an optional credit-cache route in
  Biolab.
- Every stabilizer apron, ordinary room link, mandatory landing, and pickup
  footprint remains free of initial contact damage.
- The Uplink Gate requires twelve fragments, both stabilizers, and the cleared
  Vesperite lock. It opens The Wound and establishes the boss checkpoint; it
  is not the Episode 01 completion card.

These are release-candidate placement values, subject to the playtest
acceptance checklist in the level-design contract. They should not be changed
as isolated coordinates without updating that contract and its verifier.

## Provisional artwork contract

- The expanded Foundry plate supplies the approved upper-gantry vocabulary.
- The legacy Refinery, Biolab, and Uplink plates remain at their original scale
  and are bottom-aligned beneath the upper gantry.
- Repeated plates alternate orientation and receive restrained zone color.
- Replacement art must preserve the existing world coordinates and collision
  surfaces so final artwork can be swapped without redesigning gameplay.
- The shared upper plate no longer displays the non-collidable center junction
  at local `y = 600`. A mirrored 16-bit negative-space patch exposes the real
  330-pixel gap between `x = 646` and `x = 976`; the collision-backed runtime
  platform is the only horizontal surface allowed to appear there.
- Visual affordance rule: a background surface may resemble a walkable deck
  only when matching collision exists.

## Beta population systems

### Enemy-annihilation bonus

- Track total enemies spawned and total enemies destroyed.
- Award a completion bonus only when every spawned enemy has been destroyed.
- The bonus affects score and rewards but does not block the Uplink Gate.
- Deepworks remains enemy-free unless a later design pass explicitly changes it.

### Coin boxes and coins

- Credit caches are shootable world objects.
- A hit cache releases a readable, physical burst of collectible coins.
- Coins are optional and never required to complete a level.
- Tutorial credits persist across the overworld-to-Foundry scene handoff.
- Collected coins will feed a between-level purchase screen; that store is not
  part of this beta.
- Purchases provide start-of-next-level power-ups rather than permanent account
  upgrades.
- Coin values, banking rules, death penalties, box density, and shop prices will
  be balanced after the platform route and level duration are stable.

### Candidate next-level power-ups

- backpack jet-assist upgrade for higher jumps;
- temporary invincibility;
- rapid-fire blaster;
- longer-range blaster;
- automatic targeting or auto-fire.

Power-ups must not be required to escape a room unless the level explicitly
guarantees that power-up before the route begins.

Aryn's baseline jump height is fixed. Any higher jump or secondary airborne
boost must visibly come from the backpack's jet-assist module.
Deepworks entry remains unavailable until that module is online because the
return through the concrete deck requires its secondary boost.

## Promotion rule

The unified preview replaces the canonical game only after:

- all mandatory jumps pass the movement-safety margin;
- every painted walkable surface has matching collision;
- all eight plates and every Deepworks entrance are reachable;
- the Uplink Gate can be completed from the intended route;
- the Seam Hunter checkpoint preserves Foundry state and retries from the safe
  portal bay;
- Wound-touched Vesperite recovery completes the run and returns Aryn to the
  surface through a locked black transition;
- desktop and 360–390 px portrait-mobile testing passes;
- no existing audio, pause, input, selection, or zoom protections regress;
- the full-site audit reports zero errors and zero warnings.
