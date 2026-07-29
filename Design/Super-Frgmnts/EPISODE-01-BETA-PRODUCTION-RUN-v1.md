# SUPER FRGMNTS // Episode 01 Beta 2 Production Run

**Status:** Beta 2 production release
**Release:** `episode-01-beta-2`
**Episode:** Arrival on Veyra
**Build target:** One uninterrupted in-page run
**Completion state:** Dras briefed, Wound-touched Vesperite scanned, and
Chapter 01 closed on the Primary Biolab response

## Player-facing sequence

1. The title screen performs the intentional sound handshake.
2. A skippable RD-42 atmospheric-approach beat bridges the title and planet;
   arrival begins on the ship above Landing Flats.
3. The complete four-plate Overworld is available. Western Signal Flats is
   exploration space only; no assignment or tutorial objective appears there.
4. Dras's first-contact scene prepares the Coreworks transport. No tutorial
   platforms, calibration lane, or worker-droid discovery task interrupts the
   Overworld route.
5. The physical transport locks Aryn in place, fades her out, and hands the
   run to The Shard Foundry without reloading the page.
6. The eight-plate Foundry run requires twelve Signal Shards, the Foundry and
   Biolab atmospheric stabilizers, and the cleared three-hit Vesperite lock.
7. Entering the complete Uplink Gate freezes the Foundry state, awards the
   optional annihilation bonus once, establishes the boss checkpoint, and
   plays a skippable five-second descent beat.
8. The Uplink route materializes Aryn in The Wound's safe portal bay and starts
   the boss music immediately. Crossing the combat-runway threshold starts the
   skippable Seam Hunter announcement without restarting the score.
9. Seam Hunter's defeat opens a playable aftermath. Completion still requires
   approaching the exposed Wound-touched Vesperite and pressing Down.
10. Recovery stores the specimen, applies the final time and health bonuses,
    fades the entire stage to black, and automatically returns Aryn beside the
    Coreworks transport on the surface. The return route is sealed and cannot
    send her back into the completed Foundry. The restored stabilizers and
    reduced infestation pressure visibly thin the storm deck and restore
    horizon warmth, while a violet Coreworks remnant remains unresolved.
11. Aryn walks back to Dras and reports both restored atmospheric stabilizers,
    the eliminated Seam Hunter, the geological Wound, and the recovered
    Wound-touched Vesperite. Dras's field probe confirms that the specimen
    holds a signal without losing charge.
12. The report distinguishes the processing-floor Biolab from the Primary
    Biolab below. The transport answers the specimen without input, closing
    Chapter 01 on the Primary Biolab signal.

The production-beta endpoint is the stable post-report Chapter 01 completion
state. The transport repair, RD-42 service-kit objective, and Chapter 02
Primary Biolab expedition remain separate future work.

## Checkpoint contract

The Uplink Gate is the only new production checkpoint in this assembly.

The checkpoint carries:

| State | Foundry → Wound | Wound retry | Wound → surface |
| --- | --- | --- | --- |
| Score | preserve | restore | preserve final |
| Hearts already lost | preserve | restore | clear for safe surface |
| Remaining mission time | preserve | restore | surface becomes untimed |
| Signal Shards | preserve all 12 | restore | no longer an objective |
| Galactic Credits | preserve | restore | preserve |
| Optional Vesperite count | preserve | restore | preserve |
| Jet assist | preserve | restore | preserve |
| Heavy rifle | force ready | restore ready | preserve |
| Seeker tier | preserve | restore | preserve |
| Wound-touched Vesperite | unavailable | unavailable | store as pack material |

A boss loss restarts at the safe Wound portal bay. It must never demand another
eight-plate Foundry clear. A full episode restart remains available through
the normal title/start-over path.

## Transition safety

### Surface transport → Foundry

- Movement is locked for the authored transport cycle.
- Aryn fades before the Foundry scene is configured.
- Galactic Credits persist across the handoff.
- The eight-minute mission clock begins only after Foundry materialization.

### Uplink Gate → The Wound

- The Gate cannot trigger until all three Foundry requirements are true.
- Controls and the mission clock stop at contact.
- The descent bridge may be skipped once and cannot double-trigger.
- The Wound score begins on room entry and remains audible beneath the
  announcement.
- Aryn begins inside the safe portal bay, outside Seam Hunter's activation
  threshold.

### Wound recovery → surface

- Boss death alone never exits the room.
- The timer remains frozen throughout corpse hold, dissolve, reward reveal,
  approach, and material recovery.
- The whole stage reaches opaque black before scene replacement.
- Controls remain locked until the surface fade-in finishes.
- Reduced-motion mode shortens both fades without bypassing the locked state.
- The return URL is reloadable:
  `?episode=01&stage=overworld&autostart=1&return=1`.
- The Coreworks transport remains physically present but sealed. Stepping on
  its deck produces one clear status message and never starts activation.
- Returning to Dras starts the report once. Completing it cannot reopen the
  sealed transport or replay the arrival dialogue.

## Failure and input rules

- Pause, mute, focus loss, touch cancellation, and keyboard control release
  remain valid in every scene.
- Enter/Start only skips the boss announcement; held movement never does.
- Down is the sole Vesperite recovery action on keyboard and touch.
- Aryn cannot take contact, laser, or sweep damage before entering the combat
  runway.
- The production route and the isolated `preview=wound-boss` balancing route
  use the same boss implementation.
- Coarse-pointer and portrait play automatically use the documented mobile
  boss assist; desktop remains on the standard 50-health encounter.

## Review routes

- Full episode:
  `super_frgmnts.html`
- Overworld:
  `super_frgmnts.html?episode=01&stage=overworld&autostart=1`
- Foundry:
  `super_frgmnts.html?episode=01&stage=foundry&autostart=1`
- Production Wound checkpoint:
  `super_frgmnts.html?episode=01&stage=wound&autostart=1`
- Production recovery and return QA:
  `super_frgmnts.html?episode=01&stage=wound&autostart=1&qa=reward`
- Reloadable surface return:
  `super_frgmnts.html?episode=01&stage=overworld&autostart=1&return=1`

The reloadable surface-return route is the fastest report-and-cliffhanger QA
entry. Walk left to Dras and press Down at `REPORT`.

## Beta acceptance gate

- Arrival, all four Overworld plates, transport, all eight Foundry plates,
  The Wound, and surface return render without console errors or missing
  critical artwork.
- The Uplink checkpoint preserves the state matrix above.
- Boss retry begins in the safe bay with the announcement rearmed.
- Recovery is impossible before the corpse dissolve and material reveal.
- The black transition cannot expose the scene swap or allow invisible input.
- The return report names both stabilizers, the Seam Hunter, the Wound, the
  Wound-touched Vesperite, and the Primary Biolab before the cliffhanger.
- Chapter completion leaves Aryn on Veyra with the transport visible and
  inactive.
- Arrival and post-Wound return expose distinct sky states: the return is
  clearer, but the Coreworks infestation remnant survives the stabilizer
  restoration and supports the Primary Biolab cliffhanger.
- Entering the RD-42 preloads and crossfades to its dedicated interior loop;
  exiting returns to the Overworld score without a hard cut.
- Desktop and 390 × 844 portrait framing keep Aryn, the current objective, and
  the next commitment legible.
- JavaScript syntax, every `verify_super_frgmnts_*.py` contract, and
  `git diff --check` pass before a production deployment is considered.
- Deployment still requires explicit approval and a separate live GitHub
  Pages verification.
