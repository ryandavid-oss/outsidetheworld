#!/usr/bin/env python3
"""Build the curated Aryn Ludo run loop and its review artifacts."""

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
SOURCE_SHEET = LUDO_ROOT / "Raw" / "aryn-ludo-run-sheet-v3.png"
SOURCE_METADATA = LUDO_ROOT / "Raw" / "aryn-ludo-run-sheet-v3.json"
CURRENT_RUNTIME = (
    PROJECT_ROOT
    / "Images"
    / "Builder"
    / "aryn-run-10pose-balanced-gait-sheet.png"
)
RUNTIME_OUTPUT = (
    PROJECT_ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "aryn-run-ludo-runtime-v2.png"
)
REVIEW_DIRECTORY = LUDO_ROOT / "Reviews"
REVIEW_COMPARISON = REVIEW_DIRECTORY / "aryn-ludo-run-runtime-comparison-v2.png"
REVIEW_ANIMATION = REVIEW_DIRECTORY / "aryn-ludo-run-runtime-preview-v2.gif"
MANIFEST_OUTPUT = LUDO_ROOT / "aryn-ludo-run-runtime-v2.json"

# The generated sequence contains several gait cycles, but its final cycle
# develops an arm reversal across frames 30-34. Frames 15-22 form a complete,
# internally consistent eight-frame gait: the following source frame (23)
# returns to nearly the same pose as frame 15, so the loop closes cleanly.
SOURCE_FRAME_INDICES = tuple(range(15, 23))
SOURCE_FRAME_SIZE = (418, 556)
RUNTIME_FRAME_SIZE = 112
RUNTIME_RESIZE = (69, 92)
RUNTIME_OFFSET = (22, 13)
RUNTIME_FPS = 12
PACK_EMITTER_ANCHORS = (
    {"x": 61, "y": 13},
    {"x": 61, "y": 14},
    {"x": 61, "y": 13},
    {"x": 60, "y": 13},
    {"x": 60, "y": 13},
    {"x": 60, "y": 14},
    {"x": 59, "y": 13},
    {"x": 59, "y": 14},
)
REVIEW_BACKGROUND = (3, 6, 18, 255)


def load_source_frames() -> list[Image.Image]:
    sheet = Image.open(SOURCE_SHEET).convert("RGBA")
    metadata = json.loads(SOURCE_METADATA.read_text())
    frame_entries = [
        metadata["frames"][key]
        for key in sorted(metadata["frames"])
    ]

    if len(frame_entries) != 36:
        raise ValueError(f"Expected 36 source frames, found {len(frame_entries)}")

    frames: list[Image.Image] = []
    for source_index in SOURCE_FRAME_INDICES:
        entry = frame_entries[source_index]
        rect = entry["frame"]
        source_size = (rect["w"], rect["h"])
        if source_size != SOURCE_FRAME_SIZE:
            raise ValueError(
                f"Frame {source_index} is {source_size}; expected {SOURCE_FRAME_SIZE}"
            )

        source_frame = sheet.crop(
            (
                rect["x"],
                rect["y"],
                rect["x"] + rect["w"],
                rect["y"] + rect["h"],
            )
        )
        reduced = source_frame.resize(
            RUNTIME_RESIZE,
            Image.Resampling.LANCZOS,
        )
        runtime_frame = Image.new(
            "RGBA",
            (RUNTIME_FRAME_SIZE, RUNTIME_FRAME_SIZE),
            (0, 0, 0, 0),
        )
        runtime_frame.alpha_composite(reduced, RUNTIME_OFFSET)
        frames.append(runtime_frame)

    return frames


def build_runtime_strip(frames: list[Image.Image]) -> Image.Image:
    strip = Image.new(
        "RGBA",
        (RUNTIME_FRAME_SIZE * len(frames), RUNTIME_FRAME_SIZE),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        strip.alpha_composite(frame, (index * RUNTIME_FRAME_SIZE, 0))
    return strip


def build_comparison(runtime_strip: Image.Image) -> Image.Image:
    current_strip = Image.open(CURRENT_RUNTIME).convert("RGBA")
    if current_strip.size != (1120, 112):
        raise ValueError(
            f"Current run strip is {current_strip.size}; expected (1120, 112)"
        )

    comparison = Image.new("RGBA", (1120, 280), REVIEW_BACKGROUND)
    draw = ImageDraw.Draw(comparison)
    draw.text((8, 6), "CURRENT RUN // 10 FRAMES", fill=(235, 240, 255, 255))
    comparison.alpha_composite(current_strip, (0, 22))
    draw.text(
        (8, 145),
        "LUDO V3 CLEAN GAIT // FRAMES 15-22",
        fill=(235, 240, 255, 255),
    )
    comparison.alpha_composite(runtime_strip, (0, 164))
    return comparison.resize((2240, 560), Image.Resampling.NEAREST)


def build_animation(frames: list[Image.Image]) -> None:
    gif_frames: list[Image.Image] = []
    for frame in frames:
        review_frame = Image.new(
            "RGBA",
            (RUNTIME_FRAME_SIZE, RUNTIME_FRAME_SIZE),
            REVIEW_BACKGROUND,
        )
        review_frame.alpha_composite(frame)
        gif_frames.append(review_frame.convert("RGB"))

    gif_frames[0].save(
        REVIEW_ANIMATION,
        save_all=True,
        append_images=gif_frames[1:],
        duration=round(1000 / RUNTIME_FPS),
        loop=0,
        disposal=2,
        optimize=False,
    )


def write_manifest() -> None:
    manifest = {
        "asset": "Aryn Sol-Mavi curated Ludo run loop",
        "status": "local preview candidate",
        "source_sheet": str(SOURCE_SHEET.relative_to(PROJECT_ROOT)),
        "source_metadata": str(SOURCE_METADATA.relative_to(PROJECT_ROOT)),
        "source_frames": list(SOURCE_FRAME_INDICES),
        "runtime_output": str(RUNTIME_OUTPUT.relative_to(PROJECT_ROOT)),
        "runtime_contract": {
            "frame_count": len(SOURCE_FRAME_INDICES),
            "frame_size": [RUNTIME_FRAME_SIZE, RUNTIME_FRAME_SIZE],
            "sheet_size": [
                RUNTIME_FRAME_SIZE * len(SOURCE_FRAME_INDICES),
                RUNTIME_FRAME_SIZE,
            ],
            "fps": RUNTIME_FPS,
            "source_resize": list(RUNTIME_RESIZE),
            "source_offset": list(RUNTIME_OFFSET),
        },
        "pack_emitter_anchors": list(PACK_EMITTER_ANCHORS),
        "preview_query": "aryn=ludo",
        "notes": [
            "Frames 0-5 are excluded standing lead-in frames.",
            "Frames 15-22 form a complete eight-frame gait cycle.",
            "Source frame 23 closely matches frame 15, confirming the loop closure.",
            "The malformed arm reversal in the final generated gait cycle is excluded.",
            "The existing production run remains the default asset.",
        ],
    }
    MANIFEST_OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n")


def main() -> None:
    REVIEW_DIRECTORY.mkdir(parents=True, exist_ok=True)
    RUNTIME_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    frames = load_source_frames()
    runtime_strip = build_runtime_strip(frames)
    runtime_strip.save(RUNTIME_OUTPUT, optimize=True)

    comparison = build_comparison(runtime_strip)
    comparison.save(REVIEW_COMPARISON, optimize=True)
    build_animation(frames)
    write_manifest()

    print(f"Wrote {RUNTIME_OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {REVIEW_COMPARISON.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {REVIEW_ANIMATION.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {MANIFEST_OUTPUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
