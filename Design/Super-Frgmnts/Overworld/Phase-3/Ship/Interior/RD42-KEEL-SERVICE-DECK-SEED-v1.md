# SUPER FRGMNTS // RD-42 Keel Service Deck Seed v1

**Status:** Reserved future design; not a runtime or production commitment

**Established:** 2026-07-28

The keel service deck is the compact lower area beneath the RD-42's occupied
main deck. Its current presence is communicated only by the sealed hatch
beneath the pack bench at x 962–1,086.

The eventual area should be a separate scene, not a second room compressed
into the current 1,672 × 941 rear plate. A short authored ladder or service
lift can preserve the physical descent while allowing the lower space its own
camera, collision, lighting, and damage states.

## Spatial seed

The lower deck should feel narrower, denser, and more structural than the
main cabin:

```text
          FROM PACK-BENCH HATCH
                    ↓
        ┌──── ACCESS / LOCKDOWN ────┐
        │                           │
 PORT   │ REPAIR     CRAWLWAY       │   STARBOARD
 MANIFOLD                       SHIELD BUS
        │                           │
        │  EMERGENCY CONCEALMENT    │
        └────── KEEL STRUCTURE ─────┘
```

Potential zones:

- **Access / lockdown:** ladder or short lift, hatch controls, and a positive
  seal so an invasion cannot silently follow Aryn downstairs.
- **Repair manifold:** phase coupler bus, shielded field-braid conduits,
  coolant isolation, and visible damage states.
- **Crawlway:** a low, readable traversal lane that makes this deck feel
  structurally different without forcing a crouch mechanic.
- **Emergency concealment:** a compact shelter or maintenance recess where
  Aryn can survive a boarding search.
- **Shield bus:** aft power distribution and a future reason to restore or
  reroute ship systems.

## Future gameplay uses

### Repair state

A fault on the main deck identifies a specific lower-deck system. Aryn opens
the hatch, descends, isolates the damaged line, and returns. Repairs should be
physical and legible rather than a generic menu.

### Lockdown / concealment state

An enemy boarding event can turn the safe ship into a tense noncombat scene:

1. an external breach warning begins;
2. Aryn reaches the keel hatch before the upper-deck search locks down;
3. the hatch seals and upper-deck movement becomes audible overhead;
4. the player manages one or two quiet ship systems rather than fighting in
   the shelter; and
5. emergence becomes an authored story beat.

This is not approval for a general stealth system. The concealment behavior
should remain a bounded ship sequence unless a broader stealth contract is
approved.

### Invasion state

A later damaged or breached variant may place enemies in the crawlway and
repair bays. That state requires its own combat, companion, damage, camera,
and recovery contract. The normal RD-42 interior remains a safe room.

## Art direction

- Lighter Aryn-led cabin colors end at the hatch threshold.
- The keel deck shifts darker and warmer: blue-gray structure, amber repair
  lamps, pale cyan system traces, and limited emergency pink.
- Machinery is chunky and readable, not Foundry-like wallpaper.
- Structural ribs and the narrow ceiling communicate the exterior hull.
- No baked enemies, Aryn, quest items, or readable environmental text.

## Current boundary

- The main-deck hatch stays sealed and noninteractive.
- No lower-deck collision, route, save state, enemy, prompt, or asset is live.
- The service-kit objective does not require this area.
- Final geometry, access timing, hiding rules, invasion fiction, and rewards
  require separate approval.
