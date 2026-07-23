#!/usr/bin/env python3
"""Validate OTW's public-intake and privacy guardrails."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_LEDGER_PATHS = {
    "frgmnts_waitlist.json",
    "professional_inquiries.json",
    "frgmnts_support_requests.json",
    "frgmnts_seat_checkins.json",
}
GA_MARKERS = {"G-YKRKPFV2MB", "googletagmanager.com/gtag/js"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def managed_html_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*.html")
        if not any(part in {".git", ".claude"} for part in path.parts)
    ]


def main() -> None:
    for path in FORBIDDEN_LEDGER_PATHS:
        require(not (ROOT / path).exists(), f"{path} must not exist in the public source tree")

    gitignore = read(".gitignore")
    for path in FORBIDDEN_LEDGER_PATHS:
        require(path in gitignore, f"{path} must remain ignored")

    for path in managed_html_files():
        source = path.read_text(encoding="utf-8")
        require(
            not any(marker in source for marker in GA_MARKERS),
            f"{path.relative_to(ROOT)} must not load retired Google Analytics",
        )

    intake_worker = read("cloudflare/otw-private-intake/src/index.js")
    require("env.INTAKE_DB.prepare" in intake_worker, "Private intake must write to D1")
    require("GITHUB_TOKEN" not in intake_worker, "Private intake must not hold GitHub credentials")
    require("api.github.com" not in intake_worker, "Private intake must not call GitHub")
    require('"access-control-allow-origin": "*"' not in intake_worker, "Private intake must restrict CORS")
    require("purgeExpiredRecords" in intake_worker, "Private intake must delete expired records")

    intake_config = read("cloudflare/otw-private-intake/wrangler.toml")
    require("[triggers]" in intake_config, "Private intake must schedule its retention purge")
    require("crons =" in intake_config, "Private intake must define a retention cron")

    publishing_worker = read("cloudflare/otw-fragments-publish/src/index.js")
    require(
        "RETIRED_PUBLIC_INTAKE_PATHS.has(url.pathname)" in publishing_worker,
        "Privileged publishing worker must retire its legacy public intake routes",
    )

    frgmnts = read("frgmnts.html")
    professional = read("professional.html")
    private_origin = "https://otw-private-intake.ryandavid.workers.dev/"
    require(private_origin in frgmnts, "Waitlist must use the private intake Worker")
    require(private_origin in professional, "Professional form must use the private intake Worker")
    require("privacy.html" in frgmnts, "Waitlist must link to the privacy notice")
    require("privacy.html" in professional, "Professional form must link to the privacy notice")

    privacy = read("privacy.html")
    require("Effective July 23, 2026" in privacy, "Privacy notice must identify its effective date")
    require("private Cloudflare D1 database" in privacy, "Privacy notice must describe private intake storage")
    require("Do Not Track and Global Privacy Control" in privacy, "Privacy notice must address browser signals")

    print("privacy contract checks passed")


if __name__ == "__main__":
    main()
