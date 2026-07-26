#!/usr/bin/env python3
"""Verify the SUPER FRGMNTS Phase 1 stabilization contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    required_tokens = (
        'class="signal-boot"',
        'id="signalBootButton"',
        "Load Game",
        "function initializeSignal()",
        "signalInitialized = true",
        "document.body.classList.remove(\"is-signal-locked\")",
        'id="backgroundMusicSecondary"',
        "function setAudioScene(nextScene, immediate)",
        "var musicTracks = {",
        "var musicVolumes = {",
        "musicFadeTimer = window.setInterval(fadeMusic, 24)",
        "outgoing.pause();",
        "function configureEpisodeScene(scene, historyMode)",
        "function configureTitleScene()",
        "applySceneAssets();",
        "buildOverworldPlatforms()",
        "buildExpansionPreviewPlatforms()",
        "buildDeepworksRooms()",
        "window.history.pushState(",
        'window.addEventListener("popstate"',
        '"?episode=01&stage=" + scene + "&autostart=1"',
        'configureEpisodeScene("overworld")',
        'configureEpisodeScene("foundry")',
        "super-frgmnts-sound",
        'window.addEventListener("pagehide", function ()',
        'document.addEventListener("visibilitychange"',
        "assets.overworld0 = loadImage(",
        "assets.foundryExpanded = loadImage(",
    )
    for token in required_tokens:
        require(token in source, f"Missing Phase 1 contract: {token}")

    require(
        "window.location.href" not in source,
        "A scene transition still performs a full page reload",
    )
    require(
        source.index('id="signalBoot"') < source.index('id="titleScreen"'),
        "The signal initializer is not layered before the title scene",
    )
    require(
        source.index("setAudioScene(scene);") <
        source.index("resetGame(true);", source.index("function configureEpisodeScene")),
        "Scene audio must switch before the new mission begins",
    )

    print("SUPER FRGMNTS Phase 1 stabilization: PASS")
    print("- explicit mobile-safe audio initialization is present")
    print("- title, overworld, and Foundry share one audio director")
    print("- episode scenes change in-page and preserve a reloadable URL")
    print("- both playable environments preload before the first handoff")
    print("- pause, mute, visibility, and preference safeguards are retained")


if __name__ == "__main__":
    main()
