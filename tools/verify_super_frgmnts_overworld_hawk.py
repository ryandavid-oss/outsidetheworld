#!/usr/bin/env python3
"""Verify the ambient, non-hostile SUPER FRGMNTS Overworld hawk."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Sky-Wildlife/Hawk-Ludo"
)
MANIFEST = FAMILY / "overworld-hawk-runtime-v1.json"
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def verify_atlas(path: Path) -> None:
    atlas = Image.open(path).convert("RGBA")
    assert atlas.size == (720, 560), (
        f"{path.name}: expected 720x560, got {atlas.size}"
    )
    for index in range(25):
        x = index % 5 * 144
        y = index // 5 * 112
        frame = atlas.crop((x, y, x + 144, y + 112))
        bound = frame.getchannel("A").getbbox()
        assert bound is not None, f"{path.name}: frame {index} is blank"
        assert bound[0] > 0 and bound[1] > 0
        assert bound[2] < 144 and bound[3] < 112


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["workingName"] == "Overworld Hawk"
    assert manifest["status"] == "overworld-runtime"
    assert manifest["scene"] == "overworld"
    assert manifest["role"] == "ambient sky wildlife"
    assert manifest["hostile"] is False
    assert manifest["solid"] is False
    assert manifest["targetable"] is False
    assert manifest["source"]["frameCount"] == 25
    assert manifest["source"]["frameDurationMs"] == 58
    assert manifest["validation"]["result"] == "pass-with-source-warning"
    assert manifest["validation"]["edgeContactFrames"]["bottom"] == [12, 13]
    assert manifest["runtime"]["atlasFrameCount"] == 25
    assert manifest["runtime"]["playbackFrameCount"] == 16
    assert manifest["runtime"]["playbackSequence"] == [
        5,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        22,
        24,
    ]
    assert manifest["runtime"]["loopDurationMs"] == 928
    assert manifest["behavior"]["collision"] is False
    assert manifest["behavior"]["friendlySeekerSafety"] is True
    assert manifest["behavior"]["maxConcurrent"] == 1
    assert manifest["behavior"]["directionPattern"] == (
        "alternate after every completed pass"
    )
    assert manifest["behavior"]["guideTargets"] == [
        "survey-echo",
        "recover-trillian",
        "field-harness",
        "sealed-salvage",
    ]
    verify_atlas(ROOT / manifest["runtime"]["image"])

    required_fragments = (
        "overworldHawk: {",
        '"overworldHawk",',
        "var HAWK_FRAME_WIDTH = 144;",
        "var HAWK_FRAME_HEIGHT = 112;",
        "var HAWK_FLIGHT_SEQUENCE = [",
        "function drawOverworldHawk(now)",
        "drawOverworldHawk(now);",
        'canvas.dataset.overworldHawkHostile = "false";',
        'canvas.dataset.overworldHawkSolid = "false";',
        'canvas.dataset.overworldHawkTargetable = "false";',
        'canvas.dataset.overworldHawkDirection =',
        '"guide-circle"',
        "canvas.dataset.overworldHawkGuideTarget",
        "var hawkGuideTarget =",
        "assignment.x < WIDTH",
        "hawkPassIndex % 2 === 0 ? -1 : 1;",
        "if (hawkDirection > 0) {",
    )
    for fragment in required_fragments:
        assert fragment in SOURCE, (
            f"Overworld hawk runtime registration is missing: {fragment}"
        )

    assert SOURCE.count("function drawOverworldHawk(now)") == 1
    assert SOURCE.count("drawOverworldHawk(now);") == 1
    assert 'makeEnemy("overworldHawk"' not in SOURCE
    assert "enemies.push(overworldHawk)" not in SOURCE
    assert 'enemy.type === "overworldHawk"' not in SOURCE

    print("SUPER FRGMNTS Overworld hawk: PASS")
    print("- validated 25-frame flight loop")
    print("- tuned 16-frame playback removes duplicate loop-boundary holds")
    print("- one hawk alternates direction after each atmospheric pass")
    print("- on-screen western assignments receive a guide-circle")
    print("- non-hostile, non-solid, and absent from enemy targeting")
    print("- 720x560 runtime atlas includes transparent padding")


if __name__ == "__main__":
    main()
