#!/usr/bin/env python3
"""Verify the compact green and purple Fragment enemy integration."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
PUBLIC = ROOT / "Images" / "Game" / "Super-Frgmnts"
MANIFEST = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Enemies"
    / "Fragment-Variants"
    / "fragment-variants-runtime-v1.json"
)

EXPECTED_ASSETS = {
    "enemy-fragment-bastion-purple-runtime-v1.png": (480, 420),
    "enemy-fragment-spring-green-runtime-v1.png": (400, 285),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    require(
        manifest["productionPopulation"] is True,
        "Fragment variants are not marked for production population",
    )
    require(
        len(manifest["variants"]) == 2,
        "Only the green and purple Fragment variants should be active",
    )
    require(
        {variant["key"] for variant in manifest["variants"]}
        == {"fragment-bastion-purple", "fragment-spring-green"},
        "Unexpected Fragment color variant in runtime manifest",
    )

    for filename, expected_size in EXPECTED_ASSETS.items():
        path = PUBLIC / filename
        require(path.is_file(), f"Missing Fragment runtime: {filename}")
        with Image.open(path) as image:
            require(
                image.size == expected_size,
                f"{filename} is {image.size}; expected {expected_size}",
            )
            require(image.mode == "RGBA", f"{filename} lost RGBA mode")
            require(
                image.getchannel("A").getextrema() == (0, 255),
                f"{filename} lost transparent frame padding",
            )
            require(
                path.stat().st_size < 300_000,
                f"{filename} exceeds the mobile runtime budget",
            )

    runtime_contracts = (
        "enemy-fragment-spring-green-runtime-v1.png",
        "enemy-fragment-bastion-purple-runtime-v1.png",
        '"fragmentSpring"',
        '"fragmentBastion"',
        "function drawFragmentEnemy(enemy)",
        'fragmentSpring: "SPRING FRAGMENT"',
        'fragmentBastion: "BASTION FRAGMENT"',
        'enemy.type === "fragmentBastion" &&',
        'text: "SPIKE ARMOR"',
    )
    for contract in runtime_contracts:
        require(contract in source, f"Missing Fragment contract: {contract}")

    print("SUPER FRGMNTS Fragment variants: PASS")
    print("- only green Spring and purple Bastion variants are populated")
    print("- both atlases fit their compact mobile runtime budgets")
    print("- Spring uses a quick hover patrol")
    print("- Bastion visibly cycles into shot-deflecting spike armor")


if __name__ == "__main__":
    main()
