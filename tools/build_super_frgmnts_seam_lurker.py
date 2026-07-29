#!/usr/bin/env python3
"""Validate and build the SUPER FRGMNTS Seam Lurker crawl asset."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "Design/Super-Frgmnts/Foundry/Enemies/Seam-Lurker"
RAW_IMAGE = FAMILY / "Raw/seam-lurker-crawl-source-v1.png"
RAW_MANIFEST = FAMILY / "Raw/seam-lurker-crawl-source-v1.json"
RUNTIME_IMAGE = (
    ROOT / "Images/Game/Super-Frgmnts/enemy-seam-lurker-crawl-sheet-v1.png"
)
PREVIEW = FAMILY / "Reviews/seam-lurker-crawl-preview-v1.gif"
BEHAVIOR_PREVIEW = FAMILY / "Reviews/seam-lurker-ceiling-preview-v1.gif"
MANIFEST = FAMILY / "seam-lurker-runtime-v1.json"

COLUMNS = 5
ROWS = 5
FRAME_COUNT = COLUMNS * ROWS
RUNTIME_FRAME_WIDTH = 128
RUNTIME_FRAME_HEIGHT = 64
MAX_CONTENT_WIDTH = 120
MAX_CONTENT_HEIGHT = 56
CEILING_PADDING = 4
NEAR_EDGE_THRESHOLD = 2


def build_behavior_preview(
    runtime_frames: list[Image.Image],
    durations: list[int],
) -> None:
    """Show the normalized creature patrolling a ceiling in both directions."""

    preview_frames: list[Image.Image] = []
    preview_durations: list[int] = []
    left_positions = [
        round(642 - index * (564 / (FRAME_COUNT - 1)))
        for index in range(FRAME_COUNT)
    ]
    for direction in (-1, 1):
        positions = (
            left_positions
            if direction == -1
            else list(reversed(left_positions))
        )
        for frame_index, center_x in enumerate(positions):
            canvas = Image.new("RGBA", (720, 144), (8, 14, 28, 255))
            draw = ImageDraw.Draw(canvas)
            draw.rectangle((0, 0, 719, 30), fill=(31, 42, 52, 255))
            draw.line((0, 31, 719, 31), fill=(116, 135, 128, 255), width=2)
            for marker_x in range(12, 720, 48):
                draw.rectangle(
                    (marker_x, 12, marker_x + 20, 15),
                    fill=(49, 63, 69, 255),
                )
            draw.ellipse(
                (center_x - 42, 27, center_x + 42, 37),
                fill=(2, 5, 11, 140),
            )

            sprite = runtime_frames[frame_index]
            if direction == 1:
                sprite = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            canvas.alpha_composite(
                sprite,
                (
                    round(center_x - RUNTIME_FRAME_WIDTH / 2),
                    28,
                ),
            )
            preview_frames.append(canvas)
            preview_durations.append(durations[frame_index])

    preview_frames[0].save(
        BEHAVIOR_PREVIEW,
        save_all=True,
        append_images=preview_frames[1:],
        duration=preview_durations,
        disposal=2,
        loop=0,
        optimize=False,
    )


def main() -> None:
    metadata = json.loads(RAW_MANIFEST.read_text(encoding="utf-8"))
    source = Image.open(RAW_IMAGE)
    if source.mode != "RGBA":
        raise ValueError(f"Expected RGBA source, got {source.mode}")
    records = metadata.get("frames")
    if not isinstance(records, dict):
        raise ValueError("Metadata has no frame dictionary")

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
    near_edges: dict[str, list[int]] = {
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
            raise ValueError(f"Frame {index} breaks the 5x5 grid")
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
        distances = {
            "left": bound[0],
            "right": source_frame_width - bound[2],
            "top": bound[1],
            "bottom": source_frame_height - bound[3],
        }
        for edge, distance in distances.items():
            if distance == 0:
                contacts[edge].append(index)
            if distance <= NEAR_EDGE_THRESHOLD:
                near_edges[edge].append(index)
        frames.append(frame)
        bounds.append(bound)
        durations.append(max(20, int(record.get("duration", 50))))

    active_contacts = {
        edge: indices for edge, indices in contacts.items() if indices
    }
    active_near_edges = {
        edge: indices for edge, indices in near_edges.items() if indices
    }
    max_width = max(bound[2] - bound[0] for bound in bounds)
    max_height = max(bound[3] - bound[1] for bound in bounds)
    scale = min(
        MAX_CONTENT_WIDTH / max_width,
        MAX_CONTENT_HEIGHT / max_height,
    )

    runtime_frames: list[Image.Image] = []
    for frame, bound in zip(frames, bounds):
        source_content = frame.crop(bound)
        content = source_content.resize(
            (
                max(1, round(source_content.width * scale)),
                max(1, round(source_content.height * scale)),
            ),
            Image.Resampling.NEAREST,
        ).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        runtime_frame = Image.new(
            "RGBA",
            (RUNTIME_FRAME_WIDTH, RUNTIME_FRAME_HEIGHT),
            (0, 0, 0, 0),
        )
        runtime_frame.alpha_composite(
            content,
            (
                (RUNTIME_FRAME_WIDTH - content.width) // 2,
                CEILING_PADDING,
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
    runtime_frames[0].save(
        PREVIEW,
        save_all=True,
        append_images=runtime_frames[1:],
        duration=durations,
        disposal=2,
        loop=0,
        optimize=False,
    )
    build_behavior_preview(runtime_frames, durations)

    report = {
        "workingName": "Seam Lurker",
        "runtimeType": "seamLurker",
        "status": "runtime-ready-unpopulated",
        "productionPopulation": False,
        "role": "ceiling patrol and future drop ambusher",
        "source": {
            "image": "Raw/seam-lurker-crawl-source-v1.png",
            "manifest": "Raw/seam-lurker-crawl-source-v1.json",
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": source_frame_width,
            "frameHeight": source_frame_height,
            "frameCount": FRAME_COUNT,
            "frameDurationMs": durations[0],
            "orientation": "ground-facing",
        },
        "validation": {
            "result": (
                "pass-with-source-warning"
                if active_contacts or active_near_edges
                else "pass"
            ),
            "edgeContactFrames": active_contacts,
            "nearEdgeThresholdPixels": NEAR_EDGE_THRESHOLD,
            "nearEdgeFrames": active_near_edges,
            "warning": (
                "Source silhouettes approach cell edges but do not touch them; "
                "the runtime derivative adds padding without reconstructing art."
            ),
        },
        "runtime": {
            "image": str(RUNTIME_IMAGE.relative_to(ROOT)),
            "preview": str(PREVIEW.relative_to(ROOT)),
            "behaviorPreview": str(BEHAVIOR_PREVIEW.relative_to(ROOT)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": RUNTIME_FRAME_WIDTH,
            "frameHeight": RUNTIME_FRAME_HEIGHT,
            "frameCount": FRAME_COUNT,
            "loopDurationMs": sum(durations),
            "rendering": "nearest-neighbor",
            "orientation": "ceiling-facing vertical normalization",
            "anchor": "ceiling",
            "hitboxSize": [104, 44],
            "drawSize": [120, 60],
        },
        "behavior": {
            "locomotion": "horizontal ceiling patrol",
            "crawlAnimation": "ready",
            "dropAttackAnimation": "not supplied",
            "dropAttackBehavior": "unimplemented",
            "spawned": False,
            "combatBalance": "unassigned",
        },
    }
    MANIFEST.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
