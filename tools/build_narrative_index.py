#!/usr/bin/env python3
"""Build the compact data feed used by the current-writing archive."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from build_frontpage_payload import (
    archive_path,
    build_excerpt,
    clean_text,
    parse_js_array,
    slugify,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "narrative_index.json"


def publisher_subhead(post: dict[str, Any]) -> str:
    publisher = post.get("publisher") if isinstance(post.get("publisher"), dict) else {}
    return clean_text(publisher.get("subhead"))


def without_leading_deck(markdown: str, deck: str) -> str:
    if not deck:
        return str(markdown or "")
    blocks = re.split(r"\n\s*\n", str(markdown or "").strip())
    if blocks and clean_text(blocks[0]) == clean_text(deck):
        return "\n\n".join(blocks[1:]).strip()
    return str(markdown or "")


def word_count(markdown: str) -> int:
    words = re.findall(r"[A-Za-z0-9]+(?:[’'][A-Za-z0-9]+)?", clean_text(markdown))
    return len(words)


def normalize_post(post: dict[str, Any]) -> dict[str, Any]:
    title = clean_text(post.get("title")) or "Untitled essay"
    date = str(post.get("date") or "")
    deck = publisher_subhead(post)
    body = without_leading_deck(str(post.get("body") or ""), deck)
    words = word_count(body)
    url = archive_path(post)
    return {
        "postId": f"{date or 'undated'}--{slugify(title or 'untitled')}",
        "title": title,
        "date": date,
        "url": url,
        "subhead": deck,
        "excerpt": build_excerpt(body, 520),
        "wordCount": words,
        "readMinutes": max(1, (words + 224) // 225),
    }


def build_payload() -> dict[str, Any]:
    posts = [normalize_post(post) for post in parse_js_array(ROOT / "narrative_data.js")]
    core = {"posts": posts}
    content_hash = hashlib.sha256(
        json.dumps(core, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "schema": "otw.narrative.index",
        "version": 1,
        "contentHash": content_hash,
        **core,
    }


def write_payload() -> dict[str, Any]:
    payload = build_payload()
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    compressed = len(gzip.compress(OUTPUT_PATH.read_bytes(), compresslevel=9))
    print(
        f"Wrote {OUTPUT_PATH.relative_to(ROOT)} with {len(payload['posts'])} records "
        f"({OUTPUT_PATH.stat().st_size:,} bytes raw; {compressed:,} bytes compressed)."
    )
    return payload


def main() -> int:
    write_payload()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
