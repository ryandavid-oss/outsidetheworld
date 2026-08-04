#!/usr/bin/env python3
"""Verify the local SUPER FRGMNTS Revision 3 packet and preview integration."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
PHASE = ROOT / "Design/Super-Frgmnts/Overworld/Phase-3"


def require(path: Path) -> Path:
    if not path.exists():
        raise AssertionError(f"Missing required Revision 3 artifact: {path}")
    return path


def verify_image(
    path: Path,
    *,
    expected_size: tuple[int, int] | None = None,
    alpha: bool | None = None,
) -> None:
    require(path)
    with Image.open(path) as image:
        image.load()
        if expected_size is not None:
            assert image.size == expected_size, (path, image.size, expected_size)
        if alpha is True:
            assert image.mode == "RGBA", (path, image.mode)
            alpha_channel = image.getchannel("A")
            assert alpha_channel.getbbox() is not None, f"No visible alpha: {path}"
            corners = (
                alpha_channel.getpixel((0, 0)),
                alpha_channel.getpixel((image.width - 1, 0)),
                alpha_channel.getpixel((0, image.height - 1)),
                alpha_channel.getpixel((image.width - 1, image.height - 1)),
            )
            assert corners == (0, 0, 0, 0), (path, corners)


def load_manifest(
    path: Path,
    revision: str,
    statuses: tuple[str, ...],
) -> dict:
    with require(path).open(encoding="utf-8") as source:
        manifest = json.load(source)
    assert manifest["revision"] == revision
    assert manifest["status"] in statuses
    return manifest


def verify_release_scope(scope: dict) -> None:
    assert scope["live_game_modified"] is True
    assert scope["integrated"] is True
    assert scope["deployed"] is True
    assert scope["committed"] is True


def verify_local_integration() -> None:
    source = require(ROOT / "super_frgmnts.html").read_text(encoding="utf-8")
    for token in (
        'previewParameters.get("preview") === "overworld"',
        "aryn-ship-v2.png",
        "dras-ehdre-runtime-v1.png",
        "aryn-command-rest-runtime-v1.png",
        "aryn-dialogue-portrait-runtime-v3.png",
        "dras-dialogue-portrait-runtime-v2.png",
        "veyra-camp-dog-walk-sheet-v3.png",
        "veyra-camp-dog-sniff-sheet-v3.png",
        "drawOverworldVolcano()",
        "startArrivalDialogue()",
        'loadAndConfigureEpisodeScene("foundry")',
    ):
        assert token in source, f"Missing Revision 3 runtime integration: {token}"


def main() -> None:
    ship = load_manifest(
        PHASE / "Ship/ship-revision-3a-manifest.json",
        "3A",
        ("approved-production",),
    )
    assert ship["integration"]["integrated"] is True
    assert ship["integration"]["deployed"] is True
    assert ship["integration"]["committed"] is True

    verify_image(
        PHASE / "Dras/Assets/dras-transparent-master-v1.png",
        alpha=True,
    )
    verify_image(
        PHASE / "Dras/Assets/dras-runtime-candidate-v1.png",
        expected_size=(96, 112),
        alpha=True,
    )
    dras = load_manifest(
        PHASE / "Dras/dras-revision-3b-manifest.json",
        "3B",
        ("approved-production",),
    )
    assert dras["runtime_candidate"]["visible_height"] == 104
    assert dras["runtime_candidate"]["world_anchor_local_plate_2"] == {
        "x": 280,
        "ground_y": 744,
    }
    verify_release_scope(dras["scope"])

    dialogue = load_manifest(
        PHASE / "Dialogue/dialogue-revision-3c-manifest.json",
        "3C",
        ("approved-production",),
    )
    assert dialogue["recommendation"]["character_dialogue"] == "field-relay"
    assert dialogue["recommendation"]["terminal_and_system_dialogue"] == (
        "coreworks-archive"
    )
    assert dialogue["canon_cards"] == 36
    verify_release_scope(dialogue["scope"])

    portraits = load_manifest(
        PHASE / "Dialogue/dialogue-portrait-revision-3g-manifest.json",
        "3G",
        ("approved-production",),
    )
    verify_release_scope(portraits["scope"])
    for portrait_name in (
        "aryn-dialogue-portrait-v2.png",
        "dras-dialogue-portrait-v2.png",
    ):
        verify_image(
            PHASE / "Dialogue/Assets" / portrait_name,
            expected_size=(1318, 1318),
            alpha=True,
        )
    for portrait_name in (
        "aryn-dialogue-portrait-runtime-v2.png",
        "dras-dialogue-portrait-runtime-v2.png",
    ):
        verify_image(
            PHASE / "Dialogue/Assets" / portrait_name,
            expected_size=(512, 512),
            alpha=True,
        )
    assert portraits["dras_world_alignment"] == {
        "physics_ground_y": 744,
        "player_physics_height": 100,
        "player_draw_height": 112,
        "visible_boot_y": 756,
        "dras_draw_top_y": 644,
        "dras_draw_height": 112,
    }

    aryn_portrait = load_manifest(
        PHASE / "Dialogue/dialogue-portrait-revision-3i-manifest.json",
        "3I",
        ("approved-production",),
    )
    verify_release_scope(aryn_portrait["scope"])
    assert aryn_portrait["portrait"]["character"] == "Aryn Sol-Mavi"
    assert aryn_portrait["portrait"]["generation_path"] == (
        "built-in ImageGen with local chroma-key removal"
    )
    verify_image(
        PHASE / "Dialogue/Assets/aryn-dialogue-portrait-v3.png",
        expected_size=(1254, 1254),
        alpha=True,
    )
    verify_image(
        PHASE / "Dialogue/Assets/aryn-dialogue-portrait-runtime-v3.png",
        expected_size=(512, 512),
        alpha=True,
    )

    atmosphere = load_manifest(
        PHASE / "Outpost/outpost-revision-3h-manifest.json",
        "3H",
        ("approved-production",),
    )
    verify_release_scope(atmosphere["scope"])
    assert atmosphere["atmosphere"]["cloud_layers"] == 3
    assert atmosphere["atmosphere"]["distant_birds"] == 5
    assert atmosphere["camp_life"]["dras_local_plate_2_x"] == 560
    assert atmosphere["camp_life"]["dog_local_plate_2_x"] == 810
    verify_image(
        PHASE / "Outpost/Assets/veyra-camp-dog-master-v1.png",
        expected_size=(1514, 1039),
        alpha=True,
    )
    verify_image(
        PHASE / "Outpost/Assets/veyra-camp-dog-runtime-v1.png",
        expected_size=(96, 64),
        alpha=True,
    )
    assert atmosphere["dialogue_actions"] == {
        "left": "Skip",
        "right": "Continue",
        "confirmation_left": "Skip scene",
        "confirmation_right": "Keep listening",
    }

    closing_pass = load_manifest(
        PHASE / "Outpost/outpost-revision-3j-manifest.json",
        "3J",
        ("approved-production",),
    )
    verify_release_scope(closing_pass["scope"])
    assert closing_pass["volcano"]["source_plate_preserved"] is True
    assert closing_pass["volcano"]["seam_redraw"] is False
    assert closing_pass["camp_dog"]["walk_frames"] == 2
    assert closing_pass["camp_dog"]["camp_travel_pixels"] == 130
    for walk_master in (
        "veyra-camp-dog-walk-contact-master-v2.png",
        "veyra-camp-dog-walk-pass-master-v2.png",
    ):
        verify_image(
            PHASE / "Outpost/Assets" / walk_master,
            alpha=True,
        )
    for walk_runtime in (
        "veyra-camp-dog-walk-contact-runtime-v2.png",
        "veyra-camp-dog-walk-pass-runtime-v2.png",
    ):
        verify_image(
            PHASE / "Outpost/Assets" / walk_runtime,
            expected_size=(96, 64),
            alpha=True,
        )
    verify_image(
        PHASE / "Outpost/Assets/veyra-camp-dog-walk-sheet-v2.png",
        expected_size=(192, 64),
        alpha=True,
    )
    source = (ROOT / "super_frgmnts.html").read_text(encoding="utf-8")
    assert "x: 1376,\n                        y: 680" not in source

    outpost = load_manifest(
        PHASE / "Outpost/outpost-revision-3d-manifest.json",
        "3D",
        ("approved-production",),
    )
    assert outpost["anchors_local_plate_2"]["dras"] == {
        "x": 280,
        "feet_y": 744,
    }
    for zone in outpost["anchors_local_plate_2"]["zones"].values():
        left, top, right, bottom = zone
        assert 0 <= left < right <= 1672
        assert 0 <= top < bottom <= 941
    verify_release_scope(outpost["scope"])

    aryn = load_manifest(
        PHASE / "Aryn/aryn-revision-3e-manifest.json",
        "3E",
        ("approved-production",),
    )
    assert aryn["runtime"]["recommendation"] == "command-rest"
    verify_release_scope(aryn["scope"])
    verify_image(
        PHASE / "Aryn/Assets/aryn-command-rest-runtime-candidate-v1.png",
        expected_size=(112, 112),
        alpha=True,
    )

    review_images = (
        PHASE / "Dras/Reviews/dras-scale-study-v1.png",
        PHASE / "Dialogue/Reviews/dialogue-directions-comparison-v1.png",
        PHASE / "Outpost/Reviews/outpost-blocking-contact-sheet-v1.png",
        PHASE / "Morning-Review/revision-3-morning-approval-sheet-v1.png",
    )
    for path in review_images:
        verify_image(path)

    verify_local_integration()
    print("Revision 3 packet: PASS")
    print("Aryn and Dras runtime alpha: PASS")
    print("3A–3J manifests and production scope guards: PASS")
    print("Review images: PASS")
    print("super_frgmnts.html local preview integration: PASS")


if __name__ == "__main__":
    main()
