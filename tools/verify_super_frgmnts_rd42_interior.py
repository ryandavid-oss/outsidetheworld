#!/usr/bin/env python3
"""Verify the isolated RD-42 hatch and interior-greybox contract."""

from __future__ import annotations

import json
import struct
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
KEEL_DECK_SEED = INTERIOR_DIR / "RD42-KEEL-SERVICE-DECK-SEED-v1.md"
ART_CANDIDATE = (
    INTERIOR_DIR
    / "Assets"
    / "rd42-interior-rear-plate-pixel-candidate-v2.png"
)
SCALE_CHECK = (
    INTERIOR_DIR
    / "Reviews"
    / "rd42-interior-rear-plate-scale-check-v2.png"
)
ART_MANIFEST = (
    INTERIOR_DIR
    / "rd42-interior-rear-plate-candidate-v2.json"
)
PRODUCTION_ART = (
    INTERIOR_DIR
    / "Assets"
    / "rd42-interior-rear-plate-production-v1.png"
)
PRODUCTION_RUNTIME_ART = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "rd42-interior-rear-plate-runtime-v1.png"
)
PRODUCTION_SCALE_CHECK = (
    INTERIOR_DIR
    / "Reviews"
    / "rd42-interior-rear-plate-scale-check-production-v1.png"
)
PRODUCTION_ART_MANIFEST = (
    INTERIOR_DIR
    / "rd42-interior-rear-plate-production-v1.json"
)
REJECTED_ART_MANIFEST = (
    INTERIOR_DIR
    / "rd42-interior-rear-plate-candidate-v1.json"
)
ARMOR_CHANGE_DIR = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Armor-Change"
)
ARMOR_CHANGE_MANIFEST = (
    ARMOR_CHANGE_DIR / "aryn-armor-change-v1.json"
)
ARMOR_CHANGE_ATLAS = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "aryn-armor-change-runtime-v1.png"
)
ARMOR_CHANGE_PREVIEW = (
    ARMOR_CHANGE_DIR
    / "Reviews"
    / "aryn-armor-change-preview-v1.gif"
)
FLIGHT_SUIT_DIR = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Overworld"
    / "Phase-3"
    / "Aryn"
    / "Flight-Suit"
)
FLIGHT_SUIT_MANIFEST = (
    FLIGHT_SUIT_DIR / "aryn-flight-suit-movement-v1.json"
)
FLIGHT_SUIT_ATLASES = {
    "run": (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "aryn-flight-suit-run-runtime-v1.png"
    ),
    "jump": (
        ROOT
        / "Images"
        / "Game"
        / "Super-Frgmnts"
        / "aryn-flight-suit-jump-runtime-v1.png"
    ),
}
FLIGHT_SUIT_PREVIEWS = {
    "run": (
        FLIGHT_SUIT_DIR
        / "Reviews"
        / "aryn-flight-suit-run-preview-v1.gif"
    ),
    "jump": (
        FLIGHT_SUIT_DIR
        / "Reviews"
        / "aryn-flight-suit-jump-preview-v1.gif"
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        signature = image.read(24)
    require(
        signature[:8] == b"\x89PNG\r\n\x1a\n",
        f"{path} is not a PNG",
    )
    return struct.unpack(">II", signature[16:24])


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    for artifact in (
        CONTRACT,
        WIREFRAME,
        WIREFRAME_SVG,
        KEEL_DECK_SEED,
    ):
        require(artifact.exists(), f"Missing RD-42 design artifact: {artifact}")
        require(
            artifact.stat().st_size > 500,
            f"RD-42 design artifact is unexpectedly small: {artifact}",
        )

    for image in (ART_CANDIDATE, SCALE_CHECK):
        require(image.exists(), f"Missing RD-42 art review: {image}")
        require(
            png_size(image) == (1672, 941),
            f"Unexpected RD-42 art review size: {image}",
        )

    require(ART_MANIFEST.exists(), "Missing RD-42 art manifest")
    art_manifest = json.loads(
        ART_MANIFEST.read_text(encoding="utf-8")
    )
    require(
        art_manifest["status"] == "approved-scale-reference",
        "RD-42 v2 must remain a scale reference, not approved runtime art",
    )
    require(
        art_manifest["runtime_integrated"] is False,
        "RD-42 art manifest incorrectly claims runtime integration",
    )
    require(
        art_manifest["asset"]["style"] ==
        "16-bit SNES-era pixel art",
        "RD-42 rear plate is not marked with the approved pixel style",
    )
    require(
        art_manifest["geometry"]["gameplay_deck_y"] == 744,
        "RD-42 art manifest deck line drifted",
    )
    require(
        art_manifest["geometry"]["normal_occupied_ceiling_y"] == 438,
        "RD-42 art manifest occupied ceiling drifted",
    )
    require(
        art_manifest["geometry"]["occupied_volume_height"] == 306,
        "RD-42 art manifest occupied volume drifted",
    )
    require(
        REJECTED_ART_MANIFEST.exists(),
        "Missing superseded RD-42 scale-study manifest",
    )
    rejected_manifest = json.loads(
        REJECTED_ART_MANIFEST.read_text(encoding="utf-8")
    )
    require(
        rejected_manifest["status"] == "rejected-scale-study",
        "The oversized v1 plate must remain recorded as rejected",
    )

    for image in (
        PRODUCTION_ART,
        PRODUCTION_RUNTIME_ART,
        PRODUCTION_SCALE_CHECK,
    ):
        require(
            image.exists(),
            f"Missing RD-42 production-art artifact: {image}",
        )
        require(
            png_size(image) == (1672, 941),
            f"Unexpected RD-42 production-art size: {image}",
        )
    require(
        PRODUCTION_ART_MANIFEST.exists(),
        "Missing RD-42 production-art manifest",
    )
    production_manifest = json.loads(
        PRODUCTION_ART_MANIFEST.read_text(encoding="utf-8")
    )
    require(
        production_manifest["status"] ==
        "approved-runtime-art",
        "RD-42 production plate must remain approved runtime art",
    )
    require(
        production_manifest["runtime_integrated"] is True,
        "RD-42 production manifest must claim its live integration",
    )
    require(
        production_manifest["palette"]["usage"][
            "dominant_occupied_cabin"
        ] == ["#A0BEF5", "#91AFB3", "#EEEEEE"],
        "RD-42 production plate lost its light OTW palette contract",
    )
    require(
        production_manifest["brandmark"]["ui_watermark"] is False,
        "The OTW mark must remain an in-world ship emblem",
    )
    require(
        production_manifest["geometry"]["flight_suit_alcove_x"] ==
        [438, 562],
        "RD-42 production art lost the suit-alcove reservation",
    )
    require(
        production_manifest["geometry"]["sealed_keel_hatch_x"] ==
        [962, 1086],
        "RD-42 production art lost the keel-hatch reservation",
    )

    require(
        ARMOR_CHANGE_MANIFEST.exists(),
        "Missing Aryn armor-change manifest",
    )
    armor_manifest = json.loads(
        ARMOR_CHANGE_MANIFEST.read_text(encoding="utf-8")
    )
    require(
        armor_manifest["status"] ==
        "normalized and integrated with persistent RD-42 flight-suit movement",
        "Aryn armor-change manifest integration boundary drifted",
    )
    require(
        armor_manifest["source"]["frame_count"] == 36,
        "Aryn armor-change source must retain all 36 frames",
    )
    require(
        armor_manifest["source"]["frame_duration_ms"] == 76,
        "Aryn armor-change cadence drifted",
    )
    require(
        armor_manifest["source"]["total_duration_ms"] == 2736,
        "Aryn armor-change duration drifted",
    )
    require(
        png_size(ARMOR_CHANGE_ATLAS) == (672, 672),
        "Aryn armor-change runtime atlas must remain a 6x6 112 px grid",
    )
    require(
        ARMOR_CHANGE_PREVIEW.exists(),
        "Missing Aryn armor-change animated review",
    )

    require(
        FLIGHT_SUIT_MANIFEST.exists(),
        "Missing Aryn flight-suit movement manifest",
    )
    flight_suit_manifest = json.loads(
        FLIGHT_SUIT_MANIFEST.read_text(encoding="utf-8")
    )
    require(
        flight_suit_manifest["status"] ==
        "normalized and integrated for persistent RD-42 movement",
        "Aryn flight-suit movement integration boundary drifted",
    )
    expected_movement = {
        "run": (78, 2808),
        "jump": (71, 2556),
    }
    for sequence_name, (
        frame_duration,
        total_duration,
    ) in expected_movement.items():
        sequence = flight_suit_manifest["sequences"][
            sequence_name
        ]
        require(
            sequence["source"]["frame_count"] == 36,
            f"Aryn flight-suit {sequence_name} must retain all 36 frames",
        )
        require(
            sequence["source"]["frame_duration_ms"] ==
            frame_duration,
            f"Aryn flight-suit {sequence_name} cadence drifted",
        )
        require(
            sequence["source"]["total_duration_ms"] ==
            total_duration,
            f"Aryn flight-suit {sequence_name} duration drifted",
        )
        require(
            png_size(FLIGHT_SUIT_ATLASES[sequence_name]) ==
            (672, 672),
            f"Aryn flight-suit {sequence_name} atlas must remain a "
            "6x6 112 px grid",
        )
        require(
            FLIGHT_SUIT_PREVIEWS[sequence_name].exists(),
            f"Missing Aryn flight-suit {sequence_name} animated review",
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
        "var SHIP_INTERIOR_CEILING_Y = 438",
        "var SHIP_INTERIOR_DECK_Y = 744",
        "var SHIP_SUIT_CRADLE_X = 506",
        "var SHIP_KEEL_HATCH_X = 1024",
        'source: "/Images/Game/Super-Frgmnts/aryn-armor-change-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/aryn-flight-suit-run-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/aryn-flight-suit-jump-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/rd42-interior-rear-plate-runtime-v1.png"',
        "function buildShipInteriorPlatforms()",
        "shipInteriorDeck: true",
        "function playerNearShipExteriorHatch()",
        "function beginShipEntry()",
        "var shipEntryLoadPending = false",
        "Hold position for hatch entry.",
        "missingShipAssets.map(function",
        "RD-42 interior systems are ready.",
        'shipTransitionMode = "exterior-enter"',
        'shipTransitionMode = "interior-enter"',
        "function beginShipExit()",
        'shipTransitionMode = "interior-exit"',
        'shipTransitionMode = "exterior-exit"',
        "function configureShipInteriorWorld(descending)",
        "function configureShipExteriorWorld(emerging)",
        'setAudioScene("interior", false);',
        'preloadIdleMusicScene("interior");',
        "function updateShipTransition(delta)",
        "function activateShipInteriorInteraction()",
        "function beginShipServiceKitRecovery()",
        "function beginShipSuitChange()",
        "function beginShipSuitRearm()",
        "function updateShipSuitChange(delta)",
        "function drawShipSuitChange()",
        "function currentShipFlightSuitFrame()",
        "function drawShipFlightSuitPlayer()",
        "function drawShipInteriorProductionArt()",
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
        "↓ CHANGE OUT OF ARMOR",
        "↓ RESTORE FIELD ARMOR",
        "FIELD ARMOR REQUIRED // HATCH LOCKED",
        "FIELD ARMOR REQUIRED // PACK RAIL OFFLINE",
        "PARTIAL MATCH // RESTRICTED",
        "UNKNOWN MATERIAL // INSTALLATION LOCKED",
        "TRILLIAN // BERTH SECURE",
        "FLIGHT / SUIT ALCOVE",
        "KEEL ACCESS // SEALED",
        "PRODUCTION ART LOAD FAILURE // FALLBACK",
        'canvas.dataset.scene = shipInteriorActive',
        "canvas.dataset.shipHatchArmed",
        "canvas.dataset.shipInteriorState",
        "canvas.dataset.shipServiceKit",
        "canvas.dataset.shipSpecimenResponse",
        "canvas.dataset.shipCockpitMatch",
        "canvas.dataset.shipTrillianBerth",
        "canvas.dataset.shipSuitAlcove",
        'canvas.dataset.shipKeelHatch = "sealed"',
        "canvas.dataset.shipSuitFrame",
        'canvas.dataset.shipArt = "production-v1"',
        "canvas.dataset.shipCameraMode",
        "canvas.dataset.shipTransitionProgress",
        "canvas.dataset.playerSupportedBy",
        'state === "ship-transition"',
        'state === "ship-kit"',
        'state === "ship-suit"',
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
        "overworldPreview" in exterior_guard,
        "Exterior hatch must be active in the production Overworld",
    )
    require(
        "shipEntryPreview || shipInteriorPreview" not in exterior_guard,
        "Exterior hatch is still isolated to explicit review routes",
    )
    require(
        "RD-42 INTERIOR LOADING" in source,
        "Production hatch does not safely prefetch missing interior art",
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
    print("- dorsal hatch entry is active throughout the production Overworld")
    print("- missing interior art is prefetched before the hatch transition")
    print("- Aryn descends into and re-emerges from the ship")
    print("- one-plate cockpit, airlock, hab, pack, and cargo zones are present")
    print("- service-kit, post-Wound, and Trillian review states are wired")
    print("- down-interaction priority and no-fire interior controls are present")
    print("- deterministic RD-42 telemetry hooks are present")
    print("- 306 px occupied volume is fixed between y438 and y744")
    print("- flight/suit alcove and sealed future keel access are reserved")
    print("- armor change persists into flight-suit main-deck movement")
    print("- 36-frame flight-suit run and jump atlases are integrated")
    print("- lighter 1672 x 941 OTW production rear plate is runtime-integrated")
    print("- in-world pixel brandmark, suit alcove, and keel hatch are present")
    print("- dedicated interior music preloads and crossfades at the hatch")


if __name__ == "__main__":
    main()
