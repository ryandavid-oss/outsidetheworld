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
    "blaster": "super-frgmnts-blaster-shot.mp3",
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
        "var soundEffects = {",
        "poolSize: 10",
        'playSoundEffect("blaster")',
        'playSoundEffect("deepSelect", 0.58)',
        'playSoundEffect(state === "lost" ? "crashSelect" : "deepSelect")',
        'playSoundEffect("crashSelect")',
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
        "playSoundEffect(\"blaster\")" in blaster_body.group(1),
        "Blaster does not use the sampled shot",
    )
    require(
        "playTone(" not in blaster_body.group(1),
        "Legacy synthesized blaster tones still double the sampled shot",
    )

    require(
        source.count('playSoundEffect("crashSelect")') >= 4,
        "Crash select is not mapped across destructive actions",
    )

    print("SUPER FRGMNTS audio contract: PASS")
    print("- title, overworld, and Foundry music routes are distinct")
    print("- rapid-fire blaster uses a ten-channel sampled-audio pool")
    print("- deep select confirms forward actions and dialogue")
    print("- crash select confirms retry, restart, start-over, and skip")
    print("- sampled effects stop on pause, mute, and focus loss")


if __name__ == "__main__":
    main()
