# Aryn Sol-Mavi // Pack Chassis Contract v1

Status: approved production integration
Naming: “Pack Chassis” is descriptive working language, not final lore terminology.

## Character rule

Aryn's backpack is her persistent equipment and power-up chassis. Every
intrinsic mobility, targeting, fire, and defensive upgrade must read as a new
state or module of that same backpack rather than as an unrelated ability.

The backpack's telescoping antenna is the **telescopic laser seeker**: her
only always-carried self-defense weapon and its targeting array. It is always
equipped and available from the moment Aryn arrives on Veyra, including on
the Overworld. Her hands remain free during locomotion, traversal,
conversation, and combat.

A recovered heavy rifle is a specialized combat weapon, not part of Aryn's
intrinsic loadout or backpack power progression. Its three roles are clearing
Vesperite route obstructions, killing bosses, and handling heavy combat. Its
ammo model, damage, boss effectiveness, and interaction with armor remain
undecided.

Aryn has no stomp or contact-damage attack. Touching a hostile actor damages
her even when she is descending; hostile actors are defeated with the seeker
or a recovered heavy rifle.

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

- Friendly avoidance that repels a shot's course away from nearby allies.
- Longer acquisition distance.
- Faster course correction.
- Wider forward acquisition cone.
- Multiple simultaneous locks.
- Rapid-fire or automatic defensive fire.
- Longer effective projectile life.

Seeking should assist aim without invalidating level geometry. Rounds may bend through open space but should not eventually pathfind through solid walls or sealed floors.

Dras, Jane, and future actors marked friendly are invalid targets. When one is
near the projected firing line, the seeker bends away from that friendly with
the same readable course correction it uses to bend toward an enemy. Friendly
avoidance wins if attraction to a hostile and protection of an ally conflict.

## Open weapon decisions

The following are not canon yet. Current runtime values are provisional
playtest behavior only:

- whether the heavy rifle consumes ammo and how that supply works;
- whether the telescopic laser seeker overheats;
- the seeker's blast range and projectile lifetime;
- whether backpack power increases range, damage, or both;
- boss durability and required hit counts;
- any additional rifle, seeker, or backpack mechanic.

### Mobility

- Jet-assisted jump.
- Increased launch height.
- Limited midair correction or one short secondary boost.
- Reduced landing recovery at advanced tiers.

This remains platforming assistance, not unrestricted flight.

Aryn has one consistent unassisted jump. Location, room, and traversal layer
must never silently increase its launch velocity. Any higher jump or secondary
airborne boost requires the backpack's jet-assist module to be online.

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
