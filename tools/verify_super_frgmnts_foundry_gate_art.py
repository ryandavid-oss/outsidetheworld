#!/usr/bin/env python3
"""Verify production Foundry gate, portal, and traversal-cleanup artwork."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
HAZARD_MANIFEST = (
    ROOT
    / "Design/Super-Frgmnts/Foundry/Hazards"
    / "foundry-hazard-runtime-v1.json"
)
GATE_MANIFEST = (
    ROOT
    / "Design/Super-Frgmnts/Foundry/Uplink-Gate"
    / "foundry-uplink-boss-gate-runtime-v1.json"
)
ATMOSPHERE_LOCK_MANIFEST = (
    ROOT
    / "Design/Super-Frgmnts/Foundry/Atmosphere-Lock"
    / "foundry-atmosphere-lock-runtime-v1.json"
)
FALSE_BRIDGE_MANIFEST = (
    ROOT
    / "Design/Super-Frgmnts/Foundry/Traversal-Cleanup"
    / "foundry-false-bridge-removal-runtime-v1.json"
)
LEVEL_CONTRACT = (
    ROOT
    / "Design/Super-Frgmnts/Foundry"
    / "SHARD-FOUNDRY-LEVEL-DESIGN-v1.md"
).read_text(encoding="utf-8")
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def verify_image(
    relative_path: str,
    expected_size: list[int],
    expected_hash: str,
    require_transparency: bool = True,
) -> None:
    path = ROOT / relative_path
    assert path.exists(), f"Missing {relative_path}"
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == expected_hash, (
        f"{relative_path}: expected {expected_hash}, got {digest}"
    )
    image = Image.open(path).convert("RGBA")
    assert list(image.size) == expected_size
    alpha_extrema = image.getchannel("A").getextrema()
    if require_transparency:
        assert alpha_extrema == (0, 255)
    else:
        assert alpha_extrema[1] == 255
    assert image.getbbox() is not None


def main() -> None:
    hazard = json.loads(HAZARD_MANIFEST.read_text(encoding="utf-8"))
    gate = json.loads(GATE_MANIFEST.read_text(encoding="utf-8"))
    atmosphere_lock = json.loads(
        ATMOSPHERE_LOCK_MANIFEST.read_text(encoding="utf-8")
    )
    false_bridge = json.loads(
        FALSE_BRIDGE_MANIFEST.read_text(encoding="utf-8")
    )

    assert hazard["status"] == "production-runtime"
    coupler = hazard["assets"]["arcCoupler"]
    assert coupler["placement"] == {
        "room": 7,
        "localX": 520,
        "drawWidth": 240,
        "drawHeight": 72,
        "visualSink": 36,
        "visualClipBottom": 10,
        "floorTreatment": (
            "recessed collision-backed channel with explicit warning rails"
        ),
    }
    assert coupler["cycleSeconds"] == {
        "safe": 1.6,
        "warning": 0.6,
        "active": 1.8,
    }
    arc = hazard["assets"]["arcDischarge"]
    verify_image(
        arc["chromaSource"],
        arc["chromaSourceSize"],
        arc["chromaSourceSha256"],
        require_transparency=False,
    )
    verify_image(
        arc["alphaSource"],
        arc["alphaSourceSize"],
        arc["alphaSourceSha256"],
    )
    verify_image(
        arc["runtime"],
        arc["runtimeSize"],
        arc["runtimeSha256"],
    )
    assert arc["replaces"] == "procedural parallel zigzag strokes"

    assert gate["status"] == "production-runtime-environment"
    environment = gate["integratedEnvironment"]
    for asset_key in (
        "reference",
        "lockedSource",
        "signGeneratedSource",
        "openSource",
        "lockedRuntime",
        "openRuntime",
    ):
        asset = environment[asset_key]
        verify_image(
            asset["path"],
            asset["size"],
            asset["sha256"],
            require_transparency=False,
        )
    assert environment["placement"] == {
        "room": 7,
        "worldY": 941,
        "drawWidth": 1672,
        "drawHeight": 941,
        "mirroredAtRuntime": False,
        "environmentTreatment": (
            "The full lower-half plate carries the main deck, lower-third "
            "terrain, cavern-rock transition, machinery, right wall, and "
            "Wound opening as one authored image."
        ),
    }
    assert gate["worksiteSign"] == {
        "text": ["DANGER", "ACTIVE WORK"],
        "treatment": (
            "A small weathered amber-red metal placard with warm "
            "block-pixel lettering, corner bolts, and a slight physical cant."
        ),
        "placement": (
            "Baked into the pipe-and-rock structure directly above the "
            "far-right side-entry threshold."
        ),
        "stateContinuity": (
            "Identical in locked, opening, and open states; it is "
            "environmental storytelling, never floating UI."
        ),
    }
    threshold = gate["runtimeThreshold"]
    assert threshold["orientation"] == "side-entry-right-boundary"
    assert threshold["room"] == 7
    assert threshold["wallLocalX"] == 1580
    assert threshold["wallWidth"] == 92
    assert threshold["membraneContactLocalX"] == 1468
    assert threshold["doorWidth"] == 112
    assert threshold["doorHeight"] == 320
    assert threshold["trigger"] == {
        "localX": 1584,
        "y": 1364,
        "width": 90,
        "height": 240,
    }
    assert threshold["openingDurationSeconds"] == 0.72
    assert threshold["runway"]["clearWidth"] == 368
    assert "permanent floating label remains retired" in threshold["label"]
    locked_plate = Image.open(
        ROOT / environment["lockedRuntime"]["path"]
    ).convert("RGB")
    open_plate = Image.open(
        ROOT / environment["openRuntime"]["path"]
    ).convert("RGB")
    assert ImageChops.difference(
        locked_plate,
        open_plate,
    ).getbbox() == (1447, 370, 1537, 655)

    assert atmosphere_lock["status"] == "implemented"
    assert atmosphere_lock["placement"]["approach"] == "left-to-right"
    assert atmosphere_lock["runtime"]["dimensions"] == [80, 206]
    assert atmosphere_lock["housing_runtime"]["dimensions"] == [80, 206]
    assert atmosphere_lock["membrane_runtime"]["dimensions"] == [80, 206]
    assert atmosphere_lock["seam_wall"]["dimensions"] == [128, 1882]
    assert atmosphere_lock["placement"]["wall_span_y"] == [0, 1882]
    assert atmosphere_lock["placement"]["door_floor_bottom_y"] == (
        "deckTop + 24, except Biolab → Uplink lands at deckTop"
    )
    assert atmosphere_lock["placement"]["deck_top_y_by_multiplier"] == [
        338, 338, 600, 600, 338, 1508, 600
    ]
    assert atmosphere_lock["placement"]["boundary_multipliers"] == [
        1, 2, 3, 4, 5, 6, 7
    ]
    assert atmosphere_lock["placement"][
        "tunnel_floor_width_by_multiplier"
    ] == [128, 128, 128, 128, 128, 636, 128]
    assert atmosphere_lock["placement"]["tunnel_floor_y_by_multiplier"] == [
        338, 338, 600, 600, 338, 1508, 600
    ]
    assert len(atmosphere_lock["instances"]) == 7
    assert atmosphere_lock["instances"][1]["condition"] == (
        "Foundry atmospheric stabilizer active"
    )
    assert atmosphere_lock["instances"][5]["condition"] == (
        "Biolab atmospheric stabilizer active"
    )
    assert atmosphere_lock["instances"][5]["visual_offset_y"] == -24
    assert atmosphere_lock["instances"][5]["housing_bottom_y"] == 1508
    assert (
        atmosphere_lock["placement"]["right_door_transform"]
        == "horizontal mirror"
    )
    assert (
        atmosphere_lock["generation"]["rejected_direction"]
        == "A front-facing rectangular arch was rejected because it contradicted the side-on approach."
    )
    assert "remains latched" in atmosphere_lock["states"]["rearm"]
    for source_asset in atmosphere_lock["sources"]:
        verify_image(
            source_asset["path"],
            source_asset["dimensions"],
            source_asset["sha256"],
            require_transparency=(
                "chroma-source" not in source_asset["path"]
            ),
        )
    lock_runtime = atmosphere_lock["runtime"]
    verify_image(
        lock_runtime["path"],
        lock_runtime["dimensions"],
        lock_runtime["sha256"],
    )
    for layer_key in ("housing_runtime", "membrane_runtime"):
        layer = atmosphere_lock[layer_key]
        verify_image(
            layer["path"],
            layer["dimensions"],
            layer["sha256"],
        )
    seam_wall = atmosphere_lock["seam_wall"]
    verify_image(
        seam_wall["path"],
        seam_wall["dimensions"],
        seam_wall["sha256"],
    )

    assert false_bridge["status"] == "implemented"
    assert false_bridge["placement"]["applies_to_rooms"] == list(range(8))
    assert false_bridge["placement"]["local_x_normal"] == 520
    assert false_bridge["placement"]["local_x_mirrored"] == 522
    assert false_bridge["placement"]["world_y"] == 520
    assert false_bridge["traversal_contract"]["collision_left_end_x"] == 646
    assert false_bridge["traversal_contract"]["collision_right_start_x"] == 976
    assert false_bridge["traversal_contract"]["gap_width"] == 330
    assert false_bridge["traversal_contract"]["collision_changes"] == "none"
    for source_asset in false_bridge["sources"]:
        verify_image(
            source_asset["path"],
            source_asset["dimensions"],
            source_asset["sha256"],
            require_transparency=False,
        )
    false_bridge_runtime = false_bridge["runtime"]
    verify_image(
        false_bridge_runtime["path"],
        false_bridge_runtime["dimensions"],
        false_bridge_runtime["sha256"],
    )

    required_runtime = (
        'source: "/Images/Game/Super-Frgmnts/foundry-arc-discharge-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-housing-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-membrane-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-uplink-room7-lower-locked-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-uplink-room7-lower-open-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-seam-wall-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-false-bridge-removal-runtime-v1.png"',
        '"foundryArcDischarge"',
        '"foundryAtmosphereLock"',
        '"foundryAtmosphereLockHousing"',
        '"foundryAtmosphereLockMembrane"',
        '"foundryUplinkThresholdLocked"',
        '"foundryUplinkThresholdOpen"',
        '"foundryAtmosphereWall"',
        '"foundryFalseBridgeRemoval"',
        "assets.foundryArcDischarge",
        "assets.foundryAtmosphereLock",
        "assets.foundryAtmosphereLockHousing",
        "assets.foundryAtmosphereLockMembrane",
        "assets.foundryUplinkThresholdLocked",
        "assets.foundryUplinkThresholdOpen",
        "assets.foundryAtmosphereWall",
        "assets.foundryFalseBridgeRemoval",
        "var foundryUplinkQa =",
        'previewParameters.get("qa") === "uplink"',
        "function drawUplink()",
        "function drawUplinkForeground()",
        "function updateUplinkGate(",
        "function constrainUplinkWoundLockMovement(",
        "UPLINK_WOUND_OPEN_DURATION = 0.72",
        'canvas.dataset.uplinkGateArt =',
        '"integrated-room7-lower-third-v1"',
        '"side-entry-right-boundary"',
        '"368px-clear-after-pale-watcher"',
        '"room-eyebrow-only"',
        "var atmosphereLockPortals = [",
        'id: "foundry-intake-breathing"',
        'id: "foundry-refinery"',
        'id: "refinery-compression-pressure"',
        'id: "refinery-biolab"',
        'id: "biolab-culture-specimen"',
        'id: "biolab-uplink"',
        "visualOffsetY: -24",
        "(portal.visualOffsetY || 0)",
        'id: "uplink-spine-gate"',
        'requirement: "always"',
        'requirement: "foundry-stabilizer"',
        'requirement: "biolab-stabilizer"',
        "ATMOSPHERE_LOCK_TRANSIT_OPEN_DURATION = 0.58",
        "ATMOSPHERE_LOCK_TRANSIT_CLOSE_DURATION = 0.5",
        "ATMOSPHERE_LOCK_OBJECTIVE_CLOSE_DURATION = 0.78",
        "function atmosphereLockPortalOpenDuration(portal)",
        "function atmosphereLockPortalCloseDuration(portal)",
        'previewParameters.get("seam") || "0"',
        "atmosphereLockSeamTrial",
        "function drawFoundryAtmosphereLock()",
        '"seven-fixed-housings-split-membranes-v1"',
        '"seven-seam-solid-concrete-v1"',
        "canvas.dataset.atmosphereLockFloorBottom",
        "canvas.dataset.atmosphereWallSpan",
        "canvas.dataset.atmosphereLockFloorBridge",
        "canvas.dataset.uplinkLockApproach",
        "canvas.dataset.atmosphereLockOcclusion",
        "canvas.dataset.atmosphereLockCount",
        "canvas.dataset.atmosphereLockLevels",
        "canvas.dataset.atmosphereLockRearm",
        "portal.rearmRequired",
        "var atmosphereLockCycleQa =",
        'canvas.dataset.falseAffordanceCleanup =',
        '"eight-shared-y600-gaps-v1"',
        "var falseAffordanceQa =",
        '"VISUAL AFFORDANCE // COLLISION TRUTH"',
        "FOUNDRY_UPPER_DECK_TOP = 338",
        "FOUNDRY_UPPER_DECK_BOTTOM = 362",
        "FOUNDRY_REFINERY_WALL_WIDTH = 128",
        "function drawFoundryAtmosphereLockForeground()",
        "drawFoundryAtmosphereLockForeground();",
        '"seven-concrete-foregrounds-single-pass-v2"',
        "canvas.dataset.atmosphereWallCompositing",
        '"single-full-height-foreground-pass"',
        "canvas.getBoundingClientRect()",
        "canvas.dataset.renderBacking",
        "canvas.dataset.renderScale",
        "canvas.dataset.renderGrid",
        '"display-native-camera-snapped-v1"',
        "Math.round(cameraX * renderScaleX)",
        "Math.round(cameraY * renderScaleY)",
        'canvas.dataset.seamLurkerAnchor =',
        '"uplink-catwalk-underside-y362"',
    )
    for fragment in required_runtime:
        assert fragment in SOURCE, f"Missing Foundry art token: {fragment}"
    assert "foundryUplinkWoundLock" not in SOURCE
    assert (
        "foundry-uplink-wound-side-lock-runtime-v1.png"
        not in SOURCE
    )

    assert (
        SOURCE.count(
            "assets.foundryAtmosphereWall,\n"
            "                            wallX,\n"
            "                            0,\n"
            "                            wallWidth,\n"
            "                            WORLD_HEIGHT"
        )
        == 1
    ), "Concrete walls must be rasterized in exactly one runtime draw path"

    assert "compact branching cyan-white 16-bit" in LEVEL_CONTRACT
    assert "room-specific `1672 × 941` lower-half" in LEVEL_CONTRACT
    assert "visible contact edge" in LEVEL_CONTRACT
    assert "368 pixels before the Wound-lock membrane" in LEVEL_CONTRACT
    assert "Every environment" in LEVEL_CONTRACT
    assert "far-right `92`-pixel environment slice" in LEVEL_CONTRACT
    assert "previous freestanding front-facing" in LEVEL_CONTRACT
    assert "No magical ring, floating rectangle, or dashed barrier" in (
        LEVEL_CONTRACT
    )
    assert "side-profile Atmosphere Lock" in LEVEL_CONTRACT
    assert "approaches it from the left" in LEVEL_CONTRACT
    assert "solid concrete-and-steel divider" in LEVEL_CONTRACT
    assert "mirrored door face" in LEVEL_CONTRACT
    assert "continuous collision floor" in LEVEL_CONTRACT
    assert "single full-height foreground concrete pass" in LEVEL_CONTRACT
    assert "steel housing remains permanently visible" in LEVEL_CONTRACT
    assert "pressure membranes reform" in LEVEL_CONTRACT
    assert "Lower catwalk `y = 1508`" in LEVEL_CONTRACT
    assert "`636 × 24` collision-backed approach" in LEVEL_CONTRACT
    assert "exactly one opening and one closing cycle" in LEVEL_CONTRACT
    assert "Horizontal background silhouettes must tell the truth" in (
        LEVEL_CONTRACT
    )
    assert "ending at `x = 646` and beginning at `x = 976`" in (
        LEVEL_CONTRACT
    )
    assert "Every boundary between the eight horizontal plates" in (
        LEVEL_CONTRACT
    )
    assert "`WIDTH × 6` | Biolab → Uplink" in LEVEL_CONTRACT

    print("SUPER FRGMNTS Uplink gate and arc art: PASS")
    print("- production source, alpha, and runtime hashes match manifests")
    print("- compact sprite discharge replaces procedural zigzag electricity")
    print("- the Uplink lower-half plate embeds its side-entry Wound threshold")
    print("- locked collision meets the visible membrane edge")
    print("- the localized open blend leaves every other room pixel fixed")
    print("- the authored right-wall slice hides Aryn during entry")
    print("- HUD and mission language expose all three route requirements")
    print("- Pale Watcher ends 368px before the recovery runway")
    print("- seven permanent housings and retractable membranes cover all seams")
    print("- five cyan passages and two stabilizer locks share one system")
    print("- locks are distributed across upper, middle, and lower tiers")
    print("- membranes close after clearance and reverse safely on return")
    print("- directional re-arm prevents close-open-close exit loops")
    print("- seven walls use one full-height foreground pass for Aryn occlusion")
    print("- canvas and camera share the browser's physical-pixel render grid")
    print("- the false y=600 bridge is removed from all eight mirrored plates")
    print("- the 330px visual gap now matches its unchanged collision")
    print("- QA route frames the gate with production desktop indicators")


if __name__ == "__main__":
    main()
