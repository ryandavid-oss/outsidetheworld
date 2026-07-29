# Western Signal Flats expansion contract

**Status:** Revision 4A local review; not deployed

## Purpose

The Western Signal Flats add one full 1,672 × 941 plate west of Aryn's RD-42.
The original Landing Flats, Dras Outpost, Coreworks Threshold, first-contact
dialogue, calibration lane, and transport handoff remain intact.

The west branch is optional and untimed. It makes arrival exploratory without
delaying players who choose to follow the existing route directly to Dras.

## Four-plate world

| Plate | Runtime index | Story function |
| --- | ---: | --- |
| Western Signal Flats | 0 | Optional survey, Trillian recovery, surface abilities |
| Landing Flats | 1 | RD-42 arrival and movement discovery |
| Dras Outpost | 2 | Jane, worker droid, and first contact |
| Coreworks Threshold | 3 | Calibration lane and physical transport |

- World size: 6,688 × 941 pixels.
- Ground top: y = 744 on all four plates.
- The original three-plate coordinate system receives a +1,672 pixel runtime
  origin offset. Plate-local art and authored relationships do not move.
- The camera starts on the RD-42 and can travel continuously to either side.

## Optional western assignments

The shared Down/interact action handles every assignment. No new mandatory
input is introduced.

1. **Trace the survey echo** — restart the western signal plinth. This unlocks
   Signal Sweep.
2. **Recover Trillian** — locate Aryn's dog at the failed route marker.
   Trillian joins as a non-solid surface companion.
3. **Restore the field harness** — route the second signal into Trillian's
   armor. Her follow gait switches from unarmored to armored.
4. **Breach the sealed salvage cache** — Trillian performs the authored
   armored energy lunge against an abandoned cache. The action has no living
   target and defines no combat damage.
5. **Service the Outpost worker droid** — an optional post-contact maintenance
   interaction near the abandoned exchange.

Assignments grant small Galactic Credit recoveries but never gate Dras,
calibration, the Coreworks transport, or the Foundry.

## Abilities and actor rules

### Signal Sweep

- Unlocked by the first western signal plinth.
- Uses Down/interact when no closer interaction is available.
- Emits a readable radial pulse and points toward the nearest unfinished
  optional assignment.
- Has a short cooldown and no damage hitbox.

### Trillian

- Trillian is Aryn's dog and remains distinct from Dras's dog, Jane.
- Before recovery she waits beside the western route marker.
- After recovery she follows Aryn with acceleration, terrain support, gravity,
  forward floor probes, and a comfortable trailing distance.
- She is friendly, non-solid, non-hostile, and protected by seeker-friendly
  steering.
- The unarmored and armored gait atlases are live movement states.
- The powered-jump atlas supplies charge and launch; runtime physics supplies
  the arc, and the final launch pose is held while airborne.
- The armored lunge is used only for the sealed salvage assignment. Combat
  damage, enemy targeting, hurt, incapacitated, and recovery behavior remain
  deliberately unassigned.
- Trillian stops at the Coreworks transport boundary during this Overworld
  pass and does not alter Foundry population.

### Worker droid

- The existing drift and service cycles remain autonomous.
- A nearby Down/interact service assignment triggers one immediate maintenance
  cycle and a small credit recovery.
- The droid remains non-solid and non-hostile.

### Hawk

- The hawk remains non-hostile, non-solid, and non-targetable.
- Normal travel alternates direction between passes.
- While Aryn is in the western plate with an unfinished assignment, the hawk
  transitions to a restrained guide-circle over the next assignment.
- Reduced-motion mode preserves one static flight pose.

## Safety and portability

- All optional interactions map to the shared interact action.
- Aryn, Jane, Trillian, Dras, and the worker droid never block one another.
- Friendly actors never enter enemy arrays or hostile targeting.
- All new runtime atlases stay under the 2,048-pixel texture ceiling.
- The western plate is installed locally and does not require a network
  request during episode play.
- Desktop and 390 × 844 portrait review are required before approval.

## Local review route

Use:

`?episode=01&stage=overworld&scene=western&assignment=survey&autostart=1`

The `assignment` value accepts `survey`, `trillian`, `harness`, `jump`,
`salvage`, or `droid`. Each isolated review prepares only the prerequisite
surface states needed for that animation or interaction; the production route
still starts with every optional assignment incomplete.
