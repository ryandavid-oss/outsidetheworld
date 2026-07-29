# Revision 3A — Aryn's ship

This folder contains the approval assets for the first Phase 3 revision:
ship scale, placement, hover-field grounding, and portrait framing on Landing
Flats.

Revision 3A and its continuous v2 hover loop were approved on July 25, 2026.

Nothing in this folder is wired into the live game.

## Source and extraction

The supplied ship artwork was used as the identity authority. Built-in image
generation changed its surrounding black field to a flat chroma-key color. The
exact prompt is preserved in `ship-background-extraction-prompt-v1.txt`.

The standard ImageGen chroma-removal helper produced
`Assets/aryn-ship-transparent-uncropped-v1.png`. The deterministic review
builder then removes only alpha values below 64 to eliminate two weak matte
caps above the upper pods, crops tightly to the remaining silhouette, and
leaves all stronger hull and antialias pixels unchanged.

## Build

```sh
python3 tools/build_super_frgmnts_overworld_ship_review.py
```

## Approval outputs

- `Reviews/ship-revision-3a-contact-sheet-v1.png`
- `Reviews/landing-flats-ship-composite-v1.png`
- `Reviews/landing-flats-ship-placement-guide-v1.png`
- `Reviews/landing-flats-ship-scale-detail-v1.png`
- `Reviews/landing-flats-ship-portrait-crop-v1.png`
- `Reviews/landing-flats-ship-hover-preview-v2.gif`
- `Reviews/landing-flats-ship-hover-keyframes-v2.png`
- `ship-revision-3a-manifest.json`

The hover proof uses a 1.6-second, ±3.2-pixel continuous bob rendered at
quarter-pixel precision. It contains no duplicated hold frames at its high,
low, or loop-boundary positions. Its shadow remains attached to the ground and
pulses inversely with height. Sparse sand particles and muted cyan flecks drift
outward from the lower repulsors. These are separate runtime layers and are not
baked into the landscape.

The manifest records the exact world coordinates, motion specification, and
approval questions.

## Integrated production interior

The first RD-42 interior is now defined and integrated as an isolated
one-plate playable production-art review:

- [`Interior/RD42-SHIP-INTERIOR-CONTRACT-v1.md`](Interior/RD42-SHIP-INTERIOR-CONTRACT-v1.md)
  defines top-middle dorsal-hatch entry, Aryn's continuous descent, room
  behavior, interactions, and lifecycle requirements.
- [`Interior/RD42-SHIP-INTERIOR-WIREFRAME-v1.md`](Interior/RD42-SHIP-INTERIOR-WIREFRAME-v1.md)
  defines the precise one-plate layout, collision, prop reservations, and
  desktop/mobile camera targets.
- [`Interior/RD42-SHIP-INTERIOR-WIREFRAME-v1.svg`](Interior/RD42-SHIP-INTERIOR-WIREFRAME-v1.svg)
  is the visual review artifact.
- [`Interior/Assets/rd42-interior-rear-plate-pixel-candidate-v2.png`](Interior/Assets/rd42-interior-rear-plate-pixel-candidate-v2.png)
  remains the approved scale reference with a compressed y438–744 occupied
  volume. Its dark Foundry-like palette was not promoted to runtime.
- [`Interior/Reviews/rd42-interior-rear-plate-scale-check-v2.png`](Interior/Reviews/rd42-interior-rear-plate-scale-check-v2.png)
  records that earlier geometry and scale review.
- [`Interior/Assets/rd42-interior-rear-plate-production-v1.png`](Interior/Assets/rd42-interior-rear-plate-production-v1.png)
  is the approved production master. It retains the exact 1672 × 941 geometry
  while replacing the dark material language with the light OTW blue, teal,
  and off-white palette.
- [`Interior/rd42-interior-rear-plate-production-v1.json`](Interior/rd42-interior-rear-plate-production-v1.json)
  records the authoritative palette, runtime path, OTW brandmark treatment,
  suit alcove, and sealed keel-hatch geometry.
- [`Interior/Reviews/rd42-interior-rear-plate-scale-check-production-v1.png`](Interior/Reviews/rd42-interior-rear-plate-scale-check-production-v1.png)
  verifies Aryn's unchanged 112 px physics cell and revised 168 px interior
  render cell against the cockpit control deck and promoted rear plate.
- The v1 pixel plate remains a rejected scale study; v2 supersedes it without
  changing the room geometry; production v1 supersedes v2 as the runtime
  artwork. The RD-42 scene now applies a dedicated 1.5× character render scale
  without changing Aryn's collisions or her scale elsewhere in the game.
- The cockpit-side bulkhead carries a faithful three-band OTW mark rendered as
  an in-world 16-bit mosaic, not a UI watermark.
- [`../Aryn/Armor-Change/README.md`](../Aryn/Armor-Change/README.md) documents
  the 36-frame suit-change intake and the isolated alcove interaction.
- [`../Aryn/Flight-Suit/README.md`](../Aryn/Flight-Suit/README.md) documents
  the supplied run and jump sheets and persistent flight-suit exploration on
  the RD-42 main deck.
- [`Interior/RD42-KEEL-SERVICE-DECK-SEED-v1.md`](Interior/RD42-KEEL-SERVICE-DECK-SEED-v1.md)
  reserves the future repair, concealment, and boarding-response lower deck.
- [`Interior/Audio/rd42-interior-music-v1.json`](Interior/Audio/rd42-interior-music-v1.json)
  preserves the supplied two-minute stereo master and defines the compressed
  runtime loop, mix level, hatch preload, and bidirectional crossfade.

The exterior hatch, authored descent, interior interactions, service-kit
state, exit, and exterior re-emergence are available through the review routes
in the working handoff. The live hatch now uses the dedicated interior score
on both the production surface route and the isolated review routes.
