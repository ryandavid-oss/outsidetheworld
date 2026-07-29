#!/usr/bin/env python3
"""Validate and build the Mirror Husk collapse review asset."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "Design/Super-Frgmnts/Foundry/Enemies/Mirror-Husk"
RAW_IMAGE = FAMILY / "Raw/mirror-husk-collapse-source-v1.png"
RAW_MANIFEST = FAMILY / "Raw/mirror-husk-collapse-source-v1.json"
REVIEW_ATLAS = FAMILY / "Reviews/mirror-husk-collapse-review-sheet-v1.png"
PREVIEW = FAMILY / "Reviews/mirror-husk-collapse-preview-v1.gif"
MANIFEST = FAMILY / "mirror-husk-collapse-candidate-v1.json"

COLUMNS = 5
ROWS = 5
FRAME_COUNT = COLUMNS * ROWS
REVIEW_FRAME_WIDTH = 128
REVIEW_FRAME_HEIGHT = 112
MAX_CONTENT_WIDTH = 120
MAX_CONTENT_HEIGHT = 104
EDGE_PADDING = 4
NEAR_EDGE_THRESHOLD = 2


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
    if source.size != (
        source_frame_width * COLUMNS,
        source_frame_height * ROWS,
    ):
        raise ValueError("Source image does not match its 5x5 frame grid")
    if metadata.get("meta", {}).get("size") != {
        "w": source.width,
        "h": source.height,
    }:
        raise ValueError("Metadata size does not match source image")

    frames: list[Image.Image] = []
    bounds: list[tuple[int, int, int, int]] = []
    durations: list[int] = []
    contacts = {edge: [] for edge in ("left", "right", "top", "bottom")}
    near_edges = {edge: [] for edge in contacts}
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
        durations.append(max(20, int(record.get("duration", 100))))

    active_contacts = {
        edge: indices for edge, indices in contacts.items() if indices
    }
    active_near_edges = {
        edge: indices for edge, indices in near_edges.items() if indices
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
        MAX_CONTENT_WIDTH / union_width,
        MAX_CONTENT_HEIGHT / union_height,
    )
    content_width = max(1, round(union_width * scale))
    content_height = max(1, round(union_height * scale))

    review_frames: list[Image.Image] = []
    for frame in frames:
        content = frame.crop(union).resize(
            (content_width, content_height),
            Image.Resampling.NEAREST,
        )
        review_frame = Image.new(
            "RGBA",
            (REVIEW_FRAME_WIDTH, REVIEW_FRAME_HEIGHT),
            (0, 0, 0, 0),
        )
        review_frame.alpha_composite(
            content,
            (
                (REVIEW_FRAME_WIDTH - content_width) // 2,
                REVIEW_FRAME_HEIGHT - content_height - EDGE_PADDING,
            ),
        )
        review_frames.append(review_frame)

    atlas = Image.new(
        "RGBA",
        (
            COLUMNS * REVIEW_FRAME_WIDTH,
            ROWS * REVIEW_FRAME_HEIGHT,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(review_frames):
        atlas.alpha_composite(
            frame,
            (
                index % COLUMNS * REVIEW_FRAME_WIDTH,
                index // COLUMNS * REVIEW_FRAME_HEIGHT,
            ),
        )

    REVIEW_ATLAS.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(REVIEW_ATLAS, optimize=True)
    preview_durations = list(durations)
    preview_durations[-1] = 900
    review_frames[0].save(
        PREVIEW,
        save_all=True,
        append_images=review_frames[1:],
        duration=preview_durations,
        disposal=2,
        loop=0,
        optimize=False,
    )

    report = {
        "workingName": "Mirror Husk",
        "proposedRuntimeType": "mirrorHusk",
        "status": "review-only-animation-candidate",
        "productionPopulation": False,
        "role": "slow humanoid with a frontal projectile shield",
        "animation": "collapse/death",
        "source": {
            "image": "Raw/mirror-husk-collapse-source-v1.png",
            "manifest": "Raw/mirror-husk-collapse-source-v1.json",
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": source_frame_width,
            "frameHeight": source_frame_height,
            "frameCount": FRAME_COUNT,
            "frameDurationMs": durations[0],
        },
        "validation": {
            "result": "pass-with-source-warning",
            "edgeContactFrames": active_contacts,
            "nearEdgeThresholdPixels": NEAR_EDGE_THRESHOLD,
            "nearEdgeFrames": active_near_edges,
            "warning": (
                "Frame 13 touches the right source-cell boundary and later "
                "prone frames approach the bottom boundary. Review padding "
                "does not reconstruct clipped source pixels."
            ),
        },
        "review": {
            "atlas": str(REVIEW_ATLAS.relative_to(FAMILY)),
            "preview": str(PREVIEW.relative_to(FAMILY)),
            "columns": COLUMNS,
            "rows": ROWS,
            "frameWidth": REVIEW_FRAME_WIDTH,
            "frameHeight": REVIEW_FRAME_HEIGHT,
            "frameCount": FRAME_COUNT,
            "contentSize": [content_width, content_height],
            "anchor": "ground",
            "rendering": "nearest-neighbor",
        },
        "runtime": {
            "registered": False,
            "spawned": False,
            "reason": (
                "A walk cycle and explicit vulnerable-back read are still "
                "required before frontal-blocking behavior is implemented."
            ),
        },
        "missing": [
            "walk or patrol loop",
            "turn animation",
            "readable vulnerable-back state",
            "hurt response",
            "frontal ricochet timing and balance",
        ],
    }
    MANIFEST.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
