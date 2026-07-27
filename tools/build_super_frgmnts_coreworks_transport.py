#!/usr/bin/env python3
"""Normalize the Coreworks surface transport for SUPER FRGMNTS."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"
DESIGN = ROOT / "Design/Super-Frgmnts/Overworld/Coreworks-Transport"
RAW = DESIGN / "Raw"
REVIEWS = DESIGN / "Reviews"
RUNTIME_FRAME_WIDTH = 208
RUNTIME_FRAME_HEIGHT = 240
CONTENT_WIDTH = 198
BOTTOM_PADDING = 8


@dataclass(frozen=True)
class TransportSequence:
    key: str
    source_image: Path
    source_manifest: Path
    columns: int
    rows: int
    expected_frames: int
    runtime_filename: str
    preview_filename: str


SEQUENCES = (
    TransportSequence(
        key="idle",
        source_image=Path(
            "/Users/rylee/.codex/attachments/"
            "3a6758a0-3b59-4f06-9a9c-dd176cad331a/"
            "A-full-body-side-scrolling-view-of-a-Sci-Fi-transp-"
            "max-px-frames-36-rows-6-cols-6.png"
        ),
        source_manifest=Path(
            "/Users/rylee/.codex/attachments/"
            "8d996365-7f19-4764-ae19-c7dfdc51794d/"
            "A-full-body-side-scrolling-view-of-a-Sci-Fi-transp-"
            "max-px-frames-36-rows-6-cols-6.json"
        ),
        columns=6,
        rows=6,
        expected_frames=36,
        runtime_filename="coreworks-transport-idle-sheet-v1.png",
        preview_filename="coreworks-transport-idle-preview-v1.gif",
    ),
    TransportSequence(
        key="activate",
        source_image=Path(
            "/Users/rylee/.codex/attachments/"
            "a3dbdd17-c4d8-4f71-8977-5867de575b63/"
            "A-full-body-side-scrolling-view-of-a-Sci-Fi-transp-"
            "max-px-frames-25-rows-5-cols-5.png"
        ),
        source_manifest=Path(
            "/Users/rylee/.codex/attachments/"
            "56185e10-4d7b-4b54-b1ee-18d8fc68e76f/"
            "A-full-body-side-scrolling-view-of-a-Sci-Fi-transp-"
            "max-px-frames-25-rows-5-cols-5.json"
        ),
        columns=5,
        rows=5,
        expected_frames=25,
        runtime_filename="coreworks-transport-activate-sheet-v1.png",
        preview_filename="coreworks-transport-activate-preview-v1.gif",
    ),
)


def import_source(sequence: TransportSequence) -> tuple[Path, Path]:
    RAW.mkdir(parents=True, exist_ok=True)
    raw_image = RAW / f"coreworks-transport-{sequence.key}-source-v1.png"
    raw_manifest = RAW / f"coreworks-transport-{sequence.key}-source-v1.json"
    if not raw_image.exists():
        shutil.copy2(sequence.source_image, raw_image)
    if not raw_manifest.exists():
        shutil.copy2(sequence.source_manifest, raw_manifest)
    return raw_image, raw_manifest


def normalize(sequence: TransportSequence) -> dict[str, object]:
    raw_image_path, raw_manifest_path = import_source(sequence)
    source = Image.open(raw_image_path).convert("RGBA")
    source_manifest = json.loads(raw_manifest_path.read_text())
    records = [
        source_manifest["frames"][key]
        for key in sorted(source_manifest["frames"])
    ]
    if len(records) != sequence.expected_frames:
        raise ValueError(
            f"{sequence.key}: expected {sequence.expected_frames} frames, "
            f"got {len(records)}"
        )

    frames: list[Image.Image] = []
    bounds: list[tuple[int, int, int, int]] = []
    for record in records:
        rectangle = record["frame"]
        frame = source.crop(
            (
                rectangle["x"],
                rectangle["y"],
                rectangle["x"] + rectangle["w"],
                rectangle["y"] + rectangle["h"],
            )
        )
        bound = frame.getbbox()
        if bound is None:
            raise ValueError(f"{sequence.key}: blank source frame")
        frames.append(frame)
        bounds.append(bound)

    union = (
        min(bound[0] for bound in bounds),
        min(bound[1] for bound in bounds),
        max(bound[2] for bound in bounds),
        max(bound[3] for bound in bounds),
    )
    union_width = union[2] - union[0]
    union_height = union[3] - union[1]
    content_height = round(union_height * CONTENT_WIDTH / union_width)
    if content_height > RUNTIME_FRAME_HEIGHT - BOTTOM_PADDING:
        content_height = RUNTIME_FRAME_HEIGHT - BOTTOM_PADDING
        content_width = round(union_width * content_height / union_height)
    else:
        content_width = CONTENT_WIDTH

    runtime_frames: list[Image.Image] = []
    for source_frame in frames:
        content = source_frame.crop(union).resize(
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
                RUNTIME_FRAME_HEIGHT - BOTTOM_PADDING - content_height,
            ),
        )
        runtime_frames.append(runtime_frame)

    atlas = Image.new(
        "RGBA",
        (
            sequence.columns * RUNTIME_FRAME_WIDTH,
            sequence.rows * RUNTIME_FRAME_HEIGHT,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(runtime_frames):
        atlas.alpha_composite(
            frame,
            (
                index % sequence.columns * RUNTIME_FRAME_WIDTH,
                index // sequence.columns * RUNTIME_FRAME_HEIGHT,
            ),
        )

    PUBLIC.mkdir(parents=True, exist_ok=True)
    REVIEWS.mkdir(parents=True, exist_ok=True)
    runtime_path = PUBLIC / sequence.runtime_filename
    preview_path = REVIEWS / sequence.preview_filename
    atlas.save(runtime_path, optimize=True)
    durations = [
        max(20, int(record.get("duration", 50)))
        for record in records
    ]
    runtime_frames[0].save(
        preview_path,
        save_all=True,
        append_images=runtime_frames[1:],
        duration=durations,
        disposal=2,
        loop=0,
        optimize=False,
    )

    return {
        "sequence": sequence.key,
        "runtime": str(runtime_path.relative_to(ROOT)),
        "review": str(preview_path.relative_to(ROOT)),
        "sourceAtlas": list(source.size),
        "sourceFrame": [
            records[0]["frame"]["w"],
            records[0]["frame"]["h"],
        ],
        "sourceUnion": list(union),
        "runtimeAtlas": list(atlas.size),
        "runtimeFrame": [
            RUNTIME_FRAME_WIDTH,
            RUNTIME_FRAME_HEIGHT,
        ],
        "content": [content_width, content_height],
        "columns": sequence.columns,
        "rows": sequence.rows,
        "frames": len(records),
        "frameDurationMs": durations[0],
        "sequenceDurationMs": sum(durations),
        "alpha": "preserved",
        "sampling": "nearest-neighbor",
        "anchor": "bottom-center",
    }


def main() -> None:
    reports = [normalize(sequence) for sequence in SEQUENCES]
    manifest = {
        "name": "Coreworks Surface Transport",
        "status": "episode-01-runtime",
        "behavior": (
            "Idle deck loops while online. Stepping onto its upper deck "
            "plays the one-shot vortex sequence, fades Aryn, and hands off "
            "to The Shard Foundry."
        ),
        "runtimeFrame": [
            RUNTIME_FRAME_WIDTH,
            RUNTIME_FRAME_HEIGHT,
        ],
        "sequences": reports,
    }
    manifest_path = DESIGN / "coreworks-transport-runtime-v1.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
