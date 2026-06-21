#!/usr/bin/env python3
"""Audit design inspiration research JSON for source and judgment quality."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

STANDARD_CATEGORIES = {
    "logo",
    "poster",
    "typography",
    "texture",
    "wallpaper",
    "layout",
    "color",
    "illustration",
    "web",
}

TEMPLATE_MARKET_DOMAINS = {
    "nipic.com",
    "tusij.com",
    "58pic.com",
    "588ku.com",
    "pngtree.com",
    "canva.com",
    "brandcrowd.com",
    "qianku.com",
}

VALID_SOURCE_QUALITY = {"primary", "secondary", "supplement"}
VALID_QUALITY_TIERS = {"green", "yellow", "red"}
VALID_COPYRIGHT_RISK = {"low", "medium", "high"}


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def norm(value: Any) -> str:
    return str(value or "").strip().lower()


def category_key(value: Any) -> str:
    text = norm(value)
    return text.split("/", 1)[0].strip()


def domain_of(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def is_template_market(host: str) -> bool:
    return any(host == domain or host.endswith("." + domain) for domain in TEMPLATE_MARKET_DOMAINS)


def audit(data: dict[str, Any], *, allow_template_primary: bool) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    keywords = [item for item in as_list(data.get("keywords")) if isinstance(item, dict)]
    keyword_categories = {category_key(item.get("category")) for item in keywords}
    missing = sorted(cat for cat in STANDARD_CATEGORIES if cat not in keyword_categories)
    if missing:
        warnings.append("missing standard keyword categories: " + ", ".join(missing))

    references = [item for item in as_list(data.get("references")) if isinstance(item, dict)]
    if not references:
        errors.append("references must contain at least one reference object")

    source_counts: Counter[str] = Counter()
    red_count = 0
    primary_count = 0

    for index, ref in enumerate(references, start=1):
        title = str(ref.get("title") or f"reference {index}")
        url = str(ref.get("url") or "").strip()
        host = domain_of(url)
        if host:
            source_counts[host] += 1

        source_quality = norm(ref.get("source_quality") or "primary")
        quality_tier = norm(ref.get("quality_tier") or "")
        copyright_risk = norm(ref.get("copyright_risk") or "")
        borrowable_parts = [part for part in as_list(ref.get("borrowable_parts")) if str(part).strip()]

        if source_quality not in VALID_SOURCE_QUALITY:
            errors.append(f"{title}: invalid source_quality {source_quality!r}")
        if quality_tier not in VALID_QUALITY_TIERS:
            errors.append(f"{title}: missing or invalid quality_tier")
        if copyright_risk not in VALID_COPYRIGHT_RISK:
            errors.append(f"{title}: missing or invalid copyright_risk")
        if not borrowable_parts:
            warnings.append(f"{title}: borrowable_parts is empty")
        if not str(ref.get("borrow") or "").strip():
            errors.append(f"{title}: borrow is required")
        if not str(ref.get("avoid") or "").strip():
            errors.append(f"{title}: avoid is required")

        if source_quality == "primary":
            primary_count += 1
        if quality_tier == "red":
            red_count += 1
        if host and is_template_market(host) and source_quality in {"primary", "secondary"} and not allow_template_primary:
            errors.append(f"{title}: template-market source cannot be primary/secondary ({host})")

    if references:
        red_ratio = red_count / len(references)
        if red_ratio > 0.25:
            warnings.append(f"red reference ratio is high: {red_count}/{len(references)}")
        if primary_count == 0:
            warnings.append("no primary references selected")
        for host, count in source_counts.items():
            if count > max(4, len(references) // 2):
                warnings.append(f"many references come from one domain: {host} ({count})")

    directions = [item for item in as_list(data.get("directions")) if isinstance(item, dict)]
    if not directions:
        errors.append("directions must contain at least one direction")
    for index, direction in enumerate(directions, start=1):
        name = str(direction.get("name") or f"direction {index}")
        if not str(direction.get("reference_basis") or "").strip():
            errors.append(f"{name}: reference_basis is required")
        if not as_list(direction.get("execution_steps")):
            warnings.append(f"{name}: execution_steps is empty")

    prompts = [item for item in as_list(data.get("prompts")) if isinstance(item, dict)]
    if not prompts:
        warnings.append("prompts is empty")
    for index, prompt in enumerate(prompts, start=1):
        label = str(prompt.get("direction") or f"prompt {index}")
        if not str(prompt.get("negative_prompt") or "").strip():
            warnings.append(f"{label}: negative_prompt is missing")

    for warning in warnings:
        print(f"[warn] {warning}")
    if errors:
        for error in errors:
            print(f"[error] {error}")
        print(f"Research quality audit failed: {len(errors)} errors, {len(warnings)} warnings.")
        return 1

    print(f"Research quality audit passed: {len(references)} references, {len(directions)} directions, {len(warnings)} warnings.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit design inspiration research JSON quality.")
    parser.add_argument("json", type=Path, help="Research JSON to audit.")
    parser.add_argument(
        "--allow-template-primary",
        action="store_true",
        help="Allow template-market domains as primary/secondary sources when explicitly requested.",
    )
    args = parser.parse_args()

    data = json.loads(args.json.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("[error] input JSON root must be an object", file=sys.stderr)
        return 1
    return audit(data, allow_template_primary=args.allow_template_primary)


if __name__ == "__main__":
    raise SystemExit(main())
