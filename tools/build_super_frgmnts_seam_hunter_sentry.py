#!/usr/bin/env python3
"""Build the curated Seam Hunter upward-watch and turn atlases."""

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
    / "Shaft-Sentry"
)
SOURCE = (
    ASSET_DIR
    / "Raw"
    / "seam-hunter-upward-watch-source-v2.png"
)
SOURCE_METADATA = (
    ASSET_DIR
    / "Raw"
    / "seam-hunter-upward-watch-source-v2.json"
)
RUNTIME = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-seam-hunter-upward-watch-sheet-v2.png"
)
SHEET_REVIEW = (
    ASSET_DIR
    / "Reviews"
    / "seam-hunter-upward-watch-sheet-review-v2.png"
)
GIF_REVIEW = (
    ASSET_DIR
    / "Reviews"
    / "seam-hunter-upward-watch-preview-v2.gif"
)
EXPORT_DIR = ASSET_DIR / "Exports"
LOOK_UP_EXPORT = (
    EXPORT_DIR
    / "seam-hunter-looking-up-reference-v1.png"
)
LOOK_UP_EXPORT_4X = (
    EXPORT_DIR
    / "seam-hunter-looking-up-reference-v1-4x.png"
)
TURN_SOURCE = (
    ASSET_DIR
    / "Raw"
    / "seam-hunter-upward-turn-source-v1.png"
)
TURN_SOURCE_METADATA = (
    ASSET_DIR
    / "Raw"
    / "seam-hunter-upward-turn-source-v1.json"
)
TURN_RUNTIME = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-seam-hunter-upward-turn-sheet-v1.png"
)
TURN_SHEET_REVIEW = (
    ASSET_DIR
    / "Reviews"
    / "seam-hunter-upward-turn-sheet-review-v1.png"
)
TURN_GIF_REVIEW = (
    ASSET_DIR
    / "Reviews"
    / "seam-hunter-upward-turn-preview-v1.gif"
)

SOURCE_COLUMNS = 6
SOURCE_ROWS = 6
SOURCE_FRAME_WIDTH = 378
SOURCE_FRAME_HEIGHT = 498
SOURCE_CROP_WIDTH = 364
SOURCE_CROP_HEIGHT = 458
SOURCE_FRAME_DURATION_MS = 76

RUNTIME_COLUMNS = 5
RUNTIME_ROWS = 4
RUNTIME_FRAME_WIDTH = 404
RUNTIME_FRAME_HEIGHT = 458
RUNTIME_FOOT_ROOT_X = RUNTIME_FRAME_WIDTH // 2
RUNTIME_FRAME_DURATION_MS = 76

# The authored motion rises continuously from the normal forward hunch to its
# highest upward focus on frame 15. Runtime holds that peak frame rather than
# playing the return half of the source loop.
CURATED_SOURCE_FRAMES = list(range(16))

TURN_SOURCE_COLUMNS = 6
TURN_SOURCE_ROWS = 6
TURN_SOURCE_FRAME_WIDTH = 404
TURN_SOURCE_FRAME_HEIGHT = 458
TURN_SOURCE_FRAME_DURATION_MS = 74
TURN_RUNTIME_COLUMNS = 5
TURN_RUNTIME_ROWS = 4
TURN_RUNTIME_FRAME_WIDTH = 409
TURN_RUNTIME_FRAME_HEIGHT = 458
TURN_RUNTIME_FOOT_ROOT_X = 197
TURN_RUNTIME_FRAME_DURATION_MS = 74

# Alternating source frames preserve the complete 180-degree silhouette while
# keeping the tracking response to a weighty 1.406 seconds instead of the
# source sheet's overly slow 2.664-second presentation.
CURATED_TURN_SOURCE_FRAMES = list(range(0, 36, 2)) + [35]


