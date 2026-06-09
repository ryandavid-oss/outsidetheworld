#!/usr/bin/env python3
import argparse
import copy
import http.server
import json
import os
import socket
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import narrative_sync

DEFAULT_MODEL = os.environ.get("OTW_READING_AID_MODEL", "gpt-5.4-mini")
MAX_PROMPT_CHARS = 320_000

CONTENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["signalBrief", "readerMap", "checkpoints", "plainSignals"],
    "properties": {
        "signalBrief": {
            "type": "object",
            "additionalProperties": False,
            "required": ["text", "locked"],
            "properties": {
                "text": {"type": "string"},
                "locked": {"type": "boolean"},
            },
        },
        "readerMap": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["label", "title", "summary", "locked"],
                "properties": {
                    "label": {"type": "string"},
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "locked": {"type": "boolean"},
                },
            },
        },
        "checkpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["afterParagraphId", "label", "text", "locked"],
                "properties": {
                    "afterParagraphId": {"type": "string"},
                    "label": {"type": "string"},
                    "text": {"type": "string"},
                    "locked": {"type": "boolean"},
                },
            },
        },
        "plainSignals": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paragraphId", "label", "text", "locked"],
                "properties": {
                    "paragraphId": {"type": "string"},
                    "label": {"type": "string"},
                    "text": {"type": "string"},
                    "locked": {"type": "boolean"},
                },
            },
        },
    },
}

SYSTEM_PROMPT = """You create reviewed static reading aids for Outside The World archive essays.
Do not rewrite, simplify, replace, or summarize away the essay. Build a guided reader around it.
Use clear, generous language. Do not infantilize the reader. Do not mock or flatten metaphor.
Do not say "the author means" unless the note has been explicitly author-approved.
Prefer phrases like "This passage is pointing toward..." or "In plain terms..."
Do not introduce outside claims. Do not psychoanalyze the author. Do not moralize.
Do not overexplain or turn the notes into SparkNotes.
Keep the OTW voice: warm, precise, literary, useful, and quietly directional.
Return only structured JSON matching the supplied schema."""


def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_slug(value):
    raw = str(value or "").strip()
    stem = Path(raw).stem
    return narrative_sync.essay_slug_from_stem(stem)


def find_post(posts, slug=None, latest=False):
    if latest:
        if not posts:
            raise SystemExit("No essays found in current_narrative/.")
        return posts[0]

    wanted = normalize_slug(slug)
    matches = [
        post for post in posts
        if normalize_slug(post.get("file")) == wanted
        or Path(post.get("file") or "").stem == str(slug).strip()
    ]
    if not matches:
        raise SystemExit(f"No essay found for slug: {slug}")
    if len(matches) > 1:
        files = ", ".join(post.get("file") or "unknown" for post in matches)
        raise SystemExit(f"Slug matched multiple essays: {files}")
    return matches[0]


def sidecar_path(post):
    return ROOT / narrative_sync.reading_aid_path_for_post(post)


def paragraph_context(post):
    deck = narrative_sync.publisher_subhead(post)
    body_html = narrative_sync.render_reader_body_html(post, deck)
    paragraphs = narrative_sync.extract_reader_paragraphs(body_html)
    if not paragraphs:
        raise SystemExit(f"No body paragraphs found for {post.get('file')}.")
    return paragraphs


def build_user_prompt(post, slug, essay_hash, paragraphs):
    plain_signal_candidates = [
        {"id": item["id"], "text": item["text"]}
        for item in paragraphs
        if item.get("word_count", 0) >= 45
    ]
    payload = {
        "essay": {
            "title": post.get("title"),
            "date": post.get("date"),
            "slug": slug,
            "essayHash": essay_hash,
            "deck": narrative_sync.publisher_subhead(post),
        },
        "paragraphs": [{"id": item["id"], "text": item["text"]} for item in paragraphs],
        "plainSignalCandidateParagraphs": plain_signal_candidates,
        "requirements": {
            "signalBrief": "Article Summary: 1 paragraph, roughly 90-160 words, plain-language orientation, not a replacement for the essay.",
            "readerMap": "4-8 entries with short labels and summaries describing the route through the essay.",
            "checkpoints": "3-6 total, placed after major turns or long sections, each roughly 40-90 words.",
            "plainSignals": "Clarify notes: 5-12 total, only for the densest or most metaphorically loaded candidate paragraphs, each roughly 35-90 words.",
            "labels": {
                "plainSignals": "Clarify",
                "checkpoints": "Where We Are"
            },
            "locked": "Set locked to false for every generated object."
        }
    }
    prompt = json.dumps(payload, ensure_ascii=False, indent=2)
    if len(prompt) > MAX_PROMPT_CHARS:
        raise SystemExit(
            f"Essay prompt is {len(prompt):,} characters, above the current {MAX_PROMPT_CHARS:,} character v1 limit. "
            "This needs a chunked generation pass before sending safely."
        )
    return prompt


