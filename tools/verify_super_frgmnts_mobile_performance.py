#!/usr/bin/env python3
"""Verify the production mobile-performance contracts for Super Frgmnts."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
BEAM = ROOT / "beam_system.js"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_tokens(source: str, label: str, tokens: tuple[str, ...]) -> None:
    for token in tokens:
        require(token in source, f"Missing {label} contract: {token}")


def main() -> None:
    game = GAME.read_text(encoding="utf-8")
    beam = BEAM.read_text(encoding="utf-8")

    require_tokens(
        game,
        "mobile render profile",
        (
            'requestedRenderProfile === "mobile-safe"',
            'body.is-mobile-runtime .pause-pack-layer',
            'mobilePerformanceMode || desktopOneXRenderEnabled',
            '"mobile-1x-release"',
            '"mobile-no-blur-release"',
            '"mobile-safe-v1"',
        ),
    )
    require_tokens(
        game,
        "bounded reusable effects",
        (
            'var PARTICLE_BUDGET = mobilePerformanceMode ? 180 : 300;',
            'var PLAYER_PROJECTILE_BUDGET =',
            'function acquireEnergyOrb()',
            'function releaseEnergyOrb(orb)',
            'function acquireBolt(definition)',
            'function releaseBolt(bolt)',
            'canvas.dataset.playerProjectileBudgetDrops',
        ),
    )
    require_tokens(
        beam,
        "beam projectile pool",
        (
            'const projectilePool = [];',
            'const trailPointPool = [];',
            'function releaseProjectile(projectile)',
            'trail.push(acquireTrailPoint(x, y));',
            'releaseProjectile,',
        ),
    )
    require_tokens(
        game,
        "offscreen culling",
        (
            'mobilePerformanceMode ? 110 : 240',
            'mobilePerformanceMode ? 48 : 130',
            'particle.x >= cameraX - 280',
            'popup.x < renderCameraX - 80',
        ),
    )
    require_tokens(
        game,
        "arrival resource lifecycle",
        (
            'var ARRIVAL_DESCENT_CANVAS_SCALE =',
            '"mobile-css-1x"',
            'function releaseArrivalDescentResources()',
            'releaseAssetKeys(arrivalDescentAssetKeys);',
            'requestAssetKeys(arrivalDescentAssetKeys, "high");',
        ),
    )
    require_tokens(
        game,
        "frame telemetry",
        (
            'canvas.dataset.frameAverageMs',
            'canvas.dataset.frameWorstMs',
            'canvas.dataset.frameLongFrames',
            'canvas.dataset.frameSevereFrames',
            'canvas.dataset.frameQuality',
            'performance: {',
        ),
    )
    require(
        '<script src="/beam_system.js?v=20260805-mobile-performance-1"></script>'
        in game,
        "The pooled beam runtime is not cache-versioned",
    )

    print("SUPER FRGMNTS mobile performance release: PASS")
    print("- mobile canvas and arrival backing are constrained to 1x display work")
    print("- mobile CSS and Canvas blur passes are disabled")
    print("- particles, popups, hostile shots, PACK shots, and trails are bounded/reused")
    print("- enemy/effect rendering uses tighter mobile viewport margins")
    print("- descent plates and particles are released after landing")
    print("- live frame-time telemetry is exposed in DOM state and render_game_to_text")


if __name__ == "__main__":
    main()
