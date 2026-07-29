#!/usr/bin/env python3
"""Verify the SUPER FRGMNTS Episode 01 Beta 2 release identity."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "super_frgmnts.html"
RELEASE = (
    ROOT
    / "Design"
    / "Super-Frgmnts"
    / "Releases"
    / "episode-01-beta-2.json"
)


def main() -> None:
    source = GAME.read_text(encoding="utf-8")
    release = json.loads(RELEASE.read_text(encoding="utf-8"))

    assert release["release"] == "episode-01-beta-2"
    assert release["status"] == "approved-production"
    assert release["source"]["branch"] == "main"
    assert release["source"]["published_url"] == (
        "https://outsidetheworld.com/super_frgmnts.html"
    )
    assert release["episode_flow"][-3:] == [
        "the-wound",
        "vesperite-recovery",
        "surface-return",
    ]
    assert release["world"] == {
        "overworld_plates": 4,
        "foundry_plates": 8,
        "foundry_zones": [
            "Foundry",
            "Refinery",
            "Biolab",
            "Deepworks",
            "Uplink",
        ],
        "signal_shards": 12,
        "atmospheric_stabilizers": 2,
        "foundry_enemies": 16,
        "chitin_sentinels": 7,
    }
    assert len(release["beta_2_changes"]) == 17

    required_tokens = (
        'meta name="release" content="SUPER FRGMNTS Episode 01 Beta 2"',
        'body data-release="beta-2"',
        "Season One // Veyra // Beta 2",
    )
    for token in required_tokens:
        assert token in source, f"Missing Beta 2 release token: {token}"

    print("SUPER FRGMNTS Episode 01 Beta 2 release: PASS")
    print("- live title and machine-readable release identity are present")
    print("- Arrival, Foundry, Wound, recovery, and surface-return flow is locked")
    print("- Beta 2 world, encounter, audio, and verification scope is recorded")


if __name__ == "__main__":
    main()
