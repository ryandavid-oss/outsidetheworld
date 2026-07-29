#!/usr/bin/env python3
"""Verify normalized creature intake and the camp-dog production upgrade."""

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")
DOG_MANIFEST = json.loads(
    (
        ROOT
        / "Design/Super-Frgmnts/Overworld/Phase-3/Outpost/Dog-Ludo"
        / "camp-dog-runtime-v3.json"
    ).read_text(encoding="utf-8")
)


def require_image(name: str, size: tuple[int, int]) -> None:
    path = PUBLIC / name
    assert path.exists(), f"Missing {path.relative_to(ROOT)}"
    with Image.open(path) as image:
        assert image.size == size, (
            f"{name}: expected {size}, received {image.size}"
        )
        assert image.mode == "RGBA", f"{name}: expected RGBA, received {image.mode}"


def main() -> None:
    require_image("veyra-camp-dog-walk-sheet-v3.png", (600, 480))
    require_image("veyra-camp-dog-sniff-sheet-v3.png", (400, 320))
    require_image("enemy-tall-gaunt-alien-walk-sheet-v1.png", (768, 768))
    require_image("enemy-tall-gaunt-alien-attack-sheet-v1.png", (800, 640))
    require_image("aryn-fleet-apparel-walk-sheet-v1.png", (340, 580))

    for token in (
        "veyra-camp-dog-walk-sheet-v3.png",
        "veyra-camp-dog-sniff-sheet-v3.png",
        'var DOG_NAME = "Jane";',
        "var DOG_DRAW_WIDTH = 85;",
        "var DOG_DRAW_HEIGHT = 68;",
        "function updateCampDog(delta)",
        'campDog.behavior === "wander"',
        'campDog.behavior === "approach"',
        'campDog.behavior === "returnHome"',
        "campDogHasGroundAhead(desiredDirection)",
        "updateCampDog(delta);",
        "var walkFrame = walking",
        "Math.floor(sniffProgress * 16)",
        'campDog.facing > 0 ? "right" : "left"',
        "if (campDog.facing > 0) {",
    ):
        assert token in SOURCE, f"Missing live camp-dog contract: {token}"

    assert DOG_MANIFEST["revision"] == "3L"
    assert DOG_MANIFEST["identity"] == "Jane"
    assert DOG_MANIFEST["solid"] is False
    assert DOG_MANIFEST["hostile"] is False
    assert DOG_MANIFEST["runtimeDrawSize"] == [85, 68]
    assert DOG_MANIFEST["physics"]["terrainCollision"] is True
    assert DOG_MANIFEST["physics"]["playerCollision"] is False
    assert {"idle", "wander", "sniff", "watch", "approach", "returnHome"} <= set(
        DOG_MANIFEST["behavior"]["states"]
    )

    for production_asset in (
        "enemy-tall-gaunt-alien-walk-sheet-v1.png",
        "enemy-tall-gaunt-alien-attack-sheet-v1.png",
    ):
        assert production_asset in SOURCE, (
            f"{production_asset} is not loaded by the Episode beta"
        )

    assert "aryn-fleet-apparel-walk-sheet-v1.png" not in SOURCE, (
        "Fleet-apparel Aryn must remain outside the armored Episode runtime"
    )

    print("SUPER FRGMNTS creature intake: PASS")
    print("- Jane is a terrain-aware, non-solid Overworld actor")
    print("- autonomous behavior can wander, sniff, watch, approach, and return")
    print("- 85 x 68 rendering keeps Jane subordinate to Dras's human scale")
    print("- Seam Hunter walk and sweep atlases are live in the Episode beta")
    print("- Fleet-apparel Aryn is canonically identified but not live-loaded")


if __name__ == "__main__":
    main()
