#!/usr/bin/env python3
"""Build compact runtime atlases for the green and purple Fragment enemies."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Foundry"
    / "Enemies"
    / "Fragment-Variants"
)
RAW = FAMILY / "Raw"
REVIEWS = FAMILY / "Reviews"
PUBLIC = ROOT / "Images" / "Game" / "Super-Frgmnts"


@dataclass(frozen=True)
class FragmentSpec:
    key: str
    source: Path
    metadata: Path
    output: Path
    preview: Path
    columns: int
    rows: int
    frame_width: int
    frame_height: int
    role: str
    animation: str


SPECS = (
    FragmentSpec(
        key="fragment-bastion-purple",
        source=RAW / "fragment-bastion-purple-source-v1.png",
        metadata=RAW / "fragment-bastion-purple-source-v1.json",
        output=PUBLIC / "enemy-fragment-bastion-purple-runtime-v1.png",
        preview=REVIEWS / "fragment-bastion-purple-preview-v1.gif",
        columns=6,
        rows=6,
        frame_width=80,
        frame_height=70,
        role="Alternates between a vulnerable hover cube and an armored spike form.",
        animation="state cycle",
    ),
    FragmentSpec(
        key="fragment-spring-green",
        source=RAW / "fragment-spring-green-source-v1.png",
        metadata=RAW / "fragment-spring-green-source-v1.json",
        output=PUBLIC / "enemy-fragment-spring-green-runtime-v1.png",
        preview=REVIEWS / "fragment-spring-green-preview-v1.gif",
        columns=5,
        rows=5,
        frame_width=80,
        frame_height=57,
        role="A compact, fast hover Fragment with a broad vertical patrol.",
        animation="continuous loop",
    ),
)


def ordered_records(metadata: dict[str, object]) -> list[dict[str, object]]:
    frames = metadata["frames"]
    if not isinstance(frames, dict):
        raise ValueError("Sprite metadata must contain a frame dictionary")
    return [frames[key] for key in sorted(frames)]


def build(spec: FragmentSpec) -> dict[str, object]:
    metadata = json.loads(spec.metadata.read_text(encoding="utf-8"))
    source = Image.open(spec.source).convert("RGBA")
    records = ordered_records(metadata)
    expected_count = spec.columns * spec.rows
    if len(records) != expected_count:
        raise ValueError(
            f"{spec.key}: expected {expected_count} frames, got {len(records)}"
        )

    first_rectangle = records[0]["frame"]
    source_frame_width = int(first_rectangle["w"])
    source_frame_height = int(first_rectangle["h"])
    expected_size = (
        source_frame_width * spec.columns,
        source_frame_height * spec.rows,
    )
    if source.size != expected_size:
        raise ValueError(
            f"{spec.key}: expected source {expected_size}, got {source.size}"
        )

    runtime_frames: list[Image.Image] = []
    durations: list[int] = []
    for record in records:
        rectangle = record["frame"]
        frame = source.crop(
            (
                int(rectangle["x"]),
                int(rectangle["y"]),
                int(rectangle["x"]) + int(rectangle["w"]),
                int(rectangle["y"]) + int(rectangle["h"]),
            )
        )
        runtime_frames.append(
            frame.resize(
                (spec.frame_width, spec.frame_height),
                Image.Resampling.LANCZOS,
            )
        )
        durations.append(max(20, int(record.get("duration", 60))))

    atlas = Image.new(
        "RGBA",
        (
            spec.columns * spec.frame_width,
            spec.rows * spec.frame_height,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(runtime_frames):
        atlas.alpha_composite(
            frame,
            (
                index % spec.columns * spec.frame_width,
                index // spec.columns * spec.frame_height,
            ),
        )

    spec.output.parent.mkdir(parents=True, exist_ok=True)
    spec.preview.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(spec.output, optimize=True)
    runtime_frames[0].save(
        spec.preview,
        save_all=True,
        append_images=runtime_frames[1:],
        duration=durations,
        disposal=2,
        loop=0,
        optimize=False,
    )

    return {
        "key": spec.key,
        "role": spec.role,
        "animation": spec.animation,
        "source": {
            "image": str(spec.source.relative_to(ROOT)),
            "metadata": str(spec.metadata.relative_to(ROOT)),
            "frameSize": [source_frame_width, source_frame_height],
        },
        "runtime": {
            "image": str(spec.output.relative_to(ROOT)),
            "preview": str(spec.preview.relative_to(ROOT)),
            "columns": spec.columns,
            "rows": spec.rows,
            "frameCount": len(runtime_frames),
            "frameSize": [spec.frame_width, spec.frame_height],
            "atlasSize": list(atlas.size),
            "durationMs": sum(durations),
        },
    }


def main() -> None:
    report = {
        "version": 1,
        "productionPopulation": True,
        "variants": [build(spec) for spec in SPECS],
    }
    manifest = FAMILY / "fragment-variants-runtime-v1.json"
    manifest.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
