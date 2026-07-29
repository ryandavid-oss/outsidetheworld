# SUPER FRGMNTS // The Wound Boss-Room Background

**Status:** Superseded by the approved tall v2 arena

See `WOUND-BOSS-ROOM-BACKGROUND-v2.md`.

## Approved encounter context

- The Shard Foundry retains its eight connected traversal plates.
- Restoring both atmospheric stabilizers and recovering all twelve Vesperite Fragments
  activates a portal at the end of the eighth plate.
- The portal loads a dedicated, isolated boss plate rather than extending the
  continuous Foundry world.
- Seam Hunter guards access to **the Wound**, a raw geological rupture
  surrounded by failed emergency construction.
- The Wound is the room's primary revelation. The recoverable pack-upgrade
  material is secondary and will remain a separate sprite.

Enemy annihilation remains optional and does not gate access to the boss.

## Base plate contract

- Runtime dimensions: **1,672 × 941 pixels**
- Color mode: opaque RGB
- Continuous deck top: **y = 668**
- Portal housing: far left, with no baked active portal energy
- Wound: far right, dark and unlit so its animated energy can be layered later
- Central arena: sparse, unobstructed, and free of painted hazards or platforms
- Characters, Wound glow, sampling station, upgrade material, HUD, and text
  are not baked into the plate

The 668-pixel deck elevation leaves 668 pixels of vertical room above the
combat plane. A 512-pixel Seam Hunter therefore retains 156 pixels of clear
headroom; a 560-pixel render retains 108 pixels.

## Asset paths

- Raw master:
  `Design/Super-Frgmnts/Foundry/Boss-Room/Raw/wound-boss-room-background-master-v1.png`
- Runtime plate:
  `Images/Game/Super-Frgmnts/foundry-wound-boss-room-background-runtime-v1.png`
- Walk-scale review:
  `Design/Super-Frgmnts/Foundry/Boss-Room/Reviews/wound-boss-room-scale-review-v1.png`
- Sweep-scale review:
  `Design/Super-Frgmnts/Foundry/Boss-Room/Reviews/wound-boss-room-sweep-review-v1.png`

Regenerate the runtime plate and review composites with:

```sh
python3 tools/build_super_frgmnts_wound_boss_room.py
```

Verify the package with:

```sh
python3 tools/verify_super_frgmnts_wound_boss_room.py
```

## Generation record

The base plate was produced with the built-in image-generation workflow. The
existing Uplink and Biolab plates were supplied only as style, palette, pixel
density, and material references.

Final prompt:

> Create a new wide pixel-art boss chamber called The Wound, closely matching
> the pixel density, crisp hard-edged rendering, environmental scale,
> industrial-cavern materials, and restrained palette of the supplied SUPER
> FRGMNTS Uplink and Biolab reference backgrounds. This is a new environment,
> not an edit or collage. A cavernous sealed Coreworks chamber is built around
> a raw geological rupture in the far-right wall. The rupture is an enormous
> deep black irregular vertical seam in the rock, surrounded by improvised
> emergency construction: heavy steel containment braces, broken diagnostic
> arms, bundled cables, dark floodlight housings, and reinforced machinery.
> The construction looks urgent and partly failed. The Wound itself is unlit
> and mysterious; leave its active glow for a separate overlay. Include a small
> static portal-housing recess at the far left with no active portal energy, a
> continuous straight heavy metal combat deck, a visually open central arena,
> and tall clear negative space above the deck for a giant boss. Concentrate
> structural detail at the far-left portal housing, ceiling border, far-right
> Wound construction, and below the deck. Keep the central arena and boss
> silhouette zone dark, quiet, sparse, and unobstructed. Use polished side-view
> retro pixel art with crisp deliberate pixel clusters and no antialiasing.
> Use deep navy, blue-black, charcoal steel, muted purple stone, small cyan and
> magenta accents, and tiny amber indicators. Include no characters, creatures,
> boss, player, collectible, upgrade material, sampling-station object, active
> portal energy, bright Wound glow, hazards, floating platforms, vegetation,
> text, signage, HUD, logos, or watermark.

## Deferred layered assets

- low- and high-energy Wound overlays;
- diagnostic sampling-station states;
- pack-upgrade material;
- active portal energy;
- any post-victory lighting change.

These are intentionally separate from the base background.

## Isolated gameplay trial

Open:

`super_frgmnts.html?preview=wound-boss&autostart=1`

The trial intentionally contains only the approved background plate, Aryn, and
Seam Hunter. Aryn starts with her heavy rifle selected. Seam Hunter has 20 hit
points and uses the existing walk and sweep sheets at a 512-pixel walk render
and a 640 × 512-pixel attack render.

The boss collider, sweep footprint, walk speed, frame-14-to-19 damage window,
recovery timing, rifle damage, rifle heat behavior, and arena spawn positions
are explicitly provisional playtest scaffolding. They do not settle the final
combat-balance or hitbox decisions.

Verify the route wiring with:

```sh
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```
