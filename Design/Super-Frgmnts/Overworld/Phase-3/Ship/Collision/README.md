# Revision 3A.1 — ship collision and boarding gangway

This design-only addendum makes Aryn's ship the first conquerable environment
prop in the overworld. It does not modify the live game.

Revision 3A.1 was approved on July 25, 2026.

Approaching the ship from Aryn's proposed spawn deploys a telescoping
three-tread gangway. The forgiving route continues across a boarding deck,
dorsal step, and cockpit perch. A near-limit running jump can skip directly
from the desert floor to the boarding deck.

The proposal moves the overworld spawn 120 pixels right. Aryn then moves 16
pixels back toward the ship to trigger a 450 ms deployment. This creates enough
space for the gangway to open before she can reach its lower tread.

Every surface is one-way and accepts the existing Down-to-drop behavior. The
ship, gangway, collision surfaces, and Aryn all share the approved hover
delta while she is supported. The gangway remains deployed for the rest of the
scene so collision never disappears beneath the player.

The illustrated gangway in the approval images is a structural placeholder,
not final production art.

## Build

```sh
python3 tools/build_super_frgmnts_ship_collision_review.py
```

## Approval outputs

- `ship-collision-revision-3a1-contact-sheet-v1.png`
- `ship-gangway-deployed-concept-v1.png`
- `ship-collision-revision-3a1-guide-v1.png`
- `ship-collision-route-detail-v1.png`
- `ship-collision-revision-3a1-manifest.json`
