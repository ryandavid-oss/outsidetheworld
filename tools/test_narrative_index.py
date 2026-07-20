#!/usr/bin/env python3
"""Contract and size tests for narrative_index.json."""

from __future__ import annotations

import gzip
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_narrative_index as builder  # noqa: E402


def main() -> int:
    stored = json.loads(builder.OUTPUT_PATH.read_text(encoding="utf-8"))
    generated = builder.build_payload()
    assert stored == generated, "narrative_index.json is stale; run tools/build_narrative_index.py"
    assert stored["schema"] == "otw.narrative.index"
    assert stored["version"] == 1

    full_posts = builder.parse_js_array(ROOT / "narrative_data.js")
    posts = stored["posts"]
    assert len(posts) == len(full_posts)

    source_files = sorted(path.name for path in (ROOT / "current_narrative").glob("*.md"))
    generated_files = sorted(str(post.get("file") or "") for post in full_posts)
    assert generated_files == source_files, (
        "narrative_data.js does not represent every current_narrative source; "
        "run narrative_sync.py before building the compact index"
    )
    archive_files = sorted(path.name for path in (ROOT / "archive").glob("2026-*.html"))
    expected_archive_files = sorted(f"{Path(name).stem}.html" for name in source_files)
    assert archive_files == expected_archive_files, (
        "the canonical archive does not contain exactly one reader for every current_narrative source"
    )

    assert len({post["postId"] for post in posts}) == len(posts)
    assert len({post["url"] for post in posts}) == len(posts)
    for post in posts:
        assert post["title"] and post["date"] and post["url"]
        assert post["wordCount"] >= 0 and post["readMinutes"] >= 1
        assert "body" not in post and "publisher" not in post
        assert len(post["excerpt"]) <= 523

    compressed = len(gzip.compress(builder.OUTPUT_PATH.read_bytes(), compresslevel=9))
    assert compressed < 15_000, f"narrative index grew to {compressed:,} compressed bytes"
    print(
        f"OK: narrative index is current, complete, body-free, and {compressed:,} bytes compressed."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
