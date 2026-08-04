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
MOBILE_ART = (
    ROOT
    / "Images"
    / "Game"
    / "Super-Frgmnts"
    / "super-frgmnts-title-coreworks-mobile-v1.png"
)
MANIFEST = TITLE / "title-screen-revision-1a-manifest.json"
TITLE_MUSIC = ROOT / "Audio" / "super-frgmnts-title-cue.mp3"


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
    assert MOBILE_ART.exists(), f"Missing mobile title artwork: {MOBILE_ART}"
    assert png_size(MOBILE_ART) == (941, 1672)
    assert TITLE_MUSIC.exists(), f"Missing title music: {TITLE_MUSIC}"
    assert TITLE_MUSIC.stat().st_size > 1_000_000
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
        "super-frgmnts-title-coreworks-mobile-v1.png",
        'media="(max-width: 720px) and (orientation: portrait)"',
        'meta name="release" content="SUPER FRGMNTS Episode 01 Beta 2"',
        'body data-release="beta-2"',
        '<p class="title-screen__season" id="titleSeason" hidden></p>',
        '<p class="title-screen__hero"><strong>Arrival on Veyra</strong></p>',
        "A distress signal from a world the Fleet abandoned.",
        ': "Start"',
        'id="titleControllerHint"',
        "function updateTitleInputHint(gamepad)",
        '? "Cross"',
        ': "A"',
        '"Cross / A"',
        "title-screen__atmosphere",
        "title-screen__signal",
        "title-screen__vesperite",
        "@keyframes title-panel-arrival",
        "@keyframes title-item-arrival",
        "@keyframes title-start-wake",
        "function replayTitleEntrance()",
        "function beginTitleLaunchTransition()",
        'canvas.dataset.titleLaunchTransition = "fading-to-black";',
        '"fading-from-black"',
        ".stage-shell.is-title-transition::after",
        'document.body.classList.add("is-title-launching")',
        'class="sound-button__icon"',
        "function renderSoundButton()",
        "body.is-main-title #soundButton",
        "@keyframes title-scene-breathe",
        "@keyframes title-dust-drift",
        "@keyframes title-signal-pulse",
        "@media (prefers-reduced-motion: reduce)",
        'previewParameters.get("episode") === "01"',
        'episodeStage === "overworld"',
        'episodeStage === "foundry"',
        'previewParameters.get("autostart") === "1"',
        '"?episode=01&stage="',
        "activateTitleAction()",
        "function beginEpisodeApproach()",
        'showEpisodeBridge("approach", "overworld")',
        "loadAndConfigureEpisodeScene(\"foundry\")",
        'event.code === "Enter" || event.code === "Space"',
        "Opening Arrival on Veyra.",
        'data-title-track="/Audio/super-frgmnts-title-cue.mp3"',
        "var selectedMusicTrack = mainTitleScreen",
        "backgroundMusic.loop = !mainTitleScreen",
        'id="signalBoot"',
        'id="signalBootButton"',
        "Load Game",
        "function initializeSignal()",
        "function setAudioScene(nextScene, immediate)",
        'playSoundEffect("deepSelect");',
        "signalBoot.hidden = true",
        'id="masterResetButton"',
        'id="pauseTitleButton"',
        "function masterResetToTitle()",
        '{ superFrgmntsScene: "title" }',
        'canvas.dataset.menuScreen = "title";',
        'masterResetButton.addEventListener(',
        'pauseTitleButton.addEventListener(',
    )
    for token in required_tokens:
        assert token in source, f"Missing title-screen contract: {token}"

    assert "/Images/Game/super-frgmnts-title-art.png" not in source
    assert "title-prompt 1.15s steps(2, end) infinite" not in source
    assert manifest["launch"]["duplicate_title"] is False
    assert manifest["launch"]["route"].endswith(
        "?episode=01&stage=overworld&autostart=1"
    )
    assert manifest["launch"]["foundry_handoff"].endswith(
        "?episode=01&stage=foundry&autostart=1"
    )
    assert manifest["motion"]["reduced_motion_static"] is True
    assert "window.location.href" not in source

    print("SUPER FRGMNTS title-screen Revision 1A: PASS")
    print("- native 1672 x 941 Coreworks title artwork is integrated")
    print("- Arrival on Veyra stands alone as the title-card identity")
    print("- keyboard, touch, PlayStation, and standard controller entry prompts are present")
    print("- the title card stages once, START settles, and title sound control stays compact")
    print("- START fades through black before revealing the Veyra descent")
    print("- atmospheric motion and reduced-motion safeguards are present")
    print("- dedicated title cue starts from an intentional audio handshake")
    print("- top-bar and Pause master reset controls return to the title route")
    print("- production integration and deployment scope is recorded")


if __name__ == "__main__":
    main()
