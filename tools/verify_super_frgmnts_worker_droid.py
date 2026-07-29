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
    assert manifest["behavior"]["optionalAssignment"] is None
    assert manifest["behavior"]["discoveryHook"] is False
    assert manifest["behavior"]["renderScale"] == 0.7
    assert manifest["behavior"]["talkable"] == "future"
    assert manifest["behavior"]["hoverAltitude"] == 6
    assert manifest["behavior"]["serviceDescent"] == 5
    assert manifest["behavior"]["driftSpeed"] == 18

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
        'canvas.dataset.workerDroidHostile = "false"',
        'canvas.dataset.workerDroidRole =',
        '"portal-repair-standby"',
        'canvas.dataset.workerDroidTalkable = "future";',
        'canvas.dataset.workerDroidDiscovery = "false";',
        'canvas.dataset.workerDroidScale = "0.70";',
        "OVERWORLD_ORIGIN_X + WIDTH * 2 + 1260;",
        "OVERWORLD_ORIGIN_X + WIDTH * 2 + 1160;",
        "OVERWORLD_ORIGIN_X + WIDTH * 2 + 1340;",
        "var WORKER_DROID_HOVER_BOTTOM_Y = GROUND_Y - 6;",
        "var WORKER_DROID_DRAW_WIDTH = 88;",
        "var WORKER_DROID_DRAW_HEIGHT = 85;",
    )
    for fragment in required_fragments:
        assert fragment in SOURCE, (
            f"Worker droid runtime registration is missing: {fragment}"
        )

    assert 'makeEnemy("workerDroid"' not in SOURCE
    assert "enemies.push(workerDroid)" not in SOURCE
    assert 'enemy.type === "workerDroid"' not in SOURCE
    assert 'id: "service-worker-droid"' not in SOURCE
    assert "OUTPOST_DROID_ASSIGNMENT_X" not in SOURCE

    print("SUPER FRGMNTS Overworld worker droid: PASS")
    print("- two validated 25-frame animation states")
    print("- portal-apron drift and near-ground service behavior registered")
    print("- 70% render scale keeps the droid subordinate to the player")
    print("- no discovery hook, prompt, reward, or current conversation")
    print("- future portal-repair and talk roles are reserved without activating them")
    print("- friendly, non-solid, absent from every enemy system")
    print("- both 720x700 runtime atlases include transparent padding")


if __name__ == "__main__":
    main()
