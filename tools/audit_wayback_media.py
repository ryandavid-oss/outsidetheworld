#!/usr/bin/env python3
"""Audit every image referenced by the public Wayback data set.

Local references are checked against the repository. External references are
probed with a lightweight HEAD/partial-GET sequence so aging hosts can be
identified before they turn into broken images in the archive.
"""

from __future__ import annotations

import argparse
import html
import json
import ssl
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlsplit, urlunsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "wayback_purified.js"
SITE_HOSTS = {"outsidetheworld.com", "www.outsidetheworld.com"}
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 "
    "OTW-Media-Audit/1.0"
)
IMAGE_EXTENSIONS = {
    ".avif",
    ".gif",
    ".heic",
    ".jpeg",
    ".jpg",
    ".png",
    ".svg",
    ".webp",
}


class MediaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() not in {"img", "source"}:
            return
        values = {key.lower(): value or "" for key, value in attrs}
        if values.get("src"):
            self.sources.append(values["src"])
        if values.get("srcset"):
            for candidate in values["srcset"].split(","):
                source = candidate.strip().split(None, 1)[0]
                if source:
                    self.sources.append(source)

    handle_startendtag = handle_starttag


def read_balanced_json_array(text: str, start: int) -> str:
    depth = 0
    in_string = False
    escaping = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaping:
                escaping = False
            elif char == "\\":
                escaping = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError("Wayback JSON array was not closed")


def load_wayback_records() -> list[dict[str, Any]]:
    source = DATA_PATH.read_text(encoding="utf-8")
    assignment = source.find("const wayback_raw_dump")
    start = source.find("[", assignment)
    if assignment < 0 or start < 0:
        raise ValueError(f"Could not locate wayback_raw_dump in {DATA_PATH.name}")
    records = json.loads(read_balanced_json_array(source, start))
    return [record for record in records if isinstance(record, dict)]


def normalized_source(value: str) -> str:
    source = html.unescape(str(value or "")).strip().replace("\\", "/")
    return f"https:{source}" if source.startswith("//") else source


def canonical_local_path(source: str) -> Path | None:
    parsed = urlsplit(source)
    if parsed.scheme in {"http", "https"}:
        if parsed.netloc.lower() not in SITE_HOSTS:
            return None
        raw_path = parsed.path
    elif parsed.scheme:
        return None
    else:
        raw_path = source.split("?", 1)[0].split("#", 1)[0]

    candidates: list[Path] = []
    for candidate in (raw_path, unquote(raw_path)):
        normalized = candidate.replace("\\", "/").lstrip("/")
        parts = list(PurePosixPath(normalized).parts)
        if not parts or any(part == ".." for part in parts):
            continue
        if parts[0].casefold() == "images":
            parts[0] = "Images"
        path = ROOT.joinpath(*parts)
        if path not in candidates:
            candidates.append(path)
    return next((path for path in candidates if path.is_file()), candidates[-1] if candidates else None)


