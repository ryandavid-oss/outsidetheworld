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
    "wound": "super-frgmnts-seam-hunter-boss-v1.m4a",
    "interior": "super-frgmnts-rd42-interior-loop-v1.m4a",
    "heavy_rifle": "super-frgmnts-heavy-rifle-shot.mp3",
    "heavy_rifle_overheat": "super-frgmnts-heavy-rifle-overheat.mp3",
    "pack_laser": "super-frgmnts-pack-laser-shot.mp3",
    "pack_laser_quick": "super-frgmnts-pack-laser-quick.mp3",
    "generator_startup": "super-frgmnts-generator-startup-v1.wav",
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
        '"generatorStartup"',
        "canvas.dataset.lastSoundEffect = name;",
        'playSoundEffect("deepSelect", 0.58)',
        'playSoundEffect(state === "lost" ? "crashSelect" : "deepSelect")',
        'playSoundEffect("crashSelect")',
        "function engageSceneAudioFromGesture()",
        "function initializeSignal()",
        "function setAudioScene(nextScene, immediate)",
        "function preloadIdleMusicScene(nextScene)",
        "function musicIsPlaying()",
        "var musicTracks = {",
        "var musicVolumes = {",
        "musicFadeTimer = window.setInterval(fadeMusic, 24)",
        "if (!musicIsPlaying())",
        "if (pressed) {\n                    engageSceneAudioFromGesture();",
        '"pointerdown",\n                engageSceneAudioFromGesture,',
        '"click",\n                engageSceneAudioFromGesture,',
        'window.addEventListener("keydown", engageSceneAudioFromGesture);',
        'setAudioScene(isWound ? "wound" : scene);',
        'setAudioScene("wound", false);',
        'setAudioScene("interior", false);',
        'preloadIdleMusicScene("interior");',
        'loadAndConfigureEpisodeScene("foundry")',
        "function pauseSoundEffects()",
        "pauseAudioForFocusLoss()",
        "pauseSoundEffects();",
    )
    for token in required_tokens:
        require(token in source, f"Missing audio runtime contract: {token}")

    require(
        re.search(
            r"var selectedMusicTrack = mainTitleScreen.*?"
            r"woundBossPreview.*?backgroundMusic\.dataset\.woundTrack",
            source,
            flags=re.DOTALL,
        )
        is not None,
        "Direct Wound loads do not select the boss score",
    )
    require(
        re.search(
            r"var audioScene = mainTitleScreen.*?"
            r"woundBossPreview.*?\"wound\"",
            source,
            flags=re.DOTALL,
        )
        is not None,
        "Direct Wound loads do not initialize the wound audio scene",
    )
    require(
        re.search(
            r"var selectedMusicTrack = mainTitleScreen.*?"
            r"shipInteriorPreview.*?"
            r"backgroundMusic\.dataset\.interiorTrack",
            source,
            flags=re.DOTALL,
        )
        is not None,
        "Direct RD-42 interior loads do not select the interior score",
    )
    require(
        re.search(
            r"var audioScene = mainTitleScreen.*?"
            r"shipInteriorPreview.*?\"interior\"",
            source,
            flags=re.DOTALL,
        )
        is not None,
        "Direct RD-42 interior loads do not initialize the interior audio scene",
    )

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

    stabilizer_body = re.search(
        r"function updateAtmosphericStabilizers\(delta\) \{(.*?)\n            \}\n\n"
        r"            function getOverworldAssignment",
        source,
        flags=re.DOTALL,
    )
    require(
        stabilizer_body is not None,
        "Could not inspect atmospheric stabilizer activation",
    )
    require(
        'stabilizer.activationElapsed >= 0.3' in stabilizer_body.group(1)
        and 'playSoundEffect("generatorStartup")' in stabilizer_body.group(1),
        "Generator startup sample is not synchronized to the relay beat",
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
    print("- title, Overworld, Foundry, Wound, and RD-42 music route by scene")
    print("- the RD-42 loop preloads at the hatch and crossfades on entry/exit")
    print("- heavy-rifle fire switches to its overheat sample on the threshold shot")
    print("- pack-emitter tiers select minimum-power or rapid-fire laser samples")
    print("- atmospheric stabilizers trigger the authored generator wake at 0.30 s")
    print("- deep select confirms forward actions and dialogue")
    print("- crash select confirms retry, restart, start-over, and skip")
    print("- sampled effects stop on pause, mute, and focus loss")


if __name__ == "__main__":
    main()
