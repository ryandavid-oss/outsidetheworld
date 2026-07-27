#!/usr/bin/env python3
"""Build a review-only split-body rifle-running prototype for Aryn."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "Images" / "Game" / "Super-Frgmnts"
REVIEWS = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Ludo"
    / "Reviews"
)
RUN_STRIP = PUBLIC / "aryn-run-ludo-runtime-v2.png"
RIFLE_STRIP = PUBLIC / "aryn-rifle-fire-ludo-runtime-v1.png"
PROTOTYPE_STRIP = REVIEWS / "aryn-rifle-run-composite-prototype-v2.png"
PROTOTYPE_GIF = REVIEWS / "aryn-rifle-run-composite-prototype-v2.gif"
PROTOTYPE_REVIEW = REVIEWS / "aryn-rifle-run-composite-review-v2.png"

FRAME_SIZE = 112
RUN_FRAME_COUNT = 8
RIFLE_AIM_FRAME = 0
# The rifle pose owns the helmet, chest, arms, and weapon only. The approved
# run owns Aryn's waist, pelvis, and legs so her stride can visibly originate
# at the hip instead of beneath a static armor block.
UPPER_BODY_END = 53
RUN_WAIST_START = 48
FULL_LOWER_BODY_START = 60
WAIST_HALF_WIDTH = 15
REVIEW_BACKGROUND = (3, 6, 18, 255)


def strip_frames(path: Path, frame_count: int) -> list[Image.Image]:
    strip = Image.open(path).convert("RGBA")
    expected_size = (FRAME_SIZE * frame_count, FRAME_SIZE)
    if strip.size != expected_size:
        raise ValueError(f"{path.name}: expected {expected_size}, got {strip.size}")
    return [
        strip.crop(
            (
                index * FRAME_SIZE,
                0,
                (index + 1) * FRAME_SIZE,
                FRAME_SIZE,
            )
        )
        for index in range(frame_count)
    ]


def alpha_centroid(
    frame: Image.Image,
    left: int,
    top: int,
    right: int,
    bottom: int,
) -> tuple[float, float]:
    alpha = frame.getchannel("A")
    weighted_x = 0
    weighted_y = 0
    total = 0
    for y in range(top, bottom):
        for x in range(left, right):
            value = alpha.getpixel((x, y))
            weighted_x += x * value
            weighted_y += y * value
            total += value
    if not total:
        return FRAME_SIZE / 2, (top + bottom) / 2
    return weighted_x / total, weighted_y / total


def shifted(frame: Image.Image, offset_x: int, offset_y: int = 0) -> Image.Image:
    result = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    result.alpha_composite(frame, (offset_x, offset_y))
    return result


def upper_body_layer(frame: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    layer.alpha_composite(
        frame.crop((0, 0, FRAME_SIZE, UPPER_BODY_END)),
        (0, 0),
    )
    return layer


def moving_waist_and_legs_layer(
    frame: Image.Image,
    pelvis_center_x: float,
) -> Image.Image:
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    pixels = frame.load()
    output = layer.load()
    for y in range(RUN_WAIST_START, FRAME_SIZE):
        for x in range(FRAME_SIZE):
            keep = y >= FULL_LOWER_BODY_START
            if not keep:
                keep = abs(x - pelvis_center_x) <= WAIST_HALF_WIDTH
            if keep:
                output[x, y] = pixels[x, y]
    return layer


def composite_frames() -> tuple[list[Image.Image], Image.Image]:
    run_frames = strip_frames(RUN_STRIP, RUN_FRAME_COUNT)
    rifle_frame = strip_frames(RIFLE_STRIP, 12)[RIFLE_AIM_FRAME]
    rifle_upper = upper_body_layer(rifle_frame)
    rifle_center_x, rifle_center_y = alpha_centroid(
        rifle_frame,
        40,
        48,
        78,
        68,
    )

    results: list[Image.Image] = []
    for run_frame in run_frames:
        run_center_x, run_center_y = alpha_centroid(
            run_frame,
            40,
            48,
            78,
            68,
        )
        upper_offset_x = round(run_center_x - rifle_center_x)
        upper_offset_y = max(
            -2,
            min(2, round(run_center_y - rifle_center_y)),
        )
        result = moving_waist_and_legs_layer(run_frame, run_center_x)
        result.alpha_composite(
            shifted(rifle_upper, upper_offset_x, upper_offset_y)
        )
        results.append(result)
    return results, rifle_frame


def build_strip(frames: list[Image.Image]) -> Image.Image:
    strip = Image.new(
        "RGBA",
        (FRAME_SIZE * len(frames), FRAME_SIZE),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (index * FRAME_SIZE, 0))
    return strip


def build_review(
    composite: list[Image.Image],
    rifle_frame: Image.Image,
) -> Image.Image:
    run = strip_frames(RUN_STRIP, RUN_FRAME_COUNT)
    width = FRAME_SIZE * RUN_FRAME_COUNT
    review = Image.new("RGBA", (width, 390), REVIEW_BACKGROUND)
    draw = ImageDraw.Draw(review)
    rows = (
        ("APPROVED RUN", run, 24),
        ("RIFLE AIM REFERENCE", [rifle_frame] * RUN_FRAME_COUNT, 151),
        ("SPLIT-BODY PROTOTYPE", composite, 278),
    )
    for title, frames, y in rows:
        draw.text((8, y - 17), title, fill=(235, 240, 255, 255))
        for index, frame in enumerate(frames):
            review.alpha_composite(frame, (index * FRAME_SIZE, y))
    return review.resize(
        (width * 2, review.height * 2),
        Image.Resampling.NEAREST,
    )


def build_gif(frames: list[Image.Image]) -> None:
    reviews: list[Image.Image] = []
    for frame in frames:
        review = Image.new("RGBA", frame.size, REVIEW_BACKGROUND)
        review.alpha_composite(frame)
        reviews.append(
            review.resize((336, 336), Image.Resampling.NEAREST).convert("RGB")
        )
    reviews[0].save(
        PROTOTYPE_GIF,
        save_all=True,
        append_images=reviews[1:],
        duration=round(1000 / 12),
        loop=0,
        disposal=2,
        optimize=False,
    )


def main() -> None:
    REVIEWS.mkdir(parents=True, exist_ok=True)
    composite, rifle_frame = composite_frames()
    build_strip(composite).save(PROTOTYPE_STRIP, optimize=True)
    build_review(composite, rifle_frame).save(PROTOTYPE_REVIEW, optimize=True)
    build_gif(composite)
    for output in (PROTOTYPE_STRIP, PROTOTYPE_REVIEW, PROTOTYPE_GIF):
        print(f"Wrote {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
