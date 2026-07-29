#!/usr/bin/env python3
"""Build the reusable background patch that removes the false y=600 bridge."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Traversal-Cleanup"
    / "Raw"
    / "false-bridge-removal-imagegen-source-v1.png"
)
OUTPUT = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "foundry-false-bridge-removal-runtime-v1.png"
)
RUNTIME_SIZE = (630, 180)
BAYER_4X4 = (
    (0, 8, 2, 10),
    (12, 4, 14, 6),
    (3, 11, 1, 9),
    (15, 7, 13, 5),
)


def edge_coverage(position: int, start: int, solid_start: int, solid_end: int, end: int) -> float:
    if position < start or position > end:
        return 0.0
    if position < solid_start:
        return (position - start) / max(1, solid_start - start)
    if position > solid_end:
        return (end - position) / max(1, end - solid_end)
    return 1.0


def quantize_rgba(image: Image.Image, colors: int = 64) -> Image.Image:
    alpha = image.getchannel("A")
    rgb = image.convert("RGB").quantize(
        colors=colors,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )
    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


def main() -> None:
    generated = Image.open(SOURCE).convert("RGB")
    resized = generated.resize(RUNTIME_SIZE, Image.Resampling.NEAREST)
    patch = resized.convert("RGBA")
    alpha = Image.new("L", RUNTIME_SIZE, 0)
    pixels = alpha.load()

    for y in range(RUNTIME_SIZE[1]):
        vertical = edge_coverage(y, 0, 0, 144, 179)
        for x in range(RUNTIME_SIZE[0]):
            horizontal = edge_coverage(x, 74, 96, 534, 556)
            coverage = min(horizontal, vertical)
            threshold = (BAYER_4X4[y % 4][x % 4] + 0.5) / 16
            pixels[x, y] = 255 if coverage >= threshold else 0

    patch.putalpha(alpha)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    quantize_rgba(patch).save(OUTPUT, optimize=True)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({RUNTIME_SIZE[0]}x{RUNTIME_SIZE[1]})")


if __name__ == "__main__":
    main()
