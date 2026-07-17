#!/usr/bin/env python3
"""Recover Hipsta images that were accidentally saved as tiny HTML wrappers."""

from __future__ import annotations

import io
import re
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HIPSTA = ROOT / "Images" / "Hipsta"
WRAPPER = re.compile(r'<img\s+src="([^"]+)"', re.I)
USER_AGENT = "Mozilla/5.0 OTW-Hipsta-Recovery/1.0"


def recover(path: Path) -> bool:
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    if not source.lstrip().lower().startswith("<html"):
        return False
    match = WRAPPER.search(source)
    if not match:
        raise ValueError(f"HTML image wrapper has no recoverable source: {path.relative_to(ROOT)}")

    request = Request(match.group(1), headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=30) as response:
        data = response.read()
        content_type = response.headers.get_content_type()
    if not content_type.startswith("image/"):
        raise ValueError(f"Recovery returned {content_type} for {path.relative_to(ROOT)}")

    with Image.open(io.BytesIO(data)) as recovered:
        recovered.verify()
        recovered_format = recovered.format

    expected = "GIF" if path.suffix.lower() == ".gif" else "JPEG"
    if recovered_format == expected:
        output = data
    else:
        with Image.open(io.BytesIO(data)) as recovered:
            converted = recovered.convert("P" if expected == "GIF" else "RGB")
            buffer = io.BytesIO()
            converted.save(buffer, format=expected, quality=95)
            output = buffer.getvalue()

    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(output)
        temporary_path = Path(temporary.name)
    temporary_path.replace(path)
    return True


def main() -> None:
    recovered = 0
    for path in sorted(HIPSTA.iterdir()):
        if path.suffix.lower() not in {".gif", ".jpeg", ".jpg", ".png"}:
            continue
        if recover(path):
            recovered += 1
            print(f"RECOVERED {path.relative_to(ROOT)}")
    print(f"RECOVERY_COMPLETE: {recovered} images")


if __name__ == "__main__":
    main()
