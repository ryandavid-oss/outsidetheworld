# SUPER FRGMNTS — animation intake, 2026-07-26

## Integrated

- The Veyra camp dog now uses all 36 supplied walking frames and all 16
  supplied sniffing frames. Its gait faces the direction of travel; sniffing
  occurs occasionally as one three-second dip-and-rise rather than a
  continuously repeating loop. The existing route, non-solid behavior, and
  camp staging remain intact.
- Four weapon samples are mapped locally: standard and overheated heavy-rifle
  fire, plus minimum-power and rapid-fire backpack laser-emitter shots.

## Prepared for later integration

- The Tall Gaunt Alien has separate stalking and sweeping-attack atlases.
  It is not spawned until its name, health, damage, recovery, hurt response,
  death sequence, and room population are approved.
- Aryn Sol-Mavi's standard Interworld Fleet apparel has a normalized 25-frame
  walking atlas. It is canonically Aryn, but it does not replace her armored
  Signal Ranger appearance in the Foundry.

## Storage decisions

- Full-resolution source sheets and their JSON metadata live under `Design/`.
- Only reduced runtime atlases live under `Images/Game/Super-Frgmnts/`.
- The two supplied Fleet-apparel animation folders were byte-identical. One
  canonical source copy is retained.
