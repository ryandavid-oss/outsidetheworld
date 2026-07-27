#!/usr/bin/env python3
"""Verify the complete Episode 01 enemy catalog and behavior contracts."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")
RUNTIME_ASSETS = (
    "enemy-core-leech-hover-sheet-v1.png",
    "enemy-vesper-flare-hover-sheet-v1.png",
    "enemy-pale-watcher-stalk-sheet-v1.png",
)
CATALOG_TYPES = (
    "crawler",
    "walker",
    "flyer",
    "squircle",
    "mite",
    "patroller",
    "wasp",
    "gaunt",
    "fragmentSpring",
    "fragmentBastion",
    "coreLeech",
    "vesperFlare",
    "paleWatcher",
)


def main() -> None:
    for filename in RUNTIME_ASSETS:
        path = ROOT / "Images/Game/Super-Frgmnts" / filename
        assert path.exists(), f"Missing catalog runtime asset: {path}"
        image = Image.open(path)
        assert image.size == (672, 672), (
            f"{filename}: expected 672x672, got {image.size}"
        )
        assert image.mode == "RGBA", f"{filename}: expected RGBA"

    for enemy_type in CATALOG_TYPES:
        assert f'"{enemy_type}"' in SOURCE, (
            f"Missing enemy runtime type: {enemy_type}"
        )

    episode_assets = SOURCE.split(
        "var episodeBetaAssetKeys = [",
        1,
    )[1].split("];", 1)[0]
    for key in ("coreLeech", "vesperFlare", "paleWatcher"):
        assert f'"{key}"' in episode_assets, (
            f"Episode beta does not preload {key}"
        )

    make_enemy = SOURCE.split(
        "function makeEnemy(type, x, floorOrAirY, minX, maxX, speed)",
        1,
    )[1].split("function findSurfaceCrawlerTrialPlatform", 1)[0]
    flyer_block = make_enemy.split("var isFlyer =", 1)[1].split(
        "return {",
        1,
    )[0]
    assert 'type === "mite"' not in flyer_block, (
        "Vesper Mite is still classified as a flyer"
    )
    assert 'type === "coreLeech"' in flyer_block
    assert 'type === "vesperFlare"' in flyer_block

    mite_update = SOURCE.split(
        'if (enemy.type === "mite") {',
        1,
    )[1].split('if (enemy.type === "fragmentSpring")', 1)[0]
    assert "enemy.floorY - enemy.height" in mite_update
    assert "Math.sin(elapsed * 2.35" not in mite_update
    assert "mite.hoverFloorY" not in SOURCE

    placements = SOURCE.split(
        "function makeEpisodeBetaEnemies()",
        1,
    )[1].split("function surfaceEdgePoint", 1)[0]
    for enemy_type in ("coreLeech", "vesperFlare", "paleWatcher"):
        assert f'"{enemy_type}"' in placements, (
            f"Episode beta does not populate {enemy_type}"
        )

    print("SUPER FRGMNTS complete enemy catalog: PASS")
    print("- 13 cataloged enemy families are represented")
    print("- Vesper Mite uses ground-patrol physics")
    print("- Core Leech, Vesper Flare, and Pale Watcher are production-loaded")
    print("- all three new 36-frame atlases are normalized for mobile")


if __name__ == "__main__":
    main()
