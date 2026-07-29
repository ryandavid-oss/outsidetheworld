#!/usr/bin/env python3
"""Validate and build the SUPER FRGMNTS Overworld worker droid."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Outpost/Worker-Droid"
)
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"
MANIFEST = FAMILY / "worker-droid-runtime-v1.json"

COLUMNS = 5
ROWS = 5
FRAME_COUNT = COLUMNS * ROWS
RUNTIME_FRAME_WIDTH = 144
RUNTIME_FRAME_HEIGHT = 140
MAX_CONTENT_WIDTH = 136
MAX_CONTENT_HEIGHT = 132


@dataclass(frozen=True)
class AnimationSpec:
    key: str
    source_stem: str
    runtime_filename: str
    preview_filename: str
    role: str
    draw_offset: tuple[int, int]


SPECS = (
    AnimationSpec(
        key="drift",
        source_stem="worker-droid-drift-source-v1",
        runtime_filename="overworld-worker-droid-drift-sheet-v1.png",
        preview_filename="worker-droid-drift-preview-v1.gif",
        role="continuous hover-drift manipulation loop",
        draw_offset=(20, 0),
    ),
    AnimationSpec(
        key="service",
        source_stem="worker-droid-service-source-v1",
        runtime_filename="overworld-worker-droid-service-sheet-v1.png",
        preview_filename="worker-droid-service-preview-v1.gif",
        role="periodic low-hover maintenance loop with dust",
        draw_offset=(0, 0),
    ),
)


def source_paths(spec: AnimationSpec) -> tuple[Path, Path]:
    return (
        FAMILY / "Raw" / f"{spec.source_stem}.png",
        FAMILY / "Raw" / f"{spec.source_stem}.json",
    )


def edge_contacts(
    bound: tuple[int, int, int, int],
    width: int,
    height: int,
) -> list[str]:
    contacts: list[str] = []
    if bound[0] == 0:
        contacts.append("left")
    if bound[2] == width:
        contacts.append("right")
    if bound[1] == 0:
        contacts.append("top")
    if bound[3] == height:
        contacts.append("bottom")
    return contacts


def build_animation(spec: AnimationSpec) -> dict[str, object]:
    raw_image, raw_manifest = source_paths(spec)
    metadata = json.loads(raw_manifest.read_text(encoding="utf-8"))
    source = Image.open(raw_image)
    if source.mode != "RGBA":
        raise ValueError(f"{spec.key}: expected RGBA source, got {source.mode}")
    records = metadata.get("frames")
    if not isinstance(records, dict):
        raise ValueError(f"{spec.key}: metadata has no frame dictionary")

    expected_keys = [f"frame_{index:03d}" for index in range(FRAME_COUNT)]
    if list(sorted(records)) != expected_keys:
        raise ValueError(
            f"{spec.key}: expected frame_000..frame_024"
        )

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
            f"{spec.key}: expected {expected_source_size}, got {source.size}"
        )
    if metadata.get("meta", {}).get("size") != {
        "w": source.width,
        "h": source.height,
    }:
        raise ValueError(f"{spec.key}: metadata size does not match source")

    frames: list[Image.Image] = []
    bounds: list[tuple[int, int, int, int]] = []
    durations: list[int] = []
    contacts_by_edge: dict[str, list[int]] = {
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
            raise ValueError(f"{spec.key}: frame {index} breaks the 5x5 grid")
        if record.get("rotated") or record.get("trimmed"):
            raise ValueError(f"{spec.key}: frame {index} is rotated or trimmed")

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
            raise ValueError(f"{spec.key}: frame {index} is blank")
        for edge in edge_contacts(
            bound,
            source_frame_width,
            source_frame_height,
        ):
            contacts_by_edge[edge].append(index)
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

    output = PUBLIC / spec.runtime_filename
    preview = FAMILY / "Reviews" / spec.preview_filename
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

    active_contacts = {
        edge: indices
        for edge, indices in contacts_by_edge.items()
        if indices
    }
    return {
        "key": spec.key,
        "role": spec.role,
        "source": {
            "image": str(raw_image.relative_to(FAMILY)),
            "manifest": str(raw_manifest.relative_to(FAMILY)),
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
                "Boundary contact exists in the supplied source; transparent "
                "runtime padding prevents additional clipping."
                if active_contacts
                else "No source boundary contact detected."
            ),
        },
        "runtime": {
            "image": str(output.relative_to(ROOT)),
            "preview": str(preview.relative_to(ROOT)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": RUNTIME_FRAME_WIDTH,
            "frameHeight": RUNTIME_FRAME_HEIGHT,
            "frameCount": FRAME_COUNT,
            "loopDurationMs": sum(durations),
            "contentSize": [content_width, content_height],
            "rendering": "nearest-neighbor",
            "drawOffset": list(spec.draw_offset),
        },
    }


def main() -> None:
    report = {
        "workingName": "Worker Droid",
        "status": "overworld-runtime",
        "hostile": False,
        "solid": False,
        "scene": "overworld",
        "role": "ambient worker near the abandoned credit terminal",
        "animations": [build_animation(spec) for spec in SPECS],
        "behavior": {
            "driftSpeed": 26,
            "hoverAltitude": 30,
            "patrolRange": [
                "WIDTH + 980",
                "WIDTH + 1500",
            ],
            "serviceIntervalSeconds": 7.5,
            "serviceDurationSeconds": 1.75,
            "serviceDescent": 22,
            "friendlySeekerSafety": True,
        },
    }
    MANIFEST.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
