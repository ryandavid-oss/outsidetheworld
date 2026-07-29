#!/usr/bin/env python3
"""Build Aryn's supplied Ludo jetpack animation as a fixed runtime strip."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LUDO_ROOT = (
    PROJECT_ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Ludo"
)
RAW_ROOT = LUDO_ROOT / "Raw"
REVIEW_ROOT = LUDO_ROOT / "Reviews"
RUNTIME_ROOT = PROJECT_ROOT / "Images" / "Game" / "Super-Frgmnts"

SOURCE = RAW_ROOT / "aryn-ludo-jetpack-sheet-v1.png"
METADATA = RAW_ROOT / "aryn-ludo-jetpack-sheet-v1.json"
RUNTIME = RUNTIME_ROOT / "aryn-jetpack-ludo-runtime-v1.png"
REVIEW = REVIEW_ROOT / "aryn-ludo-jetpack-preview-v1.gif"
CONTACT = REVIEW_ROOT / "aryn-ludo-jetpack-contact-v1.png"
MANIFEST = LUDO_ROOT / "aryn-ludo-jetpack-runtime-v1.json"

FRAME_SIZE = 112
BASELINE_Y = 105
SOURCE_SCALE = 0.165
FRAME_COUNT = 16
FRAME_DURATION_MS = 120
BACKGROUND = (3, 6, 18, 255)


def load_frames() -> list[Image.Image]:
    sheet = Image.open(SOURCE).convert("RGBA")
    metadata = json.loads(METADATA.read_text())
    entries = [metadata["frames"][key] for key in sorted(metadata["frames"])]
    if len(entries) != FRAME_COUNT:
        raise ValueError(
            f"Expected {FRAME_COUNT} jetpack frames; found {len(entries)}"
        )

    frames: list[Image.Image] = []
    for index, entry in enumerate(entries):
        rect = entry["frame"]
        if (rect["w"], rect["h"]) != (360, 608):
            raise ValueError(
                f"Jetpack frame {index} is {rect['w']}x{rect['h']}; "
                "expected 360x608"
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
    reduced = source.resize(
        (
            round(source.width * SOURCE_SCALE),
            round(source.height * SOURCE_SCALE),
        ),
        Image.Resampling.LANCZOS,
    )
    bounds = reduced.getbbox()
    if bounds is None:
        raise ValueError("Jetpack source frame contains no visible pixels")
    trimmed = reduced.crop(bounds)
    if trimmed.width > FRAME_SIZE or trimmed.height > BASELINE_Y:
        raise ValueError(
            f"Normalized jetpack frame {trimmed.size} exceeds runtime cell"
        )
    runtime = Image.new(
        "RGBA",
        (FRAME_SIZE, FRAME_SIZE),
        (0, 0, 0, 0),
    )
    runtime.alpha_composite(
        trimmed,
        (
            round((FRAME_SIZE - trimmed.width) / 2),
            BASELINE_Y - trimmed.height,
        ),
    )
    return runtime


def build_strip(frames: list[Image.Image]) -> None:
    strip = Image.new(
        "RGBA",
        (FRAME_SIZE * len(frames), FRAME_SIZE),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (index * FRAME_SIZE, 0))
    strip.save(RUNTIME, optimize=True)


def build_review(frames: list[Image.Image]) -> None:
    reviews: list[Image.Image] = []
    for frame in frames:
        review = Image.new("RGBA", (FRAME_SIZE, FRAME_SIZE), BACKGROUND)
        review.alpha_composite(frame)
        reviews.append(
            review.resize(
                (FRAME_SIZE * 3, FRAME_SIZE * 3),
                Image.Resampling.NEAREST,
            ).convert("RGB")
        )
    reviews[0].save(
        REVIEW,
        save_all=True,
        append_images=reviews[1:],
        duration=[FRAME_DURATION_MS] * len(reviews),
        loop=0,
        disposal=2,
        optimize=False,
    )


def build_contact(frames: list[Image.Image]) -> None:
    columns = 8
    rows = 2
    panel = 128
    contact = Image.new(
        "RGBA",
        (columns * panel, rows * 144),
        BACKGROUND,
    )
    draw = ImageDraw.Draw(contact)
    for index, frame in enumerate(frames):
        column = index % columns
        row = index // columns
        x = column * panel
        y = row * 144
        contact.alpha_composite(frame, (x + 8, y + 4))
        draw.text(
            (x + 8, y + 120),
            f"{index:02d}",
            fill=(88, 245, 223, 255),
        )
    contact.resize(
        (contact.width * 2, contact.height * 2),
        Image.Resampling.NEAREST,
    ).save(CONTACT, optimize=True)


def main() -> None:
    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    frames = [normalize(frame) for frame in load_frames()]
    build_strip(frames)
    build_review(frames)
    build_contact(frames)

    manifest = {
        "asset": "Aryn Sol-Mavi Ludo jetpack animation",
        "status": "normalized and integrated as the backpack jet-assist module",
        "runtime": str(RUNTIME.relative_to(PROJECT_ROOT)),
        "runtime_contract": {
            "frame_size": [FRAME_SIZE, FRAME_SIZE],
            "baseline_y": BASELINE_Y,
            "source_scale": SOURCE_SCALE,
            "frame_count": len(frames),
            "source_frame_ms": FRAME_DURATION_MS,
        },
        "phase_map": {
            "brace": [0, 1, 2],
            "ignition": [3, 4, 5, 6, 7],
            "lift_off": [8, 9, 10, 11],
            "sustained_thrust": [12, 13, 14, 15],
        },
        "design_boundaries": [
            "This build does not assign fuel, duration, height, or recharge behavior.",
            "The animation remains separate from Aryn's unassisted jump.",
            "The jet-assist module remains part of the backpack while a temporary heavy-rifle tool is carried.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")

    for output in (RUNTIME, REVIEW, CONTACT, MANIFEST):
        print(f"Wrote {output.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
