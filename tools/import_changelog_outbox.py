import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = ROOT / "changelog.json"


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid JSON in {path}: {exc}") from exc


def load_existing_entries() -> list:
    if not CHANGELOG_PATH.exists():
        return []

    data = load_json(CHANGELOG_PATH)
    if not isinstance(data, list):
        raise SystemExit("ERROR: changelog.json must contain an array")
    return data


def load_outbox(path: Path) -> list:
    if not path.exists():
        raise SystemExit(f"ERROR: outbox file does not exist: {path}")

    data = load_json(path)
    if not isinstance(data, list):
        raise SystemExit("ERROR: outbox must contain an array of changelog entries")
    return data


def normalize_entry(entry: dict) -> dict:
    if not isinstance(entry, dict):
        raise SystemExit("ERROR: each outbox entry must be an object")

    date = str(entry.get("date", "")).strip()
    entry_type = str(entry.get("type", "")).strip() or "Other"
    text = str(entry.get("text", "")).strip()

    if len(date) != 10 or date[4] != "-" or date[7] != "-":
        raise SystemExit(f"ERROR: invalid changelog date: {date}")
    if not text:
        raise SystemExit("ERROR: changelog text cannot be empty")

    return {"date": date, "type": entry_type, "text": text}


def dedupe(entries: list) -> list:
    seen = set()
    out = []
    for entry in entries:
        normalized = normalize_entry(entry)
        key = (
            normalized["date"],
            normalized["type"].strip().lower(),
            normalized["text"].strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(normalized)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge a changelog outbox JSON export into changelog.json")
    parser.add_argument("outbox", help="Path to changelog outbox JSON")
    parser.add_argument("--dry-run", action="store_true", help="Validate and report without writing")
    args = parser.parse_args()

    outbox_path = Path(args.outbox).expanduser().resolve()
    existing = load_existing_entries()
    incoming = load_outbox(outbox_path)

    merged = dedupe([*incoming, *existing])
    merged.sort(key=lambda entry: entry["date"], reverse=True)

    if args.dry_run:
        additions = len(merged) - len(dedupe(existing))
        print(f"OK: would add {additions} changelog entr{'' if additions == 1 else 'ies'} from {outbox_path.name}")
        return 0

    CHANGELOG_PATH.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    print(f"OK: merged {len(incoming)} outbox entr{'' if len(incoming) == 1 else 'ies'} into changelog.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
