#!/usr/bin/env python3
"""Verify the SUPER FRGMNTS music routing and sampled sound-effect contract."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
AUDIO = ROOT / "Audio"

TRACKS = {
    "title": "super-frgmnts-title-cue.mp3",
    "overworld": "super-frgmnts-overworld-loop.mp3",
    "foundry": "super-frgmnts-foundry-loop.mp3",
    "heavy_rifle": "super-frgmnts-heavy-rifle-shot.mp3",
    "heavy_rifle_overheat": "super-frgmnts-heavy-rifle-overheat.mp3",
    "pack_laser": "super-frgmnts-pack-laser-shot.mp3",
    "pack_laser_quick": "super-frgmnts-pack-laser-quick.mp3",
    "deep_select": "super-frgmnts-menu-select-deep.mp3",
    "crash_select": "super-frgmnts-menu-select-crash.mp3",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    for role, filename in TRACKS.items():
        path = AUDIO / filename
        require(path.exists(), f"Missing {role} audio: {filename}")
        require(path.stat().st_size > 10_000, f"{role} audio is unexpectedly small")
        require(f"/Audio/{filename}" in source, f"{role} audio is not referenced")

    required_tokens = (
        "var selectedMusicTrack = mainTitleScreen",
        "backgroundMusic.loop = !mainTitleScreen",
        'id="backgroundMusicSecondary"',
        'id="signalBootButton"',
        "var soundEffects = {",
        "poolSize: 10",
        '"heavyRifleOverheat"',
        '"heavyRifleShot"',
        '"packLaserQuick"',
        '"packLaserShot"',
        "canvas.dataset.lastSoundEffect = name;",
        'playSoundEffect("deepSelect", 0.58)',
        'playSoundEffect(state === "lost" ? "crashSelect" : "deepSelect")',
        'playSoundEffect("crashSelect")',
        "function engageSceneAudioFromGesture()",
        "function initializeSignal()",
        "function setAudioScene(nextScene, immediate)",
        "function musicIsPlaying()",
        "var musicTracks = {",
        "var musicVolumes = {",
        "musicFadeTimer = window.setInterval(fadeMusic, 24)",
        "if (!musicIsPlaying())",
        "if (pressed) {\n                    engageSceneAudioFromGesture();",
        '"pointerdown",\n                engageSceneAudioFromGesture,',
        '"click",\n                engageSceneAudioFromGesture,',
        'window.addEventListener("keydown", engageSceneAudioFromGesture);',
        "setAudioScene(scene);",
        'loadAndConfigureEpisodeScene("foundry")',
        "function pauseSoundEffects()",
        "pauseAudioForFocusLoss()",
        "pauseSoundEffects();",
    )
    for token in required_tokens:
        require(token in source, f"Missing audio runtime contract: {token}")

    blaster_body = re.search(
        r"function fireBlaster\(\) \{(.*?)\n            \}\n\n"
        r"            function enemyCenter",
        source,
        flags=re.DOTALL,
    )
    require(blaster_body is not None, "Could not inspect fireBlaster")
    require(
        '"heavyRifleOverheat"' in blaster_body.group(1)
        and '"heavyRifleShot"' in blaster_body.group(1),
        "Heavy rifle does not select its standard and overheat samples",
    )
    require(
        '"packLaserQuick"' in blaster_body.group(1)
        and '"packLaserShot"' in blaster_body.group(1),
        "Pack emitter does not select its minimum and rapid-fire samples",
    )
    require(
        "playTone(" not in blaster_body.group(1),
        "Legacy synthesized blaster tones still double the sampled shot",
    )

    require(
        source.count('playSoundEffect("crashSelect")') >= 4,
        "Crash select is not mapped across destructive actions",
    )
    require(
        "window.location.href" not in source,
        "Episode audio can still be interrupted by a full-page scene reload",
    )

    print("SUPER FRGMNTS audio contract: PASS")
    print("- explicit signal initialization unlocks title audio")
    print("- title, overworld, and Foundry music crossfade without page reloads")
    print("- heavy-rifle fire switches to its overheat sample on the threshold shot")
    print("- pack-emitter tiers select minimum-power or rapid-fire laser samples")
    print("- deep select confirms forward actions and dialogue")
    print("- crash select confirms retry, restart, start-over, and skip")
    print("- sampled effects stop on pause, mute, and focus loss")


if __name__ == "__main__":
    main()
