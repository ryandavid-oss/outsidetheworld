#!/usr/bin/env python3
"""Build a review-only contact sheet for Aryn's existing web-game artwork."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Aryn"
    / "aryn-reference-contact-sheet-v1.png"
)
FRAME_SIZE = 112

ASSETS = [
    ("LIVE ARMOR", "Command rest", "Images/Game/Super-Frgmnts/aryn-command-rest-runtime-v1.png"),
    ("LIVE ARMOR", "Field rest", "Images/Game/Super-Frgmnts/aryn-field-rest-runtime-v1.png"),
    ("LIVE ARMOR", "Run v2 — live", "Images/Game/Super-Frgmnts/aryn-run-ludo-runtime-v2.png"),
    ("LIVE ARMOR", "Jump / landing", "Images/Game/Super-Frgmnts/aryn-jump-ludo-runtime-v1.png"),
    ("LIVE ARMOR", "Drop", "Images/Game/Super-Frgmnts/aryn-drop-ludo-runtime-v1.png"),
    ("LIVE ARMOR", "Light impact", "Images/Game/Super-Frgmnts/aryn-impact-light-ludo-runtime-v1.png"),
    ("LIVE ARMOR", "Heavy impact", "Images/Game/Super-Frgmnts/aryn-impact-heavy-ludo-runtime-v1.png"),
    ("LIVE ARMOR", "Death", "Images/Game/Super-Frgmnts/aryn-death-ludo-runtime-v1.png"),
    ("LIVE ARMOR", "Jet Assist", "Images/Game/Super-Frgmnts/aryn-jetpack-ludo-runtime-v1.png"),
    ("SUPPORT", "Dialogue portrait v3", "Images/Game/Super-Frgmnts/aryn-dialogue-portrait-runtime-v3.png"),
    ("SUPPORT", "Armor-change storyboard", "Images/Game/Super-Frgmnts/aryn-armor-change-runtime-v1.png"),
    ("SUPPORT", "Fleet-apparel walk", "Images/Game/Super-Frgmnts/aryn-fleet-apparel-walk-sheet-v1.png"),
    ("ARCHIVE", "Run v1 — superseded", "Images/Game/Super-Frgmnts/aryn-run-ludo-runtime-v1.png"),
    ("ARCHIVE", "Rifle draw — retired weapon", "Images/Game/Super-Frgmnts/aryn-rifle-draw-ludo-runtime-v1.png"),
    ("ARCHIVE", "Rifle fire — retired weapon", "Images/Game/Super-Frgmnts/aryn-rifle-fire-ludo-runtime-v1.png"),
    ("ARCHIVE", "Rifle run-ready — retired weapon", "Images/Game/Super-Frgmnts/aryn-rifle-run-ready-ludo-runtime-v1.png"),
    ("ARCHIVE", "Rifle run-fire — retired weapon", "Images/Game/Super-Frgmnts/aryn-rifle-run-fire-ludo-runtime-v1.png"),
    ("ARCHIVE", "Flight-suit run", "Images/Game/Super-Frgmnts/aryn-flight-suit-run-runtime-v1.png"),
    ("ARCHIVE", "Flight-suit jump", "Images/Game/Super-Frgmnts/aryn-flight-suit-jump-runtime-v1.png"),
    ("LEGACY", "Builder balanced run", "Images/Builder/aryn-run-10pose-balanced-gait-sheet.png"),
    ("LEGACY", "Signal Ranger idle", "Images/Builder/signal-ranger-idle-focused-v2.png"),
    ("LEGACY", "Signal Ranger takeoff", "Images/Builder/signal-ranger-jump-takeoff.png"),
    ("LEGACY", "Signal Ranger airborne", "Images/Builder/signal-ranger-jump-airborne.png"),
    ("LEGACY", "Signal Ranger crouch", "Images/Builder/signal-ranger-crouch.png"),
    ("LEGACY", "Signal Ranger run / armswing", "Images/Builder/signal-ranger-run-10pose-headlocked-armswing-sheet.png"),
]

STATUS_COLORS = {
    "LIVE ARMOR": "#58f5df",
    "SUPPORT": "#7aa7ff",
    "ARCHIVE": "#ffd36c",
    "LEGACY": "#ff69b4",
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    font_path = Path("/System/Library/Fonts/SFNSMono.ttf")
    if bold:
        bold_path = Path("/System/Library/Fonts/SFNSMono.ttf")
        if bold_path.exists():
            font_path = bold_path
    return ImageFont.truetype(str(font_path), size=size)


def checkerboard(width: int, height: int, cell: int = 12) -> Image.Image:
    image = Image.new("RGBA", (width, height), "#111a2b")
    draw = ImageDraw.Draw(image)
    for row in range(0, height, cell):
        for column in range(0, width, cell):
            if (row // cell + column // cell) % 2:
                draw.rectangle(
                    (column, row, column + cell - 1, row + cell - 1),
                    fill="#17243a",
                )
    return image


def representative_frames(image: Image.Image) -> tuple[list[Image.Image], str]:
    width, height = image.size
    if width % FRAME_SIZE or height % FRAME_SIZE:
        return [image], "single composition"

    columns = width // FRAME_SIZE
    rows = height // FRAME_SIZE
    frame_count = columns * rows
    frames = []
    for index in range(frame_count):
        column = index % columns
        row = index // columns
        frames.append(
            image.crop(
                (
                    column * FRAME_SIZE,
                    row * FRAME_SIZE,
                    (column + 1) * FRAME_SIZE,
                    (row + 1) * FRAME_SIZE,
                )
            )
        )

    if frame_count <= 4:
        selection = list(range(frame_count))
    else:
        selection = sorted(
            set(
                [
                    0,
                    round((frame_count - 1) / 3),
                    round((frame_count - 1) * 2 / 3),
                    frame_count - 1,
                ]
            )
        )
    return [frames[index] for index in selection], f"{columns}×{rows} tiles / {frame_count} frames"


def fit_frame(frame: Image.Image, width: int, height: int) -> Image.Image:
    source = frame.convert("RGBA")
    scale = min(width / source.width, height / source.height)
    scale = max(1, int(scale)) if source.width <= width and source.height <= height else scale
    destination = (
        max(1, round(source.width * scale)),
        max(1, round(source.height * scale)),
    )
    return source.resize(destination, Image.Resampling.NEAREST)


def build_sheet(output: Path) -> None:
    canvas_width = 2200
    margin = 56
    header_height = 255
    card_gap = 34
    card_width = (canvas_width - margin * 2 - card_gap) // 2
    card_height = 330
    row_count = (len(ASSETS) + 1) // 2
    canvas_height = header_height + row_count * (card_height + card_gap) + margin

    canvas = Image.new("RGB", (canvas_width, canvas_height), "#070b16")
    draw = ImageDraw.Draw(canvas)
    title_font = font(52, bold=True)
    subtitle_font = font(22)
    card_title_font = font(25, bold=True)
    small_font = font(17)
    tiny_font = font(15)

    draw.text((margin, 42), "ARYN // EXISTING ASSET REFERENCE", font=title_font, fill="#f4f7ff")
    draw.text(
        (margin, 116),
        "Review artifact only — no new poses and no gameplay changes",
        font=subtitle_font,
        fill="#9eb4cc",
    )
    legend_x = margin
    for status in ("LIVE ARMOR", "SUPPORT", "ARCHIVE", "LEGACY"):
        color = STATUS_COLORS[status]
        draw.rounded_rectangle(
            (legend_x, 172, legend_x + 230, 215),
            radius=8,
            outline=color,
            width=2,
            fill="#0d1424",
        )
        draw.text((legend_x + 15, 183), status, font=small_font, fill=color)
        legend_x += 248

    for asset_index, (status, label, relative_path) in enumerate(ASSETS):
        row = asset_index // 2
        column = asset_index % 2
        x = margin + column * (card_width + card_gap)
        y = header_height + row * (card_height + card_gap)
        color = STATUS_COLORS[status]
        path = ROOT / relative_path
        image = Image.open(path).convert("RGBA")
        frames, layout = representative_frames(image)

        draw.rounded_rectangle(
            (x, y, x + card_width, y + card_height),
            radius=14,
            fill="#0d1424",
            outline="#29405c",
            width=2,
        )
        draw.rectangle((x, y, x + 9, y + card_height), fill=color)
        draw.text((x + 28, y + 22), label, font=card_title_font, fill="#f4f7ff")
        status_width = max(136, draw.textlength(status, font=tiny_font) + 34)
        draw.rounded_rectangle(
            (x + card_width - status_width - 24, y + 20, x + card_width - 24, y + 53),
            radius=7,
            outline=color,
            width=2,
        )
        draw.text(
            (x + card_width - status_width - 7, y + 29),
            status,
            font=tiny_font,
            fill=color,
        )
        draw.text(
            (x + 28, y + 63),
            f"{image.width}×{image.height}  •  {layout}",
            font=small_font,
            fill="#9eb4cc",
        )
        display_path = relative_path.replace("Images/Game/Super-Frgmnts/", "…/Super-Frgmnts/")
        draw.text((x + 28, y + 92), display_path, font=tiny_font, fill="#6f89a8")

        preview_x = x + 28
        preview_y = y + 126
        available_width = card_width - 56
        preview_gap = 14
        slot_width = (available_width - preview_gap * 3) // 4
        slot_height = 176
        for frame_index, frame in enumerate(frames[:4]):
            slot_x = preview_x + frame_index * (slot_width + preview_gap)
            backdrop = checkerboard(slot_width, slot_height)
            fitted = fit_frame(frame, slot_width - 12, slot_height - 12)
            backdrop.alpha_composite(
                fitted,
                (
                    (slot_width - fitted.width) // 2,
                    (slot_height - fitted.height) // 2,
                ),
            )
            canvas.paste(backdrop.convert("RGB"), (slot_x, preview_y))
            draw.rectangle(
                (slot_x, preview_y, slot_x + slot_width, preview_y + slot_height),
                outline="#263a55",
                width=2,
            )

    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, optimize=True)
    print(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build_sheet(args.output.resolve())


if __name__ == "__main__":
    main()
