#!/usr/bin/env python3
"""Audit the complete tracked OTW web surface.

The discovery validator protects canonical generated records. This crawler is
deliberately broader: it includes every deployed HTML/HTM document, validates
local links and fragments, decodes referenced images, scans CSS assets, and can
probe both external dependencies and the deployed copies of every page.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import ssl
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://outsidetheworld.com"
SITE_HOSTS = {"outsidetheworld.com", "www.outsidetheworld.com"}
DOCUMENT_SUFFIXES = {".html", ".htm"}
IMAGE_SUFFIXES = {".avif", ".gif", ".heic", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
SKIP_SCHEMES = {"blob", "data", "javascript", "mailto", "sms", "tel"}
REFERENCE_ATTRIBUTES = {
    "a": ("href",),
    "area": ("href",),
    "audio": ("src",),
    "embed": ("src",),
    "form": ("action",),
    "iframe": ("src",),
    "img": ("src", "srcset"),
    "input": ("src",),
    "link": ("href",),
    "object": ("data",),
    "script": ("src",),
    "source": ("src", "srcset"),
    "track": ("src",),
    "video": ("src", "poster"),
}
SKIP_TEXT_TAGS = {"script", "style", "template", "svg"}
MOJIBAKE = re.compile(r"(?:â€[™œ¦]|Ã[-¿]|Â[-¿])")
RAW_MARKDOWN = re.compile(r"!?(?:\[[^\]\n]+\])\((?:https?://|/|\.\.?/)[^)\n]+\)")
CSS_REFERENCE = re.compile(r"url\(\s*([\"']?)(.*?)\1\s*\)", re.I)
QUOTED_IMAGE_REFERENCE = re.compile(
    r'''(?P<quote>["'])(?P<value>[^"'\n]+?\.(?:avif|gif|heic|jpe?g|png|svg|webp)(?:[?#][^"'\n]*)?)(?P=quote)''',
    re.I,
)
TEMPLATED_REFERENCE = re.compile(r"(?:\$[A-Za-z_]|\$this->|\[[A-Za-z_]+\]|\{\{?|<\?=?)")
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 "
    "OTW-Site-Audit/1.0"
)


@dataclass(frozen=True)
class Reference:
    source: str
    line: int
    tag: str
    attribute: str
    value: str
    scope: str


@dataclass
class Document:
    path: str
    scope: str
    title: str = ""
    title_count: int = 0
    h1_count: int = 0
    lang: str = ""
    robots: str = ""
    visible_text: str = ""
    ids: Counter[str] = field(default_factory=Counter)
    references: list[Reference] = field(default_factory=list)
    json_ld: list[tuple[int, str]] = field(default_factory=list)


@dataclass
class Issue:
    severity: str
    code: str
    source: str
    scope: str
    line: int = 0
    reference: str = ""
    target: str = ""
    detail: str = ""


class DocumentParser(HTMLParser):
    def __init__(self, path: str, scope: str) -> None:
        super().__init__(convert_charrefs=True)
        self.document = Document(path=path, scope=scope)
        self._skip_depth = 0
        self._in_title = False
        self._title_parts: list[str] = []
        self._visible_parts: list[str] = []
        self._json_ld_line = 0
        self._json_ld_parts: list[str] | None = None

    @staticmethod
    def srcset_values(value: str) -> list[str]:
        return [candidate.strip().split(None, 1)[0] for candidate in value.split(",") if candidate.strip()]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): value or "" for key, value in attrs}
        line, _ = self.getpos()
        if tag == "html":
            self.document.lang = values.get("lang", "").strip()
        if values.get("id"):
            self.document.ids[values["id"]] += 1
        if tag == "a" and values.get("name"):
            self.document.ids[values["name"]] += 1
        if tag == "title":
            self.document.title_count += 1
            self._in_title = True
        if tag == "h1":
            self.document.h1_count += 1
        if tag == "meta" and values.get("name", "").lower() == "robots":
            self.document.robots = values.get("content", "")
        if tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._json_ld_line = line
            self._json_ld_parts = []
        for attribute in REFERENCE_ATTRIBUTES.get(tag, ()):
            link_rel = set(values.get("rel", "").lower().split())
            if tag == "link" and attribute == "href" and link_rel & {"dns-prefetch", "preconnect"}:
                continue
            raw = values.get(attribute, "").strip()
            if not raw:
                continue
            candidates = self.srcset_values(raw) if attribute == "srcset" else [raw]
            for candidate in candidates:
                self.document.references.append(
                    Reference(self.document.path, line, tag, attribute, candidate, self.document.scope)
                )
        if tag in SKIP_TEXT_TAGS:
            self._skip_depth += 1

    handle_startendtag = handle_starttag

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._json_ld_parts is not None:
            self.document.json_ld.append((self._json_ld_line, "".join(self._json_ld_parts).strip()))
            self._json_ld_parts = None
        if tag in SKIP_TEXT_TAGS and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        if self._json_ld_parts is not None:
            self._json_ld_parts.append(data)
        if not self._skip_depth:
            self._visible_parts.append(data)

    def close(self) -> None:
        super().close()
        self.document.title = re.sub(r"\s+", " ", "".join(self._title_parts)).strip()
        self.document.visible_text = re.sub(r"\s+", " ", " ".join(self._visible_parts)).strip()


def git_files() -> list[Path]:
    raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8", "surrogateescape")
    return [Path(value) for value in raw.split("\0") if value]


def configured_excludes() -> set[str]:
    excludes: set[str] = set()
    config = ROOT / "_config.yml"
    in_excludes = False
    for line in config.read_text(encoding="utf-8").splitlines() if config.exists() else []:
        if re.match(r"^exclude\s*:\s*$", line):
            in_excludes = True
            continue
        if in_excludes:
            match = re.match(r"^\s+-\s+(.+?)\s*$", line)
            if match:
                excludes.add(match.group(1).strip("\"'"))
                continue
            if line and not line.startswith((" ", "\t")):
                in_excludes = False
    return excludes


def is_deployed(path: Path, excludes: set[str]) -> bool:
    return not any(
        part in excludes or part.startswith(".") or part.startswith("_")
        for part in path.parts
    )


def sitemap_paths() -> set[str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    paths: set[str] = set()
    for node in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
        parsed = urlsplit(node.text or "")
        path = unquote(parsed.path).lstrip("/") or "index.html"
        paths.add(path)
    return paths


def url_for_path(path: str) -> str:
    return f"{SITE_URL}/{quote(path, safe='/+@,;=-_.()')}"


def parse_documents(paths: list[Path], canonical: set[str]) -> dict[str, Document]:
    documents: dict[str, Document] = {}
    for path in paths:
        relative = path.as_posix()
        scope = "canonical" if relative in canonical else "legacy"
        parser = DocumentParser(relative, scope)
        parser.feed((ROOT / path).read_text(encoding="utf-8", errors="replace"))
        parser.close()
        documents[relative] = parser.document
    return documents


def local_candidates(url_path: str) -> list[str]:
    candidates: list[str] = []
    for raw in (url_path, unquote(url_path)):
        value = raw.replace("\\", "/").lstrip("/")
        parts = PurePosixPath(value).parts
        if any(part == ".." for part in parts):
            continue
        if not value or value.endswith("/"):
            value += "index.html"
        if value not in candidates:
            candidates.append(value)
    return candidates


def resolve_local(reference: Reference, deployed: set[str]) -> tuple[str, str | None]:
    absolute = urljoin(url_for_path(reference.source), html.unescape(reference.value.strip()))
    parsed = urlsplit(absolute)
    if parsed.scheme.lower() in SKIP_SCHEMES:
        return "ignored", None
    if parsed.scheme not in {"", "http", "https"}:
        return "external", absolute
    if parsed.netloc.lower() not in {"", *SITE_HOSTS}:
        return "external", absolute
    for candidate in local_candidates(parsed.path):
        if candidate in deployed:
            return "local", candidate
    fallback = local_candidates(parsed.path)
    return "missing", fallback[-1] if fallback else ""


def is_image_reference(reference: Reference) -> bool:
    if reference.tag in {"img", "input"} or reference.attribute == "poster":
        return True
    return (
        reference.tag in {"source", "css", "data"}
        and Path(urlsplit(reference.value).path).suffix.lower() in IMAGE_SUFFIXES
    )


def check_document_contracts(documents: dict[str, Document]) -> list[Issue]:
    issues: list[Issue] = []
    for document in documents.values():
        def add(severity: str, code: str, detail: str = "", line: int = 0) -> None:
            issues.append(Issue(severity, code, document.path, document.scope, line, detail=detail))

        if document.title_count == 0 or not document.title:
            add("error", "missing_title")
        elif document.title_count > 1:
            add("error", "duplicate_title", f"{document.title_count} title elements")
        if document.scope == "canonical" and not document.lang:
            add("warning", "missing_language")
        if not document.visible_text:
            add("warning", "empty_visible_text")
        if "\ufffd" in document.visible_text:
            add("error", "replacement_character", "Visible text contains U+FFFD")
        if MOJIBAKE.search(document.visible_text):
            add("warning", "possible_mojibake")
        if RAW_MARKDOWN.search(document.visible_text):
            add("warning", "visible_markdown_link")
        if "[caption" in document.visible_text.lower():
            add("warning", "visible_caption_shortcode")
        for identifier, count in document.ids.items():
            if count > 1:
                add("warning", "duplicate_id", f"{identifier!r} appears {count} times")
        for line, payload in document.json_ld:
            if not payload:
                add("error", "empty_json_ld", line=line)
                continue
            try:
                json.loads(payload)
            except json.JSONDecodeError as exc:
                add("error", "invalid_json_ld", str(exc), line)
    return issues


def check_references(
    documents: dict[str, Document],
    deployed: set[str],
) -> tuple[list[Issue], dict[str, list[Reference]], dict[str, list[Reference]]]:
    issues: list[Issue] = []
    external: dict[str, list[Reference]] = defaultdict(list)
    images: dict[str, list[Reference]] = defaultdict(list)
    casefold_map: dict[str, list[str]] = defaultdict(list)
    for path in deployed:
        casefold_map[path.casefold()].append(path)

    for document in documents.values():
        for reference in document.references:
            value = html.unescape(reference.value.strip())
            if TEMPLATED_REFERENCE.search(value):
                issues.append(Issue(
                    "warning", "unrendered_template_reference", reference.source, reference.scope,
                    reference.line, value, detail="A server-side template token is publicly visible.",
                ))
                continue
            kind, target = resolve_local(reference, deployed)
            if kind == "external" and target:
                external[target].append(reference)
                continue
            if kind == "missing":
                suggestion = casefold_map.get(str(target).casefold(), [])
                detail = f"Case-sensitive candidate: {suggestion[0]}" if len(suggestion) == 1 else ""
                issues.append(Issue(
                    "error", "missing_local_reference", reference.source, reference.scope,
                    reference.line, value, str(target or ""), detail,
                ))
                continue
            if kind != "local" or not target:
                continue
            if is_image_reference(reference):
                images[target].append(reference)
            fragment = unquote(urlsplit(urljoin(url_for_path(reference.source), value)).fragment)
            if fragment and target in documents and fragment not in documents[target].ids:
                issues.append(Issue(
                    "error", "missing_fragment_target", reference.source, reference.scope,
                    reference.line, value, f"{target}#{fragment}",
                ))
    return issues, dict(external), dict(images)


def css_references(css_paths: list[Path], canonical_assets: set[str]) -> list[Reference]:
    references: list[Reference] = []
    for path in css_paths:
        source = path.as_posix()
        scope = "canonical" if source in canonical_assets else "legacy"
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        for match in CSS_REFERENCE.finditer(text):
            value = match.group(2).strip()
            if value and not value.lower().startswith("data:"):
                line = text.count("\n", 0, match.start()) + 1
                references.append(Reference(source, line, "css", "url", value, scope))
    return references


def data_image_references(data_paths: list[Path]) -> list[Reference]:
    """Extract image paths from JSON/JavaScript-backed galleries and manifests."""
    references: list[Reference] = []
    for path in data_paths:
        source = path.as_posix()
        text = (ROOT / path).read_text(encoding="utf-8", errors="replace")
        for match in QUOTED_IMAGE_REFERENCE.finditer(text):
            prefix = text[max(0, match.start() - 80):match.start()]
            if re.search(r'["\']objectKey["\']\s*:\s*$', prefix):
                continue
            value = match.group("value").replace("\\/", "/")
            if "\\" in value:
                continue
            parsed = urlsplit(value)
            if parsed.scheme and parsed.scheme.lower() not in {"http", "https"}:
                # JSON card identifiers can contain an image URL as one segment
                # (for example, ``iotd:date:https://...jpg``). They are identity
                # keys, not fetchable image references.
                continue
            references.append(Reference(
                source,
                text.count("\n", 0, match.start()) + 1,
                "data",
                "value",
                value,
                "data",
            ))
    return references


def verify_images(images: dict[str, list[Reference]]) -> list[Issue]:
    issues: list[Issue] = []
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError:
        Image = None
        UnidentifiedImageError = OSError

    for path, references in sorted(images.items()):
        source = references[0]
        suffix = Path(path).suffix.lower()
        if suffix not in IMAGE_SUFFIXES:
            issues.append(Issue(
                "error", "non_image_resource", source.source, source.scope, source.line,
                source.value, path, f"Image element resolves to {suffix or 'an extensionless file'}.",
            ))
            continue
        try:
            if suffix == ".svg":
                ET.parse(ROOT / path)
            elif Image is not None:
                with Image.open(ROOT / path) as image:
                    image.verify()
        except (OSError, ValueError, ET.ParseError, UnidentifiedImageError) as exc:
            issues.append(Issue(
                "error", "undecodable_image", source.source, source.scope, source.line,
                source.value, path, f"{type(exc).__name__}: {exc}",
            ))
    return issues


def request_url(url: str, timeout: float, expect_image: bool = False) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    candidates = [url]
    parsed = urlsplit(url)
    if parsed.scheme == "http":
        secure = urlunsplit(("https", parsed.netloc, parsed.path, parsed.query, parsed.fragment))
        candidates.insert(0, secure)
    for candidate in candidates:
        for method in ("HEAD", "GET"):
            headers = {"User-Agent": USER_AGENT, "Accept": "image/*,*/*;q=0.8" if expect_image else "*/*"}
            if method == "GET":
                headers["Range"] = "bytes=0-1023"
            request = Request(candidate, headers=headers, method=method)
            try:
                with urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
                    status = int(getattr(response, "status", 200))
                    content_type = response.headers.get_content_type().lower()
                    ok = 200 <= status < 400 and (not expect_image or content_type.startswith("image/"))
                    result = {
                        "ok": ok,
                        "status": status,
                        "content_type": content_type,
                        "final_url": response.geturl(),
                        "method": method,
                        "error": "" if ok else f"unexpected content type: {content_type or 'unknown'}",
                    }
            except HTTPError as exc:
                result = {
                    "ok": False,
                    "status": exc.code,
                    "content_type": exc.headers.get_content_type().lower() if exc.headers else "",
                    "final_url": exc.geturl(),
                    "method": method,
                    "error": f"HTTP {exc.code}",
                }
            except (URLError, TimeoutError, ssl.SSLError, OSError) as exc:
                reason = getattr(exc, "reason", exc)
                result = {
                    "ok": False,
                    "status": None,
                    "content_type": "",
                    "final_url": candidate,
                    "method": method,
                    "error": f"{type(reason).__name__}: {reason}",
                }
            attempts.append(result)
            if result["ok"]:
                return {"url": url, "attempts": attempts, **result}
    return {"url": url, "attempts": attempts, **attempts[-1]}


def probe_urls(
    urls: dict[str, list[Reference]],
    image_urls: set[str],
    timeout: float,
    workers: int,
) -> tuple[list[Issue], list[dict[str, Any]]]:
    issues: list[Issue] = []
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for url, references in urls.items():
            if all(reference.tag == "form" for reference in references):
                results.append({
                    "url": url,
                    "ok": None,
                    "classification": "form_action_not_probed",
                    "detail": "Submission endpoints are not called by this read-only audit.",
                })
                continue
            futures[executor.submit(request_url, url, timeout, url in image_urls)] = url
        for future in as_completed(futures):
            url = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                result = {"url": url, "ok": False, "status": None, "error": f"{type(exc).__name__}: {exc}"}
            results.append(result)
            if result.get("ok"):
                continue
            reference = urls[url][0]
            status = result.get("status")
            if status in {401, 403, 405, 406, 409, 412, 415, 417, 418, 425, 429, 451, 500, 502, 503, 600, 999} or status is None:
                severity, code = "warning", "external_reference_unverified"
            else:
                severity, code = "error", "broken_external_reference"
            issues.append(Issue(
                severity, code, reference.source, reference.scope, reference.line,
                reference.value, url, result.get("error", "External request failed"),
            ))
    return issues, sorted(results, key=lambda item: item["url"])


def live_page_references(paths: list[str], canonical: set[str]) -> dict[str, list[Reference]]:
    references: dict[str, list[Reference]] = {}
    for path in paths:
        scope = "canonical" if path in canonical else "legacy"
        url = url_for_path(path)
        references[url] = [Reference(path, 0, "document", "live", url, scope)]
    return references


def summarize(issues: list[Issue]) -> dict[str, Any]:
    return {
        "total": len(issues),
        "by_severity": dict(Counter(issue.severity for issue in issues)),
        "by_scope": dict(Counter(issue.scope for issue in issues)),
        "by_code": dict(Counter(issue.code for issue in issues).most_common()),
    }


def run(args: argparse.Namespace) -> int:
    excludes = configured_excludes()
    tracked = git_files()
    deployed_paths = {path.as_posix() for path in tracked if is_deployed(path, excludes)}
    canonical = sitemap_paths()
    document_paths = sorted(
        path for path in tracked
        if is_deployed(path, excludes) and path.suffix.lower() in DOCUMENT_SUFFIXES
    )
    documents = parse_documents(document_paths, canonical)
    issues = check_document_contracts(documents)
    reference_issues, external, images = check_references(documents, deployed_paths)
    issues.extend(reference_issues)

    css_paths = sorted(path for path in tracked if is_deployed(path, excludes) and path.suffix.lower() == ".css")
    referenced_css = {
        target
        for document in documents.values()
        if document.scope == "canonical"
        for reference in document.references
        for kind, target in [resolve_local(reference, deployed_paths)]
        if kind == "local" and target and Path(target).suffix.lower() == ".css"
    }
    css_refs = css_references(css_paths, referenced_css)
    css_docs = {ref.source: Document(path=ref.source, scope=ref.scope, references=[ref]) for ref in css_refs}
    css_issues, css_external, css_images = check_references(css_docs, deployed_paths)
    issues.extend(css_issues)
    for url, refs in css_external.items():
        external.setdefault(url, []).extend(refs)
    for path, refs in css_images.items():
        images.setdefault(path, []).extend(refs)

    data_paths = sorted(
        path for path in tracked
        if (
            is_deployed(path, excludes)
            and path.suffix.lower() in {".js", ".json"}
            and "tools" not in path.parts
            and Path(path.stem).suffix.lower() not in IMAGE_SUFFIXES
        )
    )
    data_refs = data_image_references(data_paths)
    data_docs: dict[str, Document] = {}
    for ref in data_refs:
        data_docs.setdefault(ref.source, Document(path=ref.source, scope=ref.scope)).references.append(ref)
    data_issues, data_external, data_images = check_references(data_docs, deployed_paths)
    issues.extend(data_issues)
    for url, refs in data_external.items():
        external.setdefault(url, []).extend(refs)
    for path, refs in data_images.items():
        images.setdefault(path, []).extend(refs)

    referenced_image_count = len(images)
    deployable_images = sorted(
        path for path in deployed_paths if Path(path).suffix.lower() in IMAGE_SUFFIXES
    )
    for path in deployable_images:
        images.setdefault(path, [Reference(path, 0, "asset", "file", path, "asset")])
    issues.extend(verify_images(images))

    external_results: list[dict[str, Any]] = []
    if args.external:
        external_issues, external_results = probe_urls(
            external,
            {url for url, references in external.items() if any(is_image_reference(ref) for ref in references)},
            args.timeout,
            args.workers,
        )
        issues.extend(external_issues)

    live_results: list[dict[str, Any]] = []
    if args.live:
        page_paths = list(documents) if args.all_pages else sorted(path for path in canonical if path in documents)
        live_refs = live_page_references(page_paths, canonical)
        live_issues, live_results = probe_urls(live_refs, set(), args.timeout, args.workers)
        for issue in live_issues:
            issue.code = "live_page_unverified" if issue.severity == "warning" else "live_page_failed"
        issues.extend(live_issues)

    issues.sort(key=lambda item: (item.severity != "error", item.scope != "canonical", item.code, item.source, item.line))
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "site": SITE_URL,
        "scope": {
            "tracked_deployed_files": len(deployed_paths),
            "documents": len(documents),
            "canonical_documents": sum(document.scope == "canonical" for document in documents.values()),
            "legacy_documents": sum(document.scope == "legacy" for document in documents.values()),
            "unique_external_references": len(external),
            "referenced_local_images": referenced_image_count,
            "deployable_images": len(deployable_images),
        },
        "summary": summarize(issues),
        "issues": [asdict(issue) for issue in issues],
        "external_results": external_results,
        "live_results": live_results,
    }
    print(
        "SITE_SURFACE: "
        f"{len(documents)} documents ({report['scope']['canonical_documents']} canonical, "
        f"{report['scope']['legacy_documents']} legacy); {len(deployed_paths)} deployed tracked files"
    )
    print(
        "REFERENCES: "
        f"{referenced_image_count} referenced local images; "
        f"{len(deployable_images)} deployable images decoded; {len(external)} unique external URLs"
    )
    print(
        "ISSUES: "
        f"{report['summary']['by_severity'].get('error', 0)} errors; "
        f"{report['summary']['by_severity'].get('warning', 0)} warnings"
    )
    for code, count in list(report["summary"]["by_code"].items())[:15]:
        print(f"  {code}: {count}")
    for issue in issues[: args.show]:
        location = f"{issue.source}:{issue.line}" if issue.line else issue.source
        target = f" -> {issue.target}" if issue.target else ""
        print(f"{issue.severity.upper()} {issue.code} {location}{target} {issue.detail}".rstrip())

    if args.json_output:
        output = Path(args.json_output)
        if not output.is_absolute():
            output = ROOT / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"REPORT_WRITTEN: {output.relative_to(ROOT) if output.is_relative_to(ROOT) else output}")

    errors = sum(issue.severity == "error" for issue in issues)
    return 1 if args.strict and errors else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", action="store_true", help="Probe every external link and dependency.")
    parser.add_argument("--live", action="store_true", help="Probe deployed page URLs.")
    parser.add_argument("--all-pages", action="store_true", help="With --live, include unsitemapped legacy pages.")
    parser.add_argument("--strict", action="store_true", help="Exit nonzero when errors are found.")
    parser.add_argument("--json", dest="json_output", help="Write a machine-readable report.")
    parser.add_argument("--show", type=int, default=30, help="Maximum detailed issues to print.")
    parser.add_argument("--timeout", type=float, default=12.0, help="Seconds per network attempt.")
    parser.add_argument("--workers", type=int, default=16, help="Concurrent network probes.")
    args = parser.parse_args()
    if args.timeout <= 0 or args.workers <= 0 or args.show < 0:
        parser.error("timeout/workers must be positive and show cannot be negative")
    if args.all_pages and not args.live:
        parser.error("--all-pages requires --live")
    return args


if __name__ == "__main__":
    try:
        sys.exit(run(parse_args()))
    except (OSError, ValueError, ET.ParseError, subprocess.CalledProcessError) as exc:
        print(f"AUDIT_ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
