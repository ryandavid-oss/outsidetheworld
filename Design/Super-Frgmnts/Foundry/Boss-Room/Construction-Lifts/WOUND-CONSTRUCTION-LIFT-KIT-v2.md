# SUPER FRGMNTS // The Wound Construction Lift Kit v2

**Status:** Approved wide-arena implementation

## Runtime contract

- Left fixed tower and lift: **x = 250**, width **320 px**
- Right fixed tower and lift: **x = 1,990**, width **320 px**
- Tower sprites: **320 × 592 px**, world y = **768**
- Moving lift sprites: **320 × 72 px**
- Vertical lift collision surfaces: world y = **1,090** at rest
- Vertical travel: **480 px**, continuous, opposed phase, speed **0.5**
- Cable tile: **8 × 64 px**
- Upper runway: **1,420 × 64 px**, world x = **570**, y = **690**
- Upper trolley/platform: **300 × 152 px**
- Upper collision surface: world y = **780** at rest
- Horizontal home x: **1,140**
- Horizontal travel: **1,100 px**, continuous, speed **0.5**
- Moving-platform walk surface: **12 px** below the lift sprite top
- Gantry walk surface: **86 px** below the trolley sprite top

The v1 tower, platform, cable, and trolley assets are unchanged. Only the fixed
upper runway is extended to span the approved 1,420 px combat lane.

## Runtime assets

- `Images/Game/Super-Frgmnts/wound-construction-lift-tower-runtime-v1.png`
- `Images/Game/Super-Frgmnts/wound-construction-lift-platform-runtime-v1.png`
- `Images/Game/Super-Frgmnts/wound-construction-lift-cable-tile-v1.png`
- `Images/Game/Super-Frgmnts/wound-construction-gantry-runway-runtime-v2.png`
- `Images/Game/Super-Frgmnts/wound-construction-gantry-car-runtime-v1.png`

Reviews:

- `Reviews/wound-construction-lift-kit-review-v2.png`
- `Reviews/wound-construction-lifts-room-review-v2.png`

Regenerate:

```sh
python3 tools/build_super_frgmnts_wound_construction_lifts.py
python3 tools/verify_super_frgmnts_wound_boss_trial.py
```
