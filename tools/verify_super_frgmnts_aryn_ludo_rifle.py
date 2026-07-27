#!/usr/bin/env python3
"""Verify Aryn's opt-in Ludo heavy-rifle preview contract."""

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
MANIFEST = LUDO_ROOT / "aryn-ludo-rifle-runtime-v1.json"
RUN_MANIFEST = LUDO_ROOT / "aryn-ludo-rifle-run-runtime-v1.json"
DRAW_RUNTIME = (
    ROOT / "Images/Game/Super-Frgmnts/aryn-rifle-draw-ludo-runtime-v1.png"
)
FIRE_RUNTIME = (
    ROOT / "Images/Game/Super-Frgmnts/aryn-rifle-fire-ludo-runtime-v1.png"
)
RUN_READY_RUNTIME = (
    ROOT
    / "Images/Game/Super-Frgmnts/aryn-rifle-run-ready-ludo-runtime-v1.png"
)
RUN_FIRE_RUNTIME = (
    ROOT
    / "Images/Game/Super-Frgmnts/aryn-rifle-run-fire-ludo-runtime-v1.png"
)


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
            bounds[3] == baseline,
            f"{path.name} frame {index} ends at {bounds[3]}; expected {baseline}",
        )
        require(
            bounds[0] >= 0 and bounds[2] <= 112,
            f"{path.name} frame {index} exceeds its fixed runtime cell",
        )


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text())
    run_manifest = json.loads(RUN_MANIFEST.read_text())
    contract = manifest["runtime_contract"]

    verify_strip(
        DRAW_RUNTIME,
        contract["draw_frame_count"],
        contract["baseline_y"],
    )
    verify_strip(
        FIRE_RUNTIME,
        contract["fire_frame_count"],
        contract["baseline_y"],
    )
    verify_strip(
        RUN_READY_RUNTIME,
        run_manifest["ready_run"]["frame_count"],
        contract["baseline_y"],
    )
    verify_strip(
        RUN_FIRE_RUNTIME,
        run_manifest["moving_fire"]["frame_count"],
        contract["baseline_y"],
    )

    require(
        manifest["design_contract"]["production_default"]
        == "pack-mounted seeking blaster",
        "The rifle replaced the production-default pack blaster",
    )
    require(
        manifest["design_contract"]["episode_beta_pickup"] is True,
        "The rifle is not marked as an Episode beta pickup",
    )

    runtime_contracts = (
        'previewParameters.get("weapon") === "rifle";',
        "/Images/Game/Super-Frgmnts/aryn-rifle-draw-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-rifle-fire-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-rifle-run-ready-ludo-runtime-v1.png",
        "/Images/Game/Super-Frgmnts/aryn-rifle-run-fire-ludo-runtime-v1.png",
        '"rifleDrawLudo",',
        '"rifleFireLudo",',
        '"rifleRunReadyLudo",',
        '"rifleRunFireLudo",',
        "var rifleReady = false;",
        "var riflePendingFire = false;",
        "var rifleIdleStowTime = 0;",
        "function stowRifle()",
        "function beginRifleDraw()",
        "rifleDrawTime = 0;",
        "function heavyRifleActive()",
        "rifleFireTime = rifleActive ? RIFLE_FIRE_DURATION : 0;",
        "rifleIdleStowTime = RIFLE_IDLE_STOW_DELAY;",
        'visual.pose = "rifleDrawLudo";',
        'visual.pose = "rifleAirborneReadyLudo";',
        '? "rifleRunFireLudo"',
        '? "rifleRunReadyLudo"',
        '? "rifle-ready"',
        ': "rifle-stowed"',
        "direct: rifleActive,",
        'canvas.dataset.arynWeapon = heavyRifleActive()',
        "riflePreview ||",
    )
    for runtime_contract in runtime_contracts:
        require(
            runtime_contract in source,
            f"Missing rifle preview contract: {runtime_contract}",
        )

    require(
        "aryn-ludo-rifle-shoot-reference-v1.png" not in source,
        "The raw rifle shooting master is loaded by the game",
    )
    require(
        "aryn-ludo-rifle-draw-reference-v1.png" not in source,
        "The raw rifle draw master is loaded by the game",
    )
    require(
        run_manifest["design_contract"]["ground_running_does_not_stow_rifle"]
        is True,
        "The authored running-rifle contract still stows during ground movement",
    )
    require(
        run_manifest["design_contract"]["airborne_movement_preserves_rifle"]
        is True,
        "The running-rifle contract does not preserve the rifle in the air",
    )
    require(
        run_manifest["design_contract"][
            "airborne_fire_uses_authored_full_body_motion"
        ]
        is True,
        "The running-rifle contract does not support airborne fire",
    )
    require(
        "rifleReady &&\n                    requestedDirection !== 0"
        not in source,
        "Ground movement still stows the ready rifle",
    )
    require(
        "if (rifleActive) {\n                    player.vx = 0;"
        not in source,
        "Heavy-rifle firing still forcibly stops Aryn",
    )
    require(
        'return event.code === "KeyX";' in source,
        "Keyboard firing is not mapped to X",
    )
    require(
        "ControlLeft" not in source and "ControlRight" not in source,
        "The conflicting macOS Control firing shortcut is still active",
    )
    require(
        "function beginPlatformDrop(platform) {\n                stowRifle();"
        not in source,
        "Dropping through a platform still stows the rifle",
    )
    require(
        "if (heavyRifleActive()) {\n                    if (!player.onGround)"
        not in source,
        "Airborne movement still forcibly stows the rifle",
    )
    require(
        "rifleReady &&\n                    player.onGround &&\n"
        in source,
        "The rifle idle holster is not restricted to grounded time",
    )
    require(
        "var RIFLE_IDLE_STOW_DELAY = 2.25;" in source,
        "Heavy rifle does not have the approved idle stow delay",
    )
    require(
        "if (rifleIdleStowTime === 0) {\n                        stowRifle();"
        in source,
        "Heavy rifle does not return to the stowed traversal state",
    )
    require(
        contract["standing_foresection_shift"] == 14,
        "Standing rifle foresection is not normalized to the running rifle",
    )

    print("SUPER FRGMNTS Aryn Ludo heavy-rifle contract: PASS")
    print("- fixed-canvas standing and moving animation alignment")
    print("- rifle remains an optional Episode beta special weapon")
    print("- first fire draws; ground running preserves the ready rifle")
    print("- moving fire uses the authored full-body gait and muzzle pulse")
    print("- jumping, dropping, and falling preserve the ready rifle")
    print("- airborne heavy-rifle fire uses authored full-body motion")
    print("- standing barrel length is normalized to the running silhouette")
    print("- rifle stows after 2.25 grounded seconds without firing")
    print("- keyboard fire uses X, avoiding the macOS Control-arrow shortcut")
    print("- firing is a fast direct amber route-clearing round")
    print("- pack blaster remains the production default")


if __name__ == "__main__":
    main()