def collect_references(records: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    references: dict[str, list[dict[str, str]]] = defaultdict(list)
    for record in records:
        parser = MediaParser()
        parser.feed(html.unescape(str(record.get("body") or "")))
        for raw_source in parser.sources:
            source = normalized_source(raw_source)
            if not source or source.lower().startswith(("data:", "blob:", "javascript:")):
                continue
            occurrence = {
                "file": str(record.get("file") or "unknown source"),
                "title": str(record.get("title") or "Untitled"),
            }
            if occurrence not in references[source]:
                references[source].append(occurrence)
    return dict(references)


def secure_variant(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme.lower() != "http":
        return url
    return urlunsplit(("https", parsed.netloc, parsed.path, parsed.query, parsed.fragment))


def request_image(url: str, method: str, timeout: float) -> dict[str, Any]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
    }
    if method == "GET":
        headers["Range"] = "bytes=0-1023"
    request = Request(url, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            status = int(getattr(response, "status", 200))
            content_type = response.headers.get_content_type().lower()
            final_url = response.geturl()
            suffix = Path(unquote(urlsplit(final_url).path)).suffix.lower()
            image_response = content_type.startswith("image/") or (
                not content_type and suffix in IMAGE_EXTENSIONS
            )
            return {
                "ok": 200 <= status < 400 and image_response,
                "status": status,
                "content_type": content_type,
                "final_url": final_url,
                "method": method,
                "error": "" if image_response else f"unexpected content type: {content_type or 'unknown'}",
            }
    except HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "content_type": exc.headers.get_content_type().lower() if exc.headers else "",
            "final_url": exc.geturl(),
            "method": method,
            "error": f"HTTP {exc.code}",
        }
    except (URLError, TimeoutError, ssl.SSLError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        return {
            "ok": False,
            "status": None,
            "content_type": "",
            "final_url": url,
            "method": method,
            "error": f"{type(reason).__name__}: {reason}",
        }


def probe_external(url: str, timeout: float) -> dict[str, Any]:
    candidates = [secure_variant(url)]
    if candidates[0] != url:
        candidates.append(url)
    attempts: list[dict[str, Any]] = []
    for candidate in candidates:
        for method in ("HEAD", "GET"):
            result = request_image(candidate, method, timeout)
            attempts.append(result)
            if result["ok"]:
                return {"url": url, "ok": True, "attempts": attempts, **result}
    final = attempts[-1]
    has_http_evidence = any(attempt.get("status") is not None for attempt in attempts)
    return {
        "url": url,
        "ok": False,
        "classification": "remote_broken" if has_http_evidence else "remote_unverified",
        "attempts": attempts,
        **final,
    }


def source_summary(occurrences: list[dict[str, str]]) -> str:
    names = [occurrence["file"] for occurrence in occurrences]
    preview = ", ".join(names[:3])
    return f"{preview}, +{len(names) - 3} more" if len(names) > 3 else preview


def audit(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    records = load_wayback_records()
    references = collect_references(records)
    local_ok: list[dict[str, Any]] = []
    local_missing: list[dict[str, Any]] = []
    external: dict[str, list[dict[str, str]]] = {}

    for source, occurrences in sorted(references.items()):
        local_path = canonical_local_path(source)
        parsed = urlsplit(source)
        is_site_url = parsed.scheme in {"http", "https"} and parsed.netloc.lower() in SITE_HOSTS
        if parsed.scheme in {"http", "https"} and not is_site_url:
            external[source] = occurrences
            continue
        relative = str(local_path.relative_to(ROOT)) if local_path and local_path.is_relative_to(ROOT) else ""
        item = {"source": source, "path": relative, "occurrences": occurrences}
        if local_path and local_path.is_file():
            local_ok.append(item)
        else:
            local_missing.append(item)

    remote_results: list[dict[str, Any]] = []
    if not args.local_only and external:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(probe_external, url, args.timeout): url
                for url in external
            }
            for future in as_completed(futures):
                url = futures[future]
                try:
                    result = future.result()
                except Exception as exc:  # Defensive isolation for scheduled audits.
                    result = {
                        "url": url,
                        "ok": False,
                        "classification": "remote_unverified",
                        "status": None,
                        "content_type": "",
                        "final_url": url,
                        "method": "",
                        "error": f"{type(exc).__name__}: {exc}",
                        "attempts": [],
                    }
                result["occurrences"] = external[url]
                remote_results.append(result)
        remote_results.sort(key=lambda item: item["url"])

    remote_ok = [result for result in remote_results if result["ok"]]
    remote_broken = [
        result for result in remote_results
        if not result["ok"] and result.get("classification") == "remote_broken"
    ]
    remote_unverified = [
        result for result in remote_results
        if not result["ok"] and result.get("classification") != "remote_broken"
    ]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(DATA_PATH.relative_to(ROOT)),
        "records": len(records),
        "unique_references": len(references),
        "summary": {
            "local_ok": len(local_ok),
            "local_missing": len(local_missing),
            "remote_total": len(external),
            "remote_ok": len(remote_ok) if not args.local_only else None,
            "remote_broken": len(remote_broken) if not args.local_only else None,
            "remote_unverified": len(remote_unverified) if not args.local_only else None,
        },
        "local_missing": local_missing,
        "remote_ok": remote_ok,
        "remote_broken": remote_broken,
        "remote_unverified": remote_unverified,
    }

    print(
        "WAYBACK_MEDIA: "
        f"{len(records)} records; {len(references)} unique references; "
        f"{len(local_ok)} local present; {len(local_missing)} local missing; "
        f"{len(external)} external"
    )
    if args.local_only:
        print("REMOTE_CHECK: skipped (--local-only)")
    else:
        print(
            f"REMOTE_CHECK: {len(remote_ok)} healthy; {len(remote_broken)} broken; "
            f"{len(remote_unverified)} unverified"
        )
    for item in local_missing:
        print(f"MISSING_LOCAL: {item['source']} [{source_summary(item['occurrences'])}]")
    for item in remote_broken:
        print(
            f"BROKEN_REMOTE: {item['url']} ({item.get('error') or 'failed'}) "
            f"[{source_summary(item['occurrences'])}]"
        )
    for item in remote_unverified:
        print(
            f"UNVERIFIED_REMOTE: {item['url']} ({item.get('error') or 'failed'}) "
            f"[{source_summary(item['occurrences'])}]"
        )

    if args.json_output:
        output = Path(args.json_output)
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"REPORT_WRITTEN: {output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}")

    failures = len(local_missing)
    if not args.local_only:
        failures += len(remote_broken) + len(remote_unverified)
    return report, 1 if args.strict and failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local-only", action="store_true", help="Skip all network probes.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when any reference fails.")
    parser.add_argument("--json", dest="json_output", help="Write a machine-readable report.")
    parser.add_argument("--timeout", type=float, default=15.0, help="Seconds per network attempt.")
    parser.add_argument("--workers", type=int, default=10, help="Concurrent external probes.")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if args.workers <= 0:
        parser.error("--workers must be greater than zero")
    return args


if __name__ == "__main__":
    try:
        _, exit_code = audit(parse_args())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"AUDIT_ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
    sys.exit(exit_code)
