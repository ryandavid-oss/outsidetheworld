#!/usr/bin/env python3
"""Verify the beta-production polish decisions from the July playtest."""

import hashlib
import wave
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
SOURCE = GAME.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    required = (
        "function beginEpisodeApproach()",
        '"rd42-atmospheric-approach"',
        "function beginWoundDescentBridge()",
        '"foundry-to-wound-descent"',
        'setAudioScene(isWound ? "wound" : scene);',
        'setAudioScene("wound", false);',
        "var WOUND_BOSS_MOBILE_HEALTH = 136;",
        "var WOUND_BOSS_MOBILE_SPEED_SCALE = 0.72;",
        "var WOUND_BOSS_MOBILE_LASER_COOLDOWN = 6.6;",
        "var WOUND_BOSS_MOBILE_INVULNERABILITY = 1.65;",
        "var WOUND_BOSS_MOBILE_SWEEP_FIRST_FRAME = 16;",
        "var WOUND_BOSS_MOBILE_LASER_LAST_ACTIVE_FRAME = 26;",
        ".touch-key.touch-key--weapon {",
        "var WORKER_DROID_DRAW_WIDTH = 88;",
        "var WORKER_DROID_DRAW_HEIGHT = 85;",
        'canvas.dataset.workerDroidRole =',
        '"portal-repair-standby"',
        'canvas.dataset.workerDroidTalkable = "future";',
        'canvas.dataset.workerDroidScale = "0.70";',
        '"world-space-sky-pass"',
        'canvas.dataset.overworldHawkGuideTarget = "none";',
        "episodeArrivalTutorial = false;",
        'canvas.dataset.assignmentsOptional =',
        '"OPTIONAL"',
        'makeBetaPickup("jetpack", WIDTH * 2 + 240, 280)',
        "function betaPickupAvailable(pickup)",
        '"stabilizer-locked"',
        '"beyond-atmosphere-lock"',
        "heavyRifleOwned = false;",
        'selectedWeapon = "pack";',
        'makeShard(WIDTH * 7 + 430, 548',
        "makeBetaRifleObstacle(WIDTH * 2 + 1280, GROUND_Y)",
        "var cageLeft = obstacle.x + 12;",
        "foundryPlatformModule: {",
        "assets.foundryPlatformModule",
        "foundryThermalPurgeVent: {",
        "foundryArcCoupler: {",
        "function hazardCycleState(hazard)",
        "safeDuration: 1.9",
        "safeDuration: 2.25",
        "activeDuration: 1.1",
        'kind: "thermal"',
        'kind: "arc"',
        'canvas.dataset.sovaRifleHitbox =',
        '"visual-silhouette"',
        "WOUND_COMBAT_LANE_X - 12;",
        "canvas.dataset.woundBossEngageX =",
        "function surfaceTransportIsSealed()",
        '"sealed-after-return"',
        '"RETURN ROUTE SEALED"',
        'canvas.dataset.betaSentinelCount = "7";',
        '"spore-wisp,clacker-beetle,ridge-skitter"',
        '["wasp", WIDTH * 4 + 780',
        "squircle.speed = 124;",
        "coreLeech: { width: 90, height: 110 }",
        "drawSize: 140",
        'enemy.type !== "coreLeech"',
        'enemy.type === "paleWatcher"',
        "var biolabRestoration = biolabStabilizer",
        "canvas.dataset.ventFansMoving",
        'src: "/Audio/super-frgmnts-aryn-jump-v2.wav"',
        'src: "/Audio/super-frgmnts-aryn-land-v2.wav"',
        'src: "/Audio/super-frgmnts-aryn-footstep-v1.wav"',
        'src: "/Audio/super-frgmnts-atmosphere-lock-shimmer-v1.wav"',
        'recordMovementAudio("jump");',
        'recordMovementAudio("footstep");',
        '"landing",',
        '"atmosphereLockShimmer",',
    )
    for token in required:
        require(token in SOURCE, f"Missing beta-polish contract: {token}")

    forbidden = (
        'id: "service-worker-droid"',
        "OUTPOST_DROID_ASSIGNMENT_X",
        '"guide-circle"',
        '"VESPERITE LOCK"',
        'source: "/Images/Game/enemy-crawler-ridge-skitter.png"',
        'source: "/Images/Game/enemy-flyer-spore-wisp.png"',
        'source: "/Images/Game/enemy-walker-clacker-beetle.png"',
    )
    for token in forbidden:
        require(token not in SOURCE, f"Retired behavior remains: {token}")
    require(
        'makeBetaPickup("rifle"' not in SOURCE,
        "The retired production heavy-rifle pickup is still spawned",
    )

    episode_assets = SOURCE.split(
        "var episodeBetaAssetKeys = [",
        1,
    )[1].split("];", 1)[0]
    for retired in ('"crawler"', '"walker"', '"flyer"'):
        require(
            retired not in episode_assets,
            f"Retired placeholder still preloads: {retired}",
        )

    hawk = SOURCE.split(
        "function drawOverworldHawk(now)",
        1,
    )[1].split("function drawOverworldBirds", 1)[0]
    travel = hawk.split(
        "var hawkTotalTravel =",
        1,
    )[1].split(";", 1)[0]
    require("cameraX" not in travel, "Hawk travel still depends on camera")
    require("player." not in hawk, "Hawk flight still depends on Aryn")

    platform_path = (
        ROOT
        / "Images/Game/Super-Frgmnts/foundry-platform-module-runtime-v1.png"
    )
    require(platform_path.exists(), "Missing 16-bit platform runtime sprite")
    with Image.open(platform_path) as platform:
        require(platform.size == (416, 60), "Platform sprite size drifted")
        require(platform.mode == "RGBA", "Platform sprite lost alpha")

    hazard_assets = {
        "thermal purge": (
            ROOT
            / "Images/Game/Super-Frgmnts/"
            "foundry-thermal-purge-vent-runtime-v1.png",
            (512, 128),
        ),
        "arc coupler": (
            ROOT
            / "Images/Game/Super-Frgmnts/"
            "foundry-arc-coupler-runtime-v1.png",
            (512, 160),
        ),
    }
    for label, (path, expected_size) in hazard_assets.items():
        require(path.exists(), f"Missing {label} runtime sprite")
        with Image.open(path) as hazard:
            require(
                hazard.size == expected_size,
                f"{label} sprite size drifted",
            )
            require(
                hazard.mode == "RGBA",
                f"{label} sprite lost alpha",
            )
            require(
                hazard.getchannel("A").getextrema() == (0, 255),
                f"{label} sprite alpha is not production-ready",
            )

    audio_assets = {
        "jump": (
            ROOT / "Audio/super-frgmnts-aryn-jump-v2.wav",
            "4cc651857aa31156869d70fac42610edf1b03818dbc43587cb48039d7eeb602e",
            44100,
            14208,
        ),
        "landing": (
            ROOT / "Audio/super-frgmnts-aryn-land-v2.wav",
            "02a8675ab02fd0cff86a9580a4c2b8919e611c1ebb6c019642a7f155e48917ac",
            44100,
            4736,
        ),
        "footstep": (
            ROOT / "Audio/super-frgmnts-aryn-footstep-v1.wav",
            "911e5849683e090c83263d1adc2ff071c262d1a3a79ceb83c674112ea10469fb",
            44100,
            2560,
        ),
        "atmosphere-lock shimmer": (
            ROOT / "Audio/super-frgmnts-atmosphere-lock-shimmer-v1.wav",
            "8862cfd44215d6ced14c66a2d0ce3c9a168145622e773876e4b7e7f79654e1f5",
            48000,
            48000,
        ),
    }
    for label, (path, expected_hash, expected_rate, expected_frames) in audio_assets.items():
        require(path.exists(), f"Missing {label} audio")
        require(
            hashlib.sha256(path.read_bytes()).hexdigest() == expected_hash,
            f"{label} audio hash drifted",
        )
        with wave.open(str(path), "rb") as audio:
            require(audio.getnchannels() == 2, f"{label} must remain stereo")
            require(
                audio.getsampwidth() == 2,
                f"{label} must remain 16-bit PCM",
            )
            require(
                audio.getframerate() == expected_rate,
                f"{label} sample rate drifted",
            )
            require(
                audio.getnframes() == expected_frames,
                f"{label} duration drifted",
            )

    print("SUPER FRGMNTS beta-production polish: PASS")
    print("- opening and boss-room transition beats are explicit")
    print("- Overworld tutorials and droid discovery task are removed")
    print("- hawk flight is autonomous and Aryn-independent")
    print("- PACK acquisition, obstruction, and combat lanes are separated")
    print("- authored industrial hazards replace abstract colored spikes")
    print("- jump, landing, footsteps, and reversible lock sounds retain source WAVs")
    print("- Sova, boss threshold, and post-return transport states are locked")
    print("- active roster, ventilation restoration, and 16-bit platforms are locked")
    print("- mobile Seam Hunter assist preserves the desktop encounter")


if __name__ == "__main__":
    main()
