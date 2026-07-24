#!/usr/bin/env python3
"""Normalize an ImageGen expansion draft and restore protected source pixels."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops


WIDTH = 1672
PLATE_HEIGHT = 941
COMPOSITE_HEIGHT = 1882
PROTECT_TOP = 1121
BLEND_HEIGHT = PROTECT_TOP - PLATE_HEIGHT


def smoothstep(value: float) -> float:
    return value * value * (3 - 2 * value)


def build_blend_mask() -> Image.Image:
    mask = Image.new("L", (WIDTH, BLEND_HEIGHT), 0)
    pixels = mask.load()
    denominator = max(1, BLEND_HEIGHT - 1)
    for y in range(BLEND_HEIGHT):
        amount = round(255 * smoothstep(y / denominator))
        for x in range(WIDTH):
            pixels[x, y] = amount
    return mask


def compose(generated_path: Path, source_path: Path, output_path: Path) -> None:
    generated = Image.open(generated_path).convert("RGB")
    source = Image.open(source_path).convert("RGB")
    if source.size != (WIDTH, PLATE_HEIGHT):
        raise ValueError(f"Source plate has unexpected dimensions {source.size}")

    normalized = generated.resize((WIDTH, COMPOSITE_HEIGHT), Image.Resampling.NEAREST)
    result = normalized.copy()

    generated_blend = normalized.crop((0, PLATE_HEIGHT, WIDTH, PROTECT_TOP))
    source_blend = source.crop((0, 0, WIDTH, BLEND_HEIGHT))
    blended = Image.composite(source_blend, generated_blend, build_blend_mask())
    result.paste(blended, (0, PLATE_HEIGHT))

    protected_source = source.crop((0, BLEND_HEIGHT, WIDTH, PLATE_HEIGHT))
    result.paste(protected_source, (0, PROTECT_TOP))

    protected_result = result.crop((0, PROTECT_TOP, WIDTH, COMPOSITE_HEIGHT))
    if ImageChops.difference(protected_result, protected_source).getbbox() is not None:
        raise ValueError("Protected source pixels changed during composition")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path, optimize=True)
    print(f"wrote {output_path}")
    print(f"  generated input  {generated.size[0]}×{generated.size[1]}")
    print(f"  normalized       {WIDTH}×{COMPOSITE_HEIGHT}")
    print(f"  blended          y={PLATE_HEIGHT}–{PROTECT_TOP - 1}")
    print(f"  exact source     y={PROTECT_TOP}–{COMPOSITE_HEIGHT - 1}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("generated", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    compose(args.generated, args.source, args.output)


if __name__ == "__main__":
    main()
