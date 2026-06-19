#!/usr/bin/env python3
"""Local-only publishing command center server for Outside The World essays."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import mimetypes
import os
import re
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import narrative_sync
from tools import publisher_source_contract as source_contract

BACKUP_ROOT = ROOT / "backups" / "published_essays"
PREVIEW_ROOT = ROOT / ".publisher_preview"
DEFAULT_PRIVATE_REPO = ROOT.parent / "otw-private-writing"
READING_AIDS_ROOT = ROOT / narrative_sync.reading_aids_folder
CURRENT_NARRATIVE_ROOT = ROOT / narrative_sync.input_folder
ARCHIVE_ROOT = ROOT / narrative_sync.share_output_folder
OG_ROOT = ROOT / narrative_sync.og_output_folder
PUBLISHER_HTML = ROOT / "publisher.html"
BACKUP_ID_PATTERN = re.compile(r"^[0-9]{8}T[0-9]{6}Z(?:-[A-Za-z0-9_-]{2,16})?$")
SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"\b(?:OPENAI_API_KEY|GITHUB_TOKEN|PUBLISH_KEY|PUBLISHER_ACCESS_KEY)\s*[=:]\s*\S+",
    re.I,
)
SECRET_VALUE_PATTERN = re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b")
PRIVATE_ARCHIVE_SCHEMA = "otw.privateWritingArchive"
PRIVATE_ARCHIVE_REQUEST_SCHEMA = "otw.publisher.privateArchiveRequest"
PRIVATE_GIT_NAME = "OTW Private Publisher"
PRIVATE_GIT_EMAIL = "private@localhost"

ALLOWED_STATIC_ROOTS = {
    "Images": ROOT / "Images",
    "media": ROOT / "media",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def safe_slug(value: str) -> str:
    return source_contract.slug_for_path(Path(str(value or "").strip()))


def re_safe_backup_id(value: str) -> bool:
    return bool(BACKUP_ID_PATTERN.match(str(value or "")))


def unique_backup_id(state: "PublisherState", slug: str) -> str:
    base = stamp()
    root = state.history_dir(slug)
    if not (root / base).exists():
        return base
    for index in range(1, 100):
        candidate = f"{base}-{index:02d}"
        if not (root / candidate).exists():
            return candidate
    return f"{base}-{secrets.token_urlsafe(4)}"


def run_command(args: list[str]) -> dict:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "args": args,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "ok": result.returncode == 0,
    }


def path_hashes(paths: set[Path]) -> dict[str, str | None]:
    hashes: dict[str, str | None] = {}
    for path in paths:
        if path.exists() and path.is_file():
            hashes[rel(path)] = sha256_bytes(path.read_bytes())
        else:
            try:
                hashes[rel(path)] = None
            except ValueError:
                continue
    return hashes


def changed_hashes(before: dict[str, str | None], after: dict[str, str | None]) -> list[str]:
    keys = set(before) | set(after)
    return sorted(key for key in keys if before.get(key) != after.get(key))


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def private_repo_from_value(value: str | None = None) -> Path:
    selected = value or os.environ.get("OTW_PRIVATE_WRITING_REPO") or str(DEFAULT_PRIVATE_REPO)
    return Path(selected).expanduser().resolve()


def private_rel(repo: Path, path: Path) -> str:
    return str(path.resolve().relative_to(repo.resolve()))


def run_private_git(repo: Path, args: list[str]) -> dict:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)
    return {
        "args": ["git", *args],
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "ok": result.returncode == 0,
    }


def private_repo_has_remote(repo: Path) -> bool:
    if not (repo / ".git").exists():
        return False
    result = run_private_git(repo, ["remote"])
    return result["ok"] and bool(result["stdout"].strip())


def private_repo_status(repo: Path) -> dict:
    initialized = (repo / ".git").exists()
    inside_public_repo = is_relative_to(repo, ROOT)
    has_remote = private_repo_has_remote(repo) if initialized else False
    dirty: list[str] = []
    staged: list[str] = []
    if initialized:
        status = run_private_git(repo, ["status", "--porcelain"])
        if status["ok"]:
            dirty = [line for line in status["stdout"].splitlines() if line.strip()]
        cached = run_private_git(repo, ["diff", "--cached", "--name-only"])
        if cached["ok"]:
            staged = [line for line in cached["stdout"].splitlines() if line.strip()]
    available = not inside_public_repo and not has_remote
    reason = ""
    if inside_public_repo:
        reason = "Private archive path is inside the public site repository."
    elif has_remote:
        reason = "Private archive repository has a remote configured."
    return {
        "repoPath": str(repo),
        "initialized": initialized,
        "insidePublicRepo": inside_public_repo,
        "hasRemote": has_remote,
        "dirty": dirty,
        "staged": staged,
        "available": available,
        "reason": reason,
    }


def ensure_private_repo(repo: Path) -> dict:
    status = private_repo_status(repo)
    if status["insidePublicRepo"]:
        raise ValueError("Private archive path must live outside the public site repository.")
    repo.mkdir(parents=True, exist_ok=True)
    if not (repo / ".git").exists():
        result = run_private_git(repo, ["init"])
        if not result["ok"]:
            raise RuntimeError(f"Could not initialize private archive repository: {result['stderr'] or result['stdout']}")

    if private_repo_has_remote(repo):
        raise ValueError("Private archive repository has a remote configured; remove it before archiving private writing.")

    configure_private_git_identity(repo)
    readme = repo / "README.md"
    created_readme = False
    if not readme.exists():
        readme.write_text(
            "# OTW Private Writing Archive\n\n"
            "Local-only source material archived from the Outside The World publisher.\n"
            "This repository is intentionally private and should not have a remote.\n",
            encoding="utf-8",
        )
        created_readme = True

    if not run_private_git(repo, ["rev-parse", "--verify", "HEAD"]).get("ok"):
        result = commit_private_paths(repo, ["README.md"], "Initialize private writing archive")
        if not result.get("ok"):
            raise RuntimeError(f"Could not create initial private archive commit: {result.get('stderr') or result.get('stdout')}")
    elif created_readme:
        result = commit_private_paths(repo, ["README.md"], "Add private writing archive README")
        if not result.get("ok"):
            raise RuntimeError(f"Could not commit private archive README: {result.get('stderr') or result.get('stdout')}")

    staged = private_repo_status(repo).get("staged") or []
    if staged:
        raise ValueError("Private archive repository has staged changes; clear them before archiving.")
    return private_repo_status(repo)


def configure_private_git_identity(repo: Path) -> None:
    name = run_private_git(repo, ["config", "--get", "user.name"])
    email = run_private_git(repo, ["config", "--get", "user.email"])
    if not name["ok"] or not name["stdout"].strip():
        run_private_git(repo, ["config", "user.name", PRIVATE_GIT_NAME])
    if not email["ok"] or not email["stdout"].strip():
        run_private_git(repo, ["config", "user.email", PRIVATE_GIT_EMAIL])


def commit_private_paths(repo: Path, paths: list[str], message: str) -> dict:
    add = run_private_git(repo, ["add", *paths])
    if not add["ok"]:
        return add
    commit = run_private_git(repo, ["commit", "-m", message])
    if not commit["ok"]:
        return commit
    rev = run_private_git(repo, ["rev-parse", "HEAD"])
    if rev["ok"]:
        commit["commit"] = rev["stdout"].strip()
    return commit


def reject_secret_text(value: str) -> None:
    text = str(value or "")
    if SECRET_ASSIGNMENT_PATTERN.search(text) or SECRET_VALUE_PATTERN.search(text):
        raise ValueError("Private archive blocked because the draft appears to contain a secret.")


def sanitize_private_value(value):
    if isinstance(value, list):
        return [sanitize_private_value(item) for item in value]
    if isinstance(value, dict):
        output = {}
        for key, child in value.items():
            normalized = str(key).lower().replace("_", "").replace("-", "")
            if normalized in {"publishkey", "publisherkey", "publisheraccesskey", "accesskey"}:
                continue
            if key == "dataUrl":
                output["dataUrlLength"] = len(str(child or ""))
                continue
            output[key] = sanitize_private_value(child)
        return output
    if isinstance(value, str):
        reject_secret_text(value)
        return (
            value
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace("blob:", "local-blob-redacted:")
        )
    return value


def block_has_visible_content(block: dict) -> bool:
    if not isinstance(block, dict):
        return False
    for key in ("text", "html", "raw", "markdown", "alt", "caption"):
        if re.sub(r"<[^>]+>", "", str(block.get(key) or "")).strip():
            return True
    items = block.get("items")
    if isinstance(items, list):
        return any(block_has_visible_content(item) for item in items if isinstance(item, dict))
    return False


def article_has_visible_content(article: dict) -> bool:
    if not isinstance(article, dict):
        return False
    if str(article.get("title") or "").strip():
        return True
    body = article.get("body") if isinstance(article.get("body"), dict) else {}
    blocks = body.get("blocks") if isinstance(body.get("blocks"), list) else []
    return any(block_has_visible_content(block) for block in blocks)


def private_archive_slug(article: dict) -> str:
    metadata = article.get("metadata") if isinstance(article.get("metadata"), dict) else {}
    raw_slug = str(metadata.get("slug") or "").strip()
    if raw_slug and ("/" in raw_slug or "\\" in raw_slug or ".." in raw_slug):
        raise ValueError("Private archive slug cannot contain path traversal characters.")
    source = raw_slug or str(article.get("title") or metadata.get("docName") or "untitled-draft")
    slug = narrative_sync.slugify(source) or "untitled-draft"
    return slug[:96].strip("-") or "untitled-draft"


def private_archive_date(article: dict) -> str:
    metadata = article.get("metadata") if isinstance(article.get("metadata"), dict) else {}
    for key in ("publishDate", "articleDate"):
        value = str(metadata.get(key) or "").strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return value
    return datetime.now().strftime("%Y-%m-%d")


def private_archive_markdown(article: dict, publish_payload: dict) -> str:
    content = publish_payload.get("content") if isinstance(publish_payload.get("content"), dict) else {}
    markdown = str(content.get("markdown") or "").strip()
    if markdown:
        reject_secret_text(markdown)
        return source_contract.normalize_newlines(markdown).strip() + "\n"

    title = str(article.get("title") or "Untitled Draft").strip() or "Untitled Draft"
    date = private_archive_date(article)
    subhead = str(article.get("subhead") or "").strip()
    lines = [f"# {title}", f"Date: {date}", ""]
    if subhead:
        lines.extend([f"_{subhead}_", ""])
    body = article.get("body") if isinstance(article.get("body"), dict) else {}
    blocks = body.get("blocks") if isinstance(body.get("blocks"), list) else []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        markdown_block = str(block.get("sourceMarkdown") or block.get("markdown") or block.get("text") or "").strip()
        if markdown_block:
            lines.extend([markdown_block, ""])
    markdown = "\n".join(lines).strip() + "\n"
    reject_secret_text(markdown)
    return markdown


def local_image_warnings(article: dict) -> list[str]:
    body = article.get("body") if isinstance(article.get("body"), dict) else {}
    blocks = body.get("blocks") if isinstance(body.get("blocks"), list) else []
    count = 0
    for block in blocks:
        if not isinstance(block, dict) or block.get("type") != "image":
            continue
        source = block.get("source") if isinstance(block.get("source"), dict) else {}
        upload = block.get("upload") if isinstance(block.get("upload"), dict) else {}
        url = source.get("url") or upload.get("uploadedUrl")
        if source.get("kind") != "url" or not url:
            count += 1
    if not count:
        return []
    suffix = "s" if count != 1 else ""
    return [f"{count} local-only image preview{suffix} were not embedded in the private archive."]


def unique_private_paths(repo: Path, date: str, slug: str) -> tuple[Path, Path]:
    year = date[:4]
    folder = repo / "drafts" / year
    for index in range(1, 1000):
        suffix = "" if index == 1 else f"-{index}"
        base = f"{date}-{slug}{suffix}"
        markdown_path = folder / f"{base}.md"
        article_path = folder / f"{base}.article.json"
        if not markdown_path.exists() and not article_path.exists():
            return markdown_path, article_path
    raise RuntimeError("Could not find an available private archive filename.")


def read_private_manifest(repo: Path) -> dict:
    path = repo / "manifest.json"
    if not path.exists():
        return {"schema": PRIVATE_ARCHIVE_SCHEMA, "version": 1, "drafts": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("drafts"), list):
        raise ValueError("Private archive manifest is malformed.")
    payload.setdefault("schema", PRIVATE_ARCHIVE_SCHEMA)
    payload.setdefault("version", 1)
    return payload


def write_private_manifest(repo: Path, manifest: dict) -> None:
    write_json(repo / "manifest.json", manifest)


def archive_private_draft(repo: Path, payload: dict) -> dict:
    ensure_private_repo(repo)
    article = payload.get("article") if isinstance(payload.get("article"), dict) else {}
    publish_payload = payload.get("publishPayload") if isinstance(payload.get("publishPayload"), dict) else {}
    if payload.get("schema") not in {PRIVATE_ARCHIVE_REQUEST_SCHEMA, None}:
        raise ValueError("Private archive request schema is invalid.")
    if not article_has_visible_content(article):
        raise ValueError("Private archive needs a title or body content.")

    sanitized_article = sanitize_private_value(article)
    sanitized_publish_payload = sanitize_private_value(publish_payload)
    title = str(sanitized_article.get("title") or "Untitled Draft").strip() or "Untitled Draft"
    date = private_archive_date(sanitized_article)
    slug = private_archive_slug(sanitized_article)
    markdown = private_archive_markdown(sanitized_article, sanitized_publish_payload)
    markdown_path, article_path = unique_private_paths(repo, date, slug)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    archived_at = utc_now()

    article_snapshot = {
        "schema": "otw.privateWritingArticle",
        "version": 1,
        "archivedAt": archived_at,
        "article": sanitized_article,
        "publishPayload": sanitized_publish_payload,
    }
    markdown_path.write_text(markdown, encoding="utf-8")
    write_json(article_path, article_snapshot)

    manifest = read_private_manifest(repo)
    entry = {
        "title": title,
        "date": date,
        "slug": slug,
        "archivedAt": archived_at,
        "path": private_rel(repo, markdown_path),
        "articlePath": private_rel(repo, article_path),
        "commit": None,
    }
    manifest["drafts"].append(entry)
    write_private_manifest(repo, manifest)

    commit_message = f"Archive private draft: {title}"[:180]
    commit = commit_private_paths(repo, [entry["path"], entry["articlePath"], "manifest.json"], commit_message)
    if not commit.get("ok"):
        raise RuntimeError(f"Could not commit private archive draft: {commit.get('stderr') or commit.get('stdout')}")
    draft_commit = commit.get("commit") or ""

    manifest = read_private_manifest(repo)
    manifest["drafts"][-1]["commit"] = draft_commit
    write_private_manifest(repo, manifest)
    manifest_commit = commit_private_paths(repo, ["manifest.json"], f"Record private archive manifest: {title}"[:180])
    if not manifest_commit.get("ok"):
        raise RuntimeError(f"Could not commit private archive manifest: {manifest_commit.get('stderr') or manifest_commit.get('stdout')}")

    return {
        "ok": True,
        "path": entry["path"],
        "articlePath": entry["articlePath"],
        "commit": draft_commit,
        "manifestCommit": manifest_commit.get("commit") or "",
        "warnings": local_image_warnings(sanitized_article),
        "message": "Private draft archived locally. Composer draft kept open.",
    }


def restore_snapshot(snapshot: dict[str, bytes | None]) -> None:
    for relative, content in snapshot.items():
        path = ROOT / relative
        if content is None:
            if path.exists() and path.is_file():
                path.unlink()
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)


def snapshot_file_contents(paths: set[Path]) -> dict[str, bytes | None]:
    snapshot: dict[str, bytes | None] = {}
    for path in paths:
        try:
            relative = rel(path)
        except ValueError:
            continue
        snapshot[relative] = path.read_bytes() if path.exists() and path.is_file() else None
    return snapshot


class PublisherState:
    def __init__(self, port: int, private_repo: Path | None = None):
        self.port = port
        self.token = secrets.token_urlsafe(32)
        self.private_repo = private_repo_from_value(str(private_repo) if private_repo else None)
        self.lock = threading.RLock()
        PREVIEW_ROOT.mkdir(parents=True, exist_ok=True)
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    @property
    def origin(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def documents(self) -> list[source_contract.SourceDocument]:
        return source_contract.library_documents()

    def slug_map(self) -> dict[str, source_contract.SourceDocument]:
        return {doc.slug: doc for doc in self.documents()}

    def require_slug(self, slug: str) -> source_contract.SourceDocument:
        normalized = safe_slug(slug)
        doc = self.slug_map().get(normalized)
        if not doc:
            raise KeyError(f"Unknown published essay slug: {slug}")
        return doc

    def draft_path(self, slug: str) -> Path:
        return BACKUP_ROOT / safe_slug(slug) / "draft_revision.json"

    def history_dir(self, slug: str) -> Path:
        return BACKUP_ROOT / safe_slug(slug)

    def sidecar_path(self, slug: str) -> Path:
        return READING_AIDS_ROOT / f"{safe_slug(slug)}.json"


def post_for_doc(doc: source_contract.SourceDocument, source: str | None = None) -> dict:
    return source_contract.post_from_source_document(doc, source)


def canonical_sidecar_status(doc: source_contract.SourceDocument) -> dict:
    path = READING_AIDS_ROOT / f"{doc.slug}.json"
    if not path.exists():
        return {"status": "none", "path": rel(path)}
    try:
        sidecar = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"status": "validation error", "path": rel(path), "errors": [str(exc)]}
    post = post_for_doc(doc)
    paragraphs = source_contract.paragraphs_for_source(doc)
    paragraph_ids = {item["id"] for item in paragraphs}
    essay_hash = narrative_sync.essay_hash_for_post(post)
    errors, warnings = narrative_sync.validate_reading_aids(sidecar, doc.slug, paragraph_ids, essay_hash)
    if errors:
        status = "validation error"
    elif sidecar.get("essayHash") != essay_hash:
        status = "stale"
    else:
        status = sidecar.get("reviewStatus") or "draft"
    return {
        "status": status,
        "path": rel(path),
        "reviewStatus": sidecar.get("reviewStatus"),
        "essayHash": sidecar.get("essayHash"),
        "errors": errors,
        "warnings": warnings,
    }


def draft_payload(state: PublisherState, doc: source_contract.SourceDocument) -> dict | None:
    payload = read_json(state.draft_path(doc.slug))
    if not payload:
        return None
    return payload if payload.get("slug") == doc.slug else None


def draft_source(state: PublisherState, doc: source_contract.SourceDocument) -> str:
    draft = draft_payload(state, doc)
    return str(draft.get("source")) if draft and draft.get("source") else doc.source


def draft_status(state: PublisherState, doc: source_contract.SourceDocument) -> dict:
    draft = draft_payload(state, doc)
    if not draft:
        return {"status": "clean", "hasDraft": False}
    source = str(draft.get("source") or "")
    if source == doc.source:
        return {"status": "clean", "hasDraft": True, "updatedAt": draft.get("updatedAt")}
    return {
        "status": "draft revision",
        "hasDraft": True,
        "updatedAt": draft.get("updatedAt"),
        "baseHash": draft.get("baseHash"),
    }


def essay_summary(state: PublisherState, doc: source_contract.SourceDocument) -> dict:
    post = post_for_doc(doc)
    deck = narrative_sync.publisher_subhead(post)
    word_count = narrative_sync.article_word_count(post, deck)
    source_path = doc.path
    stat = source_path.stat()
    return {
        "title": doc.title,
        "date": doc.date,
        "slug": doc.slug,
        "stem": doc.stem,
        "sourcePath": rel(source_path),
        "archivePath": doc.archive_path,
        "ogPath": doc.og_path,
        "publishStatus": "published",
        "readingAidStatus": canonical_sidecar_status(doc),
        "revisionStatus": draft_status(state, doc),
        "lastModified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
        "wordCount": word_count,
        "readMinutes": narrative_sync.article_read_minutes(word_count),
        "hasPublisherMetadata": bool(doc.metadata),
        "protectedBlockCount": sum(1 for block in doc.blocks if not block.editable),
    }


def load_sidecar(state: PublisherState, doc: source_contract.SourceDocument) -> dict | None:
    path = state.sidecar_path(doc.slug)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def blank_sidecar(doc: source_contract.SourceDocument, source: str | None = None) -> dict:
    post = post_for_doc(doc, source)
    return {
        "slug": doc.slug,
        "essayHash": narrative_sync.essay_hash_for_post(post),
        "reviewStatus": "draft",
        "generatedAt": utc_now(),
        "model": "manual",
        "signalBrief": {"text": "Draft article summary.", "locked": False},
        "readerMap": [],
        "checkpoints": [],
        "plainSignals": [],
    }


def validate_sidecar_for_source(doc: source_contract.SourceDocument, sidecar: dict, source: str | None = None) -> tuple[list[str], list[str], dict]:
    paragraphs = source_contract.paragraphs_for_source(doc, source)
    paragraph_ids = {item["id"] for item in paragraphs}
    post = post_for_doc(doc, source)
    essay_hash = narrative_sync.essay_hash_for_post(post) if source is None else source_contract.sha256_text(source)
    errors, warnings = narrative_sync.validate_reading_aids(sidecar, doc.slug, paragraph_ids, essay_hash)
    return errors, warnings, {"paragraphs": paragraphs, "essayHash": essay_hash}


def write_sidecar_with_backup(state: PublisherState, doc: source_contract.SourceDocument, sidecar: dict) -> dict:
    path = state.sidecar_path(doc.slug)
    backup = None
    if path.exists():
        backup_dir = state.history_dir(doc.slug) / unique_backup_id(state, doc.slug)
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup = backup_dir / "reading_aids.json"
        shutil.copy2(path, backup)
    write_json(path, sidecar)
    return {"path": rel(path), "backup": rel(backup) if backup else None}


def create_source_backup(state: PublisherState, doc: source_contract.SourceDocument, reason: str) -> dict:
    backup_id = unique_backup_id(state, doc.slug)
    backup_dir = state.history_dir(doc.slug) / backup_id
    backup_dir.mkdir(parents=True, exist_ok=True)
    source_backup = backup_dir / "source.md"
    source_backup.write_text(doc.path.read_text(encoding="utf-8"), encoding="utf-8")
    manifest = {
        "id": backup_id,
        "slug": doc.slug,
        "reason": reason,
        "createdAt": utc_now(),
        "sourcePath": rel(doc.path),
        "sourceHash": source_contract.sha256_text(source_backup.read_text(encoding="utf-8")),
        "archivePath": doc.archive_path,
        "ogPath": doc.og_path,
    }
    write_json(backup_dir / "manifest.json", manifest)
    return manifest


def list_backups(state: PublisherState, doc: source_contract.SourceDocument) -> list[dict]:
    history = []
    root = state.history_dir(doc.slug)
    if not root.exists():
        return history
    for manifest_path in sorted(root.glob("*/manifest.json"), reverse=True):
        try:
            item = json.loads(manifest_path.read_text(encoding="utf-8"))
            item["hasSource"] = (manifest_path.parent / "source.md").exists()
            history.append(item)
        except json.JSONDecodeError:
            continue
    return history


def expected_output_paths(doc: source_contract.SourceDocument) -> set[Path]:
    return {
        doc.path,
        ROOT / "narrative_data.js",
        ROOT / "atom.xml",
        ROOT / doc.archive_path,
        ROOT / doc.og_path,
    }


def snapshot_generation_scope(doc: source_contract.SourceDocument) -> set[Path]:
    paths = set(expected_output_paths(doc))
    paths.update(ARCHIVE_ROOT.glob("*.html"))
    paths.update(OG_ROOT.glob("*.png"))
    paths.add(ROOT / "narrative_data.js")
    paths.add(ROOT / "atom.xml")
    paths.add(doc.path)
    return paths


def run_generation(doc: source_contract.SourceDocument) -> dict:
    sync_result = run_command([sys.executable, "narrative_sync.py"])
    feed_result = run_command([sys.executable, "tools/generate_atom_feed.py"])
    return {"sync": sync_result, "feed": feed_result, "ok": sync_result["ok"] and feed_result["ok"]}


def regenerate_with_allowlist(doc: source_contract.SourceDocument, source: str, allow_unexpected: bool = False) -> dict:
    scope = snapshot_generation_scope(doc)
    before_hashes = path_hashes(scope)
    before_contents = snapshot_file_contents(scope)
    doc.path.write_text(source, encoding="utf-8")
    generation = run_generation(doc)
    after_hashes = path_hashes(scope)
    changed = changed_hashes(before_hashes, after_hashes)
    allowed = {rel(path) for path in expected_output_paths(doc)}
    unexpected = sorted(path for path in changed if path not in allowed)
    if (not generation["ok"] or unexpected) and not allow_unexpected:
        restore_snapshot(before_contents)
        status = "blocked" if unexpected else "failed"
    else:
        status = "ok" if generation["ok"] else "failed"
    return {
        "status": status,
        "generation": generation,
        "changedFiles": changed,
        "allowedFiles": sorted(allowed),
        "unexpectedFiles": unexpected,
    }


def current_git_branch() -> str:
    result = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return result["stdout"].strip() if result["ok"] else ""


def git_status_paths() -> list[str]:
    result = run_command(["git", "status", "--porcelain"])
    if not result["ok"]:
        return []
    paths = []
    for line in result["stdout"].splitlines():
        if not line.strip():
            continue
        paths.append(line[3:].strip())
    return paths


def compare_origin_file(branch: str, relative_path: str, local_source: str) -> dict:
    if not branch:
        return {"ok": False, "message": "Current git branch could not be detected."}
    result = run_command(["git", "show", f"origin/{branch}:{relative_path}"])
    if not result["ok"]:
        return {"ok": False, "message": f"Could not read origin/{branch}:{relative_path}."}
    origin_source = result["stdout"]
    if source_contract.normalize_newlines(origin_source) != source_contract.normalize_newlines(local_source):
        return {"ok": False, "message": "Local source differs from origin; live publish is blocked until sources are reconciled."}
    return {"ok": True, "message": "Local source matches origin."}


def preview_page(state: PublisherState, doc: source_contract.SourceDocument, source: str, include_reading_aids: bool) -> dict:
    session = secrets.token_urlsafe(10)
    preview_dir = PREVIEW_ROOT / session
    archive_dir = preview_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    for asset in ["archive_reader.css", "archive_reader.js"]:
        source_asset = ROOT / asset
        if source_asset.exists():
            shutil.copy2(source_asset, preview_dir / asset)
    post = post_for_doc(doc, source)
    posts = narrative_sync.load_posts()
    stems = [narrative_sync.post_stem(item.get("file") or "") for item in posts]
    index = stems.index(doc.stem) if doc.stem in stems else -1
    newer = posts[index - 1] if index > 0 else None
    older = posts[index + 1] if index >= 0 and index + 1 < len(posts) else None

    original_loader = narrative_sync.load_reading_aids_for_post
    if not include_reading_aids:
        narrative_sync.load_reading_aids_for_post = lambda *_args, **_kwargs: None
    try:
        html = narrative_sync.render_share_page(post, newer, older, include_draft_reading_aids=include_reading_aids)
    finally:
        narrative_sync.load_reading_aids_for_post = original_loader

    output = archive_dir / f"{doc.stem}.html"
    output.write_text(html, encoding="utf-8")
    return {
        "session": session,
        "path": rel(output),
        "url": f"/preview/{session}/archive/{doc.stem}.html",
        "includeReadingAids": include_reading_aids,
    }


class PublisherHandler(BaseHTTPRequestHandler):
    server_version = "OTWPublisher/1.0"

    @property
    def state(self) -> PublisherState:
        return self.server.state  # type: ignore[attr-defined]

    def log_message(self, format, *args):  # noqa: A002
        sys.stderr.write("%s - - [%s] %s\n" % (self.client_address[0], self.log_date_time_string(), format % args))

    def read_body(self) -> dict:
        length = int(self.headers.get("content-length") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8") or "{}")

    def send_json(self, payload, status: int = 200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json; charset=utf-8")
        self.send_header("content-length", str(len(body)))
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, value: str, content_type: str = "text/plain; charset=utf-8", status: int = 200):
        body = value.encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def error_json(self, message: str, status: int = 400, **extra):
        self.send_json({"ok": False, "error": message, **extra}, status)

    def check_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        allowed = {self.state.origin, f"http://localhost:{self.state.port}"}
        return origin in allowed

    def require_api_auth(self) -> bool:
        if not self.check_origin():
            self.error_json("Cross-origin publisher API requests are not allowed.", 403)
            return False
        token = self.headers.get("x-publisher-token") or ""
        if token != self.state.token:
            self.error_json("Missing or invalid local publisher token.", 401)
            return False
        return True

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path in {"/", "/publisher.html"}:
            return self.serve_publisher()
        if path.startswith("/api/"):
            if not self.require_api_auth():
                return
            return self.handle_api("GET", path, parse_qs(parsed.query), {})
        if path.startswith("/preview/"):
            return self.serve_preview(path)
        return self.serve_static(path)

    def do_POST(self):
        self.handle_mutation("POST")

    def do_PATCH(self):
        self.handle_mutation("PATCH")

    def do_DELETE(self):
        self.handle_mutation("DELETE")

    def handle_mutation(self, method: str):
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            return self.error_json("Unknown endpoint.", 404)
        if not self.require_api_auth():
            return
        try:
            payload = self.read_body()
        except json.JSONDecodeError:
            return self.error_json("Request body must be JSON.", 400)
        return self.handle_api(method, parsed.path, parse_qs(parsed.query), payload)

    def serve_publisher(self):
        html_text = PUBLISHER_HTML.read_text(encoding="utf-8")
        marker = "</head>"
        injection = (
            f'<meta name="otw-publisher-local-server" content="1">\n'
            f'<meta name="otw-publisher-token" content="{self.state.token}">\n'
            f'<meta name="otw-publisher-api-origin" content="{self.state.origin}">\n'
        )
        html_text = html_text.replace(marker, injection + marker, 1)
        self.send_text(html_text, "text/html; charset=utf-8")

    def serve_static(self, path: str):
        clean = Path(unquote(path.lstrip("/")))
        if clean.name in {"archive_reader.css", "archive_reader.js", "publisher_manager.js"}:
            file_path = ROOT / clean.name
        elif clean.parts and clean.parts[0] in ALLOWED_STATIC_ROOTS:
            file_path = (ALLOWED_STATIC_ROOTS[clean.parts[0]] / Path(*clean.parts[1:])).resolve()
            if not str(file_path).startswith(str(ALLOWED_STATIC_ROOTS[clean.parts[0]].resolve())):
                return self.error_json("Static path is not allowed.", 403)
        else:
            return self.error_json("Static path is not allowed.", 404)
        if not file_path.exists() or not file_path.is_file():
            return self.error_json("Static file not found.", 404)
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_preview(self, path: str):
        relative = Path(unquote(path.removeprefix("/preview/")))
        file_path = (PREVIEW_ROOT / relative).resolve()
        if not str(file_path).startswith(str(PREVIEW_ROOT.resolve())):
            return self.error_json("Preview path is not allowed.", 403)
        if not file_path.exists() or not file_path.is_file():
            return self.error_json("Preview file not found.", 404)
        content_type = mimetypes.guess_type(str(file_path))[0] or "text/html"
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("content-type", content_type)
        self.send_header("content-length", str(len(body)))
        self.send_header("cache-control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def handle_api(self, method: str, path: str, _query: dict, payload: dict):
        try:
            if method == "GET" and path == "/api/session":
                return self.send_json({
                    "ok": True,
                    "hasOpenAIKey": bool(os.environ.get("OPENAI_API_KEY")),
                    "origin": self.state.origin,
                    "privateArchive": private_repo_status(self.state.private_repo),
                })
            if method == "GET" and path == "/api/private-archive/status":
                return self.send_json({"ok": True, "privateArchive": private_repo_status(self.state.private_repo)})
            if method == "POST" and path == "/api/private-archive/drafts":
                with self.state.lock:
                    result = archive_private_draft(self.state.private_repo, payload)
                return self.send_json(result)
            if method == "GET" and path == "/api/published-essays":
                docs = self.state.documents()
                return self.send_json({"ok": True, "essays": [essay_summary(self.state, doc) for doc in docs]})

            parts = [part for part in path.split("/") if part]
            if len(parts) < 3 or parts[0] != "api" or parts[1] != "published-essays":
                return self.error_json("Unknown endpoint.", 404)
            slug = safe_slug(parts[2])
            doc = self.state.require_slug(slug)
            tail = parts[3:]

            if method == "GET" and not tail:
                return self.send_json(self.essay_detail(doc))
            if method == "POST" and tail == ["draft-revision"]:
                return self.create_draft(doc)
            if method == "PATCH" and tail == ["draft-revision"]:
                return self.update_draft(doc, payload)
            if method == "POST" and tail == ["discard-draft"]:
                return self.discard_draft(doc)
            if method == "GET" and tail == ["diff"]:
                return self.diff_detail(doc)
            if method == "POST" and tail == ["preview"]:
                return self.preview(doc, payload)
            if method == "POST" and tail == ["republish-local"]:
                return self.republish_local(doc, payload)
            if method == "POST" and tail == ["publish-live"]:
                return self.publish_live(doc, payload)
            if method == "GET" and tail == ["history"]:
                return self.send_json({"ok": True, "history": list_backups(self.state, doc)})
            if method == "POST" and tail == ["restore"]:
                return self.restore_backup(doc, payload)
            if tail and tail[0] == "reading-aids":
                return self.reading_aids(method, doc, tail[1:], payload)
            return self.error_json("Unknown endpoint.", 404)
        except KeyError as exc:
            return self.error_json(str(exc), 404)
        except Exception as exc:
            return self.error_json(str(exc), 500)

    def essay_detail(self, doc: source_contract.SourceDocument):
        current_source = doc.source
        active_source = draft_source(self.state, doc)
        draft_doc = source_contract.document_from_source_text(doc.path, active_source)
        sidecar = load_sidecar(self.state, doc)
        baseline_paragraphs = source_contract.paragraphs_for_source(doc, current_source)
        draft_paragraphs = source_contract.paragraphs_for_source(doc, active_source)
        return {
            "ok": True,
            "essay": essay_summary(self.state, doc),
            "document": draft_doc.to_json(include_source=False),
            "composerArticle": source_contract.composer_article_for_document(doc, active_source),
            "source": active_source,
            "publishedSourceHash": source_contract.sha256_text(current_source),
            "draft": draft_payload(self.state, doc),
            "diff": source_contract.diff_sources(current_source, active_source),
            "sidecar": sidecar,
            "sidecarStatus": canonical_sidecar_status(doc),
            "paragraphs": draft_paragraphs,
            "anchorAnalysis": source_contract.analyze_anchor_stability(baseline_paragraphs, draft_paragraphs, sidecar),
            "history": list_backups(self.state, doc),
            "hasOpenAIKey": bool(os.environ.get("OPENAI_API_KEY")),
        }

    def create_draft(self, doc: source_contract.SourceDocument):
        payload = {
            "slug": doc.slug,
            "createdAt": utc_now(),
            "updatedAt": utc_now(),
            "baseHash": doc.source_hash,
            "source": doc.source,
        }
        write_json(self.state.draft_path(doc.slug), payload)
        return self.send_json({"ok": True, "draft": payload})

    def update_draft(self, doc: source_contract.SourceDocument, payload: dict):
        existing = draft_payload(self.state, doc) or {
            "slug": doc.slug,
            "createdAt": utc_now(),
            "baseHash": doc.source_hash,
        }
        if payload.get("source"):
            source = source_contract.normalize_newlines(str(payload.get("source")))
            draft_doc = source_contract.document_from_source_text(doc.path, source)
        else:
            source = source_contract.serialize_document(doc, payload)
            draft_doc = source_contract.document_from_source_text(doc.path, source)
        if draft_doc.slug != doc.slug:
            return self.error_json("Slug/path changes are not supported by normal revision.", 400)
        existing.update({
            "updatedAt": utc_now(),
            "source": source,
            "sourceHash": source_contract.sha256_text(source),
        })
        write_json(self.state.draft_path(doc.slug), existing)
        return self.send_json(self.essay_detail(doc))

    def discard_draft(self, doc: source_contract.SourceDocument):
        path = self.state.draft_path(doc.slug)
        if path.exists():
            path.unlink()
        return self.send_json({"ok": True, "revisionStatus": draft_status(self.state, doc)})

    def diff_detail(self, doc: source_contract.SourceDocument):
        active = draft_source(self.state, doc)
        return self.send_json({
            "ok": True,
            "diff": source_contract.diff_sources(doc.source, active),
            "semanticSame": source_contract.semantic_same(doc.source, active),
        })

    def preview(self, doc: source_contract.SourceDocument, payload: dict):
        active = draft_source(self.state, doc)
        include_aids = bool(payload.get("includeReadingAids"))
        preview = preview_page(self.state, doc, active, include_aids)
        return self.send_json({"ok": True, "preview": preview, "message": "Preview generated. Production archive output was not modified."})

    def republish_local(self, doc: source_contract.SourceDocument, payload: dict):
        active = draft_source(self.state, doc)
        if active == doc.source:
            return self.send_json({"ok": True, "status": "clean", "message": "No draft changes to republish. Live site unchanged."})
        if not payload.get("confirmDiffViewed"):
            return self.error_json("Diff must be reviewed before local republish.", 409)
        draft_doc = source_contract.document_from_source_text(doc.path, active)
        if draft_doc.date != doc.date and not payload.get("allowDateChange"):
            return self.error_json("Publication date changes require an explicit advanced action.", 409)
        sidecar = load_sidecar(self.state, doc)
        if sidecar and sidecar.get("reviewStatus") == "approved":
            anchors = source_contract.analyze_anchor_stability(
                source_contract.paragraphs_for_source(doc, doc.source),
                source_contract.paragraphs_for_source(doc, active),
                sidecar,
            )
            if anchors.get("hasBlockingIssues"):
                return self.error_json("Approved reading aids have missing paragraph anchors.", 409, anchorAnalysis=anchors)
        backup = create_source_backup(self.state, doc, "republish-local")
        result = regenerate_with_allowlist(doc, active, allow_unexpected=bool(payload.get("allowUnexpectedGeneratedFiles")))
        if result["status"] != "ok":
            return self.error_json("Local republish blocked or failed.", 409, backup=backup, result=result)
        draft = self.state.draft_path(doc.slug)
        if draft.exists():
            draft.unlink()
        return self.send_json({
            "ok": True,
            "message": "Local archive regenerated. Live site unchanged.",
            "backup": backup,
            "result": result,
        })

    def publish_live(self, doc: source_contract.SourceDocument, payload: dict):
        allowed = {rel(path) for path in expected_output_paths(doc)}
        dirty = git_status_paths()
        unexpected_dirty = [path for path in dirty if path not in allowed]
        if unexpected_dirty:
            return self.error_json("Live publish blocked by unrelated working tree changes.", 409, unexpectedFiles=unexpected_dirty)
        branch = current_git_branch()
        origin_check = compare_origin_file(branch, rel(doc.path), doc.path.read_text(encoding="utf-8"))
        if not origin_check.get("ok"):
            return self.error_json(origin_check.get("message", "Local/live source divergence detected."), 409)
        if not payload.get("confirmLivePublish"):
            return self.error_json("Live publish requires explicit confirmation.", 409)
        add_result = run_command(["git", "add", *sorted(allowed)])
        if not add_result["ok"]:
            return self.error_json("Could not stage live publish files.", 500, result=add_result)
        commit_message = str(payload.get("message") or f"Republish essay: {doc.title}")[:180]
        commit_result = run_command(["git", "commit", "-m", commit_message])
        if not commit_result["ok"]:
            return self.error_json("Could not create live publish commit.", 500, result=commit_result)
        push_result = run_command(["git", "push"])
        if not push_result["ok"]:
            return self.error_json("Could not push live publish commit.", 500, commit=commit_result, result=push_result)
        return self.send_json({"ok": True, "message": "Live publish pushed to GitHub.", "commit": commit_result, "push": push_result})

    def restore_backup(self, doc: source_contract.SourceDocument, payload: dict):
        backup_id = str(payload.get("backupId") or "").strip()
        if not backup_id or not re_safe_backup_id(backup_id):
            return self.error_json("backupId is required.", 400)
        backup_source = self.state.history_dir(doc.slug) / backup_id / "source.md"
        if not backup_source.exists():
            return self.error_json("Backup source not found.", 404)
        source = backup_source.read_text(encoding="utf-8")
        source_contract.document_from_source_text(doc.path, source)
        pre_restore = create_source_backup(self.state, doc, "pre-restore")
        result = regenerate_with_allowlist(doc, source, allow_unexpected=bool(payload.get("allowUnexpectedGeneratedFiles")))
        if result["status"] != "ok":
            return self.error_json("Restore blocked or failed.", 409, preRestoreBackup=pre_restore, result=result)
        draft = self.state.draft_path(doc.slug)
        if draft.exists():
            draft.unlink()
        return self.send_json({
            "ok": True,
            "message": "Backup restored locally. Live site unchanged.",
            "preRestoreBackup": pre_restore,
            "result": result,
        })

    def reading_aids(self, method: str, doc: source_contract.SourceDocument, tail: list[str], payload: dict):
        if method == "GET" and not tail:
            return self.send_json({
                "ok": True,
                "sidecar": load_sidecar(self.state, doc),
                "status": canonical_sidecar_status(doc),
            })
        if method == "POST" and tail == ["create"]:
            sidecar = blank_sidecar(doc)
            result = write_sidecar_with_backup(self.state, doc, sidecar)
            return self.send_json({"ok": True, "sidecar": sidecar, "write": result})
        if method == "PATCH" and not tail:
            sidecar = copy.deepcopy(payload.get("sidecar") or {})
            if not isinstance(sidecar, dict):
                return self.error_json("sidecar object is required.", 400)
            sidecar["slug"] = doc.slug
            sidecar["reviewStatus"] = "draft"
            sidecar["essayHash"] = sidecar.get("essayHash") or source_contract.sha256_text(draft_source(self.state, doc))
            sidecar["generatedAt"] = sidecar.get("generatedAt") or utc_now()
            sidecar["model"] = sidecar.get("model") or "manual"
            errors, warnings, _context = validate_sidecar_for_source(doc, sidecar, draft_source(self.state, doc))
            if errors:
                return self.error_json("Reading aids failed validation.", 409, errors=errors, warnings=warnings)
            result = write_sidecar_with_backup(self.state, doc, sidecar)
            return self.send_json({"ok": True, "sidecar": sidecar, "write": result, "warnings": warnings})
        if method == "POST" and tail == ["approve"]:
            sidecar = load_sidecar(self.state, doc)
            if not sidecar:
                return self.error_json("No reading-aid sidecar exists.", 404)
            if draft_payload(self.state, doc) and draft_source(self.state, doc) != doc.source:
                return self.error_json("Republish the essay revision locally before approving reading aids for it.", 409)
            post = post_for_doc(doc)
            sidecar["essayHash"] = narrative_sync.essay_hash_for_post(post)
            sidecar["reviewStatus"] = "approved"
            sidecar["approvedAt"] = utc_now()
            errors, warnings, _context = validate_sidecar_for_source(doc, sidecar)
            if errors:
                return self.error_json("Reading aids are not ready for approval.", 409, errors=errors, warnings=warnings)
            result = write_sidecar_with_backup(self.state, doc, sidecar)
            return self.send_json({"ok": True, "sidecar": sidecar, "write": result, "warnings": warnings})
        if method == "POST" and tail == ["regenerate"]:
            if not os.environ.get("OPENAI_API_KEY"):
                return self.error_json("OPENAI_API_KEY is not set. Manual reading-aid editing remains available.", 424)
            try:
                from tools import generate_reading_aids
                posts = narrative_sync.load_posts()
                post = next(item for item in posts if narrative_sync.essay_slug_from_post(item) == doc.slug)
                sidecar, _changed = generate_reading_aids.generate_sidecar(
                    post,
                    payload.get("model") or generate_reading_aids.DEFAULT_MODEL,
                    force=True,
                )
                return self.send_json({"ok": True, "sidecar": sidecar})
            except StopIteration:
                return self.error_json("Essay not found for reading-aid regeneration.", 404)
        return self.error_json("Unknown reading-aids endpoint.", 404)


class PublisherHTTPServer(ThreadingHTTPServer):
    def __init__(self, server_address, handler_class, state: PublisherState):
        super().__init__(server_address, handler_class)
        self.state = state


def port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def choose_port(start: int) -> int:
    for port in range(start, start + 50):
        if port_available(port):
            return port
    raise SystemExit(f"No available local port from {start} to {start + 49}.")


def main():
    parser = argparse.ArgumentParser(description="Run the local OTW Publisher command center server.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--private-repo",
        default=None,
        help="Local-only private writing archive repo. Defaults to OTW_PRIVATE_WRITING_REPO or a sibling otw-private-writing repo.",
    )
    args = parser.parse_args()

    os.chdir(ROOT)
    port = choose_port(args.port)
    state = PublisherState(port, private_repo=private_repo_from_value(args.private_repo))
    server = PublisherHTTPServer(("127.0.0.1", port), PublisherHandler, state)
    print(f"OTW Publisher server running at http://127.0.0.1:{port}/publisher.html")
    print(f"Private archive repo: {state.private_repo}")
    print("Bound to 127.0.0.1 only. Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping publisher server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
