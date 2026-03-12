import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = ROOT / "changelog.json"


def load_entries() -> list:
    if not CHANGELOG_PATH.exists():
        return []

    try:
        data = json.loads(CHANGELOG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: changelog.json is not valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise SystemExit("ERROR: changelog.json must contain an array")

    return data


def dedupe(entries: list) -> list:
    seen = set()
    out = []
    for entry in entries:
        key = (
            str(entry.get("date", "")).strip(),
            str(entry.get("type", "")).strip().lower(),
            str(entry.get("text", "")).strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "date": str(entry.get("date", "")).strip(),
                "type": str(entry.get("type", "")).strip() or "Other",
                "text": str(entry.get("text", "")).strip(),
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Append a new changelog entry")
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    parser.add_argument("--type", dest="entry_type", default="Other", help="Entry type")
    parser.add_argument("--text", required=True, help="Entry text")
    args = parser.parse_args()

    date = args.date.strip()
    entry_type = args.entry_type.strip() or "Other"
    text = args.text.strip()

    if len(date) != 10 or date[4] != "-" or date[7] != "-":
        raise SystemExit("ERROR: --date must be in YYYY-MM-DD format")
    if not text:
        raise SystemExit("ERROR: --text is required")

    entries = load_entries()
    entries.insert(0, {"date": date, "type": entry_type, "text": text})
    entries = dedupe(entries)
    entries.sort(key=lambda x: str(x.get("date", "")), reverse=True)

    CHANGELOG_PATH.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    print(f"OK: added changelog entry for {date}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
