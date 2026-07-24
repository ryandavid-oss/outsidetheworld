#!/usr/bin/env python3
"""Independently verify SUPER FRGMNTS expansion guide revision 3."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
GAME_FILE = ROOT / "super_frgmnts.html"
GUIDE_DIR = ROOT / "Design" / "Super-Frgmnts" / "Expansion-Guides"
MANIFEST_FILE = GUIDE_DIR / "collision-manifest.json"
BUILD_SCRIPT = ROOT / "tools" / "build_super_frgmnts_expansion_guides.py"

PLATE_WIDTH = 1672
PLATE_HEIGHT = 941
COMPOSITE_HEIGHT = 1882
PROTECT_TOP = 1121
GRID = 16

SOURCES = {
    "foundry": ROOT / "Images" / "Builder" / "signal-foundry-bg.png",
    "refinery": ROOT / "Images" / "Game" / "signal-foundry-refinery.png",
    "biolab": ROOT / "Images" / "Game" / "signal-foundry-biolab.png",
    "uplink": ROOT / "Images" / "Game" / "signal-foundry-uplink.png",
}

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def number(source: str, pattern: str, label: str) -> float:
    match = re.search(pattern, source, flags=re.MULTILINE | re.DOTALL)
    if not match:
        failures.append(f"could not read {label} from the live game")
        return 0
    return float(match.group(1))


def jump_rise(velocity: float, gravity: float, delta: float) -> float:
    y = 0.0
    minimum_y = 0.0
    vertical_velocity = -velocity
    while vertical_velocity < 0:
        vertical_velocity += gravity * delta
        y += vertical_velocity * delta
        minimum_y = min(minimum_y, y)
    return -minimum_y


def horizontal_gap(first: dict, second: dict) -> int:
    if min(first["x1"], second["x1"]) >= max(first["x0"], second["x0"]):
        return 0
    return max(first["x0"], second["x0"]) - min(first["x1"], second["x1"])


def verify_images(room: str, source_path: Path) -> None:
    canvas_path = GUIDE_DIR / f"{room}-vertical-expansion-canvas.png"
    mask_path = GUIDE_DIR / f"{room}-outpaint-mask-white-edit.png"
    guide_path = GUIDE_DIR / f"{room}-collision-guide.png"

    for path in (canvas_path, mask_path, guide_path):
        check(path.exists(), f"{room}: missing {path.name}")
    if not all(path.exists() for path in (canvas_path, mask_path, guide_path)):
        return

    source = Image.open(source_path).convert("RGBA")
    canvas = Image.open(canvas_path).convert("RGBA")
    mask = Image.open(mask_path).convert("L")
    guide = Image.open(guide_path)

    check(canvas.size == (PLATE_WIDTH, COMPOSITE_HEIGHT), f"{room}: canvas dimensions changed")
    check(mask.size == (PLATE_WIDTH, COMPOSITE_HEIGHT), f"{room}: mask dimensions changed")
    check(guide.size == (PLATE_WIDTH, COMPOSITE_HEIGHT), f"{room}: guide dimensions changed")

    upper_alpha = canvas.getchannel("A").crop((0, 0, PLATE_WIDTH, PLATE_HEIGHT))
    check(upper_alpha.getextrema() == (0, 0), f"{room}: upper canvas is not transparent")
    lower = canvas.crop((0, PLATE_HEIGHT, PLATE_WIDTH, COMPOSITE_HEIGHT))
    check(
        ImageChops.difference(source, lower).getbbox() is None,
        f"{room}: source plate pixels changed",
    )
    check(
        mask.crop((0, 0, PLATE_WIDTH, PROTECT_TOP)).getextrema() == (255, 255),
        f"{room}: editable mask region is not pure white",
    )
    check(
        mask.crop((0, PROTECT_TOP, PLATE_WIDTH, COMPOSITE_HEIGHT)).getextrema() == (0, 0),
        f"{room}: protected mask region is not pure black",
    )


def main() -> int:
    check(MANIFEST_FILE.exists(), "collision manifest is missing")
    if not MANIFEST_FILE.exists():
        print("FAIL: collision manifest is missing")
        return 1

    game_source = GAME_FILE.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    movement = manifest["movement_contract"]
    anchors = manifest["composite_anchors"]

    width = int(number(game_source, r"var WIDTH = (\d+);", "WIDTH"))
    height = int(number(game_source, r"var HEIGHT = (\d+);", "HEIGHT"))
    ground_y = int(number(game_source, r"var GROUND_Y = (\d+);", "GROUND_Y"))
    deepworks_y = int(
        number(game_source, r"var deepworksRooms = .*?y: (\d+),", "Deepworks y")
    )
    velocity = number(
        game_source,
        r"player\.vy = inDeepworks \? -\d+ : -(\d+);",
        "normal jump velocity",
    )
    gravity = number(game_source, r"player\.vy \+= (\d+) \* delta;", "gravity")
    delta_cap = number(
        game_source,
        r"Math\.min\((0\.\d+), \(now - lastFrame\)",
        "frame delta cap",
    )

    check((width, height) == (PLATE_WIDTH, PLATE_HEIGHT), "live game and plate dimensions differ")
    check(anchors["concrete_deck_y"] == PLATE_HEIGHT + ground_y, "deck coordinate is not direct")
    check(
        anchors["deepworks_floor_y"] == PLATE_HEIGHT + deepworks_y,
        "Deepworks coordinate is not direct",
    )
    check(anchors["concrete_deck_y"] == 1604, "expected concrete deck y=1604")
    check(anchors["deepworks_floor_y"] == 1816, "expected Deepworks y=1816")

    worst_rise = jump_rise(velocity, gravity, delta_cap)
    normal_rise = movement["normal_rise"]
    check(
        normal_rise + movement["jump_safety_margin"] <= worst_rise,
        f"normal rise {normal_rise} is unsafe at {delta_cap:.3f}s frames ({worst_rise:.2f}px)",
    )
    check(normal_rise % GRID == 0, "normal rise is not grid aligned")

    for room, room_data in manifest["rooms"].items():
        planned = room_data["planned_platforms"]
        for route in ("left-route", "right-route"):
            route_platforms = sorted(
                (platform for platform in planned if platform["role"] == route),
                key=lambda platform: platform["y"],
                reverse=True,
            )
            check(len(route_platforms) == 12, f"{room}: {route} does not have 12 bands")
            previous = {
                "x0": 0,
                "x1": PLATE_WIDTH,
                "y": anchors["concrete_deck_y"],
            }
            for platform in route_platforms:
                check(
                    previous["y"] - platform["y"] == normal_rise,
                    f"{room}: {route} has a non-{normal_rise}px rise",
                )
                check(
                    horizontal_gap(previous, platform) <= movement["max_horizontal_gap"],
                    f"{room}: {route} has an excessive horizontal gap",
                )
                previous = platform

        room_links = [
            platform for platform in planned if platform["role"] == "room-transition"
        ]
        check(len(room_links) == 2, f"{room}: expected two room-transition anchors")
        check(
            any(platform["x0"] == 0 for platform in room_links),
            f"{room}: left room link does not touch the edge",
        )
        check(
            any(platform["x1"] == PLATE_WIDTH for platform in room_links),
            f"{room}: right room link does not touch the edge",
        )
        check(
            all(platform["y"] == anchors["room_transition_y"] for platform in room_links),
            f"{room}: room links do not share the canonical elevation",
        )

        for platform in planned:
            check(
                platform["x1"] - platform["x0"] >= 144,
                f"{room}: {platform['role']} is narrower than 144px",
            )
            check(
                platform["x0"] % GRID == 0,
                f"{room}: {platform['role']} x0 is off the 16px grid",
            )
            if platform["y"] >= PROTECT_TOP:
                check(
                    not platform["bake_into_art"],
                    f"{room}: protected geometry is marked for generated artwork",
                )
            else:
                check(
                    platform["bake_into_art"],
                    f"{room}: editable geometry is not marked for generated artwork",
                )

    for room, source_path in SOURCES.items():
        verify_images(room, source_path)

    build_source = BUILD_SCRIPT.read_text(encoding="utf-8")
    check("/home/claude" not in build_source, "build script contains a Claude-only output path")
    check("/mnt/user-data" not in build_source, "build script contains a Claude-only input path")

    if failures:
        print(f"FAIL: {len(failures)} expansion-guide violations")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("PASS: revision-3 expansion guides match the live game")
    print(f"  game / plate          {width}×{height}")
    print(
        "  deck / Deepworks      "
        f"y={anchors['concrete_deck_y']} / y={anchors['deepworks_floor_y']}"
    )
    print(f"  worst-frame jump      {worst_rise:.2f}px")
    print(f"  normal route rise     {normal_rise}px")
    print(f"  route safety margin   {worst_rise - normal_rise:.2f}px")
    print(f"  transition elevation  y={anchors['room_transition_y']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
