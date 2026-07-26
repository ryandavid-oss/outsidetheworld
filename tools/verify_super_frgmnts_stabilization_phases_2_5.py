#!/usr/bin/env python3
"""Verify the SUPER FRGMNTS stabilization contracts for Phases 2–5."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_tokens(source: str, phase: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        require(token in source, f"Missing {phase} contract: {token}")


def main() -> None:
    source = GAME.read_text(encoding="utf-8")

    require_tokens(
        source,
        "Phase 2 mobile viewport",
        (
            "--app-height: 100dvh",
            "height: var(--app-height, 100dvh)",
            "function visibleViewportSize()",
            "var viewport = window.visualViewport",
            'document.documentElement.style.setProperty(',
            '"--app-height"',
            "function scheduleGameViewportResize()",
            "function settleGameViewportAfterOrientationChange()",
            'window.addEventListener("resize", scheduleGameViewportResize)',
            '"orientationchange"',
            "window.visualViewport.addEventListener(",
        ),
    )

    require_tokens(
        source,
        "Phase 3 rendering lifecycle",
        (
            "var renderRequested = true",
            'var pageVisible = document.visibilityState !== "hidden"',
            "var simulationActive =",
            '(state === "running" || dialogueActive)',
            "if (simulationActive) {",
            "} else if (pageVisible && renderRequested) {",
            "} else if (!pageVisible) {",
            "lastFrame = 0",
        ),
    )

    require_tokens(
        source,
        "Phase 4 input recovery",
        (
            "function releaseAllControls()",
            "jumpBuffer = 0",
            "shootBuffer = 0",
            'document.querySelectorAll("[data-control]")',
            'window.addEventListener("blur", function ()',
            'window.addEventListener("pagehide", function ()',
            'document.addEventListener("visibilitychange"',
            "releaseAllControls();",
        ),
    )
    require(
        source.count("releaseAllControls();") >= 6,
        "Input recovery is not applied across all interruption paths",
    )

    require_tokens(
        source,
        "Phase 5 critical asset recovery",
        (
            "function imageHasPixels(image)",
            "image.naturalWidth > 0",
            "image.naturalHeight > 0",
            "function showCriticalAssetFailure(keys)",
            "function retryFailedCriticalAssets()",
            "function refreshCriticalAsset(key)",
            '"titleArtwork"',
            '"Retry Load"',
            '"Retrying…"',
            '"Artwork unavailable"',
            "failedAssetKeys = keys.slice()",
            "loadCriticalAssets(",
            "criticalAssetKeys.concat([\"titleArtwork\"])",
        ),
    )
    require(
        'timeoutId = window.setTimeout(finish, 20000)' in source,
        "Critical artwork timeout must allow slow mobile connections",
    )
    require(
        'window.addEventListener("resize", resizeGameViewport)' not in source,
        "Viewport changes must be coalesced instead of rendering synchronously",
    )

    print("SUPER FRGMNTS stabilization Phases 2–5: PASS")
    print("- Phase 2: visual viewport, safe height, and rotation settling")
    print("- Phase 3: active-state rendering and hidden-page suspension")
    print("- Phase 4: centralized control release on browser interruption")
    print("- Phase 5: validated critical artwork with an in-page retry path")


if __name__ == "__main__":
    main()
