#!/usr/bin/env python3
"""Audit reference images in a design inspiration research JSON file."""

from __future__ import annotations

import argparse
import hashlib
import json
import ssl
import urllib.request
from pathlib import Path
from typing import Any

USER_AGENT = "Mozilla/5.0 (Codex design-inspiration-research image auditor)"
TIMEOUT = 12
MAX_BYTES = 10 * 1024 * 1024


def is_remote(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def looks_like_image(data: bytes, content_type: str = "") -> bool:
    content_type = content_type.split(";", 1)[0].strip().lower()
    return (
        content_type.startswith("image/")
        or data.startswith(b"\xff\xd8\xff")
        or data.startswith(b"\x89PNG\r\n\x1a\n")
        or data.startswith(b"RIFF") and b"WEBP" in data[:16]
        or data.startswith(b"GIF87a")
        or data.startswith(b"GIF89a")
    )


def fetch_remote_head(url: str) -> tuple[bool, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=context) as response:
        content_type = response.headers.get("Content-Type", "")
        sample = response.read(64)
        ok = looks_like_image(sample, content_type)
        return ok, content_type, response.geturl()


def read_image(path: Path) -> tuple[bool, str, str]:
    if not path.exists():
        return False, "missing", ""
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        return False, "too large", ""
    digest = hashlib.sha256(data).hexdigest()
    if not looks_like_image(data[:64]):
        return False, "not an image", digest
    return True, "ok", digest


def audit(data: dict[str, Any], json_path: Path, *, min_ratio: float, fail_on_duplicates: bool) -> int:
    references = data.get("references")
    if not isinstance(references, list):
        print("[error] JSON must contain a references list.")
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    seen: dict[str, str] = {}
    valid_count = 0

    for index, ref in enumerate(references, start=1):
        if not isinstance(ref, dict):
            errors.append(f"reference {index}: not an object")
            continue

        title = str(ref.get("title") or f"reference-{index}")
        image = str(ref.get("image") or "").strip()
        if not image:
            warnings.append(f"{title}: missing image")
            continue

        if is_remote(image):
            try:
                ok, content_type, final_url = fetch_remote_head(image)
                if not ok:
                    errors.append(f"{title}: remote image is not image content ({content_type or 'unknown'})")
                    continue
                valid_count += 1
                warnings.append(f"{title}: remote image is reachable but not local ({final_url})")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{title}: remote image failed ({exc})")
            continue

        local_path = (json_path.parent / image).resolve()
        ok, message, digest = read_image(local_path)
        if not ok:
            errors.append(f"{title}: {message} at {local_path}")
            continue

        valid_count += 1
        if digest in seen:
            duplicate = f"{title}: duplicate image also used by {seen[digest]}"
            if fail_on_duplicates:
                errors.append(duplicate)
            else:
                warnings.append(duplicate)
        else:
            seen[digest] = title

    ratio = valid_count / len(references) if references else 0
    if ratio < min_ratio:
        errors.append(f"valid image ratio {ratio:.0%} is below required {min_ratio:.0%}")

    for warning in warnings:
        print(f"[warn] {warning}")
    if errors:
        for error in errors:
            print(f"[error] {error}")
        print(f"Image audit failed: {valid_count}/{len(references)} valid images.")
        return 1

    print(f"Image audit passed: {valid_count}/{len(references)} valid images, {len(seen)} unique local hashes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit reference images in a design report JSON.")
    parser.add_argument("json", type=Path, help="Research JSON to audit.")
    parser.add_argument("--min-ratio", type=float, default=0.85, help="Minimum ratio of references with valid images.")
    parser.add_argument("--fail-on-duplicates", action="store_true", help="Fail if two local images are byte-identical.")
    args = parser.parse_args()

    data = json.loads(args.json.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Input JSON root must be an object.")
    return audit(data, args.json, min_ratio=args.min_ratio, fail_on_duplicates=args.fail_on_duplicates)


if __name__ == "__main__":
    raise SystemExit(main())
