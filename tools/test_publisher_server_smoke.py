#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def fetch(url, token=None, payload=None, method=None):
    headers = {}
    data = None
    if token:
        headers["x-publisher-token"] = token
    if payload is not None:
        headers["content-type"] = "application/json; charset=utf-8"
        data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8")


def run_smoke():
    port = free_port()
    with tempfile.TemporaryDirectory() as temp:
        private_repo = Path(temp) / "private-writing"
        proc = subprocess.Popen(
            [sys.executable, "tools/publisher_server.py", "--port", str(port), "--private-repo", str(private_repo)],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        base = f"http://127.0.0.1:{port}"
        try:
            token = None
            for _attempt in range(60):
                try:
                    html = fetch(f"{base}/publisher.html")
                    match = re.search(r'name="otw-publisher-token" content="([^"]+)"', html)
                    if match:
                        token = match.group(1)
                        break
                except Exception:
                    time.sleep(0.1)
            assert token

            try:
                fetch(f"{base}/api/published-essays")
                raise AssertionError("API request without token should fail")
            except urllib.error.HTTPError as exc:
                assert exc.code == 401

            essays = json.loads(fetch(f"{base}/api/published-essays", token))
            assert essays["ok"]
            assert len(essays["essays"]) == 22
            assert essays["essays"][0]["slug"] == "the-crucible-of-continuous-revelation"

            source = ROOT / "current_narrative" / "2026-06-05-the-crucible-of-continuous-revelation.md"
            archive = ROOT / "archive" / "2026-06-05-the-crucible-of-continuous-revelation.html"
            narrative = ROOT / "narrative_data.js"
            before = (
                hashlib.sha256(source.read_bytes()).hexdigest(),
                hashlib.sha256(archive.read_bytes()).hexdigest(),
                hashlib.sha256(narrative.read_bytes()).hexdigest(),
            )
            preview = json.loads(fetch(
                f"{base}/api/published-essays/the-crucible-of-continuous-revelation/preview",
                token,
                {"includeReadingAids": True},
                "POST",
            ))
            after = (
                hashlib.sha256(source.read_bytes()).hexdigest(),
                hashlib.sha256(archive.read_bytes()).hexdigest(),
                hashlib.sha256(narrative.read_bytes()).hexdigest(),
            )
            assert preview["ok"]
            assert preview["preview"]["url"].startswith("/preview/")
            assert before == after

            private_payload = {
                "schema": "otw.publisher.privateArchiveRequest",
                "version": 1,
                "article": {
                    "schema": "otw.publisher.article",
                    "version": 3,
                    "title": "Smoke Private Draft",
                    "subhead": "",
                    "metadata": {"publishDate": "2026-06-18", "slug": "smoke-private-draft"},
                    "body": {"blocks": [{"type": "paragraph", "text": "Only local, only tonight."}]},
                },
                "publishPayload": {
                    "schema": "otw.publisher.publishPayload",
                    "version": 1,
                    "content": {"markdown": "# Smoke Private Draft\nDate: June 18, 2026\n\nOnly local, only tonight.\n"},
                },
            }
            private_result = json.loads(fetch(f"{base}/api/private-archive/drafts", token, private_payload, "POST"))
            assert private_result["ok"]
            assert (private_repo / private_result["path"]).exists()
            log = subprocess.check_output(["git", "log", "--oneline", "--all"], cwd=private_repo, text=True)
            assert "Archive private draft: Smoke Private Draft" in log
            assert before == (
                hashlib.sha256(source.read_bytes()).hexdigest(),
                hashlib.sha256(archive.read_bytes()).hexdigest(),
                hashlib.sha256(narrative.read_bytes()).hexdigest(),
            )
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    os.chdir(ROOT)
    run_smoke()
    print("ok publisher server smoke")
