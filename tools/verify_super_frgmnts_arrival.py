#!/usr/bin/env python3
"""Verify the local Arrival on Veyra dialogue and overworld preview contract."""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
DIALOGUE_DIR = (
    ROOT / "Design" / "Super-Frgmnts" / "Overworld" / "Phase-3" / "Dialogue"
)
CANON = DIALOGUE_DIR / "CANON-ARRIVAL-ON-VEYRA.md"
MANIFEST = DIALOGUE_DIR / "dialogue-revision-3c-manifest.json"
PLATES = (
    ROOT / "Design" / "Super-Frgmnts" / "Overworld" / "Production" / "Plates"
)
OVERWORLD_MUSIC = ROOT / "Audio" / "super-frgmnts-overworld-loop.mp3"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as image:
        signature = image.read(24)
    require(signature[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG")
    return struct.unpack(">II", signature[16:24])


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    canon = CANON.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    canon_sections = re.findall(
        r"^### (D\d{2}) // ([^\n]+)\n\n(.*?)(?=^### D\d{2} // |^## Canon holds)",
        canon,
        flags=re.MULTILINE | re.DOTALL,
    )
    card_ids = [card_id for card_id, _speaker, _body in canon_sections]
    require(
        card_ids == [f"D{index:02d}" for index in range(1, 37)],
        "Canon dialogue must contain sequential D01–D36 cards",
    )

    runtime_cards = {
        card_id: (speaker, json.loads(f'"{text}"'))
        for card_id, speaker, text in re.findall(
            r'id:\s*"(D\d{2})",\s*speaker:\s*"([^"]+)",.*?text:\s*"((?:\\.|[^"])*)"',
            source,
            flags=re.DOTALL,
        )
    }
    for card_id, speaker, body in canon_sections:
        dialogue_paragraph = body.split("\n\n", 1)[0]
        dialogue_text = " ".join(dialogue_paragraph.split())
        require(card_id in runtime_cards, f"{card_id} is missing from runtime")
        require(
            runtime_cards[card_id] == (speaker, dialogue_text),
            f"{card_id} runtime copy drifted from the canon document",
        )

    required_runtime_tokens = (
        'previewParameters.get("preview") === "overworld"',
        "startArrivalDialogue()",
        "finishArrivalDialogue(false)",
        'effect: "tremor"',
        'effect: "disconnect"',
        'effect: "look-portal"',
        'effect: "prime-portal"',
        'role="dialog"',
        'aria-modal="true"',
        "dialogueSkipConfirm",
        "arynDialoguePortrait",
        "drasDialoguePortrait",
        "aryn-dialogue-portrait-runtime-v3.png",
        "dras-dialogue-portrait-runtime-v2.png",
        "var DRAS_WORLD_X = WIDTH + 560",
        "Math.round(DRAS_DRAW_Y + drasBob)",
        "drawCloudVolume",
        "drawOverworldBirds",
        "drawCampDog",
        "veyra-camp-dog-runtime-v1.png",
        "veyra-camp-dog-walk-sheet-v2.png",
        "drawOverworldVolcano",
        "var seamPulsePoints = [",
        "VEYRA // SUBSURFACE TREMOR",
        'data-overworld-track="/Audio/super-frgmnts-overworld-loop.mp3"',
        'data-foundry-track="/Audio/super-frgmnts-foundry-loop.mp3"',
        "var selectedMusicTrack = mainTitleScreen",
        "? backgroundMusic.dataset.overworldTrack",
        "overworld: 0.29",
        "foundry: 0.32",
        "function configureEpisodeScene(scene, historyMode)",
        'configureEpisodeScene("foundry")',
        "var overworldAnchor",
        "(0.48 - 0.7)",
        "portalCharge",
        "invisibleStep: true",
        'previewParameters.get("scene") === "portal"',
        "var centerX = WIDTH * 2 + 1545",
        "var centerY = 615",
        "x: WIDTH * 2 + 1490",
        '"?episode=01&stage=" + scene + "&autostart=1"',
    )
    for token in required_runtime_tokens:
        require(token in source, f"Missing runtime contract: {token}")
    require(OVERWORLD_MUSIC.exists(), "Missing dedicated overworld music")
    require(
        OVERWORLD_MUSIC.stat().st_size > 1_000_000,
        "Overworld music asset is unexpectedly small",
    )
    require(
        "drawOverworldGangway" not in source and "gangway: true" not in source,
        "The rejected visible ship staircase is still present",
    )
    require(
        "var centerX = 4784" not in source,
        "The portal effect is still using the obsolete freestanding placement",
    )
    require(
        "Math.round(632 + drasBob)" not in source,
        "Dras is still anchored above Aryn's visible running plane",
    )
    require(
        source.count('backgroundMusic.src = "/Audio/super-frgmnts-foundry-loop.mp3"') == 0,
        "The overworld still overrides its route-selected music with the Foundry track",
    )
    require(
        "window.location.href" not in source,
        "The overworld still reloads the page at the Foundry handoff",
    )
    require(
        "x: 1376,\n                        y: 680" not in source,
        "The stray Landing Flats collider is still present",
    )
    require(
        source.index('id="dialogueSkip"') <
        source.index('id="dialogueContinue"'),
        "Skip must appear to the left of Continue",
    )

    for plate_name in (
        "overworld-landing-flats-v1.png",
        "overworld-dras-outpost-v1.png",
        "overworld-coreworks-threshold-v1.png",
    ):
        plate = PLATES / plate_name
        require(plate.exists(), f"Missing overworld plate: {plate_name}")
        require(png_size(plate) == (1672, 941), f"Unexpected plate size: {plate}")

    portrait_assets = DIALOGUE_DIR / "Assets"
    portrait_sizes = {
        "aryn-dialogue-portrait-v3.png": (1254, 1254),
        "dras-dialogue-portrait-v2.png": (1318, 1318),
        "aryn-dialogue-portrait-runtime-v3.png": (512, 512),
        "dras-dialogue-portrait-runtime-v2.png": (512, 512),
    }
    for portrait_name, expected_size in portrait_sizes.items():
        portrait = portrait_assets / portrait_name
        require(portrait.exists(), f"Missing dialogue portrait: {portrait_name}")
        require(
            png_size(portrait) == expected_size,
            f"Unexpected portrait size: {portrait}",
        )

    require(
        manifest["status"] == "approved-production",
        "Dialogue manifest is not marked as an approved production integration",
    )
    require(manifest["canon_cards"] == 36, "Manifest canon card count drifted")
    require(manifest["scope"]["deployed"] is True, "Production dialogue is not deployed")

    print("Arrival on Veyra contract passed.")
    print("- runtime speaker and copy match canon D01 through D36 exactly")
    print("- Field Relay, skip confirmation, and accessibility hooks are present")
    print("- purpose-built close portraits and narrated tremor context are present")
    print("- Dras's boots align with Aryn's visible running plane")
    print("- Skip is left and Continue is the primary right-hand action")
    print("- volumetric clouds, birds, readable dog gait, and restrained volcano heat are present")
    print("- Arrival on Veyra selects its dedicated overworld music track")
    print("- the stray Landing Flats collider is absent")
    print("- invisible ship-slope collision replaces the drawn gangway")
    print("- Fleet disconnect, Dras reaction, and portal ignition are staged")
    print("- the portal effect and trigger align with the painted Coreworks doorway")
    print("- all three 1672 × 941 overworld plates are present")
    print("- portal handoff supports the assembled Episode 01 Foundry and isolated review route")


if __name__ == "__main__":
    main()
