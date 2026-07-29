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
    assert release["episode_flow"][-7:] == [
        "the-wound",
        "vesperite-recovery",
        "surface-return",
        "return-to-dras-report",
        "wound-touched-vesperite-scan",
        "primary-biolab-response",
        "chapter-one-cliffhanger",
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
    required_stabilization_changes = {
        "production Uplink bulkhead and compact arc-discharge sprites",
        "live RD-42 dorsal-hatch entry and production-art interior",
        "return-to-Dras report and Primary Biolab cliffhanger",
        "stabilizer-driven sky clearing with a persistent infestation remnant",
    }
    assert required_stabilization_changes.issubset(
        set(release["beta_2_changes"])
    )
    assert release["audio"]["rd42_interior"] == (
        "Audio/super-frgmnts-rd42-interior-loop-v1.m4a"
    )

    required_tokens = (
        'meta name="release" content="SUPER FRGMNTS Episode 01 Beta 2"',
        'body data-release="beta-2"',
        "Season One // Veyra // Beta 2",
    )
    for token in required_tokens:
        assert token in source, f"Missing Beta 2 release token: {token}"

    print("SUPER FRGMNTS Episode 01 Beta 2 release: PASS")
    print("- live title and machine-readable release identity are present")
    print("- Arrival through the Dras report and Chapter 01 cliffhanger is locked")
    print("- Beta 2 world, encounter, audio, and verification scope is recorded")


if __name__ == "__main__":
    main()
