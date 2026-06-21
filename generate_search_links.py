#!/usr/bin/env python3
"""Generate categorized design-inspiration search links from a brief."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import quote_plus

SITES = {
    "Dribbble": "https://dribbble.com/search/{q}",
    "Behance": "https://www.behance.net/search/projects/{q}",
    "Pinterest": "https://www.pinterest.com/search/pins/?q={q}",
    "Awwwards": "https://www.awwwards.com/search/?text={q}",
    "Fonts In Use": "https://fontsinuse.com/search?terms={q}",
    "Typewolf": "https://www.typewolf.com/search?query={q}",
    "Unsplash": "https://unsplash.com/s/photos/{q}",
    "Pexels": "https://www.pexels.com/search/{q}/",
    "Mobbin": "https://mobbin.com/search?q={q}",
    "Land-book": "https://land-book.com/search?q={q}",
}

CATEGORY_PATTERNS = {
    "Logo / 标志": [
        "{topic} logo design",
        "{topic} brand identity",
        "{topic} symbol mark",
        "{topic} visual identity",
    ],
    "Poster / 海报": [
        "{topic} poster design",
        "{topic} key visual",
        "{style} campaign poster",
        "{topic} hero graphic",
    ],
    "Typography / 标题字": [
        "{topic} typography poster",
        "{topic} hand lettering",
        "{style} headline design",
        "Chinese typography poster design",
    ],
    "Texture / 纹理材质": [
        "{style} texture",
        "paper grain texture",
        "warm material texture",
        "{topic} visual texture",
    ],
    "Wallpaper / 背景壁纸": [
        "{topic} background",
        "{style} wallpaper",
        "{topic} photography background",
        "clean background with negative space",
    ],
    "Layout / 版式构图": [
        "center hero composition poster",
        "editorial poster layout",
        "campaign key visual composition",
        "{style} layout design",
    ],
    "Color / 配色灵感": [
        "{style} color palette",
        "{topic} color palette",
        "campaign color palette",
        "poster color system",
    ],
    "Illustration / 插画图形": [
        "{topic} illustration",
        "{topic} line art",
        "{style} graphic illustration",
        "{topic} icon system",
    ],
    "Web / 产品界面": [
        "{topic} landing page design",
        "{style} website design",
        "campaign landing page",
        "{topic} product UI",
    ],
}

STYLE_HINTS = {
    "科技": "futuristic technology",
    "赛博": "cyberpunk neon",
    "高级": "premium minimal",
    "极简": "minimal clean",
    "国潮": "modern Chinese style",
    "明亮": "bright clean",
    "冲击": "high impact dynamic",
    "温暖": "warm emotional",
    "复古": "vintage editorial",
    "手写": "hand lettering",
}

TOPIC_HINTS = {
    "父亲节": "Father's Day",
    "母亲节": "Mother's Day",
    "中秋": "Mid-Autumn Festival",
    "春节": "Chinese New Year",
    "logo": "logo design",
    "海报": "poster design",
    "封面": "social media cover",
    "包装": "packaging design",
    "UI": "product UI",
    "网页": "website design",
}


def infer_topic(brief: str) -> str:
    hits = [value for key, value in TOPIC_HINTS.items() if key in brief]
    if hits:
        return " ".join(dict.fromkeys(hits))
    cleaned = re.sub(r"[，。！？、,.!?]+", " ", brief).strip()
    return cleaned[:80] or "design inspiration"


def infer_style(brief: str) -> str:
    hits = [value for key, value in STYLE_HINTS.items() if key in brief]
    if hits:
        return " ".join(dict.fromkeys(hits))
    return "modern visual design"


def build_markdown(brief: str) -> str:
    topic = infer_topic(brief)
    style = infer_style(brief)
    lines = [
        "# Design Inspiration Search Links",
        "",
        f"Brief: {brief}",
        f"Inferred topic: {topic}",
        f"Inferred style: {style}",
        "",
    ]
    for category, patterns in CATEGORY_PATTERNS.items():
        lines.extend([f"## {category}", ""])
        for pattern in patterns:
            query = pattern.format(topic=topic, style=style)
            encoded = quote_plus(query)
            lines.append(f"### {query}")
            for site, template in SITES.items():
                lines.append(f"- [{site}]({template.format(q=encoded)})")
            lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate search-link matrix for design inspiration research.")
    parser.add_argument("brief", help="Design brief in Chinese or English.")
    parser.add_argument("--output", "-o", type=Path, default=Path("design-inspiration-search-links.md"))
    args = parser.parse_args()

    args.output.write_text(build_markdown(args.brief), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
