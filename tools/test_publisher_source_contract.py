#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import publisher_source_contract as contract

ROOT = Path(__file__).resolve().parents[1]


def test_all_current_narrative_round_trips_exactly():
    paths = contract.current_narrative_paths()
    assert paths

    for path in paths:
        document = contract.parse_source(path)
        assert contract.serialize_document(document) == document.source


def test_current_narrative_contract_preserves_canonical_identity():
    for path in contract.current_narrative_paths():
        document = contract.parse_source(path)
        file_date = path.name[:10]

        assert document.slug == path.stem[11:]
        assert document.archive_path == f"archive/{path.stem}.html"
        assert document.og_path == f"Images/og/archive/{path.stem}.png"
        assert document.date
        if file_date.count("-") == 2:
            assert path.name.startswith(f"{file_date}-")


def test_current_narrative_classification_is_cautious_and_visible():
    protected = []
    editable = []
    for path in contract.current_narrative_paths():
        document = contract.parse_source(path)
        for block in document.blocks:
            if block.editable:
                editable.append((path, block))
                assert block.type in contract.EDITABLE_TYPES
            else:
                protected.append((path, block))
                assert block.type == "raw"
                assert block.protected_reason

    assert editable
    assert protected
    assert any("HTML <div>" in block.protected_reason for _path, block in protected)
    assert any("HTML <figure>" in block.protected_reason for _path, block in protected)


def test_source_contract_supports_both_current_date_line_styles():
    legacy = contract.parse_source(ROOT / "current_narrative" / "2026-02-19-it-s-a-straight-vibe.md")
    publisher = contract.parse_source(ROOT / "current_narrative" / "2026-06-05-the-crucible-of-continuous-revelation.md")

    assert legacy.date_prefix == "###"
    assert publisher.date_prefix == "Date:"
    assert legacy.date == "February 19, 2026"
    assert publisher.date == "June 7, 2026"


def test_modified_serialization_keeps_slug_path_and_date_style():
    path = ROOT / "current_narrative" / "2026-02-19-it-s-a-straight-vibe.md"
    document = contract.parse_source(path)
    patched = contract.serialize_document(
        document,
        {
            "title": document.title + " Revised",
            "date": document.date,
            "subhead": document.subhead,
            "blocks": [block.to_json() for block in document.blocks],
        },
    )

    assert patched.startswith(f"# {document.title} Revised\n### {document.date}\n")
    assert document.slug == "it-s-a-straight-vibe"
    assert document.archive_path == "archive/2026-02-19-it-s-a-straight-vibe.html"


def test_published_revision_preserves_optional_narration_metadata():
    path = ROOT / "current_narrative" / "2026-08-14-still-out-there.md"
    document = contract.parse_source(path)
    narration = document.metadata.get("audio")

    assert narration
    assert narration["src"] == "/media/narrative/2026-08-14-still-out-there/still-out-there.mp3"
    assert len(narration["chapters"]) == 6

    patched = contract.serialize_document(
        document,
        {
            "title": document.title,
            "date": document.date,
            "subhead": document.subhead + " revised",
            "blocks": [block.to_json() for block in document.blocks],
        },
    )
    reparsed = contract.document_from_source_text(path, patched)

    assert reparsed.metadata["audio"] == narration


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
            print(f"ok {name}")
