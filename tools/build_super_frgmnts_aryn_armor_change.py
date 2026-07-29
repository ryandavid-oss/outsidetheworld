#!/usr/bin/env python3
"""Normalize Aryn's supplied armor-change animation for RD-42 review."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = (
    PROJECT_ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Armor-Change"
)
RAW_ROOT = ASSET_ROOT / "Raw"
REVIEW_ROOT = ASSET_ROOT / "Reviews"
RUNTIME_ROOT = PROJECT_ROOT / "Images" / "Game" / "Super-Frgmnts"

SOURCE = RAW_ROOT / "aryn-armor-change-source-v1.png"
METADATA = RAW_ROOT / "aryn-armor-change-source-v1.json"
RUNTIME = RUNTIME_ROOT / "aryn-armor-change-runtime-v1.png"
REVIEW = REVIEW_ROOT / "aryn-armor-change-preview-v1.gif"
CONTACT = REVIEW_ROOT / "aryn-armor-change-contact-v1.png"
MANIFEST = ASSET_ROOT / "aryn-armor-change-v1.json"

FRAME_SIZE = 112
SOURCE_FRAME_SIZE = (360, 514)
GRID_COLUMNS = 6
GRID_ROWS = 6
FRAME_COUNT = GRID_COLUMNS * GRID_ROWS
FRAME_DURATION_MS = 76
BASELINE_Y = 104
VISIBLE_HEIGHT_TARGET = 90
BACKGROUND = (3, 6, 18, 255)


def load_frames() -> list[Image.Image]:
    sheet = Image.open(SOURCE).convert("RGBA")
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    entries = [
        metadata["frames"][key]
        for key in sorted(metadata["frames"])
    ]
    if len(entries) != FRAME_COUNT:
        raise ValueError(
            f"Expected {FRAME_COUNT} armor-change frames; "
            f"found {len(entries)}"
        )
    durations = {entry["duration"] for entry in entries}
    if durations != {FRAME_DURATION_MS}:
        raise ValueError(
            f"Expected uniform {FRAME_DURATION_MS} ms frames; "
            f"found {sorted(durations)}"
        )

    frames: list[Image.Image] = []
    for index, entry in enumerate(entries):
        rect = entry["frame"]
        if (rect["w"], rect["h"]) != SOURCE_FRAME_SIZE:
            raise ValueError(
                f"Armor-change frame {index} is "
                f"{rect['w']}x{rect['h']}; expected "
                f"{SOURCE_FRAME_SIZE[0]}x{SOURCE_FRAME_SIZE[1]}"
            )
        frames.append(
            sheet.crop(
                (
                    rect["x"],
                    rect["y"],
                    rect["x"] + rect["w"],
                    rect["y"] + rect["h"],
                )
            )
        )
    return frames


def normalize(source: Image.Image) -> Image.Image:
    alpha_bounds = source.getchannel("A").getbbox()
    if alpha_bounds is None:
        return Image.new(
            "RGBA",
            (FRAME_SIZE, FRAME_SIZE),
            (0, 0, 0, 0),
        )

    visible_height = alpha_bounds[3] - alpha_bounds[1]
    scale = VISIBLE_HEIGHT_TARGET / visible_height
    normalized_size = (
        round(source.width * scale),
        round(source.height * scale),
    )
    reduced = source.resize(
        normalized_size,
        Image.Resampling.LANCZOS,
    )
    reduced_bounds = reduced.getchannel("A").getbbox()
    if reduced_bounds is None:
        raise ValueError("Normalized armor-change frame has no visible pixels")

    normalized_offset = (
        round(FRAME_SIZE / 2 - source.width * scale / 2),
        BASELINE_Y + 1 - reduced_bounds[3],
    )
    runtime = Image.new(
        "RGBA",
        (FRAME_SIZE, FRAME_SIZE),
        (0, 0, 0, 0),
    )
    runtime.alpha_composite(reduced, normalized_offset)
    return runtime


def build_atlas(frames: list[Image.Image]) -> None:
    atlas = Image.new(
        "RGBA",
        (
            GRID_COLUMNS * FRAME_SIZE,
            GRID_ROWS * FRAME_SIZE,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        atlas.alpha_composite(
            frame,
            (
                (index % GRID_COLUMNS) * FRAME_SIZE,
                (index // GRID_COLUMNS) * FRAME_SIZE,
            ),
        )
    atlas.save(RUNTIME, optimize=True)


def build_review(frames: list[Image.Image]) -> None:
    reviews: list[Image.Image] = []
    for frame in frames:
        review = Image.new(
            "RGBA",
            (FRAME_SIZE, FRAME_SIZE),
            BACKGROUND,
        )
        review.alpha_composite(frame)
        reviews.append(
            review.resize(
                (FRAME_SIZE * 4, FRAME_SIZE * 4),
                Image.Resampling.NEAREST,
            ).convert("RGB")
        )
    review_durations: list[int] = []
    duration_accumulator = 0
    for _ in reviews:
        duration_accumulator += 22
        if duration_accumulator >= len(reviews):
            review_durations.append(80)
            duration_accumulator -= len(reviews)
        else:
            review_durations.append(70)
    reviews[0].save(
        REVIEW,
        save_all=True,
        append_images=reviews[1:],
        duration=review_durations,
        loop=0,
        disposal=2,
        optimize=False,
    )


def build_contact(frames: list[Image.Image]) -> None:
    panel = 128
    contact = Image.new(
        "RGBA",
        (GRID_COLUMNS * panel, GRID_ROWS * 144),
        BACKGROUND,
    )
    draw = ImageDraw.Draw(contact)
    for index, frame in enumerate(frames):
        column = index % GRID_COLUMNS
        row = index // GRID_COLUMNS
        x = column * panel
        y = row * 144
        contact.alpha_composite(frame, (x + 8, y + 4))
        draw.text(
            (x + 8, y + 120),
            f"{index:02d} // {index * FRAME_DURATION_MS:04d} ms",
            fill=(88, 245, 223, 255),
        )
    contact.resize(
        (contact.width * 2, contact.height * 2),
        Image.Resampling.NEAREST,
    ).save(CONTACT, optimize=True)


def build_manifest() -> None:
    manifest = {
        "asset": "Aryn Sol-Mavi armor-change animation",
        "status": "normalized and integrated with persistent RD-42 flight-suit movement",
        "source": {
            "image": str(SOURCE.relative_to(PROJECT_ROOT)),
            "metadata": str(METADATA.relative_to(PROJECT_ROOT)),
            "frame_size": list(SOURCE_FRAME_SIZE),
            "grid": [GRID_COLUMNS, GRID_ROWS],
            "frame_count": FRAME_COUNT,
            "frame_duration_ms": FRAME_DURATION_MS,
            "total_duration_ms": FRAME_COUNT * FRAME_DURATION_MS,
        },
        "runtime_candidate": {
            "image": str(RUNTIME.relative_to(PROJECT_ROOT)),
            "frame_size": [FRAME_SIZE, FRAME_SIZE],
            "atlas_size": [
                GRID_COLUMNS * FRAME_SIZE,
                GRID_ROWS * FRAME_SIZE,
            ],
            "grid": [GRID_COLUMNS, GRID_ROWS],
            "baseline_y": BASELINE_Y,
            "visible_height_target": VISIBLE_HEIGHT_TARGET,
            "normalization":
                "per-frame visible height with source-center preservation",
        },
        "phase_map": {
            "armored_hold": [0, 10],
            "field_ignition": [11, 17],
            "armor_release": [18, 29],
            "flight_suit_resolve": [30, 35],
        },
        "direction": {
            "forward": "armored to flight suit",
            "provisional_reverse": "flight suit to armored",
        },
        "design_boundaries": [
            "The supplied sheet is a stationary costume-change interaction.",
            "Separate supplied run and jump sheets now support persistent flight-suit movement on the RD-42 main deck.",
            "It does not provide unarmored damage, weapon, descent, or hatch-traversal poses.",
            "The isolated review returns movement control after the forward sequence resolves.",
            "Reverse playback remains provisional until an authored re-arm sequence exists.",
        ],
        "review_route": "super_frgmnts.html?preview=ship-interior&autostart=1",
        "reviews": {
            "animation": str(REVIEW.relative_to(PROJECT_ROOT)),
            "contact_sheet": str(CONTACT.relative_to(PROJECT_ROOT)),
        },
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    frames = [normalize(frame) for frame in load_frames()]
    build_atlas(frames)
    build_review(frames)
    build_contact(frames)
    build_manifest()
    for output in (RUNTIME, REVIEW, CONTACT, MANIFEST):
        print(f"Wrote {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
