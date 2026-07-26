#!/usr/bin/env python3
"""Normalize the July 26 creature and camp-life animation intake."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"
MONSTER = ROOT / "Design/Super-Frgmnts/Foundry/Enemies/Tall-Gaunt-Alien"
DOG = ROOT / "Design/Super-Frgmnts/Overworld/Phase-3/Outpost/Dog-Ludo"
ARYN_FLEET = ROOT / "Design/Super-Frgmnts/Characters/Aryn-Fleet-Apparel"


@dataclass(frozen=True)
class AnimationSpec:
    name: str
    source: Path
    manifest: Path
    output: Path
    preview: Path
    columns: int
    rows: int
    runtime_width: int
    runtime_height: int


SPECS = (
    AnimationSpec(
        name="monster walk",
        source=MONSTER / "Raw/monster-walk-source-v1.png",
        manifest=MONSTER / "Raw/monster-walk-source-v1.json",
        output=PUBLIC / "enemy-tall-gaunt-alien-walk-sheet-v1.png",
        preview=MONSTER / "Reviews/monster-walk-preview-v1.gif",
        columns=6,
        rows=6,
        runtime_width=128,
        runtime_height=128,
    ),
    AnimationSpec(
        name="monster attack",
        source=MONSTER / "Raw/monster-attack-source-v1.png",
        manifest=MONSTER / "Raw/monster-attack-source-v1.json",
        output=PUBLIC / "enemy-tall-gaunt-alien-attack-sheet-v1.png",
        preview=MONSTER / "Reviews/monster-attack-preview-v1.gif",
        columns=5,
        rows=5,
        runtime_width=160,
        runtime_height=128,
    ),
    AnimationSpec(
        name="camp dog walk",
        source=DOG / "Raw/camp-dog-walk-source-v1.png",
        manifest=DOG / "Raw/camp-dog-walk-source-v1.json",
        output=PUBLIC / "veyra-camp-dog-walk-sheet-v3.png",
        preview=DOG / "Reviews/camp-dog-walk-preview-v3.gif",
        columns=6,
        rows=6,
        runtime_width=100,
        runtime_height=80,
    ),
    AnimationSpec(
        name="camp dog sniff",
        source=DOG / "Raw/camp-dog-sniff-source-v1.png",
        manifest=DOG / "Raw/camp-dog-sniff-source-v1.json",
        output=PUBLIC / "veyra-camp-dog-sniff-sheet-v3.png",
        preview=DOG / "Reviews/camp-dog-sniff-preview-v3.gif",
        columns=4,
        rows=4,
        runtime_width=100,
        runtime_height=80,
    ),
    AnimationSpec(
        name="Aryn Fleet-apparel walk",
        source=ARYN_FLEET / "Raw/aryn-fleet-apparel-walk-source-v1.png",
        manifest=ARYN_FLEET / "Raw/aryn-fleet-apparel-walk-source-v1.json",
        output=PUBLIC / "aryn-fleet-apparel-walk-sheet-v1.png",
        preview=ARYN_FLEET / "Reviews/aryn-fleet-apparel-walk-preview-v1.gif",
        columns=5,
        rows=5,
        runtime_width=68,
        runtime_height=116,
    ),
)


def build(spec: AnimationSpec) -> dict[str, object]:
    metadata = json.loads(spec.manifest.read_text())
    source = Image.open(spec.source).convert("RGBA")
    records = [metadata["frames"][key] for key in sorted(metadata["frames"])]
    expected_count = spec.columns * spec.rows
    if len(records) != expected_count:
        raise ValueError(
            f"{spec.name}: expected {expected_count} frames, got {len(records)}"
        )

    first = records[0]["frame"]
    expected_size = (first["w"] * spec.columns, first["h"] * spec.rows)
    if source.size != expected_size:
        raise ValueError(
            f"{spec.name}: expected source {expected_size}, got {source.size}"
        )

    frames: list[Image.Image] = []
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
        frame = frame.resize(
            (spec.runtime_width, spec.runtime_height),
            Image.Resampling.NEAREST,
        )
        frames.append(frame)

    atlas = Image.new(
        "RGBA",
        (
            spec.columns * spec.runtime_width,
            spec.rows * spec.runtime_height,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(frames):
        atlas.alpha_composite(
            frame,
            (
                index % spec.columns * spec.runtime_width,
                index // spec.columns * spec.runtime_height,
            ),
        )

    spec.output.parent.mkdir(parents=True, exist_ok=True)
    spec.preview.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(spec.output, optimize=True)
    durations = [
        max(20, int(record.get("duration", 58)))
        for record in records
    ]
    frames[0].save(
        spec.preview,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        disposal=2,
        loop=0,
        optimize=False,
    )
    return {
        "name": spec.name,
        "frames": len(frames),
        "frame_size": [spec.runtime_width, spec.runtime_height],
        "atlas_size": list(atlas.size),
        "duration_ms": sum(durations),
        "output": str(spec.output.relative_to(ROOT)),
        "preview": str(spec.preview.relative_to(ROOT)),
    }


def main() -> None:
    report = [build(spec) for spec in SPECS]
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
