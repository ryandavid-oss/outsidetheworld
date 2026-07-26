#!/usr/bin/env python3
"""Build mobile-safe SUPER FRGMNTS Chitin Sentinel runtime atlases."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


COLUMNS = 6
ROWS = 6
RUNTIME_FRAME_WIDTH = 114
RUNTIME_FRAME_HEIGHT = 106
SPECS = {
    "patrol": (570, 526),
    "death": (544, 482),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=sorted(SPECS))
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_frame_width, source_frame_height = SPECS[args.kind]
    source = Image.open(args.source).convert("RGBA")
    expected_size = (
        COLUMNS * source_frame_width,
        ROWS * source_frame_height,
    )
    if source.size != expected_size:
        raise SystemExit(
            f"Expected {expected_size[0]}×{expected_size[1]} for "
            f"{args.kind}, received {source.size[0]}×{source.size[1]}"
        )

    runtime = source.resize(
        (
            COLUMNS * RUNTIME_FRAME_WIDTH,
            ROWS * RUNTIME_FRAME_HEIGHT,
        ),
        Image.Resampling.NEAREST,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    runtime.save(args.output, optimize=True)
    print(
        f"Wrote {args.output} at {runtime.width}×{runtime.height} "
        f"({RUNTIME_FRAME_WIDTH}×{RUNTIME_FRAME_HEIGHT} per frame)"
    )


if __name__ == "__main__":
    main()
