# Western Signal Flats expansion contract

**Status:** Revision 5C production exploration plate

## Purpose

The Western Signal Flats add one full 1,672 × 941 plate west of Aryn's RD-42.
The original Landing Flats, Dras Outpost, Coreworks Threshold, first-contact
dialogue, and transport handoff remain intact.

The west branch is optional, untimed environmental exploration. It carries no
objective, reward, tutorial, discovery chain, or critical-path gate.

## Four-plate world

| Plate | Runtime index | Story function |
| --- | ---: | --- |
| Western Signal Flats | 0 | Optional environmental exploration |
| Landing Flats | 1 | RD-42 arrival and ship access |
| Dras Outpost | 2 | Jane, worker droid, and first contact |
| Coreworks Threshold | 3 | Physical transport |

- World size: 6,688 × 941 pixels.
- Ground top: y = 744 on all four plates.
- The original three-plate coordinate system receives a +1,672 pixel runtime
  origin offset. Plate-local art and authored relationships do not move.
- The camera starts on the RD-42 and can travel continuously to either side.

## Removed production content

The survey plinth, Signal Sweep, Trillian recovery, field harness, powered
jump lesson, sealed salvage cache, and worker-droid discovery task are removed.
Their source art and historical code do not authorize visible props, prompts,
rewards, mission counters, or navigation guidance.

## Abilities and actor rules

### Trillian

- Trillian is Aryn's dog and remains distinct from Dras's dog, Jane.
- She joins from surface start and follows Aryn with acceleration, terrain
  support, gravity, forward floor probes, and a comfortable trailing distance.
- She is friendly, non-solid, non-hostile, and protected by seeker-friendly
  steering.
- She renders at 50% of the former size, follows at 410 px/s, and uses a
  480 px/s catch-up speed so Aryn cannot permanently outrun her.
- The unarmored gait is the only production movement state. Armored, powered
  jump, lunge, combat damage, enemy targeting, hurt, incapacitated, and
  recovery behavior remain unassigned.
- Trillian stops at the Coreworks transport boundary during this Overworld
  pass and does not alter Foundry population.

### Worker droid

- The existing drift and service cycles remain autonomous inside the
  Coreworks portal apron, away from basecamp.
- The hover baseline is six pixels above grade; the service cycle nearly
  touches down.
- The droid remains non-solid and non-hostile.
- There is no current discovery hook, prompt, service assignment, or reward.
  A future talkable repair-bot role is reserved for the broken portal.

### Hawk

- The hawk remains non-hostile, non-solid, and non-targetable.
- Normal travel alternates direction between passes.
- Flight uses time-driven world-space passes only. Aryn and camera movement
  cannot steer, accelerate, or redirect it.
- Reduced-motion mode preserves one static flight pose.

## Safety and portability

- Aryn, Jane, Trillian, Dras, and the worker droid never block one another.
- Friendly actors never enter enemy arrays or hostile targeting.
- All new runtime atlases stay under the 2,048-pixel texture ceiling.
- The western plate is installed locally and does not require a network
  request during episode play.
- Desktop and 390 × 844 portrait review are required before approval.

## Local review route

Use:

`?episode=01&stage=overworld&scene=western&autostart=1`

Acceptance requires no objective props, prompts, rewards, tutorial geometry,
or hawk guidance; Trillian must be present, correctly scaled, and able to keep
up.
