#!/usr/bin/env python3
"""Build the Wound laser deck-impact runtime sheet and reviews."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
    / "Laser-Impact"
    / "Raw"
    / "wound-laser-ground-impact-alpha-v1.png"
)
RUNTIME = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "wound-laser-ground-impact-sheet-v1.png"
)
REVIEW_DIR = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Boss-Room"
    / "Laser-Impact"
    / "Reviews"
)
SHEET_REVIEW = REVIEW_DIR / "wound-laser-ground-impact-sheet-review-v1.png"
GIF_REVIEW = REVIEW_DIR / "wound-laser-ground-impact-preview-v1.gif"

SOURCE_COLUMNS = 4
SOURCE_ROWS = 3
FRAME_COUNT = 12
FRAME_SIZE = 96
CONTENT_SIZE = 90
FRAME_BASELINE = 93


def normalized_frames(source: Image.Image) -> list[Image.Image]:
    width, height = source.size
    if width % SOURCE_COLUMNS or height % SOURCE_ROWS:
        raise ValueError(
            f"source {source.size} is not an exact "
            f"{SOURCE_COLUMNS}x{SOURCE_ROWS} grid"
        )
    source_frame_width = width // SOURCE_COLUMNS
    source_frame_height = height // SOURCE_ROWS
    if source_frame_width != source_frame_height:
        raise ValueError(
            "source cells must be square, got "
            f"{source_frame_width}x{source_frame_height}"
        )

    frames: list[Image.Image] = []
    for index in range(FRAME_COUNT):
        column = index % SOURCE_COLUMNS
        row = index // SOURCE_COLUMNS
        frame = source.crop(
            (
                column * source_frame_width,
                row * source_frame_height,
                (column + 1) * source_frame_width,
                (row + 1) * source_frame_height,
            )
        )
        frame = frame.resize(
            (CONTENT_SIZE, CONTENT_SIZE),
            Image.Resampling.NEAREST,
        )
        alpha_bbox = frame.getchannel("A").getbbox()
        if not alpha_bbox:
            raise ValueError(f"source frame {index} is empty")
        left, _, right, bottom = alpha_bbox
        shift_x = FRAME_SIZE // 2 - (left + right) // 2
        shift_y = FRAME_BASELINE - bottom
        anchored = Image.new(
            "RGBA",
            (FRAME_SIZE, FRAME_SIZE),
            (0, 0, 0, 0),
        )
        anchored.alpha_composite(frame, (shift_x, shift_y))
        frames.append(anchored)
    return frames


def build_sheet(frames: list[Image.Image]) -> Image.Image:
    sheet = Image.new(
        "RGBA",
        (
            SOURCE_COLUMNS * FRAME_SIZE,
            SOURCE_ROWS * FRAME_SIZE,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        sheet.alpha_composite(
            frame,
            (
                index % SOURCE_COLUMNS * FRAME_SIZE,
                index // SOURCE_COLUMNS * FRAME_SIZE,
            ),
        )
    return sheet


def checkerboard(size: tuple[int, int], tile: int = 24) -> Image.Image:
    image = Image.new("RGBA", size, (18, 20, 30, 255))
    draw = ImageDraw.Draw(image)
    for y in range(0, size[1], tile):
        for x in range(0, size[0], tile):
            if (x // tile + y // tile) % 2:
                draw.rectangle(
                    (x, y, x + tile - 1, y + tile - 1),
                    fill=(31, 34, 48, 255),
                )
    return image


def build_reviews(
    sheet: Image.Image,
    frames: list[Image.Image],
) -> None:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    review_scale = 3
    sheet_scaled = sheet.resize(
        (
            sheet.width * review_scale,
            sheet.height * review_scale,
        ),
        Image.Resampling.NEAREST,
    )
    sheet_review = checkerboard(sheet_scaled.size)
    sheet_review.alpha_composite(sheet_scaled)
    sheet_review.convert("RGB").save(SHEET_REVIEW)

    gif_frames: list[Image.Image] = []
    for frame in frames:
        canvas = Image.new("RGB", (384, 384), (4, 7, 16))
        scaled = frame.resize((288, 288), Image.Resampling.NEAREST)
        canvas.paste(scaled, (48, 54), scaled)
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((24, 334, 360, 346), fill=(53, 57, 72))
        draw.rectangle((24, 334, 360, 337), fill=(112, 119, 138))
        gif_frames.append(canvas)
    gif_frames[0].save(
        GIF_REVIEW,
        save_all=True,
        append_images=gif_frames[1:],
        duration=65,
        loop=0,
        disposal=2,
    )


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    source = Image.open(SOURCE).convert("RGBA")
    frames = normalized_frames(source)
    sheet = build_sheet(frames)
    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(RUNTIME, optimize=True)
    build_reviews(sheet, frames)
    print(f"Wrote {RUNTIME.relative_to(ROOT)} {sheet.size}")
    print(f"Wrote {SHEET_REVIEW.relative_to(ROOT)}")
    print(f"Wrote {GIF_REVIEW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
