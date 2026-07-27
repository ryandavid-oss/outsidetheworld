#!/usr/bin/env python3
"""Verify the local pack-fire prototype's non-negotiable contracts."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def function_body(source: str, name: str, next_name: str) -> str:
    start_marker = f"function {name}("
    end_marker = f"function {next_name}("
    start = source.find(start_marker)
    end = source.find(end_marker, start + len(start_marker))
    require(start >= 0, f"Missing {name}()")
    require(end > start, f"Could not bound {name}() before {next_name}()")
    return source[start:end]


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    require("drawBlasterProp" not in source, "Legacy torso gun overlay remains")
    require("drawPackEmitter(visual)" in source, "Pack emitter is not layered over the player")
    require("PACK_EMITTER_ANCHORS" in source, "Animation-specific antenna anchors are missing")
    require("assets.commandRest" in source, "Command Rest is not available to gameplay")
    require(
        "sprite: assets.commandRest" in source and 'pose: "commandRest"' in source,
        "Command Rest is not the immediate canonical idle",
    )
    require(
        '? assets.commandRest\n                        : assets.fieldRest' not in source,
        "The rejected Field Rest to Command Rest delay remains",
    )

    fire_body = function_body(source, "fireBlaster", "enemyCenter")
    require("getPlayerVisualState()" in fire_body, "Fire origin ignores the current animation")
    require("getPackEmitterAnchor(visual)" in fire_body, "Fire origin is not attached to the pack")
    require(
        fire_body.count("player.vx =") == 0,
        "A firing route changes horizontal locomotion",
    )
    require("player.vy =" not in fire_body, "Firing changes vertical locomotion")

    draw_body = function_body(source, "drawPlayer", "drawPackEmitter")
    require("getPlayerVisualState()" in draw_body, "Player drawing bypasses the shared visual state")
    require("drawPackEmitter(visual)" in draw_body, "Emitter is not attached after sprite rendering")

    update_body = function_body(source, "updateBolts", "takeHit")
    require("stats.seekResponse" in update_body, "Seeking response is not applied")
    require("bolt.trail" in update_body, "Curved trajectory history is not maintained")

    for tier in (1, 2, 3):
        require(f"{tier}: {{" in source, f"Missing pack fire tier {tier}")
    require(source.count("seekRange:") >= 3, "Every fire tier needs one seek range")
    require(source.count("seekResponse:") >= 3, "Every fire tier needs one seek response")

    print("Pack-fire contract passed.")
    print("- torso gun overlay removed")
    print("- antenna origin mapped across locomotion states")
    print("- pack and ready-rifle firing leave player velocity untouched")
    print("- seeking and curved tracer enabled at all three tiers")
    print("- Command Rest is the immediate canonical idle")


if __name__ == "__main__":
    main()
