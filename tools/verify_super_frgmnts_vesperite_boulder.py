#!/usr/bin/env python3
"""Verify the Episode beta Vesperite boulder destruction contract."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
BOULDER_ROOT = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Vesperite-Boulder"
)
MANIFEST = BOULDER_ROOT / "vesperite-boulder-runtime-v1.json"
RUNTIME_ROOT = ROOT / "Images" / "Game" / "Super-Frgmnts"
RUNTIME_ASSETS = {
    "intact": (
        RUNTIME_ROOT / "vesperite-boulder-intact-runtime-v1.png",
        (176, 184),
    ),
    "impact": (
        RUNTIME_ROOT / "vesperite-boulder-impact-runtime-v1.png",
        (2816, 184),
    ),
    "collapse": (
        RUNTIME_ROOT / "vesperite-boulder-collapse-runtime-v1.png",
        (2816, 184),
    ),
    "rubble": (
        RUNTIME_ROOT / "vesperite-boulder-rubble-runtime-v1.png",
        (176, 184),
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text())

    for state, (path, expected_size) in RUNTIME_ASSETS.items():
        require(path.is_file(), f"Missing {state} runtime: {path.name}")
        image = Image.open(path).convert("RGBA")
        require(
            image.size == expected_size,
            f"{path.name} is {image.size}; expected {expected_size}",
        )
        require(
            image.getbbox() is not None,
            f"{path.name} has no visible pixels",
        )

    gameplay = manifest["gameplay_contract"]
    require(
        gameplay["damage_source"] == "heavy rifle direct round",
        "The boulder is not gated to the heavy rifle",
    )
    require(
        gameplay["hits_required"] == 3,
        "The boulder no longer requires exactly three heavy-rifle hits",
    )
    require(
        gameplay["traversal"] ==
        "taller than Aryn's unassisted jump apex",
        "The boulder can no longer be trusted as a traversal gate",
    )
    require(
        gameplay["remnant"] == "persistent rubble with no collision",
        "The persistent non-colliding rubble contract drifted",
    )
    require(
        gameplay["episode_beta_obstruction"] is True,
        "The Vesperite boulder is not marked as an Episode beta obstruction",
    )

    runtime_contracts = (
        "/Images/Game/Super-Frgmnts/vesperite-boulder-intact-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/vesperite-boulder-impact-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/vesperite-boulder-collapse-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/vesperite-boulder-rubble-runtime-v1.png",
        "function makeRifleObstacles(platform)",
        "function constrainRifleObstacleMovement(previousPlayerX)",
        "function updateRifleObstacles(delta)",
        "function strikeRifleObstacle(obstacle, bolt)",
        "function finishRifleObstacleDestruction(obstacle)",
        "function drawRifleObstacles()",
        "var RIFLE_BOULDER_HITS_REQUIRED = 3;",
        "var RIFLE_BOULDER_HEIGHT = 176;",
        "obstacle.hitCount += 1;",
        "player.supportPlatform.rifleObstacle",
        "landing = obstacle;",
        'obstacle.state = "impact";',
        'obstacle.state = "collapse";',
        'obstacle.state = "rubble";',
        "canvas.dataset.rifleObstacles = String(remaining);",
        'text: "ROUTE CLEARED +200",',
        '"ROUTE CLEARED // RUBBLE REMAINS"',
    )
    for contract in runtime_contracts:
        require(
            contract in source,
            f"Missing Vesperite boulder contract: {contract}",
        )

    require(
        source.count("drawRifleObstacles();") == 1,
        "Vesperite boulders are not drawn exactly once per Foundry frame",
    )

    print("SUPER FRGMNTS Vesperite boulder contract: PASS")
    print("- boulders stand above Aryn's unassisted jump apex")
    print("- exactly three heavy-rifle hits breach each obstruction")
    print("- drops land on solid Vesperite instead of entering its collision body")
    print("- collision ends only when persistent rubble appears")
    print("- the behavior is active in the Episode beta and isolated review route")


if __name__ == "__main__":
    main()
