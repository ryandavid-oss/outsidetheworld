#!/usr/bin/env python3
"""Validate and build the SUPER FRGMNTS Skree runtime atlas."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "Design/Super-Frgmnts/Foundry/Enemies/Skree"
RAW_IMAGE = FAMILY / "Raw/skree-source-v1.png"
RAW_MANIFEST = FAMILY / "Raw/skree-source-v1.json"
RUNTIME_IMAGE = (
    ROOT / "Images/Game/Super-Frgmnts/enemy-skree-walk-sheet-v1.png"
)
PREVIEW = FAMILY / "Reviews/skree-walk-preview-v1.gif"
RUNTIME_MANIFEST = FAMILY / "skree-runtime-v1.json"

COLUMNS = 5
ROWS = 5
FRAME_COUNT = COLUMNS * ROWS
RUNTIME_FRAME_WIDTH = 160
RUNTIME_FRAME_HEIGHT = 144
HORIZONTAL_PADDING = 4
VERTICAL_PADDING = 2


def ordered_records(metadata: dict[str, object]) -> list[dict[str, object]]:
    frames = metadata.get("frames")
    if not isinstance(frames, dict):
        raise ValueError("Skree metadata must contain a frame dictionary")
    expected_keys = [f"frame_{index:03d}" for index in range(FRAME_COUNT)]
    if list(sorted(frames)) != expected_keys:
        raise ValueError("Skree metadata does not contain frame_000..frame_024")
    return [frames[key] for key in expected_keys]


def build() -> dict[str, object]:
    metadata = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
    source = Image.open(RAW_IMAGE).convert("RGBA")
    records = ordered_records(metadata)

    if len(records) != FRAME_COUNT:
        raise ValueError(
            f"Skree: expected {FRAME_COUNT} frames, got {len(records)}"
        )

    first_rectangle = records[0]["frame"]
    source_frame_width = int(first_rectangle["w"])
    source_frame_height = int(first_rectangle["h"])
    expected_source_size = (
        source_frame_width * COLUMNS,
        source_frame_height * ROWS,
    )
    if source.size != expected_source_size:
        raise ValueError(
            f"Skree: expected source {expected_source_size}, got {source.size}"
        )
    if metadata.get("meta", {}).get("size") != {
        "w": source.width,
        "h": source.height,
    }:
        raise ValueError("Skree metadata size does not match the source image")

    source_frames: list[Image.Image] = []
    bounds: list[tuple[int, int, int, int]] = []
    durations: list[int] = []
    right_edge_contact_frames: list[int] = []

    for index, record in enumerate(records):
        rectangle = record["frame"]
        expected_x = index % COLUMNS * source_frame_width
        expected_y = index // COLUMNS * source_frame_height
        if (
            int(rectangle["x"]) != expected_x
            or int(rectangle["y"]) != expected_y
            or int(rectangle["w"]) != source_frame_width
            or int(rectangle["h"]) != source_frame_height
        ):
            raise ValueError(f"Skree frame {index} is outside the 5x5 grid")
        if record.get("rotated") or record.get("trimmed"):
            raise ValueError(f"Skree frame {index} is rotated or trimmed")

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
            raise ValueError(f"Skree frame {index} is blank")
        if bound[2] == source_frame_width:
            right_edge_contact_frames.append(index)
        source_frames.append(frame)
        bounds.append(bound)
        durations.append(max(20, int(record.get("duration", 53))))

    union = (
        min(bound[0] for bound in bounds),
        min(bound[1] for bound in bounds),
        max(bound[2] for bound in bounds),
        max(bound[3] for bound in bounds),
    )
    union_width = union[2] - union[0]
    union_height = union[3] - union[1]
    content_max_width = RUNTIME_FRAME_WIDTH - HORIZONTAL_PADDING * 2
    content_max_height = RUNTIME_FRAME_HEIGHT - VERTICAL_PADDING * 2
    scale = min(
        content_max_width / union_width,
        content_max_height / union_height,
    )
    content_width = max(1, round(union_width * scale))
    content_height = max(1, round(union_height * scale))

    runtime_frames: list[Image.Image] = []
    for frame in source_frames:
        content = frame.crop(union).resize(
            (content_width, content_height),
            Image.Resampling.NEAREST,
        )
        runtime_frame = Image.new(
            "RGBA",
            (RUNTIME_FRAME_WIDTH, RUNTIME_FRAME_HEIGHT),
            (0, 0, 0, 0),
        )
        x = (RUNTIME_FRAME_WIDTH - content_width) // 2
        y = RUNTIME_FRAME_HEIGHT - VERTICAL_PADDING - content_height
        runtime_frame.alpha_composite(content, (x, y))
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

    report: dict[str, object] = {
        "workingName": "Skree",
        "runtimeType": "skree",
        "status": "runtime-ready-unpopulated",
        "productionPopulation": False,
        "role": "large ground patrol",
        "source": {
            "image": "Raw/skree-source-v1.png",
            "manifest": "Raw/skree-source-v1.json",
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": source_frame_width,
            "frameHeight": source_frame_height,
            "frameCount": FRAME_COUNT,
            "frameDurationMs": durations[0],
        },
        "validation": {
            "result": "pass-with-source-warning",
            "warning": (
                "The supplied artwork already touches the right frame boundary "
                "in 19 frames; runtime padding prevents additional clipping."
            ),
            "rightEdgeContactFrames": right_edge_contact_frames,
        },
        "runtime": {
            "image": str(RUNTIME_IMAGE.relative_to(ROOT)),
            "preview": str(PREVIEW.relative_to(ROOT)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": RUNTIME_FRAME_WIDTH,
            "frameHeight": RUNTIME_FRAME_HEIGHT,
            "frameCount": FRAME_COUNT,
            "loopDurationMs": sum(durations),
            "rendering": "nearest-neighbor",
            "contentSize": [content_width, content_height],
            "anchor": "ground",
            "drawOffset": [25, 0],
            "hitboxSize": [92, 120],
        },
        "behavior": {
            "locomotion": "ground patrol",
            "spawned": False,
        },
    }
    RUNTIME_MANIFEST.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    print(json.dumps(build(), indent=2))


if __name__ == "__main__":
    main()
