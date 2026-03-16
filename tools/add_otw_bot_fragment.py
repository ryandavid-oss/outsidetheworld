import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
FRAGMENTS_PATH = ROOT / "fragments_data.js"

FRAGMENTS_PATTERN = re.compile(
    r"window\.otw_fragments\s*=\s*(\[[\s\S]*?\])\s*;",
    re.MULTILINE,
)

OTW_BOT_POOL = [
    "OTW_Bot has detected elevated emotional weather in this sector. Recommend hydration and one less tab open.",
    "Signal integrity remains acceptable. Human operator appears melodramatic but functional.",
    "Reminder: not every passing thought is a crisis. Some of them are just undercaffeinated.",
    "Your archive is not messy. It is merely experiencing historical abundance.",
    "OTW_Bot would like to congratulate you on surviving another completely unnecessary worry spiral.",
    "Please note that three good paragraphs are sometimes superior to one tortured masterpiece.",
    "There is no shame in posting a fragment instead of an essay. Efficiency is a virtue.",
    "Current recommendation: close the tab, keep the insight.",
    "Minor alert: your perfectionism has mistaken itself for taste again.",
    "OTW_Bot supports your right to leave some thoughts at one paragraph and walk away.",
    "Try not to build a cathedral every time all you need is a porch light.",
    "A passing thought has requested asylum. Fragment status granted.",
    "A fragment is simply a blog post that declined to put on formalwear.",
    "Not all signals are urgent. Some just want witness.",
    "OTW_Bot suggests you trust the reader more and explain yourself less.",
    "The signal was never lost. It was merely avoiding committee review.",
    "OTW_Bot believes in the power of one clean sentence and then leaving people alone.",
    "A reminder from the machinery: being memorable is not the same as being loud.",
    "The shortest route to coherence is often simply saying the thing plainly.",
    "You are allowed to keep the post small and the feeling true.",
]


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


def replace_fragments_array(original: str, entries: list[dict]) -> str:
    replacement = f"window.otw_fragments = {json.dumps(entries, indent=2)};"
    return FRAGMENTS_PATTERN.sub(lambda _match: replacement, original, count=1)


def dedupe(entries: list[dict]) -> list[dict]:
    seen = set()
    output = []
    for entry in entries:
        key = (
            str(entry.get("timestamp", "")).strip(),
            str(entry.get("author", "")).strip(),
            str(entry.get("tag", "")).strip(),
            str(entry.get("text", "")).strip(),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(entry)
    return output


def normalize_timestamp(value: Optional[str]) -> str:
    if not value:
        return datetime.now().astimezone().isoformat(timespec="minutes")

    raw = value.strip()
    if not raw:
        return datetime.now().astimezone().isoformat(timespec="minutes")

    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SystemExit(
            "ERROR: --timestamp must be valid ISO format, e.g. 2026-03-15T19:42:00-07:00"
        ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)

    return parsed.isoformat(timespec="minutes")


def pick_pool_text(seed_value: Optional[int]) -> str:
    if seed_value is None:
        now = datetime.now(timezone.utc)
        seed_value = int(now.timestamp() // 86400)
    return OTW_BOT_POOL[seed_value % len(OTW_BOT_POOL)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append a persistent OTW_Bot fragment into fragments_data.js"
    )
    parser.add_argument(
        "--text",
        help="Custom OTW_Bot text. If omitted, a pooled quip is used.",
    )
    parser.add_argument(
        "--timestamp",
        help="ISO timestamp for the bot post. Defaults to now with local offset.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Numeric seed for deterministic pool selection.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and preview without writing fragments_data.js",
    )
    args = parser.parse_args()

    text = (args.text or "").strip() or pick_pool_text(args.seed)
    timestamp = normalize_timestamp(args.timestamp)

    entry = {
      "timestamp": timestamp,
      "text": text,
      "tag": "OTW_BOT",
      "author": "OTW_Bot",
    }

    existing, original_raw = load_fragments_file()
    merged = dedupe([entry] + existing)
    merged.sort(key=lambda item: str(item.get("timestamp", "")), reverse=True)

    if args.dry_run:
        print("OK: would add OTW_Bot fragment")
        print(json.dumps(entry, indent=2))
        return 0

    updated_raw = replace_fragments_array(original_raw, merged)
    FRAGMENTS_PATH.write_text(
        updated_raw + ("\n" if not updated_raw.endswith("\n") else ""),
        encoding="utf-8",
    )

    print("OK: added OTW_Bot fragment")
    print(f"Updated: {FRAGMENTS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
