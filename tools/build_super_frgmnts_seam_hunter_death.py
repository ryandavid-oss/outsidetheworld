#!/usr/bin/env python3
"""Build the runtime-safe Seam Hunter death sheet and review artifacts."""

import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
    / "Seam-Hunter-Death"
)
SOURCE = ASSET_DIR / "Raw" / "seam-hunter-death-ludo-source-v1.png"
SOURCE_METADATA = (
    ASSET_DIR / "Raw" / "seam-hunter-death-ludo-source-v1.json"
)
RUNTIME = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-seam-hunter-death-sheet-v1.png"
)
SHEET_REVIEW = (
    ASSET_DIR
    / "Reviews"
    / "seam-hunter-death-sheet-review-v1.png"
)
GIF_REVIEW = (
    ASSET_DIR
    / "Reviews"
    / "seam-hunter-death-preview-v1.gif"
)

SOURCE_COLUMNS = 5
SOURCE_ROWS = 5
FRAME_COUNT = 25
SOURCE_FRAME_WIDTH = 560
SOURCE_FRAME_HEIGHT = 446
RUNTIME_FRAME_WIDTH = 280
RUNTIME_FRAME_HEIGHT = 223
FRAME_DURATION_MS = 107


def load_and_validate() -> tuple[Image.Image, list[Image.Image]]:
    source = Image.open(SOURCE).convert("RGBA")
    expected_source_size = (
        SOURCE_COLUMNS * SOURCE_FRAME_WIDTH,
        SOURCE_ROWS * SOURCE_FRAME_HEIGHT,
    )
    if source.size != expected_source_size:
        raise ValueError(
            f"source is {source.size}, expected {expected_source_size}"
        )

    metadata = json.loads(SOURCE_METADATA.read_text(encoding="utf-8"))
    frames: list[Image.Image] = []
    for index in range(FRAME_COUNT):
        key = f"frame_{index:03d}"
        record = metadata["frames"].get(key)
        if not record:
            raise ValueError(f"metadata is missing {key}")
        source_frame = record["frame"]
        expected_x = index % SOURCE_COLUMNS * SOURCE_FRAME_WIDTH
        expected_y = index // SOURCE_COLUMNS * SOURCE_FRAME_HEIGHT
        if (
            source_frame["x"] != expected_x
            or source_frame["y"] != expected_y
            or source_frame["w"] != SOURCE_FRAME_WIDTH
            or source_frame["h"] != SOURCE_FRAME_HEIGHT
        ):
            raise ValueError(f"{key} has an unexpected source rectangle")
        if record["duration"] != FRAME_DURATION_MS:
            raise ValueError(
                f"{key} duration is {record['duration']}, "
                f"expected {FRAME_DURATION_MS}"
            )
        frame = source.crop(
            (
                expected_x,
                expected_y,
                expected_x + SOURCE_FRAME_WIDTH,
                expected_y + SOURCE_FRAME_HEIGHT,
            )
        )
        frame = frame.resize(
            (RUNTIME_FRAME_WIDTH, RUNTIME_FRAME_HEIGHT),
            Image.Resampling.NEAREST,
        )
        if not frame.getchannel("A").getbbox():
            raise ValueError(f"{key} is empty")
        frames.append(frame)
    return source, frames


def build_runtime(frames: list[Image.Image]) -> Image.Image:
    sheet = Image.new(
        "RGBA",
        (
            SOURCE_COLUMNS * RUNTIME_FRAME_WIDTH,
            SOURCE_ROWS * RUNTIME_FRAME_HEIGHT,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        sheet.alpha_composite(
            frame,
            (
                index % SOURCE_COLUMNS * RUNTIME_FRAME_WIDTH,
                index // SOURCE_COLUMNS * RUNTIME_FRAME_HEIGHT,
            ),
        )
    return sheet


def checkerboard(size: tuple[int, int], tile: int = 20) -> Image.Image:
    image = Image.new("RGBA", size, (15, 18, 27, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle(
                    (x, y, x + tile - 1, y + tile - 1),
                    fill=(29, 33, 45, 255),
                )
    return image


def build_reviews(
    runtime: Image.Image,
    frames: list[Image.Image],
) -> None:
    SHEET_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    sheet_review = checkerboard(runtime.size)
    sheet_review.alpha_composite(runtime)
    sheet_review.convert("RGB").save(SHEET_REVIEW, quality=95)

    gif_frames: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGB", (640, 512), (4, 7, 16))
        scaled = frame.resize(
            (560, 446),
            Image.Resampling.NEAREST,
        )
        canvas.paste(scaled, (40, 42), scaled)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((24, 488, 616, 500), fill=(48, 54, 67))
        draw.rectangle((24, 488, 616, 491), fill=(105, 114, 132))
        gif_frames.append(canvas)
    gif_frames[0].save(
        GIF_REVIEW,
        save_all=True,
        append_images=gif_frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        disposal=2,
    )


def main() -> None:
    _, frames = load_and_validate()
    runtime = build_runtime(frames)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(RUNTIME, optimize=True)
    build_reviews(runtime, frames)
    print(f"Wrote {RUNTIME.relative_to(ROOT)} {runtime.size}")
    print(f"Wrote {SHEET_REVIEW.relative_to(ROOT)}")
    print(f"Wrote {GIF_REVIEW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
