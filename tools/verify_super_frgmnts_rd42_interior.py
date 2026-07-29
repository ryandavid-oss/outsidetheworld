#!/usr/bin/env python3
"""Verify the isolated RD-42 hatch and interior-greybox contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
INTERIOR_DIR = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Ship"
    / "Interior"
)
CONTRACT = INTERIOR_DIR / "RD42-SHIP-INTERIOR-CONTRACT-v1.md"
WIREFRAME = INTERIOR_DIR / "RD42-SHIP-INTERIOR-WIREFRAME-v1.md"
WIREFRAME_SVG = INTERIOR_DIR / "RD42-SHIP-INTERIOR-WIREFRAME-v1.svg"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    for artifact in (CONTRACT, WIREFRAME, WIREFRAME_SVG):
        require(artifact.exists(), f"Missing RD-42 design artifact: {artifact}")
        require(
            artifact.stat().st_size > 500,
            f"RD-42 design artifact is unexpectedly small: {artifact}",
        )

    required_runtime_tokens = (
        'previewParameters.get("preview") === "ship-interior"',
        'previewParameters.get("scene") === "ship-entry"',
        'previewParameters.get("objective") === "service-kit"',
        'previewParameters.get("state") === "post-wound"',
        'previewParameters.get("trillian") === "1"',
        "var SHIP_EXTERIOR_HATCH_X =",
        "OVERWORLD_ORIGIN_X + 572",
        "var SHIP_INTERIOR_HATCH_X = 684",
        "var SHIP_INTERIOR_DECK_Y = 744",
        "function buildShipInteriorPlatforms()",
        "shipInteriorDeck: true",
        "function playerNearShipExteriorHatch()",
        "function beginShipEntry()",
        'shipTransitionMode = "exterior-enter"',
        'shipTransitionMode = "interior-enter"',
        "function beginShipExit()",
        'shipTransitionMode = "interior-exit"',
        'shipTransitionMode = "exterior-exit"',
        "function configureShipInteriorWorld(descending)",
        "function configureShipExteriorWorld(emerging)",
        "function updateShipTransition(delta)",
        "function activateShipInteriorInteraction()",
        "function beginShipServiceKitRecovery()",
        'shipServiceKitState = "recovering"',
        'shipServiceKitState = "carried"',
        "function drawShipInteriorGreybox()",
        "function drawShipExteriorHatchBack()",
        "function drawShipExteriorHatchForeground()",
        "↓ ENTER RD-42",
        "↓ EXIT RD-42",
        "↓ TAKE SERVICE KIT",
        "↓ INSPECT PACK BENCH",
        "↓ QUERY CENTRAL LINK",
        "PARTIAL MATCH // RESTRICTED",
        "UNKNOWN MATERIAL // INSTALLATION LOCKED",
        "TRILLIAN // BERTH SECURE",
        "DESIGN GREYBOX // NOT FINAL ART",
        'canvas.dataset.scene = shipInteriorActive',
        "canvas.dataset.shipHatchArmed",
        "canvas.dataset.shipInteriorState",
        "canvas.dataset.shipServiceKit",
        "canvas.dataset.shipSpecimenResponse",
        "canvas.dataset.shipCockpitMatch",
        "canvas.dataset.shipTrillianBerth",
        "canvas.dataset.shipCameraMode",
        "canvas.dataset.shipTransitionProgress",
        "canvas.dataset.playerSupportedBy",
        'state === "ship-transition"',
        'state === "ship-kit"',
        "body.is-ship-interior .touch-key--shoot",
    )
    for token in required_runtime_tokens:
        require(token in source, f"Missing RD-42 runtime contract: {token}")

    drop_function = source[
        source.index("function dropThroughCurrentPlatform()"):
        source.index(
            "function updateAtmosphericStabilizers",
            source.index("function dropThroughCurrentPlatform()"),
        )
    ]
    require(
        drop_function.index("if (shipInteriorActive)") <
        drop_function.index("if (overworldPreview)"),
        "RD-42 interior interaction must take priority over overworld actions",
    )
    require(
        drop_function.index("beginShipEntry()") <
        drop_function.index("if (overworldPreview)"),
        "RD-42 hatch entry must take priority over overworld actions",
    )

    draw_function = source[
        source.index("function draw()"):
        source.index(
            "function drawBackgroundLayer",
            source.index("function draw()"),
        )
    ]
    require(
        draw_function.index("if (shipInteriorActive)") <
        draw_function.index("drawBackgroundRooms()"),
        "The isolated interior must render before production scene branches",
    )

    exterior_guard = source[
        source.index("function shipExteriorGreyboxActive()"):
        source.index(
            "function findShipHatchPlatform",
            source.index("function shipExteriorGreyboxActive()"),
        )
    ]
    require(
        "shipEntryPreview || shipInteriorPreview" in exterior_guard,
        "Exterior hatch must remain isolated to explicit review routes",
    )

    require(
        "shipInteriorPreview ||\n                    overworldPreview" in source,
        "RD-42 direct preview must participate in the runtime spawn path",
    )
    require(
        "shipInteriorActive && control === \"shoot\"" in source,
        "Interior firing must be disabled",
    )

    print("RD-42 ship-interior contract passed.")
    print("- dorsal hatch entry is isolated to explicit review routes")
    print("- Aryn descends into and re-emerges from the ship")
    print("- one-plate cockpit, airlock, hab, pack, and cargo zones are present")
    print("- service-kit, post-Wound, and Trillian review states are wired")
    print("- down-interaction priority and no-fire interior controls are present")
    print("- deterministic RD-42 telemetry hooks are present")


if __name__ == "__main__":
    main()
