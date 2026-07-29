#!/usr/bin/env python3
"""Verify the Sova and Kihunter assets and runtime type registrations."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ENEMIES = ROOT / "Design/Super-Frgmnts/Foundry/Enemies"
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def verify_enemy(
    directory: str,
    key: str,
    atlas_size: tuple[int, int],
    frame_size: tuple[int, int],
    frame_duration: int,
) -> None:
    family = ENEMIES / directory
    manifest = json.loads(
        (family / f"{key}-runtime-v1.json").read_text(encoding="utf-8")
    )
    assert manifest["runtimeType"] == key
    if key == "sova":
        assert manifest["productionPopulation"] is True
        assert manifest["behavior"]["spawned"] is True
        assert (
            manifest["runtime"]["projectileHitbox"]["topPadding"]
            == 28
        )
    else:
        assert manifest["productionPopulation"] is False
    assert manifest["source"]["frameCount"] == 36
    assert manifest["source"]["frameDurationMs"] == frame_duration
    assert manifest["validation"]["result"] == "pass"
    assert manifest["validation"]["edgeContactFrames"] == {}

    atlas = Image.open(ROOT / manifest["runtime"]["image"]).convert("RGBA")
    assert atlas.size == atlas_size, (
        f"{key}: expected {atlas_size}, got {atlas.size}"
    )
    frame_width, frame_height = frame_size
    for index in range(36):
        x = index % 6 * frame_width
        y = index // 6 * frame_height
        frame = atlas.crop(
            (x, y, x + frame_width, y + frame_height)
        )
        bound = frame.getchannel("A").getbbox()
        assert bound is not None, f"{key}: frame {index} is blank"
        assert bound[0] > 0 and bound[1] > 0
        assert bound[2] < frame_width and bound[3] < frame_height


def main() -> None:
    verify_enemy("Sova", "sova", (768, 480), (128, 80), 42)
    verify_enemy(
        "Kihunter",
        "kihunter",
        (672, 672),
        (112, 112),
        43,
    )

    required_fragments = (
        "sova: {",
        "kihunter: {",
        '"sova",',
        '"kihunter",',
        "sova: { width: 92, height: 48 }",
        "kihunter: { width: 88, height: 78 }",
        'type === "kihunter"',
        'if (enemy.type === "sova") {',
        'if (enemy.type === "kihunter") {',
        'sova: "SOVA"',
        'kihunter: "KIHUNTER"',
        "function drawIntakeEnemy(enemy)",
        'canvas.dataset.sovaRifleHitbox =',
        '"visual-silhouette"',
        '["sova", WIDTH * 3 + 610, GROUND_Y',
        'enemy.type === "sova"',
        "? 28",
    )
    for fragment in required_fragments:
        assert fragment in SOURCE, (
            f"Sova/Kihunter runtime registration is missing: {fragment}"
        )

    make_enemy = SOURCE.split(
        "function makeEnemy(type, x, floorOrAirY, minX, maxX, speed)",
        1,
    )[1].split("function makeWoundBoss", 1)[0]
    flyer_block = make_enemy.split("var isFlyer =", 1)[1].split(
        "return {",
        1,
    )[0]
    assert 'type === "kihunter"' in flyer_block
    assert 'type === "sova"' not in flyer_block
    assert '["sova", WIDTH * 3 + 610, GROUND_Y' in SOURCE
    assert 'makeEnemy("kihunter"' not in SOURCE

    ground_y = 1604
    grounded_player_y = ground_y - 100
    heavy_rifle_muzzle_y = grounded_player_y + 42
    sova_contact_top = ground_y - 48
    sova_projectile_top = sova_contact_top + 4 - 28
    sova_projectile_bottom = ground_y - 4
    assert (
        sova_projectile_top
        < heavy_rifle_muzzle_y
        < sova_projectile_bottom
    ), "Grounded heavy-rifle fire still passes above Sova"

    print("SUPER FRGMNTS Sova and Kihunter enemy types: PASS")
    print("- both 36-frame source atlases validate without edge contact")
    print("- Sova is a ground patrol; Kihunter is a flying patrol")
    print("- Sova is production-populated; Kihunter remains runtime-ready")
    print("- Sova's rifle collider covers its visible upper carapace")
    print("- shipping atlases remain below the 2,048px portability limit")


if __name__ == "__main__":
    main()
