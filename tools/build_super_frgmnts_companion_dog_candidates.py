#!/usr/bin/env python3
"""Validate and build the player's movement and armored-attack dog assets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Outpost"
    / "Player-Companion-Dog"
)
PUBLIC = ROOT / "Images/Game/Super-Frgmnts"
MANIFEST = FAMILY / "player-companion-dog-assets-v1.json"
RUNTIME_FRAME_WIDTH = 120
RUNTIME_FRAME_HEIGHT = 104
MAX_CONTENT_WIDTH = 112
MAX_CONTENT_HEIGHT = 96


@dataclass(frozen=True)
class DogSpec:
    key: str
    label: str
    role: str
    playback: str
    source_stem: str
    columns: int
    rows: int
    runtime_filename: str
    preview_filename: str
    review_only: bool = False

    @property
    def frame_count(self) -> int:
        return self.columns * self.rows


SPECS = (
    DogSpec(
        key="unarmored",
        label="Trillian — unarmored state",
        role="movement",
        playback="loop",
        source_stem="companion-dog-unarmored-walk-source-v1",
        columns=6,
        rows=6,
        runtime_filename="companion-dog-unarmored-walk-sheet-v1.png",
        preview_filename="companion-dog-unarmored-walk-preview-v1.gif",
    ),
    DogSpec(
        key="armored",
        label="Trillian — armored state",
        role="movement",
        playback="loop",
        source_stem="companion-dog-armored-walk-source-v1",
        columns=5,
        rows=5,
        runtime_filename="companion-dog-armored-walk-sheet-v1.png",
        preview_filename="companion-dog-armored-walk-preview-v1.gif",
    ),
    DogSpec(
        key="armoredAttack",
        label="Trillian — armored attack",
        role="close-range energy lunge",
        playback="one-shot",
        source_stem="companion-dog-armored-attack-source-v1",
        columns=6,
        rows=6,
        runtime_filename="companion-dog-armored-attack-sheet-v1.png",
        preview_filename="companion-dog-armored-attack-preview-v1.gif",
    ),
    DogSpec(
        key="armoredJumpLaunch",
        label="Trillian — armored jump launch",
        role="powered jump charge and launch cue",
        playback="one-shot",
        source_stem="companion-dog-armored-jump-source-v1",
        columns=6,
        rows=6,
        runtime_filename="companion-dog-armored-jump-launch-sheet-v1.png",
        preview_filename="companion-dog-armored-jump-launch-preview-v1.gif",
    ),
)

REVIEW_SPECS = (
    DogSpec(
        key="armoredRearAlternate",
        label="Trillian — armored rear/power-up alternate",
        role="rearing or power-up motion",
        playback="one-shot",
        source_stem="companion-dog-armored-rear-alternate-source-v1",
        columns=5,
        rows=5,
        runtime_filename=(
            "companion-dog-armored-rear-alternate-review-sheet-v1.png"
        ),
        preview_filename=(
            "companion-dog-armored-rear-alternate-preview-v1.gif"
        ),
        review_only=True,
    ),
)


def build(spec: DogSpec) -> dict[str, object]:
    raw_image = FAMILY / "Raw" / f"{spec.source_stem}.png"
    raw_manifest = FAMILY / "Raw" / f"{spec.source_stem}.json"
    output = (
        FAMILY / "Reviews" / spec.runtime_filename
        if spec.review_only
        else PUBLIC / spec.runtime_filename
    )
    preview = FAMILY / "Reviews" / spec.preview_filename

    metadata = json.loads(raw_manifest.read_text(encoding="utf-8"))
    source = Image.open(raw_image)
    if source.mode != "RGBA":
        raise ValueError(f"{spec.key}: expected RGBA source, got {source.mode}")
    frames = metadata.get("frames")
    if not isinstance(frames, dict):
        raise ValueError(f"{spec.key}: metadata has no frame dictionary")

    expected_keys = [
        f"frame_{index:03d}" for index in range(spec.frame_count)
    ]
    if list(sorted(frames)) != expected_keys:
        raise ValueError(
            f"{spec.key}: metadata does not contain the expected frame range"
        )
    records = [frames[key] for key in expected_keys]
    first_rectangle = records[0]["frame"]
    source_frame_width = int(first_rectangle["w"])
    source_frame_height = int(first_rectangle["h"])
    expected_source_size = (
        source_frame_width * spec.columns,
        source_frame_height * spec.rows,
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

    source_frames: list[Image.Image] = []
    bounds: list[tuple[int, int, int, int]] = []
    durations: list[int] = []
    contacts: dict[str, list[int]] = {
        "left": [],
        "right": [],
        "top": [],
        "bottom": [],
    }
    for index, record in enumerate(records):
        rectangle = record["frame"]
        expected_x = index % spec.columns * source_frame_width
        expected_y = index // spec.columns * source_frame_height
        if (
            int(rectangle["x"]) != expected_x
            or int(rectangle["y"]) != expected_y
            or int(rectangle["w"]) != source_frame_width
            or int(rectangle["h"]) != source_frame_height
        ):
            raise ValueError(f"{spec.key}: frame {index} breaks the grid")
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
        if bound[0] == 0:
            contacts["left"].append(index)
        if bound[2] == source_frame_width:
            contacts["right"].append(index)
        if bound[1] == 0:
            contacts["top"].append(index)
        if bound[3] == source_frame_height:
            contacts["bottom"].append(index)
        source_frames.append(frame)
        bounds.append(bound)
        durations.append(max(20, int(record.get("duration", 60))))

    active_contacts = {
        edge: indices for edge, indices in contacts.items() if indices
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

    runtime_frames: list[Image.Image] = []
    for frame in source_frames:
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
                RUNTIME_FRAME_HEIGHT - content_height - 4,
            ),
        )
        runtime_frames.append(runtime_frame)

    atlas = Image.new(
        "RGBA",
        (
            spec.columns * RUNTIME_FRAME_WIDTH,
            spec.rows * RUNTIME_FRAME_HEIGHT,
        ),
        (0, 0, 0, 0),
    )
    for index, frame in enumerate(runtime_frames):
        atlas.alpha_composite(
            frame,
            (
                index % spec.columns * RUNTIME_FRAME_WIDTH,
                index // spec.columns * RUNTIME_FRAME_HEIGHT,
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

    result: dict[str, object] = {
        "key": spec.key,
        "label": spec.label,
        "role": spec.role,
        "playback": spec.playback,
        "runtimeEligible": not spec.review_only,
        "source": {
            "image": str(raw_image.relative_to(FAMILY)),
            "manifest": str(raw_manifest.relative_to(FAMILY)),
            "columns": spec.columns,
            "rows": spec.rows,
            "frameWidth": source_frame_width,
            "frameHeight": source_frame_height,
            "frameCount": spec.frame_count,
            "frameDurationMs": durations[0],
        },
        "validation": {
            "result": (
                "pass-with-source-warning"
                if active_contacts
                else "pass"
            ),
            "edgeContactFrames": active_contacts,
        },
        "runtime": {
            "image": str(output.relative_to(ROOT)),
            "preview": str(preview.relative_to(ROOT)),
            "columns": spec.columns,
            "rows": spec.rows,
            "frameWidth": RUNTIME_FRAME_WIDTH,
            "frameHeight": RUNTIME_FRAME_HEIGHT,
            "frameCount": spec.frame_count,
            "loopDurationMs": sum(durations),
            "contentSize": [content_width, content_height],
            "rendering": "nearest-neighbor",
            "anchor": "ground",
        },
    }
    if spec.key == "armoredAttack":
        result["authoring"] = {
            "interpretation": (
                "brace and charge, bare teeth, lead-paw energy lunge, "
                "then recover"
            ),
            "suggestedPhases": {
                "windupFrames": [0, 11],
                "strikeFrames": [12, 23],
                "recoveryFrames": [24, 35],
            },
            "damageWindow": "unassigned until combat implementation",
        }
    elif spec.key == "armoredJumpLaunch":
        result["authoring"] = {
            "interpretation": (
                "rear, plant the forepaws, route energy through the armor, "
                "then hand off to a physics-driven jump"
            ),
            "suggestedPhases": {
                "windupFrames": [0, 17],
                "energyRampFrames": [18, 29],
                "launchHandoffFrames": [30, 35],
            },
            "runtimeMotion": (
                "The art has no baked vertical displacement. Apply the "
                "actual jump arc through actor physics after launch."
            ),
            "airborneAnimation": "not supplied",
            "landingAnimation": "not supplied",
        }
    elif spec.key == "armoredRearAlternate":
        result["authoring"] = {
            "disposition": "preserved for review only",
            "compatibility": (
                "Do not splice into armoredJumpLaunch as an airborne or "
                "landing phase."
            ),
            "reason": [
                "The sequence reads as a rear or power-up, not airborne travel.",
                "Critical upright frames 9 through 17 are clipped at the top.",
                "Frames 19 through 24 are clipped at the left edge.",
                "Frames 12 and 13 are clipped at the right edge.",
            ],
        }
    return result


def main() -> None:
    report = {
        "status": "overworld-surface-runtime",
        "name": "Trillian",
        "companionIdentity": (
            "Trillian is the player's dog and is explicitly separate from "
            "Jane."
        ),
        "assetRelationship": (
            "The unarmored movement, armored movement, armored attack, and "
            "armored jump-launch sheets all depict Trillian."
        ),
        "currentCanon": (
            "Jane remains the German Shepherd camp dog and does not enter "
            "the Coreworks transport."
        ),
        "runtimeIntegration": True,
        "behaviorProposal": (
            "Trillian is an optional non-solid Overworld companion. She "
            "waits in Western Signal Flats, follows after recovery, equips "
            "a field harness, uses a physics-driven powered launch to reach "
            "raised terrain, and performs one noncombat energy breach on "
            "sealed salvage."
        ),
        "surfaceRuntime": {
            "scene": "overworld",
            "recoverAssignmentX": 690,
            "harnessAssignmentX": 1080,
            "salvageAssignmentX": 1430,
            "followDistance": 112,
            "followSpeed": 82,
            "poweredLaunchVelocityY": -950,
            "transportLimitX": 6276,
            "friendlySeekerSafety": True,
            "solid": False,
            "hostile": False,
            "enemyTargetable": False,
            "combatDamage": False,
            "foundryHandoff": False,
        },
        "animations": [build(spec) for spec in SPECS],
        "reviewOnlyAlternates": [
            build(spec) for spec in REVIEW_SPECS
        ],
        "futureCombatCompanionRequirements": [
            "alert and target-acquisition animation",
            "approved damage frame window and hitbox for armored attack",
            "hurt, incapacitated, and recovery animation",
            "Overworld-to-Foundry scene handoff and save-state contract",
            "damage, cooldown, health, and enemy-priority balance",
        ],
    }
    MANIFEST.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
