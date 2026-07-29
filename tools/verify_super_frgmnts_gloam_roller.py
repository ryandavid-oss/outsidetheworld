#!/usr/bin/env python3
"""Verify the Gloam Roller asset and unpopulated runtime type."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT / "Design/Super-Frgmnts/Foundry/Enemies/Gloam-Roller"
)
MANIFEST = FAMILY / "gloam-roller-runtime-v1.json"
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["workingName"] == "Gloam Roller"
    assert manifest["runtimeType"] == "gloamRoller"
    assert manifest["status"] == "runtime-ready-unpopulated"
    assert manifest["productionPopulation"] is False
    assert manifest["source"]["frameCount"] == 36
    assert manifest["source"]["frameDurationMs"] == 52
    assert manifest["validation"]["result"] == "pass"
    assert manifest["validation"]["edgeContactFrames"] == {}
    assert (
        manifest["behavior"]["locomotion"]
        == "crawl-to-roll ground patrol"
    )
    assert manifest["behavior"]["phases"] == {
        "crawlFrames": [0, 27],
        "curlFrames": [28, 31],
        "rollingFrames": [32, 35],
        "uncurlFrames": [31, 28],
    }
    assert manifest["behavior"]["behaviorCycleDurationMs"] == 2912
    assert manifest["behavior"]["rollDurationMs"] == 1040
    assert manifest["behavior"]["rollSpeedMultiplier"] == 1.85
    assert manifest["behavior"]["rotation"] == (
        "distance-driven; clockwise right, counterclockwise left"
    )
    assert manifest["behavior"]["spawned"] is False

    atlas = Image.open(ROOT / manifest["runtime"]["image"]).convert("RGBA")
    assert atlas.size == (768, 480), (
        f"Expected 768x480 atlas, got {atlas.size}"
    )
    for index in range(36):
        x = index % 6 * 128
        y = index // 6 * 80
        frame = atlas.crop((x, y, x + 128, y + 80))
        bound = frame.getchannel("A").getbbox()
        assert bound is not None, f"Frame {index} is blank"
        assert bound[0] > 0 and bound[1] > 0
        assert bound[2] < 128 and bound[3] < 80

    preview = Image.open(
        ROOT / manifest["runtime"]["behaviorPreview"]
    )
    assert preview.size == (720, 160)
    assert preview.n_frames == 112

    required_fragments = (
        "gloamRoller: {",
        '"gloamRoller",',
        "gloamRoller: { width: 96, height: 50 }",
        'if (enemy.type === "gloamRoller") {',
        'gloamRoller: "GLOAM ROLLER"',
        "function gloamRollerAnimationState(enemy)",
        "GLOAM_ROLLER_ROLL_SPEED_MULTIPLIER",
        "enemy.rollAngle -=",
        'enemy.type === "gloamRoller" &&',
        "ctx.rotate(enemy.rollAngle)",
        "function drawIntakeEnemy(enemy)",
    )
    for fragment in required_fragments:
        assert fragment in SOURCE, (
            f"Gloam Roller runtime registration is missing: {fragment}"
        )

    make_enemy = SOURCE.split(
        "function makeEnemy(type, x, floorOrAirY, minX, maxX, speed)",
        1,
    )[1].split("function makeWoundBoss", 1)[0]
    flyer_block = make_enemy.split("var isFlyer =", 1)[1].split(
        "return {",
        1,
    )[0]
    assert 'type === "gloamRoller"' not in flyer_block
    assert 'makeEnemy("gloamRoller"' not in SOURCE

    print("SUPER FRGMNTS Gloam Roller enemy type: PASS")
    print("- 36-frame crawl-to-roll source validates without edge contact")
    print("- crawl, curl, rolling spin, and reverse uncurl are registered")
    print("- rightward roll spins clockwise; leftward roll spins counterclockwise")
    print("- production population remains disabled")
    print("- 768x480 shipping atlas stays below portability limits")


if __name__ == "__main__":
    main()
