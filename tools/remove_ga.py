#!/usr/bin/env python3
"""Remove the retired OTW Google Analytics tag from HTML files."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASUREMENT_ID = "G-YKRKPFV2MB"
SCRIPT_BLOCK = re.compile(r"<script\b[^>]*>[\s\S]*?</script>", re.IGNORECASE)


def is_managed_path(path: Path) -> bool:
    return not any(part in {".git", ".claude"} for part in path.parts)


def remove_ga_blocks(source: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return "" if MEASUREMENT_ID in match.group(0) else match.group(0)

    return SCRIPT_BLOCK.sub(replace, source)


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if not is_managed_path(path):
            continue
        source = path.read_text(encoding="utf-8")
        updated = remove_ga_blocks(source)
        if updated == source:
            continue
        path.write_text(updated, encoding="utf-8")
        changed.append(path.relative_to(ROOT))

    remaining = [
        path.relative_to(ROOT)
        for path in ROOT.rglob("*.html")
        if is_managed_path(path) and MEASUREMENT_ID in path.read_text(encoding="utf-8")
    ]
    if remaining:
        raise SystemExit(f"Google Analytics remains in: {', '.join(map(str, remaining))}")

    print(f"Removed Google Analytics from {len(changed)} HTML files.")


if __name__ == "__main__":
    main()
