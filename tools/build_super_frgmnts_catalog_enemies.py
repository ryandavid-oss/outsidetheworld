#!/usr/bin/env python3
"""Import and normalize the remaining SUPER FRGMNTS enemy catalog."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"
ENEMIES = ROOT / "Design/Super-Frgmnts/Foundry/Enemies"
DOWNLOADS = Path("/Users/rylee/Downloads")
COLUMNS = 6
ROWS = 6
RUNTIME_FRAME_SIZE = 112


@dataclass(frozen=True)
class EnemySpec:
    key: str
    display_name: str
    role: str
    source_directory: str
    source_stem: str
    repository_directory: str
    runtime_filename: str
    preview_filename: str
    content_height: int
    anchor: str


SPECS = (
    EnemySpec(
        key="core-leech",
        display_name="Core Leech",
        role="slow hovering parasite with a broad vertical drift",
        source_directory=(
            "A-full-body-view-of-a-hovering-parasitic-alien-pre-"
            "max-px-frames-36-rows-6-cols-6-2"
        ),
        source_stem=(
            "A-full-body-view-of-a-hovering-parasitic-alien-pre-"
            "max-px-frames-36-rows-6-cols-6"
        ),
        repository_directory="Core-Leech",
        runtime_filename="enemy-core-leech-hover-sheet-v1.png",
        preview_filename="core-leech-hover-preview-v1.gif",
        content_height=104,
        anchor="center",
    ),
    EnemySpec(
        key="vesper-flare",
        display_name="Vesper Flare",
        role="fast airborne thermal hazard with an erratic hover",
        source_directory=(
            "A-complete-view-of-a-magical-flame-entity-in-a-16--"
            "max-px-frames-36-rows-6-cols-6-2"
        ),
        source_stem=(
            "A-complete-view-of-a-magical-flame-entity-in-a-16--"
            "max-px-frames-36-rows-6-cols-6"
        ),
        repository_directory="Vesper-Flare",
        runtime_filename="enemy-vesper-flare-hover-sheet-v1.png",
        preview_filename="vesper-flare-hover-preview-v1.gif",
        content_height=104,
        anchor="center",
    ),
    EnemySpec(
        key="pale-watcher",
        display_name="Pale Watcher",
        role="tall ground stalker guarding the Uplink approach",
        source_directory=(
            "A-complete-front-facing-view-of-a-tall-symmetrical-"
            "max-px-frames-36-rows-6-cols-6"
        ),
        source_stem=(
            "A-complete-front-facing-view-of-a-tall-symmetrical-"
            "max-px-frames-36-rows-6-cols-6"
        ),
        repository_directory="Pale-Watcher",
        runtime_filename="enemy-pale-watcher-stalk-sheet-v1.png",
        preview_filename="pale-watcher-stalk-preview-v1.gif",
        content_height=106,
        anchor="ground",
    ),
)


def source_paths(spec: EnemySpec) -> tuple[Path, Path]:
    directory = DOWNLOADS / spec.source_directory
    return (
        directory / f"{spec.source_stem}.png",
        directory / f"{spec.source_stem}.json",
    )


def repository_paths(spec: EnemySpec) -> tuple[Path, Path, Path, Path, Path]:
    directory = ENEMIES / spec.repository_directory
    raw = directory / "Raw"
    reviews = directory / "Reviews"
    return (
        raw / f"{spec.key}-source-v1.png",
        raw / f"{spec.key}-source-v1.json",
        PUBLIC / spec.runtime_filename,
        reviews / spec.preview_filename,
        directory / f"{spec.key}-runtime-v1.json",
    )


def import_sources(spec: EnemySpec) -> tuple[Path, Path]:
    source_image, source_manifest = source_paths(spec)
    raw_image, raw_manifest, _, _, _ = repository_paths(spec)
    raw_image.parent.mkdir(parents=True, exist_ok=True)

    if not raw_image.exists():
        if not source_image.exists():
            raise FileNotFoundError(source_image)
        shutil.copy2(source_image, raw_image)
    if not raw_manifest.exists():
        if not source_manifest.exists():
            raise FileNotFoundError(source_manifest)
        shutil.copy2(source_manifest, raw_manifest)
    return raw_image, raw_manifest


def build(spec: EnemySpec) -> dict[str, object]:
    raw_image, raw_manifest = import_sources(spec)
    _, _, output, preview, report_path = repository_paths(spec)
    metadata = json.loads(raw_manifest.read_text())
    source = Image.open(raw_image).convert("RGBA")
    records = [metadata["frames"][key] for key in sorted(metadata["frames"])]
    if len(records) != COLUMNS * ROWS:
        raise ValueError(
            f"{spec.display_name}: expected 36 frames, got {len(records)}"
        )

    first = records[0]["frame"]
    expected_size = (first["w"] * COLUMNS, first["h"] * ROWS)
    if source.size != expected_size:
        raise ValueError(
            f"{spec.display_name}: expected {expected_size}, got {source.size}"
        )

    source_frames: list[Image.Image] = []
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
            raise ValueError(f"{spec.display_name}: blank source frame")
        source_frames.append(frame)
        bounds.append(bound)

    union = (
        min(bound[0] for bound in bounds),
        min(bound[1] for bound in bounds),
        max(bound[2] for bound in bounds),
        max(bound[3] for bound in bounds),
    )
    union_width = union[2] - union[0]
    union_height = union[3] - union[1]
    scale = spec.content_height / union_height
    content_width = max(1, round(union_width * scale))
    if content_width > RUNTIME_FRAME_SIZE - 8:
        scale = (RUNTIME_FRAME_SIZE - 8) / union_width
        content_width = RUNTIME_FRAME_SIZE - 8
    content_height = max(1, round(union_height * scale))

    runtime_frames: list[Image.Image] = []
    for source_frame in source_frames:
        cropped = source_frame.crop(union).resize(
            (content_width, content_height),
            Image.Resampling.NEAREST,
        )
        runtime_frame = Image.new(
            "RGBA",
            (RUNTIME_FRAME_SIZE, RUNTIME_FRAME_SIZE),
            (0, 0, 0, 0),
        )
        x = (RUNTIME_FRAME_SIZE - content_width) // 2
        y = (
            RUNTIME_FRAME_SIZE - content_height - 4
            if spec.anchor == "ground"
            else (RUNTIME_FRAME_SIZE - content_height) // 2
        )
        runtime_frame.alpha_composite(cropped, (x, y))
        runtime_frames.append(runtime_frame)

    atlas = Image.new(
        "RGBA",
        (
            COLUMNS * RUNTIME_FRAME_SIZE,
            ROWS * RUNTIME_FRAME_SIZE,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(runtime_frames):
        atlas.alpha_composite(
            frame,
            (
                index % COLUMNS * RUNTIME_FRAME_SIZE,
                index // COLUMNS * RUNTIME_FRAME_SIZE,
            ),
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    preview.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(output, optimize=True)
    durations = [
        max(20, int(record.get("duration", 53)))
        for record in records
    ]
    runtime_frames[0].save(
        preview,
        save_all=True,
        append_images=runtime_frames[1:],
        duration=durations,
        disposal=2,
        loop=0,
        optimize=False,
    )

    report = {
        "workingName": spec.display_name,
        "status": "episode-01-beta",
        "productionPopulation": True,
        "role": spec.role,
        "source": {
            "image": str(raw_image.relative_to(raw_image.parent.parent)),
            "manifest": str(raw_manifest.relative_to(raw_manifest.parent.parent)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": first["w"],
            "frameHeight": first["h"],
            "frameCount": len(records),
        },
        "runtime": {
            "image": str(output.relative_to(ROOT)),
            "preview": str(preview.relative_to(ROOT)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": RUNTIME_FRAME_SIZE,
            "frameHeight": RUNTIME_FRAME_SIZE,
            "frameCount": len(runtime_frames),
            "loopDurationMs": sum(durations),
            "rendering": "nearest-neighbor",
            "contentSize": [content_width, content_height],
            "anchor": spec.anchor,
        },
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    reports = [build(spec) for spec in SPECS]
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
