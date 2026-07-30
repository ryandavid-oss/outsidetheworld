#!/usr/bin/env python3
"""Build the locked/open Uplink lower-room environment plates."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
RAW = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Uplink-Gate"
    / "Environment"
    / "Raw"
)
RUNTIME = ROOT / "Images" / "Game" / "Super-Frgmnts"
LOCKED_SOURCE = RAW / "uplink-room7-lower-locked-source-v3.png"
OPEN_SOURCE = RAW / "uplink-room7-lower-open-source-v2.png"
LOCKED_RUNTIME = (
    RUNTIME / "foundry-uplink-room7-lower-locked-runtime-v1.png"
)
OPEN_RUNTIME = (
    RUNTIME / "foundry-uplink-room7-lower-open-runtime-v1.png"
)
PLATE_SIZE = (1672, 941)
OPENING_MASK = [
    (1480, 370),
    (1536, 395),
    (1536, 620),
    (1510, 654),
    (1471, 654),
    (1447, 618),
    (1447, 426),
]


def load_plate(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if image.size != PLATE_SIZE:
        image = image.resize(
            PLATE_SIZE,
            Image.Resampling.NEAREST,
        )
    return image


def main() -> None:
    locked = load_plate(LOCKED_SOURCE)
    open_source = load_plate(OPEN_SOURCE)

    opening_mask = Image.new("L", PLATE_SIZE, 0)
    ImageDraw.Draw(opening_mask).polygon(OPENING_MASK, fill=255)
    open_plate = Image.composite(open_source, locked, opening_mask)

    RUNTIME.mkdir(parents=True, exist_ok=True)
    locked.save(LOCKED_RUNTIME, optimize=True)
    open_plate.save(OPEN_RUNTIME, optimize=True)
    print(
        "Wrote "
        f"{LOCKED_RUNTIME.relative_to(ROOT)} and "
        f"{OPEN_RUNTIME.relative_to(ROOT)} "
        f"({PLATE_SIZE[0]}x{PLATE_SIZE[1]})"
    )


if __name__ == "__main__":
    main()
