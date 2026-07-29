# SUPER FRGMNTS // Seam Hunter Boss Music v1

**Status:** Approved track integrated in the isolated Wound boss trial

## Track

- Title: **Subterranean Apex**
- Runtime asset:
  `Audio/super-frgmnts-seam-hunter-boss-v1.m4a`
- Preserved source:
  `Design/Super-Frgmnts/Foundry/Boss-Room/Music/Raw/subterranean-apex-source-v1.wav`
- Runtime format: 48 kHz, stereo AAC in M4A at approximately 193 kbps
- Source format: 48 kHz, 16-bit, stereo PCM WAV
- Duration: 120.000 seconds
- Peak: -1.01 dBFS
- Integrated runtime volume: 0.38

The supplied master contains no clipped samples and retains its authored
1.88-second quiet tail. The web runtime is a high-quality 192 kbps AAC
transcode, reducing the boss-route preload from 22 MB to 2.8 MB. The
byte-identical WAV master remains in `Raw/`.

## Encounter lifecycle

- The Foundry score continues while Aryn approaches the combat threshold.
- The Foundry score ducks under the encounter announcement.
- On a full viewing, the dedicated Seam Hunter track starts from its opening
  at 5.05 seconds, exactly as the cleared screen begins revealing him.
- Skipping starts the dedicated track immediately from its opening.
- The track loops if the encounter exceeds two minutes.
- Victory, loss, and retry return to the Foundry score.
- Retrying restores the complete announcement before the boss track begins
  again.

The secondary music channel preloads the boss track on the isolated Wound
route so its first beat is ready when combat begins.

## Reveal contract

Seam Hunter and his health bar remain completely unrendered through the empty
approach and the full announcement. Once the words and darkness clear at 4.90
seconds, the music and a 1.2-second monster fade begin at 5.05 seconds. His
health bar waits until gameplay resumes. This prevents wide desktop viewports
from revealing the boss before his formal introduction. The pre-announcement
mission readout likewise identifies only an unresolved hostile signal.

## QA

Playable route:

`super_frgmnts.html?preview=wound-boss&autostart=1`

Threshold-review route:

`super_frgmnts.html?preview=wound-boss&autostart=1&qa=intro`

Key canvas telemetry:

- `data-music-scene`: `foundry` before the announcement and `wound` in combat
- `data-music-target-volume`: `0.38` during the boss score
- `data-wound-boss-reveal`: `concealed`, `fading`, or `visible`
- `data-wound-boss-reveal-alpha`: eased presentation opacity from `0.00` to
  `1.00`