def response_payload(model, user_prompt):
    return {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": SYSTEM_PROMPT}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": user_prompt}],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "otw_reading_aid_content",
                "description": "Static reviewed reading aids for one archive essay.",
                "strict": True,
                "schema": CONTENT_SCHEMA,
            }
        },
        "max_output_tokens": 9000,
    }


def extract_output_text(payload):
    if isinstance(payload, dict) and payload.get("output_text"):
        return payload["output_text"]
    for item in payload.get("output", []) if isinstance(payload, dict) else []:
        for content in item.get("content", []) if isinstance(item, dict) else []:
            if isinstance(content, dict) and content.get("text"):
                return content["text"]
    return ""


def call_openai_http(api_key, payload):
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"OpenAI API request failed ({exc.code}): {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"OpenAI API request failed: {exc.reason}") from exc

    text = extract_output_text(data)
    if not text:
        raise SystemExit("OpenAI API response did not include structured output text.")
    return json.loads(text)


def call_openai(api_key, payload):
    try:
        from openai import OpenAI
    except ImportError:
        return call_openai_http(api_key, payload)

    client = OpenAI(api_key=api_key)
    response = client.responses.create(**payload)
    text = getattr(response, "output_text", None)
    if not text and hasattr(response, "model_dump"):
        text = extract_output_text(response.model_dump())
    if not text:
        raise SystemExit("OpenAI SDK response did not include structured output text.")
    return json.loads(text)


