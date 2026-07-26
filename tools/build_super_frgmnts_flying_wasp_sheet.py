#!/usr/bin/env python3
"""Build a mobile-safe runtime atlas and review GIF for the flying wasp."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


SOURCE_COLUMNS = 6
SOURCE_ROWS = 6
RUNTIME_FRAME_WIDTH = 112
RUNTIME_FRAME_HEIGHT = 86


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("preview", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata = json.loads(args.manifest.read_text())
    source = Image.open(args.source).convert("RGBA")
    frame_records = [
        metadata["frames"][key]
        for key in sorted(metadata["frames"])
    ]

    if len(frame_records) != SOURCE_COLUMNS * SOURCE_ROWS:
        raise SystemExit(f"Expected 36 frames, received {len(frame_records)}")

    source_frame_width = frame_records[0]["frame"]["w"]
    source_frame_height = frame_records[0]["frame"]["h"]
    expected_size = (
        SOURCE_COLUMNS * source_frame_width,
        SOURCE_ROWS * source_frame_height,
    )
    if source.size != expected_size:
        raise SystemExit(
            f"Expected {expected_size[0]}×{expected_size[1]}, "
            f"received {source.width}×{source.height}"
        )

    runtime_frames = []
    for record in frame_records:
        rectangle = record["frame"]
        frame = source.crop(
            (
                rectangle["x"],
                rectangle["y"],
                rectangle["x"] + rectangle["w"],
                rectangle["y"] + rectangle["h"],
            )
        )
        runtime_frames.append(
            frame.resize(
                (RUNTIME_FRAME_WIDTH, RUNTIME_FRAME_HEIGHT),
                Image.Resampling.NEAREST,
            )
        )

    runtime = Image.new(
        "RGBA",
        (
            SOURCE_COLUMNS * RUNTIME_FRAME_WIDTH,
            SOURCE_ROWS * RUNTIME_FRAME_HEIGHT,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(runtime_frames):
        runtime.alpha_composite(
            frame,
            (
                index % SOURCE_COLUMNS * RUNTIME_FRAME_WIDTH,
                index // SOURCE_COLUMNS * RUNTIME_FRAME_HEIGHT,
            ),
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.preview.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(args.output, optimize=True)

    durations = [
        max(20, int(record.get("duration", 46)))
        for record in frame_records
    ]
    runtime_frames[0].save(
        args.preview,
        save_all=True,
        append_images=runtime_frames[1:],
        duration=durations,
        disposal=2,
        loop=0,
        optimize=False,
    )
    print(
        f"Wrote {args.output} at {runtime.width}×{runtime.height} "
        f"({RUNTIME_FRAME_WIDTH}×{RUNTIME_FRAME_HEIGHT} per frame)"
    )
    print(f"Wrote {args.preview} with {len(runtime_frames)} frames")


if __name__ == "__main__":
    main()
