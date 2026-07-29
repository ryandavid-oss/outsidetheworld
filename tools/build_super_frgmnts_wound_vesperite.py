#!/usr/bin/env python3
"""Build the Wound-touched Vesperite runtime and review assets."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "Design/Super-Frgmnts/Foundry/Boss-Room/Wound-Vesperite/Raw"
    / "wound-touched-vesperite-alpha-source-v1.png"
)
RUNTIME = (
    ROOT
    / "Images/Game/Super-Frgmnts"
    / "wound-touched-vesperite-runtime-v1.png"
)
REVIEW = (
    ROOT
    / "Design/Super-Frgmnts/Foundry/Boss-Room/Wound-Vesperite/Reviews"
    / "wound-touched-vesperite-runtime-review-v1.png"
)

RUNTIME_SIZE = (128, 144)
CONTENT_SIZE = (96, 118)


def alpha_bounds(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    bounds = alpha.point(lambda value: 255 if value >= 8 else 0).getbbox()
    if bounds is None:
        raise RuntimeError("Source image has no visible alpha content")
    return bounds


def checkerboard(size: tuple[int, int], cell: int = 16) -> Image.Image:
    review = Image.new("RGBA", size, (12, 15, 25, 255))
    draw = ImageDraw.Draw(review)
    colors = ((18, 24, 38, 255), (35, 42, 58, 255))
    for y in range(0, size[1], cell):
        for x in range(0, size[0], cell):
            draw.rectangle(
                (x, y, x + cell - 1, y + cell - 1),
                fill=colors[(x // cell + y // cell) % 2],
            )
    return review


def main() -> None:
    source = Image.open(SOURCE).convert("RGBA")
    specimen = source.crop(alpha_bounds(source))
    specimen.thumbnail(CONTENT_SIZE, Image.Resampling.NEAREST)

    runtime = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))
    destination = (
        (RUNTIME_SIZE[0] - specimen.width) // 2,
        RUNTIME_SIZE[1] - specimen.height - 8,
    )
    runtime.alpha_composite(specimen, destination)

    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(RUNTIME, optimize=True)

    review = checkerboard((512, 576), 32)
    review.alpha_composite(runtime.resize(review.size, Image.Resampling.NEAREST))
    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    review.convert("RGB").save(REVIEW, optimize=True)

    print(f"Wrote {RUNTIME.relative_to(ROOT)} ({runtime.width}x{runtime.height})")
    print(f"Wrote {REVIEW.relative_to(ROOT)} ({review.width}x{review.height})")


if __name__ == "__main__":
    main()
