# SUPER FRGMNTS dialogue contract

Status: Revision 3C approved for local integration, with the Revision 3G
portrait set under local review. Production remains untouched.

## Recommended visual direction

Use **Field Relay** for live character conversations. It makes Dras human before
he becomes a lore delivery system, gives the palette room to breathe, and
preserves the scene behind the panel. Reserve **Coreworks Archive** for abandoned
terminals, recovered logs, system warnings, and non-human transmissions.

## Interaction

- Opening dialogue pauses the simulation, timer, hostile motion, and actor input.
- Touch controls disappear while the dialogue is active.
- Keyboard: Enter or Space completes/advances; Escape opens a skip confirmation.
- Touch: first tap completes a visual text reveal; the next tap advances.
- Skip is the secondary left-hand action; Continue is the primary right-hand
  action. Confirmation screens preserve the same spatial hierarchy.
- Continue is always visible and at least 44 by 44 CSS pixels.
- Skip is available but visually secondary. Closing restores focus to gameplay.

## Text volume

- One thought per card.
- Prefer 38–44 visible characters per desktop line and 28–35 on mobile.
- Prefer 2–3 short visual lines; never exceed 5 mobile lines.
- Avoid orphaned one-word lines and text over scenic faces.

## Accessibility

- Use a labelled `role="dialog"` container while gameplay is paused.
- Put the full card text in the accessibility tree when the card opens; never
  announce typewriter characters one by one.
- Move focus to Continue and keep keyboard focus inside the dialogue.
- Speaker identity must be text, not portrait or color alone.
- Reduced motion reveals the complete card immediately and disables portrait,
  border, waveform, and indicator animation.
- High-contrast mode strengthens the panel fill and uses a 3px light border.
- Meaning never depends on amber, pink, cyan, or animated light alone.

## Presentation

- Field Relay uses `palette.html`: Brand Teal for structure, Brand Gold for the
  speaker, Brand Light Blue for actions, Brand Pink for progress, and Void Dark
  for the panel.
- The scene dims only enough to establish focus; actors remain visible.
- Dras's portrait is optional after first contact, but the nameplate is permanent.
- Dialogue animation and audio pause whenever the page loses visibility.

## Portrait authority

Revision 3G replaced magnified full-body sprites with purpose-built,
chest-and-shoulders dialogue portraits. Revision 3I raises Aryn to the same
apparent native detail and material finish as Dras while preserving her
approved helmet, visor, armor palette, signal pack, and weapon-free silhouette:

- `Assets/aryn-dialogue-portrait-v3.png`
- `Assets/dras-dialogue-portrait-v2.png`

The browser loads Aryn's 512 × 512 `runtime-v3` and Dras's 512 × 512
`runtime-v2`. Aryn's 1254 × 1254 alpha master and Dras's 1318 × 1318 padded
alpha master remain the visual authorities. Their exact built-in ImageGen
specifications are stored in `aryn-dialogue-portrait-prompt-v3.txt` and
`dras-dialogue-portrait-prompt-v2.txt`; the generated chroma sources are
retained under `Raw/`. Aryn's earlier v2 files remain available for rollback.

Dras must read as weathered and formidable rather than ill or frail. Both
portraits keep the eyes or visor in the upper third and preserve enough
shoulder mass to read clearly on a phone.

## Canon opening

`CANON-ARRIVAL-ON-VEYRA.md` is the dialogue source of truth for the first
meeting between Aryn Sol-Mavi and Dras Ehdre. The former six-card working copy
is retired.

The local integration performs these approved stage beats:

- the ground trembles after D10;
- a non-spoken `VEYRA // SUBSURFACE TREMOR` caption gives that motion context;
- Aryn disconnects her Fleet wristpad before D12;
- Dras reacts to her unsanctioned arrival;
- the portal begins its ignition after D36;
- the conversation returns control with the portal route open.
