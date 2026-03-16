import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRAGMENTS_PATH = ROOT / "fragments_data.js"

FRAGMENTS_PATTERN = re.compile(
    r"window\.otw_fragments\s*=\s*(\[[\s\S]*?\])\s*;",
    re.MULTILINE,
)


def load_fragments_file() -> tuple[list, str]:
    if not FRAGMENTS_PATH.exists():
        raise SystemExit("ERROR: fragments_data.js does not exist")

    raw = FRAGMENTS_PATH.read_text(encoding="utf-8")
    match = FRAGMENTS_PATTERN.search(raw)
    if not match:
        raise SystemExit("ERROR: could not locate window.otw_fragments in fragments_data.js")

    try:
        current = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: existing fragments array is not valid JSON: {exc}") from exc

    if not isinstance(current, list):
        raise SystemExit("ERROR: window.otw_fragments must be an array")

    return current, raw


def load_outbox(path: Path) -> list:
    if not path.exists():
        raise SystemExit(f"ERROR: outbox file does not exist: {path}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: outbox file is not valid JSON: {exc}") from exc

    if isinstance(payload, dict):
        payload = [payload]

    if not isinstance(payload, list):
        raise SystemExit("ERROR: outbox JSON must be an object or an array of objects")

    return payload


def normalize_tag(raw_tag: str) -> str:
    tag = str(raw_tag or "FRAGMENT").strip().upper()
    tag = re.sub(r"[^A-Z0-9]+", "_", tag)
    tag = tag.strip("_")
    return tag or "FRAGMENT"


def normalize_entry(entry: dict) -> dict:
    if not isinstance(entry, dict):
        raise SystemExit("ERROR: every outbox entry must be an object")

    timestamp = str(entry.get("timestamp", "")).strip()
    text = str(entry.get("text", "")).strip()
    tag = normalize_tag(str(entry.get("tag", "FRAGMENT")))

    if not timestamp:
        raise SystemExit("ERROR: each outbox entry must include a timestamp")
    if not text:
        raise SystemExit("ERROR: each outbox entry must include text")

    return {
        "timestamp": timestamp,
        "text": text,
        "tag": tag,
    }


def dedupe(entries: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for entry in entries:
        key = (
            str(entry.get("timestamp", "")).strip(),
            str(entry.get("tag", "")).strip().upper(),
            str(entry.get("text", "")).strip(),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(entry)
    return output


def replace_fragments_array(original: str, entries: list[dict]) -> str:
    replacement = f"window.otw_fragments = {json.dumps(entries, indent=2)};"
    return FRAGMENTS_PATTERN.sub(replacement, original, count=1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Import exported fragments outbox JSON into fragments_data.js"
    )
    parser.add_argument(
        "outbox",
        help="Path to exported fragments outbox JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report changes without writing fragments_data.js",
    )
    args = parser.parse_args()

    outbox_path = Path(args.outbox).expanduser()
    if not outbox_path.is_absolute():
        outbox_path = (Path.cwd() / outbox_path).resolve()

    incoming = [normalize_entry(item) for item in load_outbox(outbox_path)]
    existing, original_raw = load_fragments_file()

    merged = dedupe(incoming + existing)
    merged.sort(key=lambda item: str(item.get("timestamp", "")), reverse=True)

    added = len(merged) - len(existing)

    if args.dry_run:
        print(f"OK: would add {max(added, 0)} fragment(s) from {outbox_path.name}")
        return 0

    updated_raw = replace_fragments_array(original_raw, merged)
    FRAGMENTS_PATH.write_text(updated_raw + ("\n" if not updated_raw.endswith("\n") else ""), encoding="utf-8")

    print(f"OK: added {max(added, 0)} fragment(s) from {outbox_path.name}")
    print(f"Updated: {FRAGMENTS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
