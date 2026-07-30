#!/usr/bin/env python3
"""Verify that the native Apple SUPER FRGMNTS baseline stays canonical."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_ROOT = ROOT / "Design" / "Super-Frgmnts"
BASELINE = (DESIGN_ROOT / "IOS-PORTABILITY-BASELINE.md").read_text(
    encoding="utf-8"
)
INDEX = (DESIGN_ROOT / "README.md").read_text(encoding="utf-8")
LEVEL_PLAN = (DESIGN_ROOT / "UNIFIED-LEVEL-ONE-PLAN.md").read_text(
    encoding="utf-8"
)
HANDOFF = (DESIGN_ROOT / "SUPER-FRGMNTS-HANDOFF.md").read_text(encoding="utf-8")


def main() -> None:
    required_baseline = (
        "Native Apple Platform Baseline 2",
        "Native iOS, iPadOS, and macOS",
        "frozen as an executable design",
        "Do not add web gameplay",
        "Swift and SpriteKit",
        "Raw Metal is not the starting point.",
        "## Architectural boundaries",
        "## Input contract",
        "`switchWeapon`",
        "controller disconnect",
        "## Rendering and timing contract",
        "bounded fixed-step simulation",
        "stable 60 Hz presentation",
        "120 Hz ProMotion mode",
        "## Production-load acceptance target",
        "fifty-four enemies",
        "twenty-four Vesperite Fragments",
        "iPad Pro M4",
        "iPhone 17 Pro",
        "## Asset and memory contract",
        "2,048 pixels",
        "## Audio and lifecycle contract",
        "## Persistence contract",
        "versioned, `Codable` save model",
        "## Native integration boundary",
        "## First native milestone",
        "## Migration sequence",
        "## Out of scope",
        "Canvas renderer optimization",
        "WebGL renderer development",
        "Capacitor or WKWebView application packaging",
        "## Decision rule",
    )
    for token in required_baseline:
        assert token in BASELINE, f"Missing platform baseline contract: {token}"

    assert "Web-first, iOS-ready" not in BASELINE
    assert (
        "A full SpriteKit or other native-engine rewrite is not the baseline plan."
        not in BASELINE
    )
    assert "IOS-PORTABILITY-BASELINE.md" in INDEX
    assert "UNIFIED-LEVEL-ONE-PLAN.md" in INDEX
    assert "IOS-PORTABILITY-BASELINE.md" in LEVEL_PLAN
    assert "super_frgmnts.html" in INDEX
    assert "on `main`" in INDEX
    assert "native iOS, iPadOS, and macOS" in INDEX
    assert "native iOS, iPadOS, and macOS" in LEVEL_PLAN
    assert "Web Beta 2 frozen; native Apple migration authorized" in HANDOFF
    assert "Do not add features, optimize the browser renderer" in HANDOFF
    assert "Swift/SpriteKit Foundry vertical slice" in HANDOFF

    print("SUPER FRGMNTS Native Apple Platform Baseline 2: PASS")
    print("- native iOS, iPadOS, and macOS are the sole production targets")
    print("- the browser runtime is frozen as migration and parity evidence")
    print("- Swift/SpriteKit owns the first production-load validation path")
    print("- web, PWA, WebGL, Capacitor, and WKWebView work is out of scope")


if __name__ == "__main__":
    main()
