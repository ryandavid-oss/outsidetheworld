# SUPER FRGMNTS — animation intake, 2026-07-26

## Integrated

- The Veyra camp dog now uses all 36 supplied walking frames and all 16
  supplied sniffing frames. Its gait faces the direction of travel; sniffing
  occurs occasionally as one three-second dip-and-rise rather than a
  continuously repeating loop. The dog is canonically Jane. Her runtime draw
  size is 85 × 68 pixels, and a terrain-aware behavior actor now replaces the
  former 130-pixel timed route while preserving non-solid first-contact
  staging.
- Four weapon samples are mapped locally: standard and overheated heavy-rifle
  fire, plus minimum-power and rapid-fire backpack laser-emitter shots.
- The Overworld worker droid uses a 25-frame hover-drift loop and a separate
  25-frame low-hover service loop. It is non-solid, non-hostile, and protected
  by the telescopic laser seeker's friendly-avoidance steering. After Dras
  first contact, a nearby optional assignment can trigger one immediate
  service cycle and recover two Galactic Credits.
- The Overworld sky uses a 25-frame hawk flight source for occasional
  atmospheric passes. Only one hawk can appear at a time, and each completed
  pass alternates between right-to-left and left-to-right travel. The hawk is
  non-hostile, non-solid, and non-targetable. Runtime playback uses a curated
  16-frame cadence that omits near-duplicate wings-up holds around the source
  loop boundary. Supplied frames 12 and 13 touch the bottom source-cell edge;
  the runtime atlas adds padding without reconstructing clipped source pixels.
  In Western Signal Flats the same actor circles the next unfinished
  assignment while that target is on screen.
- Trillian, the player's dog, is live in the optional Western Signal Flats
  loop and remains explicitly separate from Jane. The 36-frame unarmored gait,
  25-frame armored gait, 36-frame powered-jump launch cue, and 36-frame energy
  lunge are loaded only for the Overworld. Recovery unlocks follow behavior;
  the field harness changes her gait and unlocks a physics-driven launch; the
  lunge breaches sealed salvage without defining combat damage. Trillian is
  non-solid, non-hostile, protected by seeker-friendly steering, stops before
  the transport, and does not enter the Foundry.

## Prepared for later integration

- The Tall Gaunt Alien has separate stalking and sweeping-attack atlases.
  It is not spawned until its name, health, damage, recovery, hurt response,
  death sequence, and room population are approved.
- Aryn Sol-Mavi's standard Interworld Fleet apparel has a normalized 25-frame
  walking atlas and a completed full-body standing reference. The standing
  canvas extends downward without rescaling or changing any pixel in the
  supplied cropped 768×768 artwork. It is canonically Aryn, but it does not
  replace her armored Signal Ranger appearance in the Foundry.
- Geemer has a 16-frame source atlas and is cataloged as a ground-and-platform
  walker. It has no runtime derivative, runtime type, or production spawn yet.
- Skree has a validated 25-frame walk atlas, a normalized runtime derivative,
  and the unpopulated runtime type `skree`. Nineteen supplied frames touch the
  right source-cell boundary; the runtime atlas adds padding but does not
  reconstruct the already-clipped source artwork.
- Sova has a validated 36-frame crawl atlas and the unpopulated ground-patrol
  runtime type `sova`.
- Gloam Roller has a validated 36-frame atlas and the unpopulated ground-patrol
  runtime type `gloamRoller`. It crawls through frames 0–27, curls through
  frames 28–31, accelerates to 1.85× patrol speed while the compact frames
  32–35 rotate with its travel direction, then reverses the curl transition
  back to walking. It spins clockwise to the right and counterclockwise to
  the left. Combat balance and production population remain unassigned.
- Seam Lurker has a validated 25-frame crawl atlas and the unpopulated
  ceiling-patrol runtime type `seamLurker`. The supplied art faces the ground;
  its normalized derivative is vertically flipped, centered, and held to a
  stable ceiling contact line. Source silhouettes approach the cell edges but
  never touch them. A drop-attack animation and behavior are not supplied.
- Kihunter has a validated 36-frame flight atlas and the unpopulated airborne
  runtime type `kihunter`.
- A supplemental 25-frame armored sheet is preserved as a review-only
  rear/power-up alternate. It is not suitable as the missing airborne or
  landing continuation: frames 9–17 are clipped at the top, frames 19–24 at
  the left edge, and frames 12–13 at the right edge.

## Storage decisions

- Full-resolution source sheets and their JSON metadata live under `Design/`.
- Only reduced runtime atlases live under `Images/Game/Super-Frgmnts/`.
- The two supplied Fleet-apparel animation folders were byte-identical. One
  canonical source copy is retained.
