#!/usr/bin/env python3
"""Verify the local SUPER FRGMNTS Revision 1A title-screen integration."""

from __future__ import annotations

import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
TITLE = ROOT / "Design" / "Super-Frgmnts" / "Title"
ART = TITLE / "Assets" / "super-frgmnts-title-coreworks-v1.png"
MANIFEST = TITLE / "title-screen-revision-1a-manifest.json"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        signature = image.read(24)
    assert signature[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    return struct.unpack(">II", signature[16:24])


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert ART.exists(), f"Missing title artwork: {ART}"
    assert png_size(ART) == (1672, 941)
    assert manifest["revision"] == "1A"
    assert manifest["status"] == "approved-production"
    assert manifest["scope"] == {
        "live_game_modified": True,
        "integrated": True,
        "committed": True,
        "deployed": True,
        "preview_route": "super_frgmnts.html",
    }

    required_tokens = (
        "super-frgmnts-title-coreworks-v1.png",
        "Season One // Veyra",
        "Episode 01 // <strong>Arrival on Veyra</strong>",
        "A distress signal from a world the Fleet abandoned.",
        "Begin episode",
        "title-screen__atmosphere",
        "title-screen__signal",
        "title-screen__vesperite",
        "@keyframes title-scene-breathe",
        "@keyframes title-dust-drift",
        "@keyframes title-signal-pulse",
        "@media (prefers-reduced-motion: reduce)",
        'previewParameters.get("episode") === "01"',
        'episodeStage === "overworld"',
        'episodeStage === "foundry"',
        'previewParameters.get("autostart") === "1"',
        "?episode=01&stage=overworld&autostart=1",
        "?episode=01&stage=foundry&autostart=1",
        "activateTitleAction()",
        'event.code === "Enter" || event.code === "Space"',
        "Opening Episode 01. Arrival on Veyra.",
    )
    for token in required_tokens:
        assert token in source, f"Missing title-screen contract: {token}"

    assert "/Images/Game/super-frgmnts-title-art.png" not in source
    assert manifest["launch"]["duplicate_title"] is False
    assert manifest["launch"]["route"].endswith(
        "?episode=01&stage=overworld&autostart=1"
    )
    assert manifest["launch"]["foundry_handoff"].endswith(
        "?episode=01&stage=foundry&autostart=1"
    )
    assert manifest["motion"]["reduced_motion_static"] is True

    print("SUPER FRGMNTS title-screen Revision 1A: PASS")
    print("- native 1672 x 941 Coreworks title artwork is integrated")
    print("- Season One and Episode 01 identity are present")
    print("- keyboard, pointer, and automatic arrival handoff are present")
    print("- atmospheric motion and reduced-motion safeguards are present")
    print("- production integration and deployment scope is recorded")


if __name__ == "__main__":
    main()
