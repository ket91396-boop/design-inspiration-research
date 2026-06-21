#!/usr/bin/env python3
"""Prepare local reference images for a design inspiration report.

This script keeps report images tied to their own reference pages. It will:

- read `references[*].url` and `references[*].image` from a research JSON file;
- fetch the reference page and extract common `og:image` / `twitter:image` /
  image URLs from that page;
- download a verified image into a local assets directory;
- rewrite `references[*].image` to a local relative path;
- fail in strict mode when images are missing, unreachable, or duplicated.

It intentionally does not search the web for replacement images. If a reference
does not expose a usable image, find a better visual reference instead of using
an unrelated image from another site.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

USER_AGENT = "Mozilla/5.0 (Codex design-inspiration-research image preparer)"
MAX_BYTES = 8 * 1024 * 1024
DEFAULT_TIMEOUT = 8
DEFAULT_MAX_CANDIDATES = 4
DEFAULT_SCREENSHOT_TIMEOUT = 18
IMAGE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def fetch_bytes(url: str, max_bytes: int = MAX_BYTES, timeout: int = DEFAULT_TIMEOUT) -> tuple[bytes, str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
        final_url = response.geturl()
        content_type = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = response.read(64 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise ValueError(f"image exceeds {max_bytes} bytes")
            chunks.append(chunk)
        return b"".join(chunks), content_type, final_url


def fetch_text(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    data, _content_type, _final_url = fetch_bytes(url, max_bytes=3 * 1024 * 1024, timeout=timeout)
    return data.decode("utf-8", errors="ignore")


def looks_like_image(data: bytes, content_type: str) -> bool:
    if content_type in IMAGE_EXTENSIONS:
        return True
    return (
        data.startswith(b"\xff\xd8\xff")
        or data.startswith(b"\x89PNG\r\n\x1a\n")
        or data.startswith(b"RIFF") and b"WEBP" in data[:16]
        or data.startswith(b"GIF87a")
        or data.startswith(b"GIF89a")
    )


def infer_ext(url: str, content_type: str, data: bytes) -> str:
    if content_type in IMAGE_EXTENSIONS:
        return IMAGE_EXTENSIONS[content_type]
    path = urllib.parse.urlparse(url).path.lower()
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        if path.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    if data.startswith(b"\x89PNG"):
        return ".png"
    if data.startswith(b"RIFF") and b"WEBP" in data[:16]:
        return ".webp"
    if data.startswith(b"GIF"):
        return ".gif"
    return ".jpg"


def absolutize(base_url: str, candidate: str) -> str:
    candidate = html.unescape(candidate).strip()
    if not candidate:
        return ""
    if candidate.startswith("//"):
        return "https:" + candidate
    return urllib.parse.urljoin(base_url, candidate)


def extract_image_candidates(page_url: str, page_html: str) -> list[str]:
    candidates: list[str] = []
    patterns = [
        r'<meta[^>]+(?:property|name)=["\'](?:og:image|og:image:secure_url|twitter:image|twitter:image:src)["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|og:image:secure_url|twitter:image|twitter:image:src)["\']',
        r'<link[^>]+rel=["\']image_src["\'][^>]+href=["\']([^"\']+)',
        r'<img[^>]+(?:src|data-src|data-original)=["\']([^"\']+)["\']',
        r'https?://[^"\'\s<>]+?\.(?:jpg|jpeg|png|webp|gif)(?:\?[^"\'\s<>]*)?',
        r'//[^"\'\s<>]+?\.(?:jpg|jpeg|png|webp|gif)(?:\?[^"\'\s<>]*)?',
    ]
    for pattern in patterns:
        for match in re.findall(pattern, page_html, flags=re.IGNORECASE | re.DOTALL):
            url = absolutize(page_url, match)
            if url and not url.startswith("data:") and url not in candidates:
                candidates.append(url)
    return candidates


def slugify(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return (cleaned[:60].strip("-") or fallback)


def same_candidate(provided: str, candidate: str) -> bool:
    left = html.unescape(provided).strip()
    right = html.unescape(candidate).strip()
    return left == right or urllib.parse.unquote(left) == urllib.parse.unquote(right)


def provided_is_on_page(provided: str, page_html: str, candidates: list[str]) -> bool:
    if not provided:
        return False
    if provided in page_html or html.escape(provided) in page_html:
        return True
    return any(same_candidate(provided, candidate) for candidate in candidates)


def is_remote_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://") or value.startswith("//")


def local_image_ok(path: Path) -> tuple[bool, str, str]:
    if not path.exists():
        return False, "local image file missing", ""
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if not looks_like_image(data[:64], ""):
        return False, "local file is not an image", digest
    return True, "ok", digest


def make_relative(target: Path, base_dir: Path) -> str:
    try:
        return target.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return target.resolve().as_posix()


def screenshot_page(page_url: str, target: Path, timeout: int = DEFAULT_SCREENSHOT_TIMEOUT) -> tuple[bool, str]:
    script = r"""
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const [url, out, timeoutMsValue] = process.argv.slice(2);
  const timeoutMs = Number(timeoutMsValue || 18000);
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1365, height: 1000 }, deviceScaleFactor: 1 });
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
    await page.waitForTimeout(1200);
    await page.screenshot({ path: out, fullPage: false });
    const stat = fs.statSync(out);
    if (!stat.size) throw new Error('empty screenshot');
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
"""
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["node", "-e", script, page_url, str(target), str(timeout * 1000)],
            capture_output=True,
            text=True,
            timeout=timeout + 8,
        )
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)
    if result.returncode != 0:
        return False, (result.stderr or result.stdout or "screenshot failed").strip()
    if not target.exists() or target.stat().st_size == 0:
        return False, "screenshot file missing or empty"
    return True, "ok"


def prepare_images(
    input_path: Path,
    output_path: Path,
    assets_dir: Path,
    *,
    strict: bool,
    trust_provided: bool,
    screenshot_missing: bool,
    timeout: int,
    max_candidates: int,
    image_mode: str,
    screenshot_timeout: int,
) -> int:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    references = data.get("references")
    if not isinstance(references, list):
        raise SystemExit("Input JSON must contain a references list.")

    report_dir = output_path.parent
    assets_dir.mkdir(parents=True, exist_ok=True)

    seen_hashes: dict[str, str] = {}
    errors: list[str] = []
    warnings: list[str] = []

    for index, ref in enumerate(references, start=1):
        if not isinstance(ref, dict):
            errors.append(f"reference {index}: not an object")
            continue

        title = str(ref.get("title") or f"reference-{index}")
        page_url = str(ref.get("url") or "").strip()
        provided_image = str(ref.get("image") or "").strip()
        ref["_image_status"] = "missing"

        if image_mode == "screenshot":
            if page_url:
                target = assets_dir / f"{index:02d}-{slugify(title, f'reference-{index}')}-page.png"
                ok, screenshot_message = screenshot_page(page_url, target, timeout=screenshot_timeout)
                if ok:
                    digest = hashlib.sha256(target.read_bytes()).hexdigest()
                    if digest in seen_hashes:
                        message = f"{title}: screenshot duplicates image used by {seen_hashes[digest]}"
                        if strict:
                            errors.append(message)
                        else:
                            warnings.append(message)
                        ref["image"] = ""
                        ref["_image_error"] = "duplicate screenshot"
                    else:
                        ref["image"] = make_relative(target, report_dir)
                        ref["_image_status"] = "screenshot"
                        ref["_image_source"] = page_url
                        seen_hashes[digest] = title
                    continue
                ref["_image_error"] = screenshot_message
                message = f"{title}: screenshot fallback failed ({screenshot_message})"
                if strict:
                    errors.append(message)
                else:
                    warnings.append(message)
            else:
                ref["_image_error"] = "no reference page URL for screenshot"
                message = f"{title}: no reference page URL for screenshot"
                if strict:
                    errors.append(message)
                else:
                    warnings.append(message)
            continue

        if provided_image and not is_remote_url(provided_image):
            local_path = (input_path.parent / provided_image).resolve()
            ok, message, digest = local_image_ok(local_path)
            if ok:
                ref["image"] = make_relative(local_path, report_dir)
                ref["_image_status"] = "local"
                if digest in seen_hashes:
                    errors.append(f"{title}: duplicate local image also used by {seen_hashes[digest]}")
                else:
                    seen_hashes[digest] = title
                continue
            warnings.append(f"{title}: {message}; will try page URL")

        page_html = ""
        candidates: list[str] = []
        if page_url:
            try:
                page_html = fetch_text(page_url, timeout=timeout)
                candidates = extract_image_candidates(page_url, page_html)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"{title}: could not fetch reference page ({exc})")

        ordered_candidates: list[str] = []
        if provided_image and is_remote_url(provided_image):
            normalized_provided = absolutize(page_url or provided_image, provided_image)
            if trust_provided or provided_is_on_page(normalized_provided, page_html, candidates):
                ordered_candidates.append(normalized_provided)
            else:
                warnings.append(f"{title}: provided image was not found on its reference page; ignoring it")
        ordered_candidates.extend([c for c in candidates if c not in ordered_candidates])
        ordered_candidates = ordered_candidates[:max_candidates]
        if ordered_candidates:
            ref["_preview_image"] = ordered_candidates[0]

        downloaded = False
        last_error = "no image candidates"
        for candidate in ordered_candidates:
            try:
                image_bytes, content_type, final_url = fetch_bytes(candidate, timeout=timeout)
                if not looks_like_image(image_bytes[:64], content_type):
                    last_error = f"{candidate} returned non-image content type {content_type or 'unknown'}"
                    continue
                digest = hashlib.sha256(image_bytes).hexdigest()
                if digest in seen_hashes:
                    last_error = f"{candidate} duplicates image used by {seen_hashes[digest]}"
                    continue
                ext = infer_ext(final_url, content_type, image_bytes[:64])
                filename = f"{index:02d}-{slugify(title, f'reference-{index}')}{ext}"
                target = assets_dir / filename
                target.write_bytes(image_bytes)
                ref["image"] = make_relative(target, report_dir)
                ref["_image_status"] = "downloaded"
                ref["_image_source"] = final_url
                seen_hashes[digest] = title
                downloaded = True
                # Be polite to visual sites when processing many references.
                time.sleep(0.15)
                break
            except Exception as exc:  # noqa: BLE001
                last_error = f"{candidate} failed: {exc}"

        if not downloaded:
            ref["_image_error"] = last_error
            if (screenshot_missing or image_mode == "hybrid") and page_url:
                target = assets_dir / f"{index:02d}-{slugify(title, f'reference-{index}')}-page.png"
                ok, screenshot_message = screenshot_page(page_url, target, timeout=screenshot_timeout)
                if ok:
                    digest = hashlib.sha256(target.read_bytes()).hexdigest()
                    if digest in seen_hashes:
                        message = f"{title}: screenshot duplicates image used by {seen_hashes[digest]}"
                        if strict:
                            errors.append(message)
                        else:
                            warnings.append(message)
                        ref["image"] = ""
                    else:
                        ref["image"] = make_relative(target, report_dir)
                        ref["_image_status"] = "screenshot"
                        ref["_image_source"] = page_url
                        seen_hashes[digest] = title
                        downloaded = True
                else:
                    warnings.append(f"{title}: screenshot fallback failed ({screenshot_message})")

            if not downloaded:
                ref["image"] = ""
                message = f"{title}: no usable unique image from its own reference page ({last_error})"
                if strict:
                    errors.append(message)
                else:
                    warnings.append(message)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for warning in warnings:
        print(f"[warn] {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1

    with_images = sum(1 for ref in references if isinstance(ref, dict) and ref.get("image"))
    print(f"Prepared {with_images}/{len(references)} reference images -> {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and localize reference images for a design report JSON.")
    parser.add_argument("input", type=Path, help="Input research JSON.")
    parser.add_argument("output", type=Path, help="Output research JSON with local image paths.")
    parser.add_argument(
        "--assets-dir",
        type=Path,
        help="Directory to store downloaded images. Defaults to <output-stem>-assets next to output.",
    )
    parser.add_argument("--strict", action="store_true", help="Fail when any reference lacks a usable unique image.")
    parser.add_argument(
        "--trust-provided",
        action="store_true",
        help="Allow provided remote image URLs even when they are not found on the reference page.",
    )
    parser.add_argument(
        "--screenshot-missing",
        action="store_true",
        help="Capture missing images with Playwright page screenshots.",
    )
    parser.add_argument(
        "--image-mode",
        choices=["extract", "hybrid", "screenshot"],
        default="extract",
        help="extract=download page images; hybrid=extract then screenshot missing; screenshot=capture page screenshots for all references.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help="Per-page and per-image fetch timeout in seconds.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=DEFAULT_MAX_CANDIDATES,
        help="Maximum image candidates to try per reference page.",
    )
    parser.add_argument(
        "--screenshot-timeout",
        type=int,
        default=DEFAULT_SCREENSHOT_TIMEOUT,
        help="Per-page screenshot timeout in seconds when screenshot fallback is enabled.",
    )
    args = parser.parse_args()

    assets_dir = args.assets_dir or (args.output.parent / f"{args.output.stem}-assets")
    return prepare_images(
        args.input,
        args.output,
        assets_dir,
        strict=args.strict,
        trust_provided=args.trust_provided,
        screenshot_missing=args.screenshot_missing,
        timeout=args.timeout,
        max_candidates=max(1, args.max_candidates),
        image_mode=args.image_mode,
        screenshot_timeout=max(3, args.screenshot_timeout),
    )


if __name__ == "__main__":
    raise SystemExit(main())
