#!/usr/bin/env python3
"""Verify the friendly Overworld worker droid and both animation states."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = (
    ROOT
    / "Design/Super-Frgmnts/Overworld/Phase-3/Outpost/Worker-Droid"
)
MANIFEST = FAMILY / "worker-droid-runtime-v1.json"
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def verify_atlas(path: Path) -> None:
    atlas = Image.open(path).convert("RGBA")
    assert atlas.size == (720, 700), (
        f"{path.name}: expected 720x700, got {atlas.size}"
    )
    for index in range(25):
        x = index % 5 * 144
        y = index // 5 * 140
        frame = atlas.crop((x, y, x + 144, y + 140))
        bound = frame.getchannel("A").getbbox()
        assert bound is not None, f"{path.name}: frame {index} is blank"
        assert bound[0] > 0 and bound[1] > 0
        assert bound[2] < 144 and bound[3] < 140


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["workingName"] == "Worker Droid"
    assert manifest["hostile"] is False
    assert manifest["solid"] is False
    assert manifest["scene"] == "overworld"

    animations = {
        animation["key"]: animation
        for animation in manifest["animations"]
    }
    assert set(animations) == {"drift", "service"}
    assert animations["drift"]["source"]["frameCount"] == 25
    assert animations["drift"]["source"]["frameDurationMs"] == 58
    assert animations["service"]["source"]["frameCount"] == 25
    assert animations["service"]["source"]["frameDurationMs"] == 70
    assert animations["drift"]["validation"]["edgeContactFrames"]["top"]
    assert animations["service"]["validation"]["edgeContactFrames"]["left"]
    assert animations["service"]["validation"]["edgeContactFrames"]["right"]
    assignment = manifest["behavior"]["optionalAssignment"]
    assert assignment["id"] == "service-worker-droid"
    assert assignment["worldX"] == 4524
    assert assignment["prerequisite"] == "Dras first contact"
    assert assignment["rewardCredits"] == 2

    for animation in animations.values():
        verify_atlas(ROOT / animation["runtime"]["image"])

    required_fragments = (
        "workerDroidDrift: {",
        "workerDroidService: {",
        '"workerDroidDrift",',
        '"workerDroidService",',
        "var workerDroid = {",
        "function resetWorkerDroid()",
        "function updateWorkerDroid(delta)",
        "function drawWorkerDroid()",
        'state: "drift"',
        'id: "worker-droid"',
        'workerDroid.state = "service"',
        'canvas.dataset.workerDroidHostile = "false"',
        'id: "service-worker-droid"',
        "OUTPOST_DROID_ASSIGNMENT_X",
    )
    for fragment in required_fragments:
        assert fragment in SOURCE, (
            f"Worker droid runtime registration is missing: {fragment}"
        )

    assert 'makeEnemy("workerDroid"' not in SOURCE
    assert "enemies.push(workerDroid)" not in SOURCE
    assert 'enemy.type === "workerDroid"' not in SOURCE

    print("SUPER FRGMNTS Overworld worker droid: PASS")
    print("- two validated 25-frame animation states")
    print("- drift and periodic low-hover service behavior registered")
    print("- Dras-cleared optional service assignment awards two credits")
    print("- friendly, non-solid, absent from every enemy system")
    print("- both 720x700 runtime atlases include transparent padding")


if __name__ == "__main__":
    main()
