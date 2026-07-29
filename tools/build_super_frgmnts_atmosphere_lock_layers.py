#!/usr/bin/env python3
"""Build fixed atmosphere-lock housing and retractable membrane runtime layers."""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Atmosphere-Lock"
    / "Raw"
)
RUNTIME = ROOT / "Images" / "Game" / "Super-Frgmnts"
CANVAS_SIZE = (80, 206)


def cropped_alpha_source(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    bounds = image.getchannel("A").getbbox()
    if not bounds:
        raise ValueError(f"{path} has no visible pixels")
    return image.crop(bounds)


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


def build_layer(
    source_name: str,
    output_name: str,
    target_size: tuple[int, int],
    paste_xy: tuple[int, int],
) -> None:
    source = cropped_alpha_source(RAW / source_name)
    resized = source.resize(target_size, Image.Resampling.NEAREST)
    canvas = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    canvas.alpha_composite(resized, paste_xy)
    output = RUNTIME / output_name
    quantize_rgba(canvas).save(output, optimize=True)
    print(f"Wrote {output.relative_to(ROOT)} ({CANVAS_SIZE[0]}x{CANVAS_SIZE[1]})")


def main() -> None:
    RUNTIME.mkdir(parents=True, exist_ok=True)
    build_layer(
        "atmosphere-lock-housing-alpha-source-v1.png",
        "foundry-atmosphere-lock-housing-runtime-v1.png",
        (54, 206),
        (26, 0),
    )
    build_layer(
        "atmosphere-lock-membrane-alpha-source-v1.png",
        "foundry-atmosphere-lock-membrane-runtime-v1.png",
        (58, 166),
        (0, 20),
    )


if __name__ == "__main__":
    main()
