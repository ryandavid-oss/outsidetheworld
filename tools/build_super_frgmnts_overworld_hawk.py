#!/usr/bin/env python3
"""Validate and build the ambient SUPER FRGMNTS Overworld hawk."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Sky-Wildlife/Hawk-Ludo"
)
RAW_IMAGE = FAMILY / "Raw/overworld-hawk-flight-source-v1.png"
RAW_MANIFEST = FAMILY / "Raw/overworld-hawk-flight-source-v1.json"
RUNTIME_IMAGE = (
    ROOT / "Images/Game/Super-Frgmnts/overworld-hawk-flight-sheet-v1.png"
)
PREVIEW = FAMILY / "Reviews/overworld-hawk-flight-preview-v1.gif"
MANIFEST = FAMILY / "overworld-hawk-runtime-v1.json"

COLUMNS = 5
ROWS = 5
FRAME_COUNT = COLUMNS * ROWS
RUNTIME_FRAME_WIDTH = 144
RUNTIME_FRAME_HEIGHT = 112
MAX_CONTENT_WIDTH = 136
MAX_CONTENT_HEIGHT = 104
PLAYBACK_SEQUENCE = [
    5,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    22,
    24,
]


def main() -> None:
    metadata = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
    source = Image.open(RAW_IMAGE)
    if source.mode != "RGBA":
        raise ValueError(f"Expected RGBA source, got {source.mode}")

    records = metadata.get("frames")
    if not isinstance(records, dict):
        raise ValueError("Source metadata has no frame dictionary")
    expected_keys = [f"frame_{index:03d}" for index in range(FRAME_COUNT)]
    if list(sorted(records)) != expected_keys:
        raise ValueError("Expected frame_000 through frame_024")

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
            raise ValueError(f"Frame {index} breaks the 5x5 source grid")
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
        durations.append(max(20, int(record.get("duration", 60))))

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
                (RUNTIME_FRAME_HEIGHT - content_height) // 2,
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
    playback_frames = [
        runtime_frames[index] for index in PLAYBACK_SEQUENCE
    ]
    playback_durations = [
        durations[index] for index in PLAYBACK_SEQUENCE
    ]
    playback_frames[0].save(
        PREVIEW,
        save_all=True,
        append_images=playback_frames[1:],
        duration=playback_durations,
        disposal=2,
        loop=0,
        optimize=False,
    )

    active_contacts = {
        edge: indices for edge, indices in contacts.items() if indices
    }
    report = {
        "workingName": "Overworld Hawk",
        "status": "overworld-runtime",
        "scene": "overworld",
        "role": "ambient sky wildlife",
        "hostile": False,
        "solid": False,
        "targetable": False,
        "source": {
            "image": str(RAW_IMAGE.relative_to(FAMILY)),
            "manifest": str(RAW_MANIFEST.relative_to(FAMILY)),
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
            "note": (
                "Frames 12 and 13 touch the supplied cell's bottom edge. "
                "Runtime padding prevents additional clipping but cannot "
                "reconstruct source pixels."
            ),
        },
        "runtime": {
            "image": str(RUNTIME_IMAGE.relative_to(ROOT)),
            "preview": str(PREVIEW.relative_to(ROOT)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": RUNTIME_FRAME_WIDTH,
            "frameHeight": RUNTIME_FRAME_HEIGHT,
            "atlasFrameCount": FRAME_COUNT,
            "playbackFrameCount": len(PLAYBACK_SEQUENCE),
            "playbackSequence": PLAYBACK_SEQUENCE,
            "loopDurationMs": sum(playback_durations),
            "contentSize": [content_width, content_height],
            "rendering": "nearest-neighbor",
            "anchor": "center",
            "loopTuning": (
                "Near-duplicate wings-up holds at the source loop boundary "
                "are omitted for an even flap cadence."
            ),
        },
        "behavior": {
            "direction": "alternates between right-to-left and left-to-right",
            "directionPattern": "alternate after every completed pass",
            "maxConcurrent": 1,
            "speedPixelsPerSecond": 80,
            "passGapPixels": 1400,
            "screenAltitude": 150,
            "altitudeDrift": 18,
            "collision": False,
            "friendlySeekerSafety": True,
            "reducedMotion": "static flight pose",
        },
    }
    MANIFEST.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
