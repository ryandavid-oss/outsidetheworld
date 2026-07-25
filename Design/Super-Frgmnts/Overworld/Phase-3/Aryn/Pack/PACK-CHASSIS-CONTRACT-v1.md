# Aryn Sol-Mavi // Pack Chassis Contract v1

Status: approved production integration
Naming: “Pack Chassis” is descriptive working language, not final lore terminology.

## Character rule

Aryn does not carry or mime a rifle.

Her pack is the persistent equipment chassis. The telescoping antenna is the weapon emitter and targeting array. Her hands remain free during locomotion, traversal, conversation, and combat.

Firing must never interrupt or replace:

- idle posture;
- walking or running;
- takeoff or airborne animation;
- landing recovery;
- turning.

The fire presentation is an additive layer attached to the pack:

1. antenna emitter brightens;
2. energy concentrates at the antenna tip;
3. a seeking round launches from that tip;
4. the round bends toward a valid target;
5. Aryn’s current locomotion animation continues unchanged.

## Upgrade families

### Targeting and fire

- Longer acquisition distance.
- Faster course correction.
- Wider forward acquisition cone.
- Multiple simultaneous locks.
- Rapid-fire or automatic defensive fire.
- Longer effective projectile life.

Seeking should assist aim without invalidating level geometry. Rounds may bend through open space but should not eventually pathfind through solid walls or sealed floors.

### Mobility

- Jet-assisted jump.
- Increased launch height.
- Limited midair correction or one short secondary boost.
- Reduced landing recovery at advanced tiers.

This remains platforming assistance, not unrestricted flight.

### Defense

- Force-field armor.
- A rechargeable impact buffer.
- Longer post-hit protection.
- Environmental resistance as later levels introduce new hazards.

The field should read around Aryn’s body while its energy source remains visibly rooted in the pack.

## Visual progression

Upgrades should enrich the same silhouette rather than replace it:

- antenna length and articulation;
- additional pack lights;
- small deployable fins or emitter vanes;
- brighter exhaust ports for mobility;
- a thin body-contour field for defense;
- distinct cyan, magenta, gold, and violet state accents.

Avoid adding a handheld gun, chest-mounted barrel, rifle stock, or aiming pose.

## Local prototype

The current local prototype:

- removes the canvas-drawn gun prop previously placed over Aryn’s torso;
- maps the antenna tip across idle, ten run frames, takeoff, airborne, and crouch;
- launches rounds from the animation-specific antenna position;
- leaves velocity and locomotion state untouched when firing;
- gives each existing tier a progressively longer and more responsive seek;
- draws a curved tracer so target correction is readable;
- is included in the unified Episode 01 production package.

## Next art pass

The approved rested pose should keep the pack and antenna clearly readable. A firing-frame repaint is not required: charge, flash, trail, field, and exhaust can be layered over the normal character animation.
