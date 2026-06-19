#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import publisher_server


def sample_payload(title="Private Weather", slug="private-weather"):
    return {
        "schema": publisher_server.PRIVATE_ARCHIVE_REQUEST_SCHEMA,
        "version": 1,
        "article": {
            "schema": "otw.publisher.article",
            "version": 3,
            "title": title,
            "subhead": "Notes that may or may not become public.",
            "metadata": {
                "publishDate": "2026-06-18",
                "articleDate": "2026-06-18",
                "slug": slug,
                "surface": "Outside The World Article",
            },
            "body": {
                "blocks": [
                    {
                        "id": "paragraph_private",
                        "type": "paragraph",
                        "text": "A private paragraph with a future-facing ember in it.",
                        "html": "A private paragraph with a future-facing ember in it.",
                    }
                ]
            },
        },
        "publishPayload": {
            "schema": "otw.publisher.publishPayload",
            "version": 1,
            "content": {
                "format": "markdown",
                "markdown": (
                    "# Private Weather\n"
                    "Date: June 18, 2026\n\n"
                    "_Notes that may or may not become public._\n\n"
                    "A private paragraph with a future-facing ember in it.\n"
                ),
            },
        },
    }


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr or result.stdout
    return result.stdout.strip()


def expect_raises(expected, fn):
    try:
        fn()
    except expected:
        return
    raise AssertionError(f"Expected {expected.__name__}")


def public_hashes():
    paths = [
        ROOT / "current_narrative" / "2026-06-05-the-crucible-of-continuous-revelation.md",
        ROOT / "archive" / "2026-06-05-the-crucible-of-continuous-revelation.html",
        ROOT / "narrative_data.js",
        ROOT / "atom.xml",
        ROOT / "reading_aids" / "the-crucible-of-continuous-revelation.json",
    ]
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}


def test_private_archive_initializes_writes_and_commits():
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "private-writing"
        result = publisher_server.archive_private_draft(repo, sample_payload())

        markdown = repo / result["path"]
        article = repo / result["articlePath"]
        manifest = json.loads((repo / "manifest.json").read_text(encoding="utf-8"))

        assert result["ok"]
        assert markdown.exists()
        assert article.exists()
        assert "# Private Weather" in markdown.read_text(encoding="utf-8")
        assert manifest["schema"] == publisher_server.PRIVATE_ARCHIVE_SCHEMA
        assert manifest["drafts"][-1]["commit"] == result["commit"]
        assert "Archive private draft: Private Weather" in git(repo, "log", "--oneline", "--all")
        assert git(repo, "status", "--porcelain") == ""


def test_private_archive_handles_filename_collisions():
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "private-writing"
        first = publisher_server.archive_private_draft(repo, sample_payload())
        second = publisher_server.archive_private_draft(repo, sample_payload())

        assert first["path"].endswith("2026-06-18-private-weather.md")
        assert second["path"].endswith("2026-06-18-private-weather-2.md")


def test_private_archive_blocks_remote_repos_empty_drafts_and_path_traversal():
    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "private-writing"
        repo.mkdir()
        git(repo, "init")
        git(repo, "remote", "add", "origin", "https://example.test/private.git")
        expect_raises(ValueError, lambda: publisher_server.archive_private_draft(repo, sample_payload()))

    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "private-writing"
        empty = sample_payload(title="", slug="")
        empty["article"]["title"] = ""
        empty["article"]["subhead"] = ""
        empty["article"]["metadata"]["slug"] = ""
        empty["article"]["body"]["blocks"] = []
        empty["publishPayload"]["content"]["markdown"] = ""
        expect_raises(ValueError, lambda: publisher_server.archive_private_draft(repo, empty))

    with tempfile.TemporaryDirectory() as temp:
        repo = Path(temp) / "private-writing"
        traversal = sample_payload()
        traversal["article"]["metadata"]["slug"] = "../escape"
        expect_raises(ValueError, lambda: publisher_server.archive_private_draft(repo, traversal))


def test_private_archive_does_not_touch_public_outputs():
    before = public_hashes()
    with tempfile.TemporaryDirectory() as temp:
        publisher_server.archive_private_draft(Path(temp) / "private-writing", sample_payload())
    assert public_hashes() == before


if __name__ == "__main__":
    for name, value in sorted(globals().items()):
        if name.startswith("test_") and callable(value):
            value()
            print(f"ok {name}")
