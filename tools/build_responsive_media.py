#!/usr/bin/env python3
"""Build and optionally upload responsive image variants used by OTW.

The source data remains authoritative. This script creates a small lookup
manifest for the browser and immutable WebP/JPEG derivatives in R2.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageOps, UnidentifiedImageError


ROOT = Path(__file__).resolve().parents[1]
STAGING_ROOT = ROOT / ".publisher_preview" / "responsive-media"
CACHE_ROOT = STAGING_ROOT / "sources"
VARIANT_ROOT = STAGING_ROOT / "variants"
OUTPUT_PATH = ROOT / "responsive_media.json"
MEDIA_ORIGIN = "https://otw-media.ryandavid.workers.dev"
LEGACY_R2_HOST = "pub-fd35040d2a3b40af985b8aa67b98eaa8.r2.dev"
WIDTHS = (480, 800, 1200, 1600, 2400)
WRANGLER_PATH = Path(
    "/Users/rylee/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm"
)
NODE_BIN = Path(
    "/Users/rylee/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
)


def parse_js_array(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"=\s*(\[.*\])\s*;\s*$", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Could not find the data array in {path.name}")
    value = json.loads(match.group(1))
    if not isinstance(value, list):
        raise ValueError(f"Expected an array in {path.name}")
    return value


def markdown_images(markdown: str) -> Iterable[str]:
    pattern = re.compile(r"!\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))")
    for match in pattern.finditer(markdown or ""):
        yield match.group(1) or match.group(2)


def collect_sources() -> list[str]:
    sources: list[str] = []

    image_manifest = json.loads((ROOT / "image_manifest.json").read_text(encoding="utf-8"))
    sources.extend(entry.get("image", "") for entry in image_manifest)

    poems = parse_js_array(ROOT / "new_poetry_data.js")
    sources.extend(entry.get("image", "") for entry in poems)

    narratives = parse_js_array(ROOT / "narrative_data.js")
    for entry in narratives:
        sources.extend(markdown_images(entry.get("body", "")))
        source_data = entry.get("sourceData") or {}
        for image in source_data.get("images") or []:
            sources.append(image.get("url", ""))

    fragments = parse_js_array(ROOT / "fragments_data.js")
    sources.extend(entry.get("image", "") for entry in fragments)

    return sorted({str(source).strip() for source in sources if str(source).strip()})


def r2_key_for(source: str) -> str | None:
    parsed = urllib.parse.urlparse(source)
    if parsed.netloc == LEGACY_R2_HOST:
        return urllib.parse.unquote(parsed.path.lstrip("/"))
    if parsed.netloc == urllib.parse.urlparse(MEDIA_ORIGIN).netloc and parsed.path.startswith("/o/"):
        return urllib.parse.unquote(parsed.path.removeprefix("/o/"))
    return None


def original_url_for(source: str) -> str:
    key = r2_key_for(source)
    if key:
        return f"{MEDIA_ORIGIN}/o/{urllib.parse.quote(key, safe='/')}"
    return source


def source_bytes(source: str) -> bytes:
    parsed = urllib.parse.urlparse(source)
    if parsed.scheme in {"http", "https"}:
        key = r2_key_for(source)
        fetch_url = (
            f"{MEDIA_ORIGIN}/o/{urllib.parse.quote(key, safe='/')}"
            if key
            else source
        )
        cache_key = hashlib.sha256(fetch_url.encode("utf-8")).hexdigest()
        cache_path = CACHE_ROOT / cache_key
        if cache_path.exists():
            return cache_path.read_bytes()
        request = urllib.request.Request(fetch_url, headers={"User-Agent": "OTW responsive-media builder/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                data = response.read()
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"{error.code} while fetching {fetch_url}") from error
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(data)
        return data

    local_path = ROOT / urllib.parse.unquote(parsed.path or source).lstrip("/")
    if not local_path.is_file():
        raise FileNotFoundError(f"Missing local image: {source}")
    return local_path.read_bytes()


def normalized_image(data: bytes) -> Image.Image:
    try:
        image = Image.open(io.BytesIO(data))
        image.seek(0)
        image.load()
    except UnidentifiedImageError as error:
        raise ValueError("unsupported image data") from error

    image = ImageOps.exif_transpose(image)
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, "white")
        background.alpha_composite(rgba)
        return background.convert("RGB")
    return image.convert("RGB")


def target_widths(source_width: int) -> list[int]:
    widths = [width for width in WIDTHS if width < source_width]
    if source_width <= WIDTHS[-1]:
        widths.append(source_width)
    return sorted(set(widths))


def save_variant(image: Image.Image, width: int, path: Path, image_format: str) -> None:
    height = max(1, round(image.height * width / image.width))
    resized = image if width == image.width else image.resize((width, height), Image.Resampling.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    if image_format == "webp":
        resized.save(path, format="WEBP", quality=78, method=6)
    elif image_format == "jpg":
        resized.save(path, format="JPEG", quality=82, optimize=True, progressive=True, subsampling="4:2:0")
    else:
        raise ValueError(f"Unsupported output format: {image_format}")


def build_source(source: str) -> tuple[str, dict[str, Any] | None, list[tuple[Path, str, str]], str | None]:
    if Path(urllib.parse.urlparse(source).path).suffix.lower() == ".gif":
        return source, None, [], "animated GIF retained as original"

    try:
        data = source_bytes(source)
        fingerprint = hashlib.sha256(data).hexdigest()[:20]
        image = normalized_image(data)
        widths = target_widths(image.width)
        uploads: list[tuple[Path, str, str]] = []

        for width in widths:
            for extension, content_type in (("webp", "image/webp"), ("jpg", "image/jpeg")):
                relative = Path("_variants") / fingerprint / f"{width}.{extension}"
                destination = VARIANT_ROOT / fingerprint / f"{width}.{extension}"
                if not destination.exists():
                    save_variant(image, width, destination, extension)
                uploads.append((destination, relative.as_posix(), content_type))

        record = {
            "fingerprint": fingerprint,
            "width": image.width,
            "height": image.height,
            "original": original_url_for(source),
            "variants": [
                {
                    "width": width,
                    "url": f"{MEDIA_ORIGIN}/v/{fingerprint}/{width}",
                }
                for width in widths
            ],
        }
        return source, record, uploads, None
    except (FileNotFoundError, RuntimeError, ValueError, OSError) as error:
        return source, None, [], str(error)


def wrangler_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["PATH"] = f"{NODE_BIN}:{WRANGLER_PATH.parent}:{environment.get('PATH', '')}"
    return environment


def upload_variant(upload: tuple[Path, str, str]) -> tuple[str, bool, str]:
    local_path, object_key, content_type = upload
    command = [
        str(WRANGLER_PATH),
        "dlx",
        "wrangler@latest",
        "r2",
        "object",
        "put",
        f"otw-iotd/{object_key}",
        "--file",
        str(local_path),
        "--content-type",
        content_type,
        "--cache-control",
        "public,max-age=31536000,immutable",
        "--remote",
        "--force",
    ]
    result = subprocess.run(
        command,
        cwd=ROOT,
        env=wrangler_environment(),
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = (result.stdout + result.stderr).strip()
    return object_key, result.returncode == 0, output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upload", action="store_true", help="Upload generated variants to the otw-iotd R2 bucket")
    parser.add_argument("--workers", type=int, default=6, help="Concurrent generation/upload workers")
    parser.add_argument("--limit", type=int, default=0, help="Process only the first N sources (for diagnostics)")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Process one exact source URL and merge it into the existing manifest; repeat as needed",
    )
    args = parser.parse_args()

    sources = sorted({str(source).strip() for source in args.source if str(source).strip()}) or collect_sources()
    if args.limit > 0:
        sources = sources[: args.limit]

    records: dict[str, dict[str, Any]] = {}
    if args.source and OUTPUT_PATH.exists():
        existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        existing_sources = existing.get("sources") if isinstance(existing, dict) else None
        if isinstance(existing_sources, dict):
            records.update(existing_sources)
    unique_uploads: dict[str, tuple[Path, str, str]] = {}
    skipped: list[tuple[str, str]] = []

    print(f"Building responsive media for {len(sources)} source images…", flush=True)
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = {executor.submit(build_source, source): source for source in sources}
        completed = 0
        for future in as_completed(futures):
            source, record, uploads, error = future.result()
            completed += 1
            if record:
                records[source] = record
                records.setdefault(record["original"], record)
                for upload in uploads:
                    unique_uploads.setdefault(upload[1], upload)
            else:
                skipped.append((source, error or "unknown error"))
            if completed % 10 == 0 or completed == len(sources):
                print(f"  generated {completed}/{len(sources)}", flush=True)

    payload = {
        "version": 1,
        "mediaOrigin": MEDIA_ORIGIN,
        "sources": {key: records[key] for key in sorted(records)},
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)} with {len(records)} lookup keys.")
    print(f"Prepared {len(unique_uploads)} immutable variants.")

    landing_result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build_iotd_landing.py")],
        cwd=ROOT,
        check=False,
    )
    if landing_result.returncode != 0:
        return landing_result.returncode

    frontpage_result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build_frontpage_payload.py")],
        cwd=ROOT,
        check=False,
    )
    if frontpage_result.returncode != 0:
        return frontpage_result.returncode

    if skipped:
        print("Skipped sources:")
        for source, reason in skipped:
            print(f"  - {source}: {reason}")

    failed_uploads: list[tuple[str, str]] = []
    if args.upload and unique_uploads:
        print(f"Uploading {len(unique_uploads)} variants…", flush=True)
        with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 8))) as executor:
            futures = {executor.submit(upload_variant, upload): key for key, upload in unique_uploads.items()}
            completed = 0
            for future in as_completed(futures):
                object_key, ok, output = future.result()
                completed += 1
                if not ok:
                    failed_uploads.append((object_key, output))
                if completed % 25 == 0 or completed == len(unique_uploads):
                    print(f"  uploaded {completed}/{len(unique_uploads)}", flush=True)

    if failed_uploads:
        print("Upload failures:", file=sys.stderr)
        for object_key, output in failed_uploads:
            print(f"  - {object_key}: {output[-500:]}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
