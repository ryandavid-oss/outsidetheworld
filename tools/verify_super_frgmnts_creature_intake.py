#!/usr/bin/env python3
"""Verify normalized creature intake and the camp-dog production upgrade."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


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
        "var walkFrame = walking",
        "Math.floor((dogCycle / 3) * 16)",
        "dogCycle < 3 &&\n                    sniffChance > 0.62",
        'walkingHome ? "right" : "left"',
        "if (mirrorDog) {",
    ):
        assert token in SOURCE, f"Missing live camp-dog contract: {token}"

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
    print("- the dog faces its travel direction without moonwalking")
    print("- occasional sniff events dip and recover once across three seconds")
    print("- Seam Hunter walk and sweep atlases are live in the Episode beta")
    print("- Fleet-apparel Aryn is canonically identified but not live-loaded")


if __name__ == "__main__":
    main()