def source_frame_box(index: int) -> tuple[int, int, int, int]:
    x = index % SOURCE_COLUMNS * SOURCE_FRAME_WIDTH
    y = index // SOURCE_COLUMNS * SOURCE_FRAME_HEIGHT
    return (
        x,
        y,
        x + SOURCE_FRAME_WIDTH,
        y + SOURCE_FRAME_HEIGHT,
    )


def foot_root_x(frame: Image.Image) -> float:
    alpha = frame.getchannel("A")
    bounds = alpha.getbbox()
    if not bounds:
        raise ValueError("curated source frame is empty")
    _, _, _, bottom = bounds
    lower_band_top = max(0, bottom - 28)
    pixels = alpha.load()
    xs = [
        x
        for y in range(lower_band_top, bottom)
        for x in range(frame.width)
        if pixels[x, y] >= 48
    ]
    if not xs:
        raise ValueError("could not locate the planted foot")
    return (min(xs) + max(xs)) / 2


def load_and_validate() -> list[Image.Image]:
    source = Image.open(SOURCE).convert("RGBA")
    expected_size = (
        SOURCE_COLUMNS * SOURCE_FRAME_WIDTH,
        SOURCE_ROWS * SOURCE_FRAME_HEIGHT,
    )
    if source.size != expected_size:
        raise ValueError(
            f"source is {source.size}, expected {expected_size}"
        )

    metadata = json.loads(SOURCE_METADATA.read_text(encoding="utf-8"))
    for index in range(SOURCE_COLUMNS * SOURCE_ROWS):
        key = f"frame_{index:03d}"
        record = metadata["frames"].get(key)
        if not record:
            raise ValueError(f"metadata is missing {key}")
        frame_record = record["frame"]
        expected_x = index % SOURCE_COLUMNS * SOURCE_FRAME_WIDTH
        expected_y = index // SOURCE_COLUMNS * SOURCE_FRAME_HEIGHT
        if (
            frame_record["x"] != expected_x
            or frame_record["y"] != expected_y
            or frame_record["w"] != SOURCE_FRAME_WIDTH
            or frame_record["h"] != SOURCE_FRAME_HEIGHT
        ):
            raise ValueError(f"{key} has an unexpected source rectangle")
        if record["duration"] != SOURCE_FRAME_DURATION_MS:
            raise ValueError(
                f"{key} duration is {record['duration']}, "
                f"expected {SOURCE_FRAME_DURATION_MS}"
            )

    runtime_frames: list[Image.Image] = []
    for source_index in CURATED_SOURCE_FRAMES:
        frame = source.crop(source_frame_box(source_index))
        frame = frame.crop(
            (0, 0, SOURCE_CROP_WIDTH, SOURCE_CROP_HEIGHT)
        )
        root_x = foot_root_x(frame)
        paste_x = round(RUNTIME_FOOT_ROOT_X - root_x)
        if paste_x < 0 or paste_x + frame.width > RUNTIME_FRAME_WIDTH:
            raise ValueError(
                f"source frame {source_index} exceeds the registered cell"
            )
        registered = Image.new(
            "RGBA",
            (RUNTIME_FRAME_WIDTH, RUNTIME_FRAME_HEIGHT),
            (0, 0, 0, 0),
        )
        registered.alpha_composite(frame, (paste_x, 0))
        runtime_frames.append(registered)
    return runtime_frames


