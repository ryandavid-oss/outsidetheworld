#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import os
import re
import socket
import subprocess
import sys
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
    proc = subprocess.Popen(
        [sys.executable, "tools/publisher_server.py", "--port", str(port)],
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
        before = (hashlib.sha256(source.read_bytes()).hexdigest(), hashlib.sha256(archive.read_bytes()).hexdigest())
        preview = json.loads(fetch(
            f"{base}/api/published-essays/the-crucible-of-continuous-revelation/preview",
            token,
            {"includeReadingAids": True},
            "POST",
        ))
        after = (hashlib.sha256(source.read_bytes()).hexdigest(), hashlib.sha256(archive.read_bytes()).hexdigest())
        assert preview["ok"]
        assert preview["preview"]["url"].startswith("/preview/")
        assert before == after
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

