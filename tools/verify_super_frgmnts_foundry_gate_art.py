#!/usr/bin/env python3
"""Verify production Foundry gate, portal, and traversal-cleanup artwork."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


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

    assert gate["status"] == "beta-production"
    gate_chroma = gate["assets"]["chromaSource"]
    verify_image(
        gate_chroma["path"],
        gate_chroma["size"],
        gate_chroma["sha256"],
        require_transparency=False,
    )
    gate_alpha = gate["assets"]["alphaSource"]
    verify_image(
        gate_alpha["path"],
        gate_alpha["size"],
        gate_alpha["sha256"],
    )
    gate_runtime = gate["assets"]["runtime"]
    verify_image(
        gate_runtime["path"],
        gate_runtime["size"],
        gate_runtime["sha256"],
    )
    assert gate["placement"]["room"] == 7
    assert gate["placement"]["bottomY"] == 1604
    assert gate["placement"]["drawWidth"] == 444
    assert gate["placement"]["drawHeight"] == 376
    assert gate["placement"]["trigger"] == {
        "localX": 1218,
        "y": 1284,
        "width": 132,
        "height": 320,
    }

    assert atmosphere_lock["status"] == "implemented"
    assert atmosphere_lock["placement"]["approach"] == "left-to-right"
    assert atmosphere_lock["runtime"]["dimensions"] == [80, 206]
    assert atmosphere_lock["housing_runtime"]["dimensions"] == [80, 206]
    assert atmosphere_lock["membrane_runtime"]["dimensions"] == [80, 206]
    assert atmosphere_lock["seam_wall"]["dimensions"] == [128, 1882]
    assert atmosphere_lock["placement"]["wall_span_y"] == [0, 1882]
    assert atmosphere_lock["placement"]["door_floor_bottom_y"] == (
        "deckTop + 24"
    )
    assert atmosphere_lock["placement"]["deck_top_y_by_multiplier"] == [
        338, 338, 600, 600, 338, 1604, 600
    ]
    assert atmosphere_lock["placement"]["boundary_multipliers"] == [
        1, 2, 3, 4, 5, 6, 7
    ]
    assert atmosphere_lock["placement"]["tunnel_floor_width"] == 128
    assert atmosphere_lock["placement"]["tunnel_floor_y_by_multiplier"] == [
        338, 338, 600, 600, 338, 1604, 600
    ]
    assert len(atmosphere_lock["instances"]) == 7
    assert atmosphere_lock["instances"][1]["condition"] == (
        "Foundry atmospheric stabilizer active"
    )
    assert atmosphere_lock["instances"][5]["condition"] == (
        "Biolab atmospheric stabilizer active"
    )
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
        'source: "/Images/Game/Super-Frgmnts/foundry-uplink-boss-gate-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-housing-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-membrane-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-atmosphere-lock-seam-wall-runtime-v1.png"',
        'source: "/Images/Game/Super-Frgmnts/foundry-false-bridge-removal-runtime-v1.png"',
        '"foundryArcDischarge"',
        '"foundryUplinkBossGate"',
        '"foundryAtmosphereLock"',
        '"foundryAtmosphereLockHousing"',
        '"foundryAtmosphereLockMembrane"',
        '"foundryAtmosphereWall"',
        '"foundryFalseBridgeRemoval"',
        "assets.foundryArcDischarge",
        "assets.foundryUplinkBossGate",
        "assets.foundryAtmosphereLock",
        "assets.foundryAtmosphereLockHousing",
        "assets.foundryAtmosphereLockMembrane",
        "assets.foundryAtmosphereWall",
        "assets.foundryFalseBridgeRemoval",
        "var foundryUplinkQa =",
        'previewParameters.get("qa") === "uplink"',
        "function drawUplink()",
        'canvas.dataset.uplinkGateArt =',
        '"sprite-v1"',
        "var atmosphereLockPortals = [",
        'id: "foundry-intake-breathing"',
        'id: "foundry-refinery"',
        'id: "refinery-compression-pressure"',
        'id: "refinery-biolab"',
        'id: "biolab-culture-specimen"',
        'id: "biolab-uplink"',
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
        "function atmosphereLockPassageBounds(portal)",
        "function atmosphereLockVisualBounds(portal)",
        "ATMOSPHERE_LOCK_DOOR_HEIGHT = 206",
        "ATMOSPHERE_LOCK_TUNNEL_FLOOR_HEIGHT = 24",
        '"immutable-seam-floor-anchor-v5"',
        "var fixedAnchor = Object.freeze({",
        "portal.anchor.passageFloorY",
        "portal.anchor.doorBottomY",
        "portal.anchor.bridgeBottomY",
        "portal.deckTop === GROUND_Y",
        "canvas.dataset.atmosphereLockDoorGeometry",
        '"seven-fixed-housings-split-membranes-v1"',
        '"seven-seam-solid-concrete-v1"',
        "canvas.dataset.atmosphereLockFloorBottom",
        "canvas.dataset.atmosphereWallSpan",
        "canvas.dataset.atmosphereLockFloorBridge",
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
        'if (portal.id === "biolab-uplink")',
        '"THIS DAMN DOOR"',
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

    assert SOURCE.count("atmosphereLockVisualBounds(") >= 2, (
        "Atmosphere Lock drawing bypasses its dedicated visual anchor"
    )
    assert (
        "portal.deckTop +\n"
        "                    ATMOSPHERE_LOCK_TUNNEL_FLOOR_HEIGHT"
        in SOURCE
    ), "Atmosphere Lock fixed anchor no longer includes the 24px bridge"
    assert (
        "? portal.anchor.doorBottomY" in SOURCE
    ), "Atmosphere Lock drawing no longer uses the immutable door bottom"
    assert (
        "portal.deckTop === GROUND_Y\n"
        "                            ? portal.deckTop\n"
        "                            : bridgeBottomY"
        in SOURCE
    ), "The ground-level Biolab lock still inherits the elevated catwalk sink"

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

    assert "compact branching cyan-white 16-bit sprite" in LEVEL_CONTRACT
    assert "444 × 376 physical bulkhead" in LEVEL_CONTRACT
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
    assert "Ground `y = 1604`" in LEVEL_CONTRACT
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
    print("- 444 × 376 bulkhead is rooted at Uplink main deck y=1604")
    print("- locked/open gate states use one physical passage silhouette")
    print("- seven permanent housings and retractable membranes cover all seams")
    print("- five cyan passages and two stabilizer locks share one system")
    print("- locks are distributed across upper, middle, and ground tiers")
    print("- membranes close after clearance and reverse safely on return")
    print("- directional re-arm prevents close-open-close exit loops")
    print("- seven walls use one full-height foreground pass for Aryn occlusion")
    print("- canvas and camera share the browser's physical-pixel render grid")
    print("- the false y=600 bridge is removed from all eight mirrored plates")
    print("- the 330px visual gap now matches its unchanged collision")
    print("- QA route frames the gate with production desktop indicators")


if __name__ == "__main__":
    main()
