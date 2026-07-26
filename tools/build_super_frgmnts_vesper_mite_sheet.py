#!/usr/bin/env python3
"""Build the mobile-safe SUPER FRGMNTS Vesper Mite runtime atlas."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


SOURCE_COLUMNS = 6
SOURCE_ROWS = 6
SOURCE_FRAME_WIDTH = 530
SOURCE_FRAME_HEIGHT = 650
RUNTIME_FRAME_WIDTH = 106
RUNTIME_FRAME_HEIGHT = 130


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Image.open(args.source).convert("RGBA")
    expected_size = (
        SOURCE_COLUMNS * SOURCE_FRAME_WIDTH,
        SOURCE_ROWS * SOURCE_FRAME_HEIGHT,
    )
    if source.size != expected_size:
        raise SystemExit(
            f"Expected {expected_size[0]}×{expected_size[1]}, "
            f"received {source.size[0]}×{source.size[1]}"
        )

    runtime = source.resize(
        (
            SOURCE_COLUMNS * RUNTIME_FRAME_WIDTH,
            SOURCE_ROWS * RUNTIME_FRAME_HEIGHT,
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