def build_runtime(frames: list[Image.Image]) -> Image.Image:
    sheet = Image.new(
        "RGBA",
        (
            RUNTIME_COLUMNS * RUNTIME_FRAME_WIDTH,
            RUNTIME_ROWS * RUNTIME_FRAME_HEIGHT,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        sheet.alpha_composite(
            frame,
            (
                index % RUNTIME_COLUMNS * RUNTIME_FRAME_WIDTH,
                index // RUNTIME_COLUMNS * RUNTIME_FRAME_HEIGHT,
            ),
        )
    return sheet


def turn_source_frame_box(index: int) -> tuple[int, int, int, int]:
    x = index % TURN_SOURCE_COLUMNS * TURN_SOURCE_FRAME_WIDTH
    y = index // TURN_SOURCE_COLUMNS * TURN_SOURCE_FRAME_HEIGHT
    return (
        x,
        y,
        x + TURN_SOURCE_FRAME_WIDTH,
        y + TURN_SOURCE_FRAME_HEIGHT,
    )


def load_and_validate_turn() -> list[Image.Image]:
    source = Image.open(TURN_SOURCE).convert("RGBA")
    expected_size = (
        TURN_SOURCE_COLUMNS * TURN_SOURCE_FRAME_WIDTH,
        TURN_SOURCE_ROWS * TURN_SOURCE_FRAME_HEIGHT,
    )
    if source.size != expected_size:
        raise ValueError(
            f"turn source is {source.size}, expected {expected_size}"
        )

    metadata = json.loads(
        TURN_SOURCE_METADATA.read_text(encoding="utf-8")
    )
    for index in range(TURN_SOURCE_COLUMNS * TURN_SOURCE_ROWS):
        key = f"frame_{index:03d}"
        record = metadata["frames"].get(key)
        if not record:
            raise ValueError(f"turn metadata is missing {key}")
        frame_record = record["frame"]
        expected_x = index % TURN_SOURCE_COLUMNS * TURN_SOURCE_FRAME_WIDTH
        expected_y = index // TURN_SOURCE_COLUMNS * TURN_SOURCE_FRAME_HEIGHT
        if (
            frame_record["x"] != expected_x
            or frame_record["y"] != expected_y
            or frame_record["w"] != TURN_SOURCE_FRAME_WIDTH
            or frame_record["h"] != TURN_SOURCE_FRAME_HEIGHT
        ):
            raise ValueError(
                f"{key} has an unexpected turn source rectangle"
            )
        if record["duration"] != TURN_SOURCE_FRAME_DURATION_MS:
            raise ValueError(
                f"{key} duration is {record['duration']}, "
                f"expected {TURN_SOURCE_FRAME_DURATION_MS}"
            )

    runtime_frames: list[Image.Image] = []
    for source_index in CURATED_TURN_SOURCE_FRAMES:
        frame = source.crop(turn_source_frame_box(source_index))
        root_x = foot_root_x(frame)
        paste_x = round(TURN_RUNTIME_FOOT_ROOT_X - root_x)
        alpha_bounds = frame.getchannel("A").getbbox()
        if (
            not alpha_bounds
            or paste_x + alpha_bounds[0] < 0
            or paste_x + alpha_bounds[2] > TURN_RUNTIME_FRAME_WIDTH
        ):
            raise ValueError(
                f"turn source frame {source_index} exceeds "
                "the registered cell"
            )
        registered = Image.new(
            "RGBA",
            (
                TURN_RUNTIME_FRAME_WIDTH,
                TURN_RUNTIME_FRAME_HEIGHT,
            ),
            (0, 0, 0, 0),
        )
        source_left = max(0, -paste_x)
        destination_left = max(0, paste_x)
        composite_width = min(
            frame.width - source_left,
            TURN_RUNTIME_FRAME_WIDTH - destination_left,
        )
        registered.alpha_composite(
            frame.crop(
                (
                    source_left,
                    0,
                    source_left + composite_width,
                    TURN_RUNTIME_FRAME_HEIGHT,
                )
            ),
            (destination_left, 0),
        )
        runtime_frames.append(registered)
    return runtime_frames


def build_turn_runtime(frames: list[Image.Image]) -> Image.Image:
    sheet = Image.new(
        "RGBA",
        (
            TURN_RUNTIME_COLUMNS * TURN_RUNTIME_FRAME_WIDTH,
            TURN_RUNTIME_ROWS * TURN_RUNTIME_FRAME_HEIGHT,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        sheet.alpha_composite(
            frame,
            (
                index % TURN_RUNTIME_COLUMNS *
                TURN_RUNTIME_FRAME_WIDTH,
                index // TURN_RUNTIME_COLUMNS *
                TURN_RUNTIME_FRAME_HEIGHT,
            ),
        )
    return sheet


def checkerboard(size: tuple[int, int], tile: int = 20) -> Image.Image:
    image = Image.new("RGBA", size, (13, 16, 24, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle(
                    (x, y, x + tile - 1, y + tile - 1),
                    fill=(29, 34, 46, 255),
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
    review_frames = frames + [frames[-1]] * 12
    for frame in review_frames:
        canvas = Image.new("RGB", (672, 640), (3, 7, 15))
        scaled = frame.resize((529, 600), Image.Resampling.NEAREST)
        canvas.paste(scaled, (71, 8), scaled)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((20, 606, 652, 622), fill=(47, 54, 68))
        draw.rectangle((20, 606, 652, 610), fill=(112, 121, 140))
        gif_frames.append(canvas)
    gif_frames[0].save(
        GIF_REVIEW,
        save_all=True,
        append_images=gif_frames[1:],
        duration=RUNTIME_FRAME_DURATION_MS,
        loop=0,
        disposal=2,
    )


def export_held_pose(frame: Image.Image) -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    frame.save(LOOK_UP_EXPORT, optimize=True)
    frame.resize(
        (frame.width * 4, frame.height * 4),
        Image.Resampling.NEAREST,
    ).save(LOOK_UP_EXPORT_4X, optimize=True)


def build_turn_reviews(
    runtime: Image.Image,
    frames: list[Image.Image],
) -> None:
    TURN_SHEET_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    sheet_review = checkerboard(runtime.size)
    sheet_review.alpha_composite(runtime)
    sheet_review.convert("RGB").save(
        TURN_SHEET_REVIEW,
        quality=95,
    )

    gif_frames: list[Image.Image] = []
    review_frames = frames + [frames[-1]] * 10
    for frame in review_frames:
        canvas = Image.new("RGB", (672, 640), (3, 7, 15))
        scaled = frame.resize((536, 600), Image.Resampling.NEAREST)
        canvas.paste(scaled, (68, 8), scaled)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((20, 606, 652, 622), fill=(47, 54, 68))
        draw.rectangle((20, 606, 652, 610), fill=(112, 121, 140))
        gif_frames.append(canvas)
    gif_frames[0].save(
        TURN_GIF_REVIEW,
        save_all=True,
        append_images=gif_frames[1:],
        duration=TURN_RUNTIME_FRAME_DURATION_MS,
        loop=0,
        disposal=2,
    )


def main() -> None:
    frames = load_and_validate()
    runtime = build_runtime(frames)
    turn_frames = load_and_validate_turn()
    turn_runtime = build_turn_runtime(turn_frames)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(RUNTIME, optimize=True)
    turn_runtime.save(TURN_RUNTIME, optimize=True)
    build_reviews(runtime, frames)
    build_turn_reviews(turn_runtime, turn_frames)
    export_held_pose(frames[-1])
    print(f"Wrote {RUNTIME.relative_to(ROOT)} {runtime.size}")
    print(
        f"Wrote {TURN_RUNTIME.relative_to(ROOT)} "
        f"{turn_runtime.size}"
    )
    print(f"Wrote {SHEET_REVIEW.relative_to(ROOT)}")
    print(f"Wrote {GIF_REVIEW.relative_to(ROOT)}")
    print(f"Wrote {TURN_SHEET_REVIEW.relative_to(ROOT)}")
    print(f"Wrote {TURN_GIF_REVIEW.relative_to(ROOT)}")
    print(f"Wrote {LOOK_UP_EXPORT.relative_to(ROOT)}")
    print(f"Wrote {LOOK_UP_EXPORT_4X.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
