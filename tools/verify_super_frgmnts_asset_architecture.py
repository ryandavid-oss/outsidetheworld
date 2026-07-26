#!/usr/bin/env python3
"""Verify scene-aware loading and mobile-safe SUPER FRGMNTS runtime art."""

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
ASSET_ROOT = ROOT / "Images" / "Game" / "Super-Frgmnts"

RUNTIME_PROPS = {
    "atmospheric-stabilizer-dormant-runtime-v2.png": (420, 735),
    "atmospheric-stabilizer-active-runtime-v2.png": (420, 735),
    "foundry-ventilation-fan-housing-runtime-v2.png": (326, 326),
    "foundry-ventilation-fan-rotor-runtime-v2.png": (326, 326),
}


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    required_contracts = (
        "var assetDefinitions = {",
        "var overworldAssetKeys = [",
        "var foundryCoreAssetKeys = [",
        "var foundryLowerAssetKeys = [",
        "function requestAsset(key, priority)",
        "function releaseInactiveSceneAssets(scene)",
        "function maintainFoundryZoneAssets(force)",
        "function loadAndConfigureEpisodeScene(scene, historyMode)",
        'loadAndConfigureEpisodeScene("overworld")',
        'loadAndConfigureEpisodeScene("foundry")',
        'releaseInactiveSceneAssets("title")',
        'preload="none" aria-hidden="true"></audio>',
        "super-frgmnts-title-coreworks-mobile-v1.png",
    )
    missing = [
        contract for contract in required_contracts
        if contract not in source
    ]
    if missing:
        raise SystemExit(
            "Missing asset-loading contracts: " + ", ".join(missing)
        )

    forbidden_contracts = (
        "assets.overworld0 = loadImage(",
        "assets.foundryExpanded = loadImage(",
        '<link rel="preload" href="/Images/Game/Super-Frgmnts/'
        'super-frgmnts-title-coreworks-v1.png"',
    )
    present = [
        contract for contract in forbidden_contracts
        if contract in source
    ]
    if present:
        raise SystemExit(
            "Eager-loading regressions found: " + ", ".join(present)
        )

    for filename, expected_size in RUNTIME_PROPS.items():
        path = ASSET_ROOT / filename
        if not path.exists():
            raise SystemExit(f"Missing runtime prop: {path}")
        with Image.open(path) as image:
            if image.size != expected_size:
                raise SystemExit(
                    f"Unexpected {filename} size: {image.size}"
                )
            if image.mode != "RGBA":
                raise SystemExit(
                    f"Unexpected {filename} mode: {image.mode}"
                )

    wasp_path = ASSET_ROOT / "enemy-flying-wasp-flight-sheet-v1.png"
    with Image.open(wasp_path) as wasp:
        if wasp.size != (672, 516):
            raise SystemExit(f"Unexpected flying-wasp size: {wasp.size}")
        if wasp.mode != "RGBA":
            raise SystemExit(f"Unexpected flying-wasp mode: {wasp.mode}")
        if wasp.getchannel("A").getextrema() != (0, 255):
            raise SystemExit("Flying-wasp runtime lost transparency")

    manifest_path = (
        ROOT
        / "Design"
        / "Super-Frgmnts"
        / "Foundry"
        / "Enemies"
        / "Flying-Wasp"
        / "flying-wasp-runtime-v1.json"
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["productionPopulation"] is not False:
        raise SystemExit("Flying wasp must remain outside production balance")
    if manifest["runtime"]["frameCount"] != 36:
        raise SystemExit("Flying-wasp manifest must retain all 36 frames")

    print("SUPER FRGMNTS asset architecture: PASS")
    print("- title, overworld, and Foundry load as explicit scene groups")
    print("- inactive scene images are released")
    print("- Foundry lower plates stream by nearby room")
    print("- large machinery uses pixel-faithful runtime dimensions")
    print("- flying wasp is normalized for review but not production-spawned")


if __name__ == "__main__":
    main()
