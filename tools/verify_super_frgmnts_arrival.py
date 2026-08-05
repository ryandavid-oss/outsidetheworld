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
DIALOGUE_SOURCE = ROOT / "super_frgmnts_dialogue.md"
PLATES = (
    ROOT / "Design" / "Super-Frgmnts" / "Overworld" / "Production" / "Plates"
)
OVERWORLD_MUSIC = ROOT / "Audio" / "super-frgmnts-overworld-loop.mp3"
PLANET_TITLE = (
    ROOT / "Images/Game/Super-Frgmnts/planet-veyra-title-v1.png"
)
DESCENT_ASSETS = {
    "veyra-descent-deep-space-v1.png": (1672, 941),
    "veyra-descent-first-light-v1.png": (1672, 941),
    "veyra-descent-starry-night-v1.png": (1672, 941),
    "veyra-descent-low-approach-v1.png": (1672, 941),
    "aryn-ship-v2.png": (1008, 396),
}


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
    dialogue_source = DIALOGUE_SOURCE.read_text(encoding="utf-8")
    source_sections = re.findall(
        r"^\*\*(D\d{2}) · ([A-Z -]+)\*\* — [^\n]+\s*\n"
        r"(.*?)(?=^\*\*[DR]\d{2} · |^## |\Z)",
        dialogue_source,
        flags=re.MULTILINE | re.DOTALL,
    )
    card_ids = [card_id for card_id, _speaker, _body in source_sections]
    expected_ids = (
        [f"D{index:02d}" for index in range(1, 8)]
        + ["D09", "D10"]
        + [f"D{index:02d}" for index in range(19, 40)]
    )
    require(
        card_ids == expected_ids,
        "Revised arrival dialogue must preserve its intentional card cuts",
    )

    runtime_deck = source.split(
        "var dialogueCards = [",
        1,
    )[1].split("var legacyReturnDialogueCards = [", 1)[0]
    runtime_cards = [
        (card_id, speaker, json.loads(f'"{text}"'))
        for card_id, speaker, text in re.findall(
            r'id:\s*"(D\d{2})",\s*speaker:\s*"([^"]+)",.*?text:\s*"((?:\\.|[^"])*)"',
            runtime_deck,
            flags=re.DOTALL,
        )
    ]
    expected_cards = []
    for card_id, speaker, body in source_sections:
        dialogue_text = " ".join(
            line.strip()
            for line in body.splitlines()
            if line.strip() and not line.strip().startswith("*")
        )
        expected_cards.append((card_id, speaker, dialogue_text))
    require(
        [card[0] for card in runtime_cards] == expected_ids,
        "Runtime arrival card order drifted from the revised source",
    )
    for runtime_card, expected_card in zip(runtime_cards, expected_cards):
        require(
            runtime_card == expected_card,
            f"{expected_card[0]} runtime copy drifted from the revised source",
        )

    required_runtime_tokens = (
        'previewParameters.get("preview") === "overworld"',
        "startArrivalDialogue()",
        "finishArrivalDialogue(false)",
        "beginPlanetVeyraInterstitial()",
        "PLANET OF VEYRA",
        "ARRIVAL_DESCENT_REDUCED_DURATION = 3.2",
        "arrivalDescentReducedMotion",
        "ARRIVAL_DESCENT_DURATION /",
        "ARRIVAL_DESCENT_REDUCED_DURATION",
        "if (!arrivalDescentReducedMotion)",
        "@media (max-width: 720px) and (orientation: portrait)",
        ".episode-bridge__descent",
        "transform: translate(-50%, -50%);",
        'mode === "planet-title"',
        "beginOverworldArrivalReveal()",
        'state = "arrival-emerge";',
        'canvas.dataset.arrivalEmergence = "rising";',
        'playSoundEffect("shipOpen")',
        'effect: "tremor"',
        'effect: "look-portal"',
        'effect: "prime-portal"',
        'role="dialog"',
        'aria-modal="true"',
        "dialogueSkipConfirm",
        "arynDialoguePortrait",
        "drasDialoguePortrait",
        "aryn-dialogue-portrait-runtime-v3.png",
        "dras-dialogue-portrait-runtime-v2.png",
        "OVERWORLD_ORIGIN_X + WIDTH + 560",
        "Math.round(DRAS_DRAW_Y + drasBob)",
        "drawCloudVolume",
        "drawOverworldBirds",
        "drawCampDog",
        "veyra-camp-dog-walk-sheet-v3.png",
        "veyra-camp-dog-sniff-sheet-v3.png",
        "drawOverworldVolcano",
        "var seamPulsePoints = [",
        "VEYRA // SUBSURFACE TREMOR",
        'data-overworld-track="/Audio/super-frgmnts-overworld-loop.mp3"',
        'data-foundry-track="/Audio/super-frgmnts-foundry-loop.mp3"',
        "var selectedMusicTrack = mainTitleScreen",
        "? backgroundMusic.dataset.overworldTrack",
        "overworld: 0.29",
        "foundry: 0.32",
        "function configureEpisodeScene(scene, historyMode, sceneOptions)",
        "loadAndConfigureEpisodeScene(destination);",
        "var overworldAnchor",
        "(0.48 - 0.7)",
        "portalCharge",
        "invisibleStep: true",
        "OVERWORLD_ORIGIN_X + 516",
        "var SHIP_HULL_TRACE = [",
        "function shipHullSurfaceYAt(platform, worldX)",
        "function platformSurfaceYAt(platform, worldX)",
        "shipHull: true",
        "var overworldShipSpawnPlatform =",
        "player.supportPlatform =",
        "overworldShipSpawnPlatform ||",
        'previewParameters.get("scene") === "portal"',
        "coreworks-transport-idle-sheet-v1.png",
        "coreworks-transport-activate-sheet-v1.png",
        "function beginCoreworksTransport()",
        "function updateCoreworksTransport(delta)",
        "function drawCoreworksTransport()",
        "function drawCoreworksTransportEnergyForeground()",
        "COREWORKS_TRANSPORT_DECK_X",
        "overworld-western-signal-flats-v1.png",
        "function drawOverworldAssignments()",
        "function activateSignalSweep()",
        'state = "transporting"',
        'canvas.dataset.coreworksTransport = "activating"',
        '"?episode=01&stage="',
    )
    for token in required_runtime_tokens:
        require(token in source, f"Missing runtime contract: {token}")
    require(OVERWORLD_MUSIC.exists(), "Missing dedicated overworld music")
    require(
        OVERWORLD_MUSIC.stat().st_size > 1_000_000,
        "Overworld music asset is unexpectedly small",
    )
    require(PLANET_TITLE.exists(), "Missing Planet of Veyra title artwork")
    require(
        png_size(PLANET_TITLE) == (1400, 320),
        "Unexpected Planet of Veyra title artwork size",
    )
    descent_asset_root = ROOT / "Images/Game/Super-Frgmnts"
    for asset_name, expected_size in DESCENT_ASSETS.items():
        asset = descent_asset_root / asset_name
        require(asset.exists(), f"Missing Veyra descent asset: {asset_name}")
        require(
            png_size(asset) == expected_size,
            f"Unexpected Veyra descent asset size: {asset}",
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
        "overworld-western-signal-flats-v1.png",
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

    print("Arrival on Veyra contract passed.")
    print("- runtime speaker and copy match all 30 revised arrival cards exactly")
    print("- Field Relay, skip confirmation, and accessibility hooks are present")
    print("- purpose-built close portraits and narrated tremor context are present")
    print("- Dras's boots align with Aryn's visible running plane")
    print("- Skip is left and Continue is the primary right-hand action")
    print("- volumetric clouds, birds, readable dog gait, and restrained volcano heat are present")
    print("- Arrival on Veyra selects its dedicated overworld music track")
    print("- the stray Landing Flats collider is absent")
    print("- traced ship-hull collision spans both wings and raised engine crowns")
    print("- Aryn begins grounded on the ship's true central roof perch")
    print("- PLANET OF VEYRA separates touchdown from Aryn's hatch emergence")
    print("- full mobile descent remains visible, with a calm animated reduced-motion path")
    print("- tremor, portal look, and transport ignition remain staged")
    print("- the physical Coreworks transport has a walkable activation deck")
    print("- its one-shot vortex fades Aryn before the Foundry handoff")
    print("- all four 1672 × 941 overworld plates are present")
    print("- transport handoff supports the assembled Episode 01 Foundry and isolated review route")


if __name__ == "__main__":
    main()
