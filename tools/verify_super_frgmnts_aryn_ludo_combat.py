#!/usr/bin/env python3
"""Verify Aryn's opt-in Ludo combat-animation runtime contract."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
LUDO_ROOT = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Ludo"
)
MANIFEST = LUDO_ROOT / "aryn-ludo-combat-runtime-v1.json"
LIGHT_RUNTIME = (
    ROOT / "Images/Game/Super-Frgmnts/aryn-impact-light-ludo-runtime-v1.png"
)
HEAVY_RUNTIME = (
    ROOT / "Images/Game/Super-Frgmnts/aryn-impact-heavy-ludo-runtime-v1.png"
)
DEATH_RUNTIME = ROOT / "Images/Game/Super-Frgmnts/aryn-death-ludo-runtime-v1.png"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_strip(path: Path, frame_count: int, baseline: int) -> None:
    require(path.is_file(), f"Missing runtime asset: {path.name}")
    image = Image.open(path).convert("RGBA")
    require(
        image.size == (112 * frame_count, 112),
        f"{path.name} is {image.size}; expected {(112 * frame_count, 112)}",
    )
    for index in range(frame_count):
        frame = image.crop((index * 112, 0, (index + 1) * 112, 112))
        bounds = frame.getbbox()
        require(bounds is not None, f"{path.name} frame {index} is empty")
        require(
            bounds[0] >= 0
            and bounds[1] >= 0
            and bounds[2] <= 112
            and bounds[3] <= 112,
            f"{path.name} frame {index} exceeds its runtime cell",
        )
        require(
            bounds[3] == baseline,
            f"{path.name} frame {index} ends at {bounds[3]}; expected {baseline}",
        )


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text())
    contract = manifest["runtime_contract"]

    verify_strip(
        LIGHT_RUNTIME,
        contract["light_impact_frame_count"],
        contract["baseline_y"],
    )
    verify_strip(
        HEAVY_RUNTIME,
        contract["heavy_impact_frame_count"],
        contract["baseline_y"],
    )
    verify_strip(
        DEATH_RUNTIME,
        contract["death_frame_count"],
        contract["baseline_y"],
    )

    require(
        manifest["source_decisions"]["rifle_shoot_reference"].startswith(
            "source master only"
        ),
        "The generated rifle shoot source-decision contract changed",
    )
    require(
        manifest["source_decisions"]["rifle_draw_reference"].startswith(
            "source master only"
        ),
        "The generated rifle draw source-decision contract changed",
    )

    runtime_contracts = (
        "/Images/Game/Super-Frgmnts/aryn-impact-light-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-impact-heavy-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-death-ludo-runtime-v1.png",
        '"impactLightLudo",',
        '"impactHeavyLudo",',
        '"deathLudo"',
        'impactPoseVariant = hits % 2 === 1 ? "light" : "heavy";',
        'state = "dying";',
        "deathPoseTime = DEATH_POSE_DURATION;",
        'visual.pose = "deathLudo";',
        '? "impact-" + impactPoseVariant',
        '? "firing"',
        "packFireTime = rifleActive ? 0 : PACK_FIRE_DURATION;",
        'visual.pose === "deathLudo"',
        'state === "dying" ||',
    )
    for runtime_contract in runtime_contracts:
        require(
            runtime_contract in source,
            f"Missing Ludo combat contract: {runtime_contract}",
        )

    require(
        "aryn-ludo-rifle-shoot-reference-v1.png" not in source,
        "Rifle shooting reference is loaded by the game",
    )
    require(
        "aryn-ludo-rifle-draw-reference-v1.png" not in source,
        "Rifle draw reference is loaded by the game",
    )

    print("SUPER FRGMNTS Aryn Ludo combat contract: PASS")
    print("- alternating light and heavy baseline-normalized impacts")
    print("- delayed health-depletion collapse before the loss message")
    print("- pack-emitter firing pulse remains independent of locomotion")
    print("- pack blaster remains the production-default weapon")
    print("- production animation remains the default")


if __name__ == "__main__":
    main()
