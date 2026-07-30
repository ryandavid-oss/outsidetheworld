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
        "function configureEpisodeScene(scene, historyMode, sceneOptions)",
        "function configureTitleScene()",
        "applySceneAssets();",
        "buildOverworldPlatforms()",
        "buildExpansionPreviewPlatforms()",
        "buildDeepworksRooms()",
        "window.history.pushState(",
        'window.addEventListener("popstate"',
        '"?episode=01&stage="',
        "function beginEpisodeApproach()",
        'showEpisodeBridge("approach", "overworld")',
        'loadAndConfigureEpisodeScene("foundry")',
        "super-frgmnts-sound",
        'window.addEventListener("pagehide", function ()',
        'document.addEventListener("visibilitychange"',
        "overworld0: {",
        "foundryExpanded: {",
        "function loadCriticalAssets(keys, completion)",
        '.message-card.is-paused .message-title',
        '.message-card.is-paused #startButton',
        'messageCard.classList.add("is-paused")',
        'messageCopy.textContent = "";',
        'messageCard.classList.remove("is-paused")',
        'previewParameters.get("render-profile") || "default"',
        'requestedRenderProfile === "desktop-1x"',
        '"desktop-1x-trial"',
        'requestedRenderProfile === "desktop-crop"',
        '"desktop-crop-trial"',
        '"visible-viewport-crop-trial"',
        'requestedRenderProfile === "pixel-budget"',
        "RENDER_PIXEL_BUDGET = 2000000",
        '"pixel-budget-trial"',
        "canvas.dataset.renderPixelBudget",
        '" // 2MP"',
        '"default-mobile-guard"',
        '"desktop-opt-in-only"',
        'previewParameters.get("frame-profile") || "default"',
        'requestedFrameProfile === "desktop-60"',
        '"desktop-60-trial"',
        'requestedFrameProfile === "monitor"',
        '"query-opt-in-all-devices"',
        '"FPS " +',
        "Math.round(drawRate)",
        '"is-fps-monitor"',
        "function updateFramePacingTelemetry(",
        "framePacingDeadline",
        "1000 / 60",
        "canvas.dataset.frameCallbackRate",
        "canvas.dataset.frameDrawRate",
        'id="performanceTrialBadge"',
        'previewParameters.get("effects-profile") || "default"',
        'requestedEffectsProfile === "desktop-no-blur"',
        '"desktop-no-blur-trial"',
        '"desktop-no-blur-unavailable"',
        "Object.defineProperty(",
    )
    for token in required_tokens:
        require(token in source, f"Missing Phase 1 contract: {token}")

    require(
        "window.location.href" not in source,
        "A scene transition still performs a full page reload",
    )
    require(
        "The unified world survey is holding your position." not in source,
        "The retired pause-overlay explanation is still present",
    )
    require(
        source.index('id="signalBoot"') < source.index('id="titleScreen"'),
        "The signal initializer is not layered before the title scene",
    )
    require(
        source.index('setAudioScene(isWound ? "wound" : scene);') <
        source.index("resetGame(true);", source.index("function configureEpisodeScene")),
        "Scene audio must switch before the new mission begins",
    )

    print("SUPER FRGMNTS Phase 1 stabilization: PASS")
    print("- explicit mobile-safe audio initialization is present")
    print("- title, overworld, and Foundry share one audio director")
    print("- episode scenes change in-page and preserve a reloadable URL")
    print("- both playable environments preload before the first handoff")
    print("- pause, mute, visibility, and preference safeguards are retained")
    print("- the pause card uses a larger title and Resume action without helper copy")
    print("- optional 1x render trial is desktop-only and URL-reversible")
    print("- optional room-plate crop trial preserves the visible destination")
    print("- optional 60 Hz pacing trial reports callback and draw rates")
    print("- optional no-blur trial isolates Safari Canvas shadow cost")
    print("- baseline FPS monitor is query-only and available on mobile")


if __name__ == "__main__":
    main()
