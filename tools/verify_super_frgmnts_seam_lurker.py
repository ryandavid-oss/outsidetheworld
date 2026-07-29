#!/usr/bin/env python3
"""Verify the Seam Lurker asset and populated Uplink ceiling patrol."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "Design/Super-Frgmnts/Foundry/Enemies/Seam-Lurker"
MANIFEST = FAMILY / "seam-lurker-runtime-v1.json"
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["workingName"] == "Seam Lurker"
    assert manifest["runtimeType"] == "seamLurker"
    assert manifest["status"] == "production-populated"
    assert manifest["productionPopulation"] is True
    assert manifest["source"]["frameCount"] == 25
    assert manifest["source"]["frameDurationMs"] == 58
    assert manifest["source"]["orientation"] == "ground-facing"
    assert manifest["validation"]["result"] == "pass-with-source-warning"
    assert manifest["validation"]["edgeContactFrames"] == {}
    assert manifest["validation"]["nearEdgeFrames"]["top"] == list(
        range(25)
    )
    assert manifest["runtime"]["orientation"] == (
        "ceiling-facing vertical normalization"
    )
    assert manifest["runtime"]["anchor"] == "ceiling"
    assert manifest["behavior"]["locomotion"] == (
        "horizontal ceiling patrol"
    )
    assert manifest["behavior"]["crawlAnimation"] == "ready"
    assert manifest["behavior"]["dropAttackAnimation"] == "not supplied"
    assert manifest["behavior"]["dropAttackBehavior"] == "unimplemented"
    assert manifest["behavior"]["spawned"] is True
    assert manifest["behavior"]["productionPlacement"] == (
        "Uplink plate 7 catwalk underside at y=362"
    )
    assert manifest["behavior"]["combatBalance"] == (
        "two rifle hits; horizontal ceiling patrol only"
    )

    atlas = Image.open(ROOT / manifest["runtime"]["image"]).convert("RGBA")
    assert atlas.size == (640, 320), (
        f"Expected 640x320 atlas, got {atlas.size}"
    )
    for index in range(25):
        x = index % 5 * 128
        y = index // 5 * 64
        frame = atlas.crop((x, y, x + 128, y + 64))
        bound = frame.getchannel("A").getbbox()
        assert bound is not None, f"Frame {index} is blank"
        assert bound[0] > 0 and bound[2] < 128
        assert bound[1] == 4, (
            f"Frame {index} lost the stable ceiling anchor: {bound}"
        )
        assert bound[3] < 64

    preview = Image.open(
        ROOT / manifest["runtime"]["behaviorPreview"]
    )
    assert preview.size == (720, 144)
    assert preview.n_frames == 50

    required_fragments = (
        "seamLurker: {",
        '"seamLurker",',
        "seamLurker: { width: 104, height: 44 }",
        'var isCeilingCrawler =',
        'type === "seamLurker"',
        'if (enemy.type === "seamLurker") {',
        'seamLurker: "SEAM LURKER"',
        "frameCount: 25",
        "columns: 5",
        "ceiling: true",
        "enemy.ceilingY +",
        "canvas.dataset.seamLurkerState",
        '["seamLurker", WIDTH * 7 + 430, 362,',
        'canvas.dataset.seamLurkerAnchor =',
        '"uplink-catwalk-underside-y362"',
    )
    for fragment in required_fragments:
        assert fragment in SOURCE, (
            f"Seam Lurker runtime registration is missing: {fragment}"
        )

    make_enemy = SOURCE.split(
        "function makeEnemy(type, x, floorOrAirY, minX, maxX, speed)",
        1,
    )[1].split("function gloamRollerAnimationState", 1)[0]
    flyer_block = make_enemy.split("var isFlyer =", 1)[1].split(
        "return {",
        1,
    )[0]
    assert 'type === "seamLurker"' not in flyer_block
    print("SUPER FRGMNTS Seam Lurker enemy type: PASS")
    print("- 25-frame source crawl validates without alpha edge contact")
    print("- vertical normalization produces a stable ceiling anchor")
    print("- horizontal ceiling-patrol runtime type is registered")
    print("- Uplink plate 7 population is rooted to the catwalk underside")
    print("- drop attack remains disabled; the patrol takes two rifle hits")
    print("- 640x320 shipping atlas stays below portability limits")


if __name__ == "__main__":
    main()
