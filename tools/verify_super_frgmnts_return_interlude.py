#!/usr/bin/env python3
"""Verify the post-Wound report, Chapter 01 close, and atmosphere polish."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "super_frgmnts.html"
INTERLUDE_PATH = (
    ROOT
    / "Design/Super-Frgmnts/Post-Foundry/RETURN-TO-DRAS-INTERLUDE-v1.md"
)
CHAPTER_TWO_PATH = (
    ROOT / "Design/Super-Frgmnts/Chapter-02/VEYRA-CHAPTER-02-PLAN-v1.md"
)
RUNTIME = RUNTIME_PATH.read_text(encoding="utf-8")
INTERLUDE = INTERLUDE_PATH.read_text(encoding="utf-8")
CHAPTER_TWO = CHAPTER_TWO_PATH.read_text(encoding="utf-8")


def require(fragment: str, label: str) -> None:
    assert fragment in RUNTIME, f"Missing {label}: {fragment}"


def main() -> None:
    return_deck = RUNTIME.split(
        "var returnDialogueCards = [",
        1,
    )[1].split("var player = {", 1)[0]
    ids = re.findall(r'id: "(R\d{2})"', return_deck)
    assert ids == [f"R{index:02d}" for index in range(1, 32)], (
        f"Return dialogue must remain R01-R31, got {ids}"
    )

    required_story = {
        "restored stabilizers": (
            "Both atmospheric stabilizers are online."
        ),
        "Foundry and Biolab": (
            "The Foundry and Biolab processing floors are breathing again."
        ),
        "Seam Hunter": "A Seam Hunter.",
        "geological Wound": "geological rupture",
        "Wound-touched Vesperite behavior": (
            "Vesperite lies still once it leaves the seam."
        ),
        "Primary Biolab distinction": (
            "The main laboratory is below it."
        ),
        "unsolicited transport response": (
            "COREWORKS TRANSPORT // UNSOLICITED RESPONSE"
        ),
        "Chapter 02 hook": (
            "something below the Primary Biolab just answered your pack."
        ),
    }
    for label, fragment in required_story.items():
        assert fragment in return_deck, f"Return deck is missing {label}"

    required_runtime = {
        "return Dras placement": "var DRAS_RETURN_X = 6090;",
        "return dialogue state": 'var dialogueMode = "arrival";',
        "return report latch": "var returnDialogueHasPlayed = false;",
        "interlude state": (
            'var postFoundryInterlude = "unstarted";'
        ),
        "Primary Biolab route state": (
            'var primaryBiolabRoute = "unknown";'
        ),
        "return mission": (
            '"RETURNED TO VEYRA // REPORT TO DRAS"'
        ),
        "return deck selection": (
            "return dialogueMode === \"return\""
        ),
        "briefed state": 'postFoundryInterlude = "briefed";',
        "identified route": 'primaryBiolabRoute = "identified";',
        "return report label": '"Return to Dras"',
        "final dialogue action": '"Close chapter"',
        "chapter card kicker": (
            '"VEYRA // CHAPTER ONE COMPLETE"'
        ),
        "chapter card title": '"THE SIGNAL ANSWERED"',
        "chapter completion state": (
            '"chapter-one-complete"'
        ),
        "chapter hook telemetry": (
            '"primary-biolab-answer"'
        ),
        "visible sealed portal": '"TRANSPORT OFFLINE"',
    }
    for label, fragment in required_runtime.items():
        require(fragment, label)

    stage_styles = re.findall(
        r"\.stage-shell::before\s*\{(?P<body>.*?)\}",
        RUNTIME,
        flags=re.DOTALL,
    )
    assert stage_styles, "Missing gameplay compositor overlay"
    for block in stage_styles:
        assert "repeating-linear-gradient" not in block, (
            "Global gameplay scanlines must not cross sprites or the RD-42"
        )

    cloud_requirements = {
        "procedural cloud builder": (
            "function buildOverworldCloudTextures()"
        ),
        "low-frequency renderer telemetry": (
            '"procedural-fbm-v1"'
        ),
        "no cloud sprites telemetry": (
            'canvas.dataset.overworldCloudSprites ='
        ),
        "wispy layer": "overworldWispyCloudTexture",
        "storm layer": "overworldStormCloudTexture",
        "asynchronous approach build": (
            "scheduleOverworldCloudTextureBuild();"
        ),
    }
    for label, fragment in cloud_requirements.items():
        require(fragment, label)
    cloud_block = RUNTIME.split(
        "function buildOverworldCloudTextures()",
        1,
    )[1].split("function drawWrappedCloudTexture", 1)[0]
    assert "createElement(\"canvas\")" in cloud_block
    assert "putImageData" in cloud_block

    assert "Return report and Chapter 01 cliffhanger integrated" in INTERLUDE
    assert "`VEYRA // CHAPTER ONE COMPLETE`" in INTERLUDE
    assert "`THE SIGNAL ANSWERED`" in INTERLUDE
    assert "The Primary Biolab" in CHAPTER_TWO
    assert "Desktop fullscreen" in CHAPTER_TWO
    assert "Controller support" in CHAPTER_TWO
    assert len(CHAPTER_TWO) > 4000

    print("SUPER FRGMNTS return interlude and atmosphere: PASS")
    print("- R01-R31 report covers stabilizers, Seam Hunter, and the Wound")
    print("- Wound-touched Vesperite points Chapter 02 to Primary Biolab")
    print("- sealed surface transport stays visible and cannot reactivate")
    print("- procedural wispy/storm masks replace gameplay-wide scanlines")
    print("- fullscreen and controller support remain planned future work")


if __name__ == "__main__":
    main()
