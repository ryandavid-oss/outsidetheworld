#!/usr/bin/env python3
"""Validate and build the SUPER FRGMNTS Sova and Kihunter enemies."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ENEMIES = ROOT / "Design/Super-Frgmnts/Foundry/Enemies"
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"
COLUMNS = 6
ROWS = 6
FRAME_COUNT = COLUMNS * ROWS


@dataclass(frozen=True)
class EnemySpec:
    key: str
    working_name: str
    role: str
    directory: str
    runtime_filename: str
    preview_filename: str
    frame_width: int
    frame_height: int
    content_max_width: int
    content_max_height: int
    anchor: str
    hitbox: tuple[int, int]
    draw_size: tuple[int, int]
    locomotion: str


SPECS = (
    EnemySpec(
        key="sova",
        working_name="Sova",
        role="low armored ground crawler",
        directory="Sova",
        runtime_filename="enemy-sova-crawl-sheet-v1.png",
        preview_filename="sova-crawl-preview-v1.gif",
        frame_width=128,
        frame_height=80,
        content_max_width=120,
        content_max_height=72,
        anchor="ground",
        hitbox=(92, 48),
        draw_size=(116, 72),
        locomotion="ground patrol",
    ),
    EnemySpec(
        key="kihunter",
        working_name="Kihunter",
        role="winged airborne insect patrol",
        directory="Kihunter",
        runtime_filename="enemy-kihunter-flight-sheet-v1.png",
        preview_filename="kihunter-flight-preview-v1.gif",
        frame_width=112,
        frame_height=112,
        content_max_width=104,
        content_max_height=104,
        anchor="center",
        hitbox=(88, 78),
        draw_size=(118, 118),
        locomotion="flying patrol",
    ),
)


def build(spec: EnemySpec) -> dict[str, object]:
    family = ENEMIES / spec.directory
    raw_image = family / "Raw" / f"{spec.key}-source-v1.png"
    raw_manifest = family / "Raw" / f"{spec.key}-source-v1.json"
    output = PUBLIC / spec.runtime_filename
    preview = family / "Reviews" / spec.preview_filename
    runtime_manifest = family / f"{spec.key}-runtime-v1.json"

    metadata = json.loads(raw_manifest.read_text(encoding="utf-8"))
    source = Image.open(raw_image)
    if source.mode != "RGBA":
        raise ValueError(
            f"{spec.working_name}: expected RGBA source, got {source.mode}"
        )
    frames = metadata.get("frames")
    if not isinstance(frames, dict):
        raise ValueError(
            f"{spec.working_name}: metadata has no frame dictionary"
        )
    expected_keys = [f"frame_{index:03d}" for index in range(FRAME_COUNT)]
    if list(sorted(frames)) != expected_keys:
        raise ValueError(
            f"{spec.working_name}: expected frame_000..frame_035"
        )

    records = [frames[key] for key in expected_keys]
    first_rectangle = records[0]["frame"]
    source_frame_width = int(first_rectangle["w"])
    source_frame_height = int(first_rectangle["h"])
    expected_source_size = (
        source_frame_width * COLUMNS,
        source_frame_height * ROWS,
    )
    if source.size != expected_source_size:
        raise ValueError(
            f"{spec.working_name}: expected source "
            f"{expected_source_size}, got {source.size}"
        )
    if metadata.get("meta", {}).get("size") != {
        "w": source.width,
        "h": source.height,
    }:
        raise ValueError(
            f"{spec.working_name}: metadata size does not match source"
        )

    source_frames: list[Image.Image] = []
    bounds: list[tuple[int, int, int, int]] = []
    durations: list[int] = []
    edge_contacts: dict[str, list[int]] = {
        "left": [],
        "right": [],
        "top": [],
        "bottom": [],
    }
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
            raise ValueError(
                f"{spec.working_name}: frame {index} breaks the 6x6 grid"
            )
        if record.get("rotated") or record.get("trimmed"):
            raise ValueError(
                f"{spec.working_name}: frame {index} is rotated or trimmed"
            )
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
            raise ValueError(
                f"{spec.working_name}: frame {index} is blank"
            )
        if bound[0] == 0:
            edge_contacts["left"].append(index)
        if bound[2] == source_frame_width:
            edge_contacts["right"].append(index)
        if bound[1] == 0:
            edge_contacts["top"].append(index)
        if bound[3] == source_frame_height:
            edge_contacts["bottom"].append(index)
        source_frames.append(frame)
        bounds.append(bound)
        durations.append(max(20, int(record.get("duration", 50))))

    active_contacts = {
        edge: indices
        for edge, indices in edge_contacts.items()
        if indices
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
        spec.content_max_width / union_width,
        spec.content_max_height / union_height,
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
            (spec.frame_width, spec.frame_height),
            (0, 0, 0, 0),
        )
        x = (spec.frame_width - content_width) // 2
        y = (
            spec.frame_height - content_height - 4
            if spec.anchor == "ground"
            else (spec.frame_height - content_height) // 2
        )
        runtime_frame.alpha_composite(content, (x, y))
        runtime_frames.append(runtime_frame)

    atlas = Image.new(
        "RGBA",
        (
            COLUMNS * spec.frame_width,
            ROWS * spec.frame_height,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(runtime_frames):
        atlas.alpha_composite(
            frame,
            (
                index % COLUMNS * spec.frame_width,
                index // COLUMNS * spec.frame_height,
            ),
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    preview.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(output, optimize=True)
    runtime_frames[0].save(
        preview,
        save_all=True,
        append_images=runtime_frames[1:],
        duration=durations,
        disposal=2,
        loop=0,
        optimize=False,
    )

    report: dict[str, object] = {
        "workingName": spec.working_name,
        "runtimeType": spec.key,
        "status": "runtime-ready-unpopulated",
        "productionPopulation": False,
        "role": spec.role,
        "source": {
            "image": f"Raw/{spec.key}-source-v1.png",
            "manifest": f"Raw/{spec.key}-source-v1.json",
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": source_frame_width,
            "frameHeight": source_frame_height,
            "frameCount": FRAME_COUNT,
            "frameDurationMs": durations[0],
        },
        "validation": {
            "result": "pass" if not active_contacts else (
                "pass-with-source-warning"
            ),
            "edgeContactFrames": active_contacts,
        },
        "runtime": {
            "image": str(output.relative_to(ROOT)),
            "preview": str(preview.relative_to(ROOT)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": spec.frame_width,
            "frameHeight": spec.frame_height,
            "frameCount": FRAME_COUNT,
            "loopDurationMs": sum(durations),
            "rendering": "nearest-neighbor",
            "contentSize": [content_width, content_height],
            "anchor": spec.anchor,
            "hitboxSize": list(spec.hitbox),
            "drawSize": list(spec.draw_size),
        },
        "behavior": {
            "locomotion": spec.locomotion,
            "spawned": False,
        },
    }
    runtime_manifest.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> None:
    print(json.dumps([build(spec) for spec in SPECS], indent=2))


if __name__ == "__main__":
    main()
