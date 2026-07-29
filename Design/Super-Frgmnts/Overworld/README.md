# SUPER FRGMNTS // Coreworks Overworld

This directory defines the four-plate prologue and recovery hub that precedes
**The Shard Foundry**.

## Western Signal Flats runtime expansion

The live Overworld now prepends a fourth 1,672 × 941 plate west of the original
Landing Flats. The original rightward route is preserved with a +1,672-pixel
runtime origin offset:

- Western Signal Flats — x=0;
- Landing Flats — x=1,672;
- Dras Outpost — x=3,344;
- Coreworks Threshold — x=5,016.

The western plate is optional, untimed exploration space. Its survey plinth,
Signal Sweep, field harness, salvage cache, tutorial props, and objective
markers are permanently absent from the production route. Trillian joins from
surface start at half her former render size and follows fast enough to keep
up with Aryn. The hawk makes autonomous world-space passes; player and camera
movement cannot steer it. Dras first contact and the Coreworks transport form
the clear rightward critical path.

The expansion contract, exact prompt, source plate, seam audit, runtime
manifest, and four-plate review sheet live in `Western-Signal-Flats/`.

## Phase 1 — composition blueprint

Phase 1 fixed the original three-plate spatial story before finished artwork or
runtime integration:

- one continuous 5,016 × 941 panorama;
- three 1,672 × 941 plates;
- a continuous ground line at y=744;
- Aryn's ship, safe spawn, and open landing flats on the first plate;
- Dras Ehdre, his base camp, and the abandoned exchange on the second plate;
- atmospheric ruins, the volcano, and the Coreworks portal on the third plate;
- dialogue, future shop, and portal-transition zones;
- the parallax and ambient-motion contract.

The current composition source of truth is `overworld-layout.json`. The
original rendered guide is `overworld-composition-guide.png`; the current
four-plate review image is
`Western-Signal-Flats/Reviews/overworld-four-plate-contact-v1.png`.

The overworld is untimed. Entering the Coreworks portal starts the eight-minute
timer for The Shard Foundry.

## Phase 2 — static landscape

After the Phase 1 composition is approved:

1. create the continuous sky and desert panorama across all three plates;
2. create separate far-mountain, near-mountain, and decayed-infrastructure
   layers;
3. split the finished panorama at x=1672 and x=3344;
4. verify that the horizon, ground, and structural silhouettes are seamless.

The first static pass deliberately excludes characters, dialogue, clouds,
smoke, dust, and portal animation. Those remain independent assets.

### Phase 2A approval image

`overworld-color-script-v1.png` is the first atmosphere and palette approval
image. It is intentionally a 1,675 × 939 color script rather than production
plate art. It establishes:

- the empty-to-dense left-to-right visual rhythm;
- the dusk sky, mountain, desert, and Vesperite palette;
- the relative emotional weight of the landing flats, Dras Outpost, and the
  Coreworks threshold;
- the volcano, viaduct, atmospheric machinery, and dark portal emplacement.

It must not be stretched into the 5,016-pixel world or wired into the game.
Once approved, it becomes a visual reference for three overlapping production
art passes at the exact plate dimensions.

`overworld-color-script-v1-prompt.txt` records the built-in image-generation
prompt. The composition guide and existing Foundry background were supplied as
composition and style references respectively.

### Phase 2B production landscape

The approved color script was resolved into three exact production plates in
`Production/`:

- Landing Flats;
- Dras Outpost;
- Coreworks Threshold.

The production builder aligns every walkable surface to y=744, applies
color-only seam harmonization, exports the continuous 5,016 × 941 master, and
regenerates the three exact 1,672 × 941 plate files. The raw built-in
image-generation results and complete prompt set remain beside the outputs for
reproducibility.

The three approved plates and Western Signal Flats are wired into the isolated
Overworld runtime.

## Phase 3 — hero props and characters

- isolate Aryn's ship as a transparent overlay;
- isolate one clean Dras Ehdre master and derive controlled idle/talk frames;
- add a non-hostile worker droid beside the Coreworks transport with a
  restrained low-hover service cycle and no current interaction;
- integrate Trillian as Aryn's separate, non-solid unarmored surface companion;
- integrate one non-hostile hawk with autonomous alternating sky passes;
- create Dras's camp, abandoned credit terminal, atmosphere tower accents, and
  Coreworks portal;
- verify scale beside Aryn's 112-pixel draw height.

Revision 3A is approved. Its design-only package lives in
`Phase-3/Ship/` and locks the ship scale, transparent asset, 16-pixel hover
height, continuous 1.6-second motion curve, inverse shadow pulse, restrained
repulsor dust, and portrait framing. The next approval gate is Revision 3B:
Dras Ehdre's definitive character master.

Revision 3A.1 is also approved. Its `Phase-3/Ship/Collision/` addendum makes
the hovering ship Aryn's first conquerable environment prop through a
proximity-deployed gangway, synchronized one-way collision surfaces, an
optional skill shortcut, and the existing Down-to-drop behavior. The proposed
overworld spawn moves 120 pixels right to give the gangway safe deployment
space.

## Phase 4 — atmosphere and charm

- deterministic low-frequency procedural wispy and storm cloud masks with
  independent parallax, blur, speed, and restrained opacity;
- slow volcanic smoke and rare crater pulses;
- dust ribbons and heat shimmer;
- ship breathing lights;
- Dras's scarf, coat, probe, blink, and glance;
- camp banner, wind chime, kettle vapor, and radio static.

## Phase 5 — isolated playable preview

Build the overworld behind an isolated preview route or query parameter. The
first playable pass includes only:

- walking and jumping;
- horizontal camera movement;
- Dras proximity dialogue;
- the portal transition into the existing Foundry preview.

The credit shop, persistent restoration, story-state variants, and rewards
remain disabled until the world itself is approved.

## Build

From the repository root:

```sh
python3 tools/build_super_frgmnts_overworld_guide.py
```

The builder validates the dimensions, plate seam, ground, bounds, anchors, and
interaction zones before replacing the rendered guides.
