#!/usr/bin/env python3
"""Verify the supplied RD-42 interior score and its runtime integration."""

from __future__ import annotations

import hashlib
import json
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
MANIFEST = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Ship/Interior/Audio"
    / "rd42-interior-music-v1.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def digest(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_audio = ROOT / manifest["source"]["path"]
    runtime_audio = ROOT / manifest["runtime"]["path"]

    require(
        manifest["status"] == "beta-production",
        "RD-42 music manifest is not beta-production",
    )
    require(source_audio.exists(), "Missing preserved RD-42 WAV master")
    require(runtime_audio.exists(), "Missing RD-42 M4A runtime loop")
    require(
        digest(source_audio) == manifest["source"]["sha256"],
        "RD-42 WAV master hash drifted",
    )
    require(
        digest(runtime_audio) == manifest["runtime"]["sha256"],
        "RD-42 M4A runtime hash drifted",
    )

    with wave.open(str(source_audio), "rb") as wav:
        require(wav.getnchannels() == 2, "RD-42 master must remain stereo")
        require(
            wav.getframerate() == 48000,
            "RD-42 master sample rate drifted",
        )
        require(
            wav.getsampwidth() == 2,
            "RD-42 master must remain 16-bit PCM",
        )
        duration = wav.getnframes() / wav.getframerate()
        require(
            abs(duration - 120.0) < 0.01,
            "RD-42 master must remain a two-minute loop",
        )

    with runtime_audio.open("rb") as stream:
        header = stream.read(32)
    require(b"ftypM4A" in header, "RD-42 runtime is not an M4A container")
    require(
        2_000_000 < runtime_audio.stat().st_size < 3_500_000,
        "RD-42 runtime compression budget drifted",
    )

    required_tokens = (
        'data-interior-track="/Audio/super-frgmnts-rd42-interior-loop-v1.m4a"',
        "interior: backgroundMusic.dataset.interiorTrack",
        "interior: 0.27",
        'setAudioScene("interior", false);',
        'setAudioScene("overworld", false);',
        'preloadIdleMusicScene("interior");',
        "function preloadIdleMusicScene(nextScene)",
        'idleMusicChannel.preload = "auto";',
        'idleMusicChannel.loop =\n                    nextScene !== "title";',
        "musicFadeTimer = window.setInterval(fadeMusic, 24)",
    )
    for token in required_tokens:
        require(token in source, f"Missing RD-42 music runtime token: {token}")

    require(
        manifest["transitions"]["crossfadeMs"] == 480,
        "RD-42 manifest crossfade timing drifted",
    )
    require(
        manifest["runtime"]["volume"] == 0.27,
        "RD-42 manifest mix level drifted",
    )

    print("SUPER FRGMNTS RD-42 interior music: PASS")
    print("- supplied 120 s stereo PCM master is preserved losslessly")
    print("- compressed M4A runtime stays inside the web delivery budget")
    print("- hatch preload and 480 ms bidirectional crossfades are wired")
    print("- interior mix participates in the shared audio lifecycle")


if __name__ == "__main__":
    main()
