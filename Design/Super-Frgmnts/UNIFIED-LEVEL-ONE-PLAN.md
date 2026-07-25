# SUPER FRGMNTS // Unified Level 1 Plan

## Locked world target

- Canonical level: **The Shard Foundry**
- Eight horizontal plates: two each for Foundry, Refinery, Biolab, and Uplink
- World dimensions: 13,376 × 1,882 pixels
- Three traversal layers: upper gantries, main deck, and Deepworks
- Eight-minute level timer
- Uplink Gate at the upper end of the eighth plate
- Down drops through one-way platforms and enters Deepworks
- Deepworks remains jump-exitable

## Current construction pass

The current pass is platform-only. It establishes:

- room order and dimensions;
- horizontal and vertical camera behavior;
- concrete-deck and Deepworks alignment;
- painted catwalk collision;
- runtime platform placement, thickness, color, and motion;
- complete start-to-Uplink reachability;
- desktop and portrait-mobile framing.

Enemies, hazards, Signal Shards, recovery hearts, coin boxes, coins, bonuses, and
power-ups are deliberately excluded until the traversal world is approved.

## Provisional artwork contract

- The expanded Foundry plate supplies the approved upper-gantry vocabulary.
- The legacy Refinery, Biolab, and Uplink plates remain at their original scale
  and are bottom-aligned beneath the upper gantry.
- Repeated plates alternate orientation and receive restrained zone color.
- Replacement art must preserve the existing world coordinates and collision
  surfaces so final artwork can be swapped without redesigning gameplay.

## Deferred population systems

### Enemy-annihilation bonus

- Track total enemies spawned and total enemies destroyed.
- Award a completion bonus only when every spawned enemy has been destroyed.
- The bonus affects score and rewards but does not block the Uplink Gate.
- Deepworks remains enemy-free unless a later design pass explicitly changes it.

### Coin boxes and coins

- Coin boxes are shootable world objects.
- A destroyed box releases a readable burst of collectible coins.
- Coins are optional and never required to complete a level.
- Collected coins feed a between-level purchase screen.
- Purchases provide start-of-next-level power-ups rather than permanent account
  upgrades.
- Coin values, banking rules, death penalties, box density, and shop prices will
  be balanced after the platform route and level duration are stable.

### Candidate next-level power-ups

- higher jump;
- temporary invincibility;
- rapid-fire blaster;
- longer-range blaster;
- automatic targeting or auto-fire.

Power-ups must not be required to escape a room unless the level explicitly
guarantees that power-up before the route begins.

## Promotion rule

The unified preview replaces the canonical game only after:

- all mandatory jumps pass the movement-safety margin;
- every painted walkable surface has matching collision;
- all eight plates and every Deepworks entrance are reachable;
- the Uplink Gate can be completed from the intended route;
- desktop and 360–390 px portrait-mobile testing passes;
- no existing audio, pause, input, selection, or zoom protections regress;
- the full-site audit reports zero errors and zero warnings.
