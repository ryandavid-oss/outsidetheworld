# SUPER FRGMNTS — title-screen contract

## Purpose

The title screen is the front door to the episodic game. It establishes the
surface and subterranean halves of Veyra, identifies Season One and Episode 01,
and hands the player directly into `Arrival on Veyra`.

## Visual authority

`Assets/super-frgmnts-title-coreworks-v1.png` is the Revision 1A title artwork.
It is a native 1672 × 941 game-stage plate and retains its original integrated
SUPER FRGMNTS wordmark. The wordmark remains baked into the artwork during this
revision to preserve its exact letterforms.

The interface is layered independently over the artwork:

- `Season One // Veyra`
- `Episode 01 // Arrival on Veyra`
- `Begin episode`
- `A distress signal from a world the Fleet abandoned.`

The central dark chamber remains the menu field. Controls must not obscure the
surface vista, the Vesperite chambers, or the distant sealed gate.

## Motion language

Motion is restrained and environmental:

- an almost imperceptible scene drift;
- sparse dust motes;
- a breathing signal around the distant gate;
- asynchronous Vesperite light fluctuations;
- a short dim-and-advance transition after activation.

All ambient animation stops under `prefers-reduced-motion: reduce`.

## Interaction

The primary action is available by button activation, Enter, Space, or touch.
It announces `Opening Episode 01. Arrival on Veyra.`, then navigates to:

`super_frgmnts.html?episode=01&stage=overworld&autostart=1`

The arrival route waits for its critical artwork, begins automatically, and
does not display a duplicate title screen. After Dras opens the Coreworks
route, the assembled episode continues to:

`super_frgmnts.html?episode=01&stage=foundry&autostart=1`

Developer review URLs using `preview=overworld` and
`preview=foundry-expansion` remain supported, but they are no longer the
player-facing episode route.

## Responsive behavior

The native plate covers the landscape game stage. Portrait layouts retain the
full plate with a darkened full-bleed copy behind it, protecting the wordmark
and central composition from cropping.

## Scope

Revision 1A is approved for the unified production release on `main`.
