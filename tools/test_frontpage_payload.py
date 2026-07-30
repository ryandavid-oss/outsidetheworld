#!/usr/bin/env python3
"""Contract tests for the compact OTW homepage payload."""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import build_frontpage_payload as builder  # noqa: E402
from tools import audit_public_site  # noqa: E402


def selection_keys(manifest: dict, sources: dict) -> list[str]:
    return [
        builder.content_key(item)
        for item in builder.selected_frontpage_items(manifest, sources)
    ]


def complete_sources() -> tuple[dict, dict]:
    manifest = json.loads((ROOT / "frontpage_manifest.json").read_text(encoding="utf-8"))
    narratives = builder.parse_js_array(ROOT / "narrative_data.js")
    image_manifest = json.loads((ROOT / "image_manifest.json").read_text(encoding="utf-8"))
    poems = builder.parse_js_array(ROOT / "new_poetry_data.js")
    fragments = builder.parse_js_array(ROOT / "fragments_data.js")
    sources = {
        "essays": [builder.normalize_essay(item) for item in narratives],
        "images": [builder.normalize_iotd(item) for item in image_manifest if item.get("date") and item.get("image")],
        "drift": [builder.normalize_drift(item) for item in poems],
        "fragments": [
            builder.normalize_fragment(item)
            for item in fragments
            if builder.founder_fragment(item)
            and (builder.clean_text(builder.fragment_text(item)) or builder.fragment_link_preview(item))
            and str(item.get("author") or "") != "OTW_Bot"
            and str(item.get("author_id") or "") != "otw_bot"
            and "worker test fragment" not in builder.clean_text(builder.fragment_text(item)).lower()
        ],
    }
    for collection in sources.values():
        collection.sort(key=builder.sort_stamp, reverse=True)
    return manifest, sources


def run_tests() -> None:
    output = json.loads(builder.OUTPUT_PATH.read_text(encoding="utf-8"))
    generated = builder.build_payload()
    assert output == generated, "frontpage_payload.json is stale; run tools/build_frontpage_payload.py"
    assert output["schema"] == "otw.frontpage.payload"
    assert output["version"] == 1

    core = {
        "manifest": output["manifest"],
        "sources": output["sources"],
        "responsiveMedia": output["responsiveMedia"],
    }
    expected_hash = hashlib.sha256(
        json.dumps(core, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert output["contentHash"] == expected_hash

    manifest, full_sources = complete_sources()
    assert selection_keys(manifest, full_sources) == selection_keys(output["manifest"], output["sources"]), (
        "compact payload does not reproduce the full-source homepage selection"
    )
    for source_name, items in output["sources"].items():
        assert items, f"compact payload unexpectedly has no {source_name} records"
        for item in items:
            assert "body" not in item
            assert "publisher" not in item
            assert "sourceData" not in item

    delayed_essay = next(
        item
        for item in output["sources"]["essays"]
        if item["url"] == "archive/2026-07-29-a-whole-lot-of-nothing.html"
    )
    assert delayed_essay["status"] == {
        "kind": "delayed",
        "label": "DELAYED — STILL COOKING",
    }

    selected = builder.selected_frontpage_items(output["manifest"], output["sources"])
    selected_candidates = {
        candidate
        for item in selected
        for candidate in item.get("imageCandidates", [])
        if candidate
    }
    full_media = json.loads((ROOT / "responsive_media.json").read_text(encoding="utf-8"))["sources"]
    for candidate in selected_candidates:
        if candidate in full_media:
            assert candidate in output["responsiveMedia"], f"missing responsive media for {candidate}"

    audited_images = audit_public_site.data_image_references([Path("frontpage_payload.json")])
    assert not any(reference.value.startswith("iotd:") for reference in audited_images), (
        "homepage content keys must not be audited as external image URLs"
    )

    compressed_size = len(gzip.compress(builder.OUTPUT_PATH.read_bytes(), compresslevel=9))
    assert compressed_size < 20_000, f"compact payload grew to {compressed_size:,} compressed bytes"

    print(
        "OK: compact homepage payload is current, deterministic, selection-equivalent, "
        f"and {compressed_size:,} bytes compressed."
    )


if __name__ == "__main__":
    run_tests()
