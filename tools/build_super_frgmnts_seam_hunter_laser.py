#!/usr/bin/env python3
"""Build the runtime Seam Hunter laser-eye sheet from the approved source."""

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Enemies"
    / "Tall-Gaunt-Alien"
    / "Raw"
    / "seam-hunter-laser-eyes-source-v1.png"
)
SOURCE_META = SOURCE.with_suffix(".json")
RUNTIME = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "enemy-tall-gaunt-alien-laser-eyes-sheet-v1.png"
)
REVIEW = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Enemies"
    / "Tall-Gaunt-Alien"
    / "Reviews"
    / "seam-hunter-laser-eyes-preview-v1.gif"
)

SOURCE_SIZE = (3840, 3360)
SOURCE_FRAME = (640, 560)
RUNTIME_SIZE = (960, 840)
RUNTIME_FRAME = (160, 140)
FRAME_COUNT = 36
FRAME_COLUMNS = 6


def frame_box(index: int, frame_size: tuple[int, int]) -> tuple[int, int, int, int]:
    width, height = frame_size
    column = index % FRAME_COLUMNS
    row = index // FRAME_COLUMNS
    return (
        column * width,
        row * height,
        (column + 1) * width,
        (row + 1) * height,
    )


def root_x(frame: Image.Image) -> float:
    """Measure the planted-foot midpoint while excluding the forward beam."""
    pixels = frame.load()
    body_points: list[tuple[int, int]] = []
    for y in range(RUNTIME_FRAME[1]):
        for x in range(min(132, RUNTIME_FRAME[0])):
            if pixels[x, y][3] > 32:
                body_points.append((x, y))
    if not body_points:
        return RUNTIME_FRAME[0] / 2
    bottom = max(y for _, y in body_points)
    foot_x = [
        x
        for x, y in body_points
        if y >= bottom - 5
    ]
    return (min(foot_x) + max(foot_x)) / 2


def main() -> int:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source sheet: {SOURCE}")
    if not SOURCE_META.exists():
        raise SystemExit(f"Missing source metadata: {SOURCE_META}")

    source = Image.open(SOURCE).convert("RGBA")
    if source.size != SOURCE_SIZE:
        raise SystemExit(
            f"Unexpected source size {source.size}; expected {SOURCE_SIZE}"
        )
    metadata = json.loads(SOURCE_META.read_text(encoding="utf-8"))
    frames = metadata.get("frames", {})
    if len(frames) != FRAME_COUNT:
        raise SystemExit(
            f"Unexpected frame count {len(frames)}; expected {FRAME_COUNT}"
        )
    durations = {
        frame.get("duration")
        for frame in frames.values()
    }
    if durations != {50}:
        raise SystemExit(
            f"Unexpected source frame durations: {sorted(durations)}"
        )

    unregistered = source.resize(
        RUNTIME_SIZE,
        Image.Resampling.NEAREST,
    )
    source_frames = [
        unregistered.crop(frame_box(index, RUNTIME_FRAME))
        for index in range(FRAME_COUNT)
    ]
    reference_root_x = root_x(source_frames[0])
    root_offsets = [
        round(reference_root_x - root_x(frame))
        for frame in source_frames
    ]

    # Ludo's exported recovery frames move the whole character left inside
    # their fixed cells. Register every frame to frame 0's planted foot so the
    # runtime boss does not jump forward after firing.
    runtime = Image.new("RGBA", RUNTIME_SIZE, (0, 0, 0, 0))
    registered_frames: list[Image.Image] = []
    for index, (frame, offset_x) in enumerate(
        zip(source_frames, root_offsets)
    ):
        registered = Image.new(
            "RGBA",
            RUNTIME_FRAME,
            (0, 0, 0, 0),
        )
        registered.paste(frame, (offset_x, 0), frame)
        registered_frames.append(registered)
        runtime.paste(
            registered,
            (
                (index % FRAME_COLUMNS) * RUNTIME_FRAME[0],
                (index // FRAME_COLUMNS) * RUNTIME_FRAME[1],
            ),
            registered,
        )

    RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(RUNTIME, optimize=True)

    bottom_pads: list[int] = []
    preview_frames: list[Image.Image] = []
    for index in range(FRAME_COUNT):
        frame = registered_frames[index]
        bounds = frame.getchannel("A").getbbox()
        bottom_pads.append(
            RUNTIME_FRAME[1] - bounds[3] if bounds else 0
        )
        preview_frames.append(
            frame.resize((480, 420), Image.Resampling.NEAREST)
        )

    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    preview_frames[0].save(
        REVIEW,
        save_all=True,
        append_images=preview_frames[1:],
        duration=50,
        loop=0,
        disposal=2,
        optimize=False,
    )

    print(f"{RUNTIME.relative_to(ROOT)} {runtime.width}x{runtime.height}")
    print(f"{REVIEW.relative_to(ROOT)}")
    print("root x offsets:", ", ".join(map(str, root_offsets)))
    print("bottom pads:", ", ".join(map(str, bottom_pads)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
