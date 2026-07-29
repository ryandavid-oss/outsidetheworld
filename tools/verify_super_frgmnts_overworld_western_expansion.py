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
    left_edge = left.crop((left.width - 8, 0, left.width, left.height))
    right_edge = right.crop((0, 0, 8, right.height))
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
        "worker_droid_service": 4524,
    }
    assert sum(
        assignment["rewardCredits"]
        for assignment in assignments.values()
    ) == 9
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
    assert seam_delta(west, landing) <= 16

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
        'id: "service-worker-droid"',
        "function activateSignalSweep()",
        "function activateNearbyOverworldAssignment()",
        "function updateTrillian(delta)",
        "function drawTrillian()",
        "function drawOverworldAssignments()",
        'canvas.dataset.trillianDamage = "noncombat-breach"',
        'canvas.dataset.overworldHawkState =',
        '"guide-circle"',
    )
    for token in required_runtime_tokens:
        assert token in SOURCE, f"Missing western runtime token: {token}"

    assert 'makeEnemy("trillian"' not in SOURCE
    assert "gatesFoundry = true" not in SOURCE

    print("SUPER FRGMNTS Western Signal Flats: PASS")
    print("- four exact 1672 x 941 plates form a 6688-pixel world")
    print("- western-to-landing seam stays within the approved color delta")
    print("- five optional assignments award nine surface credits")
    print("- Signal Sweep, Trillian, hawk guidance, and droid service are live")
    print("- no western assignment gates the existing Foundry route")


if __name__ == "__main__":
    main()
