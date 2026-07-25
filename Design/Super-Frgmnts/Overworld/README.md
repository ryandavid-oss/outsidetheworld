# SUPER FRGMNTS // Coreworks Overworld

This directory defines the three-plate prologue and recovery hub that precedes
**The Shard Foundry**.

## Phase 1 — composition blueprint

Phase 1 fixes the spatial story before finished artwork or runtime integration:

- one continuous 5,016 × 941 panorama;
- three 1,672 × 941 plates;
- a continuous ground line at y=744;
- Aryn's ship, safe spawn, and open landing flats on the first plate;
- Dras Ehdre, his base camp, and the abandoned exchange on the second plate;
- atmospheric ruins, the volcano, and the Coreworks portal on the third plate;
- dialogue, future shop, and portal-transition zones;
- the parallax and ambient-motion contract.

The composition source of truth is `overworld-layout.json`. The rendered guide
is `overworld-composition-guide.png`; the three-plate review image is
`overworld-plates-contact-sheet.png`.

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

Phase 2B is not wired into the live game. Runtime integration waits until the
static landscape receives visual approval and the Phase 3 overlay assets are
prepared.

## Phase 3 — hero props and characters

- isolate Aryn's ship as a transparent overlay;
- isolate one clean Dras Ehdre master and derive controlled idle/talk frames;
- create Dras's camp, abandoned credit terminal, atmosphere tower accents, and
  Coreworks portal;
- verify scale beside Aryn's 112-pixel draw height.

Revision 3A is approved. Its design-only package lives in
`Phase-3/Ship/` and locks the ship scale, transparent asset, 16-pixel hover
height, continuous 1.6-second motion curve, inverse shadow pulse, restrained
repulsor dust, and portrait framing. The next approval gate is Revision 3B:
Dras Ehdre's definitive character master.

## Phase 4 — atmosphere and charm

- three drifting cloud-wisp layers;
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
