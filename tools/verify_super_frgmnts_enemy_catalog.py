#!/usr/bin/env python3
"""Verify the active Episode 01 enemy population and retired placeholders."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")
RUNTIME_ASSETS = {
    "enemy-core-leech-hover-sheet-v1.png": (672, 672),
    "enemy-pale-watcher-stalk-sheet-v1.png": (672, 672),
    "enemy-skree-walk-sheet-v1.png": (800, 720),
    "enemy-sova-crawl-sheet-v1.png": (768, 480),
    "enemy-seam-lurker-crawl-sheet-v1.png": (640, 320),
    "enemy-kihunter-flight-sheet-v1.png": (672, 672),
}
PLACED_TYPES = (
    "patroller",
    "coreLeech",
    "kihunter",
    "sova",
    "wasp",
    "gaunt",
    "skree",
    "seamLurker",
    "paleWatcher",
)
ACTIVE_ASSET_KEYS = (
    "squircle",
    "patroller",
    "patrollerDeath",
    "coreLeech",
    "kihunter",
    "sova",
    "wasp",
    "gauntWalk",
    "gauntAttack",
    "skree",
    "seamLurker",
    "paleWatcher",
)
RETIRED_TYPES = ("crawler", "walker", "flyer")


def main() -> None:
    for filename, expected_size in RUNTIME_ASSETS.items():
        path = ROOT / "Images/Game/Super-Frgmnts" / filename
        assert path.exists(), f"Missing active runtime asset: {path}"
        with Image.open(path) as image:
            assert image.size == expected_size, (
                f"{filename}: expected {expected_size}, got {image.size}"
            )
            assert image.mode == "RGBA", f"{filename}: expected RGBA"

    placements = SOURCE.split(
        "function makeEpisodeBetaEnemies()",
        1,
    )[1].split("function surfaceEdgePoint", 1)[0]
    assert "makeSurfaceCrawlerTrial();" in placements
    for enemy_type in PLACED_TYPES:
        assert f'"{enemy_type}"' in placements, (
            f"Episode beta does not populate {enemy_type}"
        )

    episode_assets = SOURCE.split(
        "var episodeBetaAssetKeys = [",
        1,
    )[1].split("];", 1)[0]
    for key in ACTIVE_ASSET_KEYS:
        assert f'"{key}"' in episode_assets, (
            f"Episode beta does not preload {key}"
        )
    for key in RETIRED_TYPES:
        assert f'"{key}"' not in episode_assets, (
            f"Retired placeholder still preloads: {key}"
        )

    assert 'canvas.dataset.betaSentinelCount = "7";' in placements
    assert (
        '"spore-wisp,clacker-beetle,ridge-skitter"' in placements
    )

    catalog_draw = SOURCE.split(
        "function drawCatalogEnemy(enemy)",
        1,
    )[1].split("function drawChitinSentinel", 1)[0]
    assert "drawSize: 140" in catalog_draw
    assert 'enemy.type !== "coreLeech"' in catalog_draw
    assert 'enemy.type === "coreLeech"\n                        ? 0' in catalog_draw
    assert 'enemy.type === "paleWatcher"\n                        ? enemy.vx > 0' in catalog_draw

    print("SUPER FRGMNTS active enemy population: PASS")
    print("- ten active families are populated and preloaded")
    print("- seven Chitin Sentinels establish the recurring combat grammar")
    print("- Ridge Skitter, Clacker Beetle, and Spore Wisp are retired")
    print("- Core Leech is 15% larger without an aura or sprite glow")
    print("- Pale Watcher orientation follows its authored source direction")


if __name__ == "__main__":
    main()
