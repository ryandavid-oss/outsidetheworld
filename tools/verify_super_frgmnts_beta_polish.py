#!/usr/bin/env python3
"""Verify the beta-production polish decisions from the July playtest."""

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
        "var WOUND_BOSS_MOBILE_HEALTH = 34;",
        "var WOUND_BOSS_MOBILE_SPEED_SCALE = 0.72;",
        "var WOUND_BOSS_MOBILE_LASER_COOLDOWN = 6.6;",
        "var WOUND_BOSS_MOBILE_INVULNERABILITY = 1.65;",
        "var WOUND_BOSS_MOBILE_SWEEP_FIRST_FRAME = 16;",
        "var WOUND_BOSS_MOBILE_LASER_LAST_ACTIVE_FRAME = 26;",
        ".touch-key.touch-key--weapon {",
        "var WORKER_DROID_DRAW_WIDTH = 88;",
        "var WORKER_DROID_DRAW_HEIGHT = 85;",
        'canvas.dataset.workerDroidRole =',
        '"ambient-maintenance"',
        'canvas.dataset.workerDroidScale = "0.70";',
        '"world-space-sky-pass"',
        'canvas.dataset.overworldHawkGuideTarget = "none";',
        "episodeArrivalTutorial = false;",
        'makeBetaPickup("jetpack", 1340, 930)',
        'makeBetaPickup("rifle", WIDTH * 2 + 700, 1518)',
        "makeBetaRifleObstacle(WIDTH * 2 + 1280, GROUND_Y)",
        "var cageLeft = obstacle.x + 12;",
        "foundryPlatformModule: {",
        "assets.foundryPlatformModule",
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

    print("SUPER FRGMNTS beta-production polish: PASS")
    print("- opening and boss-room transition beats are explicit")
    print("- Overworld tutorials and droid discovery task are removed")
    print("- hawk flight is autonomous and Aryn-independent")
    print("- item acquisition, obstruction, and combat lanes are separated")
    print("- active roster, ventilation restoration, and 16-bit platforms are locked")
    print("- mobile Seam Hunter assist preserves the desktop encounter")


if __name__ == "__main__":
    main()
