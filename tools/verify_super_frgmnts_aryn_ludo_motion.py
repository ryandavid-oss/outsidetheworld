#!/usr/bin/env python3
"""Verify Aryn's active Episode run, jump, and platform-drop runtime contract."""

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
RUN_MANIFEST = LUDO_ROOT / "aryn-ludo-run-runtime-v2.json"
JUMP_MANIFEST = LUDO_ROOT / "aryn-ludo-jump-drop-runtime-v1.json"
RUN_RUNTIME = ROOT / "Images/Game/Super-Frgmnts/aryn-run-ludo-runtime-v2.png"
JUMP_RUNTIME = ROOT / "Images/Game/Super-Frgmnts/aryn-jump-ludo-runtime-v1.png"
DROP_RUNTIME = ROOT / "Images/Game/Super-Frgmnts/aryn-drop-ludo-runtime-v1.png"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_strip(path: Path, frame_count: int, baseline: int | None = None) -> None:
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
            bounds[0] >= 0 and bounds[1] >= 0 and bounds[2] <= 112 and bounds[3] <= 112,
            f"{path.name} frame {index} exceeds its runtime cell",
        )
        if baseline is not None:
            require(
                bounds[3] == baseline,
                f"{path.name} frame {index} ends at {bounds[3]}; expected {baseline}",
            )


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    run_manifest = json.loads(RUN_MANIFEST.read_text())
    jump_manifest = json.loads(JUMP_MANIFEST.read_text())
    asset_definitions = source.split(
        "var assetDefinitions = {",
        1,
    )[1].split("var sharedAssetKeys = [", 1)[0]
    shared_assets = source.split(
        "var sharedAssetKeys = [",
        1,
    )[1].split("];", 1)[0]
    player_visuals = source.split(
        "function getPlayerVisualState()",
        1,
    )[1].split("function drawPlayer()", 1)[0]

    verify_strip(
        RUN_RUNTIME,
        run_manifest["runtime_contract"]["frame_count"],
    )
    verify_strip(
        JUMP_RUNTIME,
        jump_manifest["runtime_contract"]["jump_frame_count"],
        jump_manifest["runtime_contract"]["baseline_y"],
    )
    verify_strip(
        DROP_RUNTIME,
        jump_manifest["runtime_contract"]["drop_frame_count"],
        jump_manifest["runtime_contract"]["baseline_y"],
    )

    require(
        run_manifest["source_frames"] == list(range(15, 23)),
        "The approved clean eight-frame run cycle changed",
    )
    require(
        jump_manifest["jump"]["launch_frames"] == [0, 1, 2],
        "Jump launch sequencing changed",
    )
    require(
        jump_manifest["jump"]["airborne_frame"] == 3,
        "Jump airborne hold changed",
    )
    require(
        jump_manifest["jump"]["landing_frames"] == [4, 5, 6],
        "Jump landing sequencing changed",
    )
    require(
        'runLudo: {' in asset_definitions
        and 'source: "/Images/Game/Super-Frgmnts/aryn-run-ludo-runtime-v2.png"'
        in asset_definitions,
        "The approved run is not defined as a route-independent asset",
    )
    require(
        '"runLudo"' in shared_assets,
        "The approved run is not loaded before the title-to-Episode handoff",
    )
    require(
        "visual.sprite = runningWithReadyRifle" in player_visuals
        and ": ludoRunPreview" in player_visuals
        and "? assets.runLudo" in player_visuals
        and ": assets.run;" in player_visuals,
        "Episode locomotion does not retain the approved unarmed run branch",
    )

    runtime_contracts = (
        "/Images/Game/Super-Frgmnts/aryn-run-ludo-runtime-v2.png",
        "runLudo: {",
        '"runLudo",',
        "/Images/Game/Super-Frgmnts/aryn-jump-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-drop-ludo-runtime-v1.png",
        '"jumpLudo",',
        '"dropLudo",',
        "jumpPoseTime =",
        'shipSuitState === "flight-suit"',
        "? 0.16",
        ": ludoRunPreview",
        "? 0.15",
        "dropPoseTime = ludoRunPreview ? 0.28 : 0;",
        "landPoseTime =",
        "? 0.36",
        "? 0.18",
        ": 0.11;",
        "visual.sprite = assets.jumpLudo;",
        "visual.sprite = assets.dropLudo;",
        "canvas.dataset.arynPose = visual.pose;",
        "canvas.dataset.arynFrame = String(visual.frame);",
        "(ludoRunPreview ? 8 : 10)",
        'var episodeOneRun = previewParameters.get("episode") === "01";',
        'previewParameters.get("aryn") !== "legacy" &&',
        'previewParameters.has("preview")',
        "episodeOneRun ||",
        "ludoRunPreview = true;",
        "? assets.runLudo",
        ": assets.run;",
        ': "run";',
        "Math.floor(runFrameTime * 12)",
    )
    for contract in runtime_contracts:
        require(contract in source, f"Missing Ludo motion contract: {contract}")

    print("SUPER FRGMNTS Aryn Ludo motion contract: PASS")
    print("- clean eight-frame run cycle")
    print("- three-frame launch with a dedicated airborne hold")
    print("- three-frame baseline-normalized landing recovery")
    print("- four-frame front-facing platform drop")
    print("- curated Ludo motion is active in unified Episode scenes")


if __name__ == "__main__":
    main()
