#!/usr/bin/env python3
"""Verify the four-plate Western Signal Flats Overworld expansion."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
OVERWORLD = ROOT / "Design/Super-Frgmnts/Overworld"
FAMILY = OVERWORLD / "Western-Signal-Flats"
MANIFEST = FAMILY / "western-signal-flats-runtime-v1.json"
LAYOUT = OVERWORLD / "overworld-layout.json"
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def verify_plate(path: Path) -> Image.Image:
    assert path.exists(), f"Missing {path.relative_to(ROOT)}"
    image = Image.open(path).convert("RGB")
    assert image.size == (1672, 941), (
        f"{path.name}: expected 1672x941, received {image.size}"
    )
    return image


def seam_delta(left: Image.Image, right: Image.Image) -> float:
    left_edge = left.crop((left.width - 1, 0, left.width, left.height))
    right_edge = right.crop((0, 0, 1, right.height))
    means = ImageStat.Stat(
        ImageChops.difference(left_edge, right_edge)
    ).mean
    return sum(means) / 3


def seam_structure_delta(
    left: Image.Image,
    right: Image.Image,
    width: int = 96,
) -> float:
    left_edge = left.crop(
        (left.width - width, 0, left.width, left.height)
    ).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    right_edge = right.crop((0, 0, width, right.height))
    means = ImageStat.Stat(
        ImageChops.difference(left_edge, right_edge)
    ).mean
    return sum(means) / 3


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    layout = json.loads(LAYOUT.read_text(encoding="utf-8"))

    assert manifest["status"] == "integrated-local-review"
    assert manifest["scene"] == "overworld"
    assert manifest["plate"]["groundY"] == 744
    assert manifest["world"]["plateCount"] == 4
    assert manifest["world"]["width"] == 6688
    assert manifest["world"]["originalOverworldOriginX"] == 1672
    assert manifest["world"]["plateOrder"] == [
        "western_signal_flats",
        "landing_flats",
        "dras_outpost",
        "coreworks_threshold",
    ]
    assert manifest["optional"] is True
    assert manifest["gatesFoundry"] is False

    assignments = {
        assignment["id"]: assignment
        for assignment in manifest["assignments"]
    }
    assert {
        key: assignments[key]["x"]
        for key in assignments
    } == {
        "survey_echo": 330,
        "recover_trillian": 690,
        "field_harness": 1080,
        "sealed_salvage": 1430,
    }
    assert sum(
        assignment["rewardCredits"]
        for assignment in assignments.values()
    ) == 7
    assert set(manifest["abilities"]) == {
        "signal_sweep",
        "trillian_follow",
        "trillian_powered_launch",
        "trillian_salvage_breach",
    }

    assert layout["version"] == 3
    assert layout["coordinate_system"]["world_width"] == 6688
    assert layout["coordinate_system"]["plate_seams_x"] == [
        1672,
        3344,
        5016,
    ]
    assert [plate["id"] for plate in layout["plates"]] == (
        manifest["world"]["plateOrder"]
    )

    west = verify_plate(
        ROOT / manifest["plate"]["production"]
    )
    runtime = verify_plate(ROOT / manifest["plate"]["runtime"])
    landing = verify_plate(
        OVERWORLD
        / "Production/Plates/overworld-landing-flats-v1.png"
    )
    assert ImageChops.difference(west, runtime).getbbox() is None
    assert seam_delta(west, landing) <= 0.1
    assert seam_structure_delta(west, landing) <= 5
    assert manifest["seamValidation"] == {
        "boundaryWidth": 1,
        "maxBoundaryDelta": 0.1,
        "contextWidth": 96,
        "maxStructureDelta": 5,
        "reviewGuideLine": False,
    }

    for review_name in (
        "overworld-four-plate-contact-v1.png",
        "western-to-landing-seam-audit-v1.png",
    ):
        assert (FAMILY / "Reviews" / review_name).exists()

    required_runtime_tokens = (
        "var OVERWORLD_ORIGIN_X = WIDTH;",
        "SCREEN_COUNT = isOverworld",
        "assets.background0 = assets.overworldWest;",
        "overworld-western-signal-flats-v1.png",
        'id: "survey-echo"',
        'id: "recover-trillian"',
        'id: "field-harness"',
        'id: "sealed-salvage"',
        "function activateSignalSweep()",
        "function activateNearbyOverworldAssignment()",
        "function updateTrillian(delta)",
        "function drawTrillian()",
        "function drawOverworldAssignments()",
        'canvas.dataset.trillianDamage = "noncombat-breach"',
        'canvas.dataset.overworldHawkState =',
        '"world-space-sky-pass"',
    )
    for token in required_runtime_tokens:
        assert token in SOURCE, f"Missing western runtime token: {token}"

    assert 'makeEnemy("trillian"' not in SOURCE
    assert "gatesFoundry = true" not in SOURCE
    assert 'id: "service-worker-droid"' not in SOURCE

    print("SUPER FRGMNTS Western Signal Flats: PASS")
    print("- four exact 1672 x 941 plates form a 6688-pixel world")
    print("- western-to-landing seam passes boundary and landscape checks")
    print("- four optional assignments award seven surface credits")
    print("- Signal Sweep and Trillian remain live without ambient-object errands")
    print("- no western assignment gates the existing Foundry route")


if __name__ == "__main__":
    main()
