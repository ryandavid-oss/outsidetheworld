# SUPER FRGMNTS — Overworld Revision 3 tracker

Last updated: 2026-07-27

## Approved foundations

| Revision | Scope | Status | Commit |
|---|---|---|---|
| 3A | Ship extraction, Landing Flats placement, hover field, seamless hover loop | Approved | `3f1c6aa8` |
| 3A.1 | Gangway tutorial, ship collision route, movement trigger, one-way surfaces | Approved | `37ca3a47` |

## Approved production integrations

| Revision | Scope | Direction | Status |
|---|---|---|---|
| 3B | Dras transparent master, scale, placement, restrained motion contract | 104px visible silhouette in a 96×112 canvas | Production |
| 3C | Character dialogue and terminal dialogue languages | Field Relay; all 36 canon Arrival on Veyra cards | Production |
| 3D | Dras Outpost blocking, first-contact trigger, desktop/mobile camera flow | Auto first meeting; manual return visits; non-solid Dras | Production |
| 3E | Aryn command/field rest grammar and pack-fire prototype | Command Rest is the immediate and sole runtime resting pose; Field Rest remains archived | Production |
| 3F | Close dialogue portraits, centered travel camera, tremor caption, invisible ship-slope traversal, painted-doorway portal alignment | Preserve the ship artwork; use painted surfaces and the Coreworks entrance as visual collision authorities | Production |
| 3G | Purpose-built Aryn and Dras dialogue portraits; visible boot-plane correction for Dras | Chest-and-shoulders relay portraits; Dras grounded to Aryn's rendered—not merely physical—floor line | Production |
| 3H | Volumetric cloud parallax, distant birds, rummaging camp dog, closer Dras staging, dialogue-action reversal | Add life and depth without obscuring traversal; Continue is the primary right-hand action | Production |
| 3I | High-fidelity Aryn dialogue portrait | Match Dras's native portrait detail while preserving Aryn's approved identity, palette, signal pack, and opaque visor | Production |
| 3J | Overworld closing atmosphere pass | Remove the stray collider; keep volcano animation to subtle heat and isolated sparks without tracing the plate; give the camp dog a readable contact/pass gait | Production |

## Current local review

| Revision | Scope | Direction | Status |
|---|---|---|---|
| 3K | Full camp-dog behavior animation | Replace the two-frame approximation with supplied 36-frame walking and 16-frame sniffing cycles while preserving the established non-solid camp route | Integrated locally; awaiting approval and deployment |
| 3L | Jane autonomous Overworld actor | Name and rescale Jane; replace the 130-pixel timed rail with terrain-aware wandering, player curiosity, safe first-contact staging, and a transport exclusion boundary | Integrated locally; awaiting approval and deployment |
| 4A | Western Signal Flats expansion | Prepend one production plate west of the RD-42; add five optional assignments, Signal Sweep, Trillian surface states, hawk guidance, and worker-droid service without gating the original Foundry route | Integrated locally; awaiting approval and deployment |

## Deliberately deferred

- Final Dras animation and expression frames
- Final camp prop art
- Credit-terminal behavior and economy
- Voice, dialogue sound design, or localization

## Post-deployment review gates

1. Play the complete Landing Flats-to-Dras first-contact flow.
2. Confirm the 36-card conversation pacing on a phone.
3. Confirm the portal ignition and handoff into the isolated Foundry preview.
4. Continue into the Foundry level-design pass after mobile review.

## Rebuild commands

```sh
python3 tools/build_super_frgmnts_dras_review.py --prepare-identity
python3 tools/build_super_frgmnts_dras_review.py --build-reviews
python3 tools/build_super_frgmnts_dialogue_review.py
python3 tools/build_super_frgmnts_outpost_blocking.py
python3 tools/build_super_frgmnts_dog_walk.py
python3 tools/build_super_frgmnts_creature_intake.py
python3 tools/build_super_frgmnts_revision3_review.py
python3 tools/verify_super_frgmnts_revision3.py
python3 tools/verify_super_frgmnts_creature_intake.py
python3 tools/build_super_frgmnts_overworld_western_expansion.py
python3 tools/verify_super_frgmnts_overworld_western_expansion.py
```
