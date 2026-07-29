#!/usr/bin/env python3
"""Verify the Skree source, runtime atlas, and enemy-type registration."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FAMILY = ROOT / "Design/Super-Frgmnts/Foundry/Enemies/Skree"
SOURCE_MANIFEST = FAMILY / "Raw/skree-source-v1.json"
RUNTIME_MANIFEST = FAMILY / "skree-runtime-v1.json"
RUNTIME_IMAGE = (
    ROOT / "Images/Game/Super-Frgmnts/enemy-skree-walk-sheet-v1.png"
)
SOURCE = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")


def main() -> None:
    source_manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    runtime_manifest = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))

    assert len(source_manifest["frames"]) == 25
    assert source_manifest["meta"]["size"] == {"w": 4750, "h": 4010}
    assert runtime_manifest["workingName"] == "Skree"
    assert runtime_manifest["runtimeType"] == "skree"
    assert runtime_manifest["productionPopulation"] is False
    assert runtime_manifest["validation"]["result"] == (
        "pass-with-source-warning"
    )
    assert len(
        runtime_manifest["validation"]["rightEdgeContactFrames"]
    ) == 19

    atlas = Image.open(RUNTIME_IMAGE).convert("RGBA")
    assert atlas.size == (800, 720), (
        f"Skree runtime atlas: expected 800x720, got {atlas.size}"
    )
    for index in range(25):
        x = index % 5 * 160
        y = index // 5 * 144
        frame = atlas.crop((x, y, x + 160, y + 144))
        bound = frame.getchannel("A").getbbox()
        assert bound is not None, f"Skree runtime frame {index} is blank"
        assert bound[0] > 0 and bound[1] > 0
        assert bound[2] < 160 and bound[3] < 144

    required_runtime_fragments = (
        "skree: {",
        '"skree",',
        'skree: { width: 92, height: 120 }',
        'if (enemy.type === "skree") {',
        'skree: "SKREE"',
        "function drawSkreeEnemy(enemy)",
        'enemy.type === "skree"',
    )
    for fragment in required_runtime_fragments:
        assert fragment in SOURCE, (
            f"Skree runtime registration is missing: {fragment}"
        )

    print("SUPER FRGMNTS Skree enemy type: PASS")
    print("- source atlas: 25 frames, 5x5, 53 ms each")
    print("- source warning: 19 frames touch the right cell boundary")
    print("- runtime atlas: 800x720 RGBA with per-frame padding")
    print("- runtime type: skree, ground patrol, not production-populated")


if __name__ == "__main__":
    main()