def load_existing(path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Existing sidecar is invalid JSON: {path} ({exc})") from exc


def copy_locked_fields(existing, sidecar):
    if not existing:
        return sidecar, []

    merged = copy.deepcopy(sidecar)
    warnings = []

    existing_brief = existing.get("signalBrief")
    if isinstance(existing_brief, dict) and existing_brief.get("locked") is True:
        merged["signalBrief"] = copy.deepcopy(existing_brief)

    list_keys = {
        "readerMap": "label",
        "checkpoints": "afterParagraphId",
        "plainSignals": "paragraphId",
    }
    for list_name, key_name in list_keys.items():
        locked_items = [
            item for item in existing.get(list_name, [])
            if isinstance(item, dict) and item.get("locked") is True and item.get(key_name)
        ]
        locked_by_key = {item.get(key_name): item for item in locked_items}
        used = set()
        merged_items = []
        for item in merged.get(list_name, []):
            key = item.get(key_name) if isinstance(item, dict) else None
            if key in locked_by_key:
                merged_items.append(copy.deepcopy(locked_by_key[key]))
                used.add(key)
            else:
                merged_items.append(item)
        for item in locked_items:
            key = item.get(key_name)
            if key not in used:
                merged_items.append(copy.deepcopy(item))
                warnings.append(f"Preserved locked {list_name} item for {key}, even though regeneration did not select it.")
        merged[list_name] = merged_items

    return merged, warnings


def write_sidecar(path, sidecar):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        backup = path.with_name(f"{path.name}.bak-{stamp}")
        backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup: {backup}")
    temp_path = path.with_suffix(path.suffix + ".tmp")
    temp_path.write_text(json.dumps(sidecar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp_path.replace(path)


def validate_sidecar(post, aids):
    slug = narrative_sync.essay_slug_from_post(post)
    paragraphs = paragraph_context(post)
    paragraph_ids = {item["id"] for item in paragraphs}
    essay_hash = narrative_sync.essay_hash_for_post(post)
    return narrative_sync.validate_reading_aids(aids, slug, paragraph_ids, essay_hash)


def generate_sidecar(post, model, force=False):
    slug = narrative_sync.essay_slug_from_post(post)
    path = sidecar_path(post)
    existing = load_existing(path)

    if existing and not force:
        errors, warnings = validate_sidecar(post, existing)
        for warning in warnings:
            print(f"WARNING: {warning}")
        if errors:
            print("Existing sidecar has validation errors:")
            for error in errors:
                print(f"- {error}")
        print(f"Existing sidecar preserved without regeneration: {path}")
        print("Use --force to regenerate unlocked fields.")
        return existing, False

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is not set, so I cannot generate reading aids. "
            "Export it locally, then rerun the command."
        )

    paragraphs = paragraph_context(post)
    essay_hash = narrative_sync.essay_hash_for_post(post)
    prompt = build_user_prompt(post, slug, essay_hash, paragraphs)
    print(f"Generating reading aids for {post.get('title')} with {model}...")
    content = call_openai(api_key, response_payload(model, prompt))

    sidecar = {
        "slug": slug,
        "essayHash": essay_hash,
        "reviewStatus": "draft",
        "generatedAt": iso_now(),
        "model": model,
        "signalBrief": content.get("signalBrief") or {"text": "", "locked": False},
        "readerMap": content.get("readerMap") or [],
        "checkpoints": content.get("checkpoints") or [],
        "plainSignals": content.get("plainSignals") or [],
    }
    sidecar, locked_warnings = copy_locked_fields(existing, sidecar)
    for warning in locked_warnings:
        print(f"WARNING: {warning}")

    errors, warnings = validate_sidecar(post, sidecar)
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        print("Generated sidecar failed validation:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    write_sidecar(path, sidecar)
    print(f"Wrote draft sidecar: {path}")
    return sidecar, True


def approve_sidecar(post):
    path = sidecar_path(post)
    sidecar = load_existing(path)
    if not sidecar:
        raise SystemExit(f"No sidecar exists to approve: {path}")

    errors, warnings = validate_sidecar(post, sidecar)
    essay_hash = narrative_sync.essay_hash_for_post(post)
    if sidecar.get("essayHash") != essay_hash:
        errors.append("Cannot approve: essayHash is stale for the current essay source.")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        print("Sidecar is not ready for approval:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    sidecar["reviewStatus"] = "approved"
    sidecar["approvedAt"] = iso_now()
    write_sidecar(path, sidecar)
    print(f"Approved sidecar: {path}")
    return sidecar


def sync_archive(preview=False):
    narrative_sync.sync_production(include_draft_reading_aids=preview)


def preview_paths(post, served_port=None):
    stem = narrative_sync.post_stem(post.get("file") or "")
    archive_path = ROOT / narrative_sync.share_output_folder / f"{stem}.html"
    print(f"Preview file: {archive_path}")
    print(f"Preview URL: {archive_path.as_uri()}")
    if served_port:
        print(f"Local server URL: http://127.0.0.1:{served_port}/archive/{stem}.html")


def port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def choose_port(start):
    for port in range(start, start + 50):
        if port_available(port):
            return port
    raise SystemExit(f"No available port found from {start} to {start + 49}.")


def serve(root, port):
    selected_port = choose_port(port)
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(*args, directory=str(root), **kwargs)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", selected_port), handler)
    return server, selected_port


def validate_command(posts, selected_post=None):
    sidecars = []
    if selected_post:
        path = sidecar_path(selected_post)
        if not path.exists():
            raise SystemExit(f"No sidecar found: {path}")
        sidecars.append((selected_post, path))
    else:
        by_slug = {narrative_sync.essay_slug_from_post(post): post for post in posts}
        for path in sorted((ROOT / narrative_sync.reading_aids_folder).glob("*.json")):
            if path.name == "schema.json":
                continue
            post = by_slug.get(path.stem)
            if post:
                sidecars.append((post, path))
            else:
                print(f"WARNING: No essay found for sidecar {path.name}.")

    if not sidecars:
        print("No reading aid sidecars found.")
        return

    failures = 0
    for post, path in sidecars:
        sidecar = load_existing(path)
        errors, warnings = validate_sidecar(post, sidecar)
        for warning in warnings:
            print(f"WARNING: {path.name}: {warning}")
        if errors:
            failures += 1
            print(f"FAILED: {path}")
            for error in errors:
                print(f"- {error}")
        else:
            print(f"OK: {path}")
    if failures:
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate reviewed/static reading aid sidecars for archive essays.")
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--latest", action="store_true", help="Use the newest essay in current_narrative/.")
    selector.add_argument("--slug", help="Use an essay title slug, with or without the date prefix.")
    parser.add_argument("--preview", action="store_true", help="Regenerate archive HTML with draft reading aids visible.")
    parser.add_argument("--serve", action="store_true", help="Start a local static server after preview generation.")
    parser.add_argument("--port", type=int, default=8000, help="Preferred local static server port for --serve.")
    parser.add_argument("--approve", action="store_true", help="Mark an existing valid sidecar approved without regenerating content.")
    parser.add_argument("--force", action="store_true", help="Regenerate unlocked fields even when a sidecar already exists.")
    parser.add_argument("--validate", action="store_true", help="Validate sidecars without generating.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="OpenAI model to use. Defaults to OTW_READING_AID_MODEL or gpt-5.4-mini.")
    args = parser.parse_args()

    os.chdir(ROOT)
    posts = narrative_sync.load_posts()
    selected_post = find_post(posts, args.slug, args.latest) if (args.slug or args.latest) else None

    if args.validate:
        validate_command(posts, selected_post)
        return

    if not selected_post:
        raise SystemExit("Choose --latest or --slug <slug>.")

    if args.approve:
        approve_sidecar(selected_post)
    else:
        generate_sidecar(selected_post, args.model, args.force)

    server = None
    selected_port = None
    if args.preview:
        sync_archive(preview=True)
        if args.serve:
            server, selected_port = serve(ROOT, args.port)
        preview_paths(selected_post, selected_port)

    if server:
        print("Serving local preview. Press Ctrl-C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
