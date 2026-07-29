# Wound-touched Vesperite v1

## Status

Approved and integrated into the isolated Wound boss trial.

`Wound-touched Vesperite` is the current descriptive runtime label for the
specimen. It can be renamed later without changing the encounter flow.

## Approved encounter role

- The specimen is secondary to the Wound.
- It is revealed where Seam Hunter's body finally comes to rest rather than
  being housed in a separate construction cradle.
- Seam Hunter's final death frame opens access, holds long enough to register,
  darkens into a near-black silhouette, and fades away.
- The specimen emerges beneath the fading silhouette and remains after the
  body has disappeared.
- Aryn must deliberately recover it with the shared Down/interact action.
- The touch direction stick performs the same action when dragged downward.
- Recovery stores one future pack-upgrade material.
- Recovery does not immediately modify Aryn's pack, stats, weapons, jump, or
  other abilities.

## Runtime placement and flow

- World center: captured dynamically from Seam Hunter's final resting place
- Deck: y = 1,360
- Interaction radius: 118 px
- Final corpse hold: 1.4 seconds
- Corpse darken: 1.05 seconds
- Corpse fade: 0.9 seconds
- Reveal duration: 0.9 seconds
- Recovery presentation: 1.3 seconds

The post-battle mission timer remains fixed while Aryn approaches the
specimen. The construction lifts and gantry continue moving. No additional
holder, pedestal, or cradle is drawn. A proximity prompt reads `▼ RECOVER`.
The camera centers Seam Hunter's resting place during the transition, then
dual-frames Aryn and the specimen whenever both fit inside the current desktop
or mobile viewport.

On recovery, the specimen contracts toward Aryn's backpack, the runtime stores
`wound-touched-vesperite` as the pack-upgrade material, and the completion card
reads:

- `SPECIMEN RECOVERED`
- `WOUND-TOUCHED VESPERITE`
- `Analysis: A unique specimen of vesperite, a mineral mined for its energy
  properties. Return this to Dras for further study.`

The runtime emission effect follows the specimen's transparent silhouette with
tight cyan and violet bloom layers. A shallow light pool reflects onto the deck
and five restrained energy motes rise from the fragment. No solid oval, shield,
or spotlight shape surrounds the pickup.

Developer review route:

```text
http://127.0.0.1:8765/super_frgmnts.html?preview=wound-boss&autostart=1&qa=reward
```

## Asset contract

- Generated source:
  `Raw/wound-touched-vesperite-chroma-source-v1.png`
- Alpha source:
  `Raw/wound-touched-vesperite-alpha-source-v1.png`
- Runtime:
  `Images/Game/Super-Frgmnts/wound-touched-vesperite-runtime-v1.png`
- Runtime size: 128 × 144 px RGBA
- Review:
  `Reviews/wound-touched-vesperite-runtime-review-v1.png`

Regenerate the normalized runtime and review asset with:

```sh
python3 tools/build_super_frgmnts_wound_vesperite.py
```

The specimen was created with the built-in image-generation workflow in
stylized game-sprite mode. Final generation prompt:

> Create a single isolated 2D pixel-art game pickup sprite for a dark
> industrial sci-fi Metroidvania. Subject: one rare “Wound-touched Vesperite”
> specimen, an asymmetrical hand-sized mineral fragment with a tall jagged
> silhouette, rough fractured near-black violet stone, sparse cyan-blue
> crystalline facets, and one vivid electric-blue fissure running through its
> core as if internally resonating. It must look ancient, dangerous, and
> scientifically unique—not like a polished jewel, coin, generic crystal
> cluster, or ordinary blue diamond. Crisp deliberate 16-bit/32-bit-era
> pixels, strong readable silhouette at small game scale, front three-quarter
> view, restrained glow contained close to the mineral. Center the complete
> specimen with generous padding; no crop. No pedestal, cradle, hardware,
> text, UI frame, cast shadow, watermark, particles, or animation. Background
> must be perfectly flat solid chroma-key green #00ff00 with no gradients,
> texture, shadow, or green anywhere in the subject.

## Telemetry

The canvas exposes:

- `data-wound-vesperite-reward`: `locked`, `revealing`, `ready`,
  `recovering`, or `recovered`
- `data-wound-vesperite-reveal`: normalized reveal progress
- `data-wound-vesperite-recovery`: normalized recovery progress
- `data-wound-vesperite-stored`: recovery boolean
- `data-wound-vesperite-x`: captured final resting position
- `data-pack-upgrade-material`: `none` or `wound-touched-vesperite`
- `data-wound-boss-aftermath`: `inactive`, `holding`, `darkening`, `fading`,
  or `complete`
- `data-wound-boss-aftermath-time`: post-death transition time
- `data-wound-boss-camera-mode`: `aftermath-corpse`,
  `aftermath-dual-frame`, or the normal encounter camera mode

Verify with:

```sh
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```
