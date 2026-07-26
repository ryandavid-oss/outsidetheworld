#!/usr/bin/env python3
"""Verify that the web-first, iOS-ready SUPER FRGMNTS baseline stays canonical."""

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


def main() -> None:
    required_baseline = (
        "Web-first, iOS-ready",
        "Capacitor/WKWebView",
        "A full SpriteKit or other native-engine rewrite is not the baseline plan.",
        "## Input contract",
        "`switchWeapon`",
        "`pointercancel`",
        "## Rendering and timing contract",
        "Target smooth 60 Hz presentation without an intentional FPS cap.",
        "## Asset and memory contract",
        "2,048 pixels",
        "## Audio and lifecycle contract",
        "vesperite-boulder-impact-runtime-v1.png",
        "vesperite-boulder-collapse-runtime-v1.png",
        "Before TestFlight promotion, split",
        "## Persistence contract",
        "versioned, serializable save model",
        "## Native integration boundary",
        "## Feature acceptance gate",
        "360–390 px portrait touch play",
        "## Migration sequence",
        "## Decision rule",
    )
    for token in required_baseline:
        assert token in BASELINE, f"Missing platform baseline contract: {token}"

    assert "IOS-PORTABILITY-BASELINE.md" in INDEX
    assert "UNIFIED-LEVEL-ONE-PLAN.md" in INDEX
    assert "IOS-PORTABILITY-BASELINE.md" in LEVEL_PLAN
    assert "super_frgmnts.html" in INDEX
    assert "on `main`" in INDEX

    print("SUPER FRGMNTS Platform Baseline 1: PASS")
    print("- the production web game remains canonical")
    print("- PWA and Capacitor/WKWebView are the planned portability route")
    print("- input, lifecycle, assets, saves, and native seams are explicit")
    print("- future feature reviews include desktop and portrait-mobile gates")


if __name__ == "__main__":
    main()
