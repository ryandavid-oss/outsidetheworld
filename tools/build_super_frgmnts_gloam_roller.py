#!/usr/bin/env python3
"""Validate and build the SUPER FRGMNTS Gloam Roller enemy."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT / "Design/Super-Frgmnts/Foundry/Enemies/Gloam-Roller"
)
RAW_IMAGE = FAMILY / "Raw/gloam-roller-source-v1.png"
RAW_MANIFEST = FAMILY / "Raw/gloam-roller-source-v1.json"
RUNTIME_IMAGE = (
    ROOT / "Images/Game/Super-Frgmnts/enemy-gloam-roller-sheet-v1.png"
)
PREVIEW = FAMILY / "Reviews/gloam-roller-preview-v1.gif"
BEHAVIOR_PREVIEW = (
    FAMILY / "Reviews/gloam-roller-behavior-preview-v1.gif"
)
MANIFEST = FAMILY / "gloam-roller-runtime-v1.json"

COLUMNS = 6
ROWS = 6
FRAME_COUNT = COLUMNS * ROWS
RUNTIME_FRAME_WIDTH = 128
RUNTIME_FRAME_HEIGHT = 80
MAX_CONTENT_WIDTH = 120
MAX_CONTENT_HEIGHT = 72
ROLL_DURATION_MS = 1040
ROLL_SPEED_MULTIPLIER = 1.85


def build_behavior_preview(
    runtime_frames: list[Image.Image],
    durations: list[int],
) -> None:
    """Render a seamless patrol demo of the intended crawl/roll behavior."""

    from PIL import ImageDraw

    crawl = list(range(28))
    curl = list(range(28, 32))
    roll = [32 + index % 4 for index in range(20)]
    uncurl = list(range(31, 27, -1))
    outbound = crawl + curl + roll + uncurl
    phase_steps = (
        [4] * len(crawl)
        + [2] * len(curl)
        + [22] * len(roll)
        + [2] * len(uncurl)
    )
    start_x = 74
    centers = [start_x]
    for step in phase_steps[:-1]:
        centers.append(centers[-1] + step)

    preview_frames: list[Image.Image] = []
    preview_durations: list[int] = []
    roll_start = len(crawl) + len(curl)
    roll_end = roll_start + len(roll)
    for direction in (1, -1):
        sequence = outbound if direction == 1 else outbound
        positions = centers if direction == 1 else list(reversed(centers))
        roll_angle = 0
        for sequence_index, (frame_index, center_x) in enumerate(
            zip(sequence, positions)
        ):
            canvas = Image.new("RGBA", (720, 160), (8, 14, 28, 255))
            draw = ImageDraw.Draw(canvas)
            draw.rectangle((0, 124, 720, 159), fill=(31, 42, 52, 255))
            draw.line((0, 123, 720, 123), fill=(116, 135, 128, 255), width=2)
            for marker_x in range(12, 720, 48):
                draw.rectangle(
                    (marker_x, 135, marker_x + 20, 138),
                    fill=(49, 63, 69, 255),
                )
            draw.ellipse(
                (center_x - 44, 116, center_x + 44, 130),
                fill=(2, 5, 11, 125),
            )

            sprite = runtime_frames[frame_index]
            if direction == 1:
                sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            rolling = roll_start <= sequence_index < roll_end
            if rolling:
                # A wheel moving right rotates clockwise in screen space.
                roll_angle = (
                    roll_angle - 42 * direction
                ) % 360
                sprite = sprite.rotate(
                    roll_angle,
                    resample=Image.Resampling.NEAREST,
                    expand=False,
                )
            canvas.alpha_composite(
                sprite,
                (round(center_x - RUNTIME_FRAME_WIDTH / 2), 44),
            )
            preview_frames.append(canvas)
            preview_durations.append(durations[frame_index])

    preview_frames[0].save(
        BEHAVIOR_PREVIEW,
        save_all=True,
        append_images=preview_frames[1:],
        duration=preview_durations,
        disposal=2,
        loop=0,
        optimize=False,
    )


def main() -> None:
    metadata = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
    source = Image.open(RAW_IMAGE)
    if source.mode != "RGBA":
        raise ValueError(f"Expected RGBA source, got {source.mode}")
    records = metadata.get("frames")
    if not isinstance(records, dict):
        raise ValueError("Metadata has no frame dictionary")

    expected_keys = [f"frame_{index:03d}" for index in range(FRAME_COUNT)]
    if list(sorted(records)) != expected_keys:
        raise ValueError("Expected frame_000 through frame_035")
    ordered_records = [records[key] for key in expected_keys]
    first_rectangle = ordered_records[0]["frame"]
    source_frame_width = int(first_rectangle["w"])
    source_frame_height = int(first_rectangle["h"])
    expected_source_size = (
        source_frame_width * COLUMNS,
        source_frame_height * ROWS,
    )
    if source.size != expected_source_size:
        raise ValueError(
            f"Expected source size {expected_source_size}, got {source.size}"
        )
    if metadata.get("meta", {}).get("size") != {
        "w": source.width,
        "h": source.height,
    }:
        raise ValueError("Metadata size does not match source image")

    frames: list[Image.Image] = []
    bounds: list[tuple[int, int, int, int]] = []
    durations: list[int] = []
    contacts: dict[str, list[int]] = {
        "left": [],
        "right": [],
        "top": [],
        "bottom": [],
    }
    for index, record in enumerate(ordered_records):
        rectangle = record["frame"]
        expected_x = index % COLUMNS * source_frame_width
        expected_y = index // COLUMNS * source_frame_height
        if (
            int(rectangle["x"]) != expected_x
            or int(rectangle["y"]) != expected_y
            or int(rectangle["w"]) != source_frame_width
            or int(rectangle["h"]) != source_frame_height
        ):
            raise ValueError(f"Frame {index} breaks the 6x6 grid")
        if record.get("rotated") or record.get("trimmed"):
            raise ValueError(f"Frame {index} is rotated or trimmed")
        frame = source.crop(
            (
                expected_x,
                expected_y,
                expected_x + source_frame_width,
                expected_y + source_frame_height,
            )
        )
        bound = frame.getchannel("A").getbbox()
        if bound is None:
            raise ValueError(f"Frame {index} is blank")
        if bound[0] == 0:
            contacts["left"].append(index)
        if bound[2] == source_frame_width:
            contacts["right"].append(index)
        if bound[1] == 0:
            contacts["top"].append(index)
        if bound[3] == source_frame_height:
            contacts["bottom"].append(index)
        frames.append(frame)
        bounds.append(bound)
        durations.append(max(20, int(record.get("duration", 50))))

    active_contacts = {
        edge: indices for edge, indices in contacts.items() if indices
    }
    union = (
        min(bound[0] for bound in bounds),
        min(bound[1] for bound in bounds),
        max(bound[2] for bound in bounds),
        max(bound[3] for bound in bounds),
    )
    union_width = union[2] - union[0]
    union_height = union[3] - union[1]
    scale = min(
        MAX_CONTENT_WIDTH / union_width,
        MAX_CONTENT_HEIGHT / union_height,
    )
    content_width = max(1, round(union_width * scale))
    content_height = max(1, round(union_height * scale))

    runtime_frames: list[Image.Image] = []
    for frame in frames:
        content = frame.crop(union).resize(
            (content_width, content_height),
            Image.Resampling.NEAREST,
        )
        runtime_frame = Image.new(
            "RGBA",
            (RUNTIME_FRAME_WIDTH, RUNTIME_FRAME_HEIGHT),
            (0, 0, 0, 0),
        )
        runtime_frame.alpha_composite(
            content,
            (
                (RUNTIME_FRAME_WIDTH - content_width) // 2,
                RUNTIME_FRAME_HEIGHT - content_height - 4,
            ),
        )
        runtime_frames.append(runtime_frame)

    atlas = Image.new(
        "RGBA",
        (
            COLUMNS * RUNTIME_FRAME_WIDTH,
            ROWS * RUNTIME_FRAME_HEIGHT,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(runtime_frames):
        atlas.alpha_composite(
            frame,
            (
                index % COLUMNS * RUNTIME_FRAME_WIDTH,
                index // COLUMNS * RUNTIME_FRAME_HEIGHT,
            ),
        )

    RUNTIME_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(RUNTIME_IMAGE, optimize=True)
    runtime_frames[0].save(
        PREVIEW,
        save_all=True,
        append_images=runtime_frames[1:],
        duration=durations,
        disposal=2,
        loop=0,
        optimize=False,
    )
    build_behavior_preview(runtime_frames, durations)

    report = {
        "workingName": "Gloam Roller",
        "runtimeType": "gloamRoller",
        "status": "runtime-ready-unpopulated",
        "productionPopulation": False,
        "role": "armored ground crawler with a crawl-to-roll patrol cycle",
        "source": {
            "image": "Raw/gloam-roller-source-v1.png",
            "manifest": "Raw/gloam-roller-source-v1.json",
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": source_frame_width,
            "frameHeight": source_frame_height,
            "frameCount": FRAME_COUNT,
            "frameDurationMs": durations[0],
        },
        "validation": {
            "result": (
                "pass-with-source-warning"
                if active_contacts
                else "pass"
            ),
            "edgeContactFrames": active_contacts,
        },
        "runtime": {
            "image": str(RUNTIME_IMAGE.relative_to(ROOT)),
            "preview": str(PREVIEW.relative_to(ROOT)),
            "behaviorPreview": str(BEHAVIOR_PREVIEW.relative_to(ROOT)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": RUNTIME_FRAME_WIDTH,
            "frameHeight": RUNTIME_FRAME_HEIGHT,
            "frameCount": FRAME_COUNT,
            "loopDurationMs": sum(durations),
            "rendering": "nearest-neighbor",
            "contentSize": [content_width, content_height],
            "anchor": "ground",
            "hitboxSize": [96, 50],
            "drawSize": [120, 72],
        },
        "behavior": {
            "locomotion": "crawl-to-roll ground patrol",
            "animationRead": (
                "crawl, curl, accelerated shell roll, reverse uncurl"
            ),
            "phases": {
                "crawlFrames": [0, 27],
                "curlFrames": [28, 31],
                "rollingFrames": [32, 35],
                "uncurlFrames": [31, 28],
            },
            "behaviorCycleDurationMs": (
                28 * durations[0]
                + 4 * durations[0]
                + ROLL_DURATION_MS
                + 4 * durations[0]
            ),
            "rollDurationMs": ROLL_DURATION_MS,
            "rollSpeedMultiplier": ROLL_SPEED_MULTIPLIER,
            "rotation": (
                "distance-driven; clockwise right, counterclockwise left"
            ),
            "spawned": False,
            "combatBalance": "unassigned",
        },
    }
    MANIFEST.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
