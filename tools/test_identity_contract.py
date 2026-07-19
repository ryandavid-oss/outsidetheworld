#!/usr/bin/env python3
"""Regression checks for OTW's canonical site and author identities."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHOR_URL = "https://outsidetheworld.com/ryandavid-burningham.html"
AUTHOR_ID = f"{AUTHOR_URL}#person"
GITHUB_URL = "https://github.com/ryandavid-oss"


def json_ld_graph(path: Path) -> list[dict]:
    source = path.read_text(encoding="utf-8")
    blocks = re.findall(
        r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>',
        source,
        re.I | re.S,
    )
    nodes: list[dict] = []
    for block in blocks:
        payload = json.loads(block)
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            nodes.extend(node for node in payload["@graph"] if isinstance(node, dict))
        elif isinstance(payload, dict):
            nodes.append(payload)
    return nodes


def node_by_type(nodes: list[dict], type_name: str) -> dict:
    return next(node for node in nodes if node.get("@type") == type_name)


def run_tests() -> None:
    homepage = ROOT / "index.html"
    homepage_source = homepage.read_text(encoding="utf-8")
    homepage_nodes = json_ld_graph(homepage)
    website = node_by_type(homepage_nodes, "WebSite")
    organization = node_by_type(homepage_nodes, "Organization")
    person = node_by_type(homepage_nodes, "Person")

    assert website["name"] == "Outside The World"
    assert website["alternateName"] == ["OTW", "outsidetheworld.com"]
    assert organization["name"] == "Outside The World"
    assert organization["legalName"] == "Outside the World is New, LLC"
    assert person["@id"] == AUTHOR_ID
    assert person["givenName"] == "RyanDavid"
    assert person["familyName"] == "Burningham"
    assert GITHUB_URL in person["sameAs"]
    assert '<h1 class="site-title">' in homepage_source
    assert '<h1 class="visually-hidden">Outside The World</h1>' not in homepage_source
    assert "Outside The World by RyanDavid Burningham." in homepage_source

    profile_nodes = json_ld_graph(ROOT / "ryandavid-burningham.html")
    profile_person = node_by_type(profile_nodes, "Person")
    assert profile_person["@id"] == AUTHOR_ID
    assert profile_person["givenName"] == "RyanDavid"
    assert profile_person["familyName"] == "Burningham"
    assert GITHUB_URL in profile_person["sameAs"]

    founder_pages = 0
    for folder in ["archive", "wayback", "poems", "iotd", "fragments"]:
        for path in (ROOT / folder).glob("*.html"):
            source = path.read_text(encoding="utf-8", errors="ignore")
            if '/ryandavid-burningham.html" rel="author"' not in source:
                continue
            founder_pages += 1
            assert AUTHOR_ID in source, f"canonical author id missing from {path.relative_to(ROOT)}"

    assert founder_pages >= 800, founder_pages
    atom = (ROOT / "atom.xml").read_text(encoding="utf-8")
    assert "<name>RyanDavid Burningham</name>" in atom
    assert f"<uri>{AUTHOR_URL}</uri>" in atom

    print(f"OK: canonical Website, Organization, and Person identity spans {founder_pages} generated records.")


if __name__ == "__main__":
    run_tests()
