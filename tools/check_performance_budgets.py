#!/usr/bin/env python3
"""Enforce stable code/data budgets for OTW's first-click routes."""

from __future__ import annotations

import gzip
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ROUTE_BUDGETS = {
    "home": (60_000, ["index.html", "theme.css", "frontpage_payload.json"]),
    "current-writing": (32_000, ["residue_archive.html", "theme.css", "narrative_index.json"]),
    "fragments": (22_000, ["fragments.html", "fragments.css", "fragments.js", "fragments_users.json"]),
    "poetry": (20_000, ["drift_poetry.html", "theme.css", "new_poetry_data.js"]),
    "professional": (18_000, ["professional.html", "theme.css"]),
    "current-essay": (
        24_000,
        [
            "@current-essay",
            "theme.css",
            "archive_reader.css",
            "archive_reader.js",
        ],
    ),
    "image-of-the-day": (
        23_000,
        ["image_of_the_day.html", "IOTD_Main.html", "theme.css", "image_manifest.json"],
    ),
}


def compressed_size(relative_path: str) -> int:
    return len(gzip.compress((ROOT / relative_path).read_bytes(), compresslevel=9))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_route_budgets() -> list[str]:
    lines = []
    for route, (budget, files) in ROUTE_BUDGETS.items():
        resolved_files = list(files)
        if "@current-essay" in resolved_files:
            narrative_index = json.loads((ROOT / "narrative_index.json").read_text(encoding="utf-8"))
            current_url = narrative_index["posts"][0]["url"]
            resolved_files[resolved_files.index("@current-essay")] = current_url
        actual = sum(compressed_size(path) for path in resolved_files)
        require(actual <= budget, f"{route} route grew to {actual:,} compressed bytes (budget {budget:,})")
        lines.append(f"{route}: {actual:,}/{budget:,} compressed bytes")
    return lines


def check_loading_contracts() -> None:
    index = (ROOT / "index.html").read_text(encoding="utf-8")
    writing = (ROOT / "residue_archive.html").read_text(encoding="utf-8")
    fragments_html = (ROOT / "fragments.html").read_text(encoding="utf-8")
    fragments_js = (ROOT / "fragments.js").read_text(encoding="utf-8")
    poetry = (ROOT / "drift_poetry.html").read_text(encoding="utf-8")
    professional = (ROOT / "professional.html").read_text(encoding="utf-8")
    reader_css = (ROOT / "archive_reader.css").read_text(encoding="utf-8")
    reader_js = (ROOT / "archive_reader.js").read_text(encoding="utf-8")
    generator = (ROOT / "narrative_sync.py").read_text(encoding="utf-8")

    require("frontpage_payload.json" in index, "homepage must load the compact frontpage payload")
    require(
        not re.search(r'<script[^>]+src=["\']narrative_data\.js', index, re.I),
        "homepage may load the full narrative archive only through its legacy fallback",
    )
    require("narrative_index.json" in writing, "Current Writing must load the compact narrative index")
    require(
        not re.search(r'<script[^>]+src=["\']narrative_data\.js', writing, re.I),
        "Current Writing may fetch the legacy archive only as a fallback",
    )

    for path, text in {
        "index.html": index,
        "residue_archive.html": writing,
        "fragments.html": fragments_html,
        "drift_poetry.html": poetry,
        "professional.html": professional,
    }.items():
        require(
            not re.search(r'<script[^>]+src=["\']https://www\.googletagmanager\.com/gtag/js', text, re.I),
            f"{path} must delay analytics instead of parser-discovering it",
        )

    require("@import url('https://fonts.googleapis.com" not in poetry, "Poetry fonts must not block its inline CSS")
    require("@import url('https://fonts.googleapis.com" not in reader_css, "Reader fonts must not block article CSS")
    require("data-fragment-src" in fragments_js, "Fragments must viewport-gate remote card media")
    require("IntersectionObserver" in fragments_js, "Fragments must retain its explicit image viewport gate")
    require("data-reader-src" in generator, "Generated adjacent-essay images must be source-deferred")
    require("data-reader-src" in reader_js, "Archive reader must activate deferred adjacent images")

    for archive_path in sorted((ROOT / "archive").glob("*.html")):
        archive_html = archive_path.read_text(encoding="utf-8")
        adjacent_images = re.findall(
            r'<span class="reader-nav-media">\s*(<img\b[^>]*>)',
            archive_html,
            flags=re.I,
        )
        for tag in adjacent_images:
            require("data-reader-src=" in tag and " src=" not in tag, f"{archive_path.name} eagerly loads adjacent media")


def main() -> int:
    lines = check_route_budgets()
    check_loading_contracts()
    print("OK: first-click performance contracts are intact.")
    for line in lines:
        print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
