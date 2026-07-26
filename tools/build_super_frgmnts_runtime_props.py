#!/usr/bin/env python3
"""Build pixel-faithful runtime sizes for large Foundry prop source art."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "Images" / "Game" / "Super-Frgmnts"

RESIZE_JOBS = (
    (
        "atmospheric-stabilizer-dormant-v1.png",
        "atmospheric-stabilizer-dormant-runtime-v2.png",
        (420, 735),
    ),
    (
        "atmospheric-stabilizer-active-v1.png",
        "atmospheric-stabilizer-active-runtime-v2.png",
        (420, 735),
    ),
    (
        "foundry-ventilation-fan-housing-v1.png",
        "foundry-ventilation-fan-housing-runtime-v2.png",
        (326, 326),
    ),
    (
        "foundry-ventilation-fan-rotor-v1.png",
        "foundry-ventilation-fan-rotor-runtime-v2.png",
        (326, 326),
    ),
)


def main() -> None:
    for source_name, output_name, size in RESIZE_JOBS:
        source_path = ASSET_DIR / source_name
        output_path = ASSET_DIR / output_name
        with Image.open(source_path) as source:
            runtime = source.convert("RGBA").resize(size, Image.Resampling.NEAREST)
            runtime.save(output_path, optimize=True)
        print(f"{output_path.relative_to(ROOT)} {size[0]}x{size[1]}")


if __name__ == "__main__":
    main()
