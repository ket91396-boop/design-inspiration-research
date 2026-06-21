#!/usr/bin/env python3
"""Build a single-file HTML report from design inspiration research JSON.

Expected input shape is intentionally small and forgiving:

{
  "title": "Mooncake packaging inspiration",
  "subtitle": "Sourced visual directions for a premium Mid-Autumn gift box",
  "brief": {
    "artifact_type": "packaging",
    "use_context": "gift box",
    "audience_tone": "premium, warm",
    "core_symbols": ["moon", "tea", "jade"],
    "visual_risks": ["generic red-gold palette"]
  },
  "keywords": [
    {"category": "Packaging / 包装", "priority": "primary",
     "zh": ["中秋 礼盒 包装"], "en": ["mid autumn packaging"],
     "site": ["site:behance.net mooncake packaging"]}
  ],
  "references": [
    {"category": "Packaging / 包装", "title": "Reference title",
     "url": "https://example.com", "image": "https://example.com/image.jpg",
     "source": "Behance", "borrow": "layered paper texture",
     "avoid": "copying exact illustration"}
  ],
  "deconstruction": {
    "composition": ["close crop hero object"],
    "type": ["condensed sans headline"],
    "color": ["warm neutral with green accent"]
  },
  "directions": [
    {"name": "Quiet Lunar Ritual", "best_use_case": "hero KV",
     "visual_keywords": ["moon", "paper", "tea"],
     "reference_basis": "Paper textures + centered compositions",
     "composition_advice": "Use a calm central axis.",
     "type_advice": "Pair serif Chinese title with small sans metadata.",
     "color_advice": "Ivory base, jade accent, tiny red seal.",
     "graphic_texture_advice": "Use handmade paper grain.",
     "execution_steps": ["Collect references", "Build palette", "Sketch cover"]}
  ],
  "prompts": [
    {"direction": "Quiet Lunar Ritual", "artifact_type": "poster",
     "prompt": "premium poster design...",
     "negative_prompt": "gibberish text, watermark"}
  ],
  "copyright_notes": ["Use references for direction only."],
  "next_prompt": "Now turn direction 1 into three layout variations."
}
"""

from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
from pathlib import Path
from typing import Any


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def text_list(items: Any) -> str:
    values = [esc(item) for item in as_list(items) if str(item).strip()]
    if not values:
        return '<span class="muted">Not specified</span>'
    return "<ul>" + "".join(f"<li>{item}</li>" for item in values) + "</ul>"


def comma_list(items: Any) -> str:
    values = [esc(item) for item in as_list(items) if str(item).strip()]
    return "、".join(values) if values else '<span class="muted">未指定</span>'


def reference_label(key: str, value: Any) -> str:
    labels = {
        "source_quality": {"primary": "主要来源", "secondary": "辅助来源", "supplement": "补充参考"},
        "quality_tier": {"green": "可借鉴", "yellow": "需转化", "red": "避坑参考"},
        "copyright_risk": {"low": "低风险", "medium": "中风险", "high": "高风险"},
    }
    text = str(value or "").strip()
    return labels.get(key, {}).get(text.lower(), text)


def render_missing_image(url: str, status: str, error: str) -> str:
    status_text = {
        "missing": "未提取到图片",
        "local": "本地图片不可用",
        "downloaded": "图片不可用",
        "screenshot": "截图不可用",
    }.get(status, "未提取到图片")
    detail = f"<small>{esc(error)}</small>" if error else "<small>保留高质量来源链接，不使用无关缩略图替代。</small>"
    action = (
        f'<a class="source-button" href="{url}" target="_blank" rel="noreferrer">打开原始页面</a>'
        if url
        else '<span class="source-button muted">无来源链接</span>'
    )
    return (
        '<div class="thumb placeholder">'
        f"<span>{esc(status_text)}</span>"
        f"{detail}"
        f"{action}"
        "</div>"
    )


def section(title: str, body: str, extra_class: str = "") -> str:
    class_attr = f' class="section {extra_class}"' if extra_class else ' class="section"'
    return f"<section{class_attr}><h2>{esc(title)}</h2>{body}</section>"


def render_brief(data: dict[str, Any]) -> str:
    brief = data.get("brief") or {}
    if not isinstance(brief, dict):
        brief = {"summary": brief}

    fields = [
        ("产物类型", brief.get("artifact_type")),
        ("使用场景", brief.get("use_context")),
        ("受众 / 气质", brief.get("audience_tone")),
        ("核心符号", comma_list(brief.get("core_symbols"))),
        ("视觉风险", comma_list(brief.get("visual_risks"))),
    ]
    cards = []
    for label, value in fields:
        if value is None:
            value = '<span class="muted">未指定</span>'
        cards.append(f'<div class="fact"><span>{esc(label)}</span><strong>{value}</strong></div>')

    assumptions = data.get("assumptions")
    if assumptions:
        cards.append(f'<div class="fact wide"><span>假设</span>{text_list(assumptions)}</div>')
    return '<div class="facts">' + "".join(cards) + "</div>"


def render_keywords(data: dict[str, Any]) -> str:
    rows = []
    for item in as_list(data.get("keywords")):
        if not isinstance(item, dict):
            continue
        priority = esc(item.get("priority", ""))
        rows.append(
            "<tr>"
            f"<td><strong>{esc(item.get('category', 'Uncategorized'))}</strong>"
            f"{f'<small>{priority}</small>' if priority else ''}</td>"
            f"<td>{text_list(item.get('zh'))}</td>"
            f"<td>{text_list(item.get('en'))}</td>"
            f"<td>{text_list(item.get('site'))}</td>"
            "</tr>"
        )
    if not rows:
        return '<p class="muted">暂无关键词分类。</p>'
    return (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>分类</th><th>中文关键词</th><th>英文关键词</th><th>限定站点搜索</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def render_references(data: dict[str, Any]) -> str:
    cards = []
    for item in as_list(data.get("references")):
        if not isinstance(item, dict):
            continue
        raw_title = str(item.get("title") or "").strip()
        display_title = str(item.get("title_zh") or raw_title or "未命名参考").strip()
        title = esc(display_title)
        url = esc(item.get("url", ""))
        image = esc(item.get("image", ""))
        preview = esc(item.get("_preview_image", ""))
        source = esc(item.get("source", "Reference"))
        if image:
            image_html = (
                f'<a class="thumb" href="{url or image}" target="_blank" rel="noreferrer">'
                f'<img src="{image}" alt="{title}" loading="lazy"></a>'
            )
        elif preview:
            image_html = (
                f'<a class="thumb remote-preview" href="{url or preview}" target="_blank" rel="noreferrer">'
                f'<img src="{preview}" alt="{title}" loading="lazy">'
                '<span>远程预览</span></a>'
            )
        else:
            image_html = render_missing_image(url, str(item.get("_image_status") or ""), str(item.get("_image_error") or ""))
        link_html = f'<a href="{url}" target="_blank" rel="noreferrer">{title}</a>' if url else title
        chips = []
        for key, label in [
            ("source_quality", "来源"),
            ("quality_tier", "分级"),
            ("copyright_risk", "版权风险"),
        ]:
            value = item.get(key)
            if value:
                chips.append(f'<span class="chip">{esc(label)}：{esc(reference_label(key, value))}</span>')
        borrowable = comma_list(item.get("borrowable_parts"))
        chip_html = f'<div class="chips">{"".join(chips)}</div>' if chips else ""
        original_title = (
            f'<p class="original-title">原始标题：{esc(raw_title)}</p>'
            if raw_title and raw_title != display_title
            else ""
        )
        cards.append(
            '<article class="reference-card">'
            f"{image_html}"
            '<div class="reference-body">'
            f"<p class=\"source\">{source} · {esc(item.get('category', 'General'))}</p>"
            f"<h3>{link_html}</h3>"
            f"{original_title}"
            f"{chip_html}"
            f"<p><b>可借鉴：</b>{borrowable}</p>"
            f"<p><b>怎么借：</b>{esc(item.get('borrow', '未填写'))}</p>"
            f"<p><b>别照抄：</b>{esc(item.get('avoid', '未填写'))}</p>"
            "</div></article>"
        )
    if not cards:
        return '<p class="muted">暂无参考。</p>'
    return '<div class="reference-grid">' + "".join(cards) + "</div>"


def render_deconstruction(data: dict[str, Any]) -> str:
    deconstruction = data.get("deconstruction") or {}
    if not isinstance(deconstruction, dict):
        return f"<p>{esc(deconstruction)}</p>"

    order = ["composition", "type", "color", "motifs", "texture", "mood", "application"]
    labels = {
        "composition": "构图",
        "type": "字体 / 字形",
        "color": "配色",
        "motifs": "符号",
        "texture": "质感",
        "mood": "气质",
        "application": "应用",
    }
    keys = order + [key for key in deconstruction.keys() if key not in order]
    blocks = []
    for key in keys:
        if key not in deconstruction:
            continue
        blocks.append(
            '<div class="analysis-block">'
            f"<h3>{esc(labels.get(key, key.replace('_', ' ').title()))}</h3>"
            f"{text_list(deconstruction.get(key))}"
            "</div>"
        )
    return '<div class="analysis-grid">' + "".join(blocks) + "</div>" if blocks else '<p class="muted">暂无审美拆解。</p>'


def render_directions(data: dict[str, Any]) -> str:
    cards = []
    for index, item in enumerate(as_list(data.get("directions")), start=1):
        if not isinstance(item, dict):
            continue
        cards.append(
            '<article class="direction-card">'
            f'<span class="count">{index:02d}</span>'
            f"<h3>{esc(item.get('name', f'Direction {index}'))}</h3>"
            f"<p class=\"use\"><b>适合场景：</b>{esc(item.get('best_use_case', '未指定'))}</p>"
            f"<p><b>视觉关键词：</b>{comma_list(item.get('visual_keywords'))}</p>"
            f"<p><b>参考依据：</b>{esc(item.get('reference_basis', '未指定'))}</p>"
            f"<p><b>构图建议：</b>{esc(item.get('composition_advice', '未指定'))}</p>"
            f"<p><b>字体 / 字形建议：</b>{esc(item.get('type_advice', '未指定'))}</p>"
            f"<p><b>配色建议：</b>{esc(item.get('color_advice', '未指定'))}</p>"
            f"<p><b>图形 / 质感建议：</b>{esc(item.get('graphic_texture_advice', '未指定'))}</p>"
            f"<div><b>今天怎么做：</b>{text_list(item.get('execution_steps'))}</div>"
            "</article>"
        )
    return '<div class="direction-list">' + "".join(cards) + "</div>" if cards else '<p class="muted">暂无设计方向。</p>'


def render_prompts(data: dict[str, Any]) -> str:
    cards = []
    for item in as_list(data.get("prompts")):
        if not isinstance(item, dict):
            continue
        prompt = esc(item.get("prompt", ""))
        negative = esc(item.get("negative_prompt", ""))
        cards.append(
            '<article class="prompt-card">'
            f"<h3>{esc(item.get('direction', 'Prompt'))}</h3>"
            f"<p class=\"source\">{esc(item.get('artifact_type', ''))}</p>"
            f"<pre>{prompt}</pre>"
            f"{f'<p><b>负面提示：</b>{negative}</p>' if negative else ''}"
            "</article>"
        )
    return '<div class="prompt-list">' + "".join(cards) + "</div>" if cards else '<p class="muted">暂无提示词。</p>'


def render_notes(data: dict[str, Any]) -> str:
    parts = []
    if data.get("copyright_notes"):
        parts.append("<h3>版权与使用提醒</h3>" + text_list(data.get("copyright_notes")))
    if data.get("next_prompt"):
        parts.append(f"<h3>下一步提示词</h3><pre>{esc(data.get('next_prompt'))}</pre>")
    return "".join(parts) if parts else '<p class="muted">暂无备注。</p>'


def build_html(data: dict[str, Any]) -> str:
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    title = data.get("title") or "Design Inspiration Research"
    subtitle = data.get("subtitle") or "Sourced references, visual analysis, directions, and image prompts."

    body = "\n".join(
        [
            section("需求简析", render_brief(data)),
            section("搜索关键词", render_keywords(data)),
            section("视觉参考", render_references(data)),
            section("审美拆解", render_deconstruction(data)),
            section("可执行设计方向", render_directions(data)),
            section("AI 生图提示词", render_prompts(data)),
            section("备注", render_notes(data)),
        ]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #151515;
      --muted: #68645e;
      --paper: #f6f0e7;
      --panel: #fffdf8;
      --line: #ddd2c4;
      --accent: #1f7a64;
      --accent-2: #d9553f;
      --accent-3: #2f5f9c;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        linear-gradient(90deg, rgba(21,21,21,.04) 1px, transparent 1px),
        linear-gradient(rgba(21,21,21,.035) 1px, transparent 1px),
        var(--paper);
      background-size: 28px 28px;
    }}
    main {{ width: min(1180px, calc(100% - 32px)); margin: 0 auto; padding: 48px 0 72px; }}
    header {{ min-height: 52vh; display: grid; align-content: end; padding: 56px 0 40px; border-bottom: 2px solid var(--ink); }}
    .kicker {{ margin: 0 0 18px; color: var(--accent-2); font-size: .78rem; font-weight: 850; letter-spacing: .12em; text-transform: uppercase; }}
    h1 {{ max-width: 980px; margin: 0; font-family: ui-serif, Georgia, "Times New Roman", serif; font-size: clamp(3rem, 8vw, 7.4rem); line-height: .9; letter-spacing: 0; }}
    .subtitle {{ max-width: 760px; margin: 22px 0 0; color: var(--muted); font-size: 1.08rem; line-height: 1.7; }}
    .section {{ padding: 34px 0; border-bottom: 1px solid var(--line); }}
    h2 {{ margin: 0 0 18px; font-size: 1.35rem; letter-spacing: 0; }}
    h3 {{ margin: 0 0 10px; font-size: 1rem; }}
    p {{ line-height: 1.62; }}
    a {{ color: var(--accent-3); text-decoration-thickness: 1px; text-underline-offset: 3px; }}
    ul {{ margin: 8px 0 0; padding-left: 1.1rem; }}
    li {{ margin: 5px 0; line-height: 1.45; }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; margin: 10px 0 0; padding: 14px; border: 1px solid var(--line); background: #f9f5ee; font: .92rem/1.55 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); }}
    th, td {{ vertical-align: top; padding: 14px; border: 1px solid var(--line); text-align: left; }}
    th {{ font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; }}
    small {{ display: block; margin-top: 5px; color: var(--accent-2); font-weight: 800; text-transform: uppercase; }}
    .muted {{ color: var(--muted); }}
    .facts, .analysis-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }}
    .fact, .analysis-block, .direction-card, .prompt-card, .reference-card {{ border: 1px solid var(--line); background: rgba(255,253,248,.88); }}
    .fact {{ min-height: 110px; padding: 16px; }}
    .fact.wide {{ grid-column: 1 / -1; }}
    .fact span, .source {{ display: block; margin: 0 0 8px; color: var(--muted); font-size: .78rem; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
    .fact strong {{ font-size: 1.05rem; line-height: 1.45; }}
    .table-wrap {{ overflow-x: auto; }}
    .reference-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
    .reference-card {{ display: grid; grid-template-columns: 190px minmax(0, 1fr); min-height: 190px; overflow: hidden; }}
    .thumb {{ display: block; width: 100%; height: 100%; min-height: 190px; background: #eee5d8; }}
    .thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .remote-preview {{ position: relative; }}
    .remote-preview span {{ position: absolute; left: 8px; bottom: 8px; padding: 4px 7px; background: rgba(21,21,21,.72); color: #fff; font-size: .72rem; font-weight: 850; }}
    .thumb.placeholder {{ display: grid; align-content: center; justify-items: center; gap: 8px; padding: 16px; text-align: center; color: var(--muted); font-weight: 800; }}
    .thumb.placeholder small {{ display: block; max-width: 150px; font-weight: 600; line-height: 1.35; text-transform: none; letter-spacing: 0; }}
    .source-button {{ display: inline-flex; align-items: center; justify-content: center; min-height: 30px; padding: 0 10px; border: 1px solid var(--line); background: var(--panel); color: var(--accent-3); font-size: .78rem; font-weight: 850; text-decoration: none; }}
    .reference-body, .analysis-block, .direction-card, .prompt-card {{ padding: 16px; }}
    .original-title {{ margin: -2px 0 8px; color: var(--muted); font-size: .82rem; }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 10px; }}
    .chip {{ display: inline-flex; align-items: center; border: 1px solid var(--line); background: #f9f5ee; padding: 3px 8px; font-size: .76rem; font-weight: 800; color: var(--muted); }}
    .direction-list, .prompt-list {{ display: grid; gap: 14px; }}
    .direction-card {{ position: relative; padding-left: 64px; }}
    .count {{ position: absolute; left: 16px; top: 16px; color: var(--accent); font-weight: 950; }}
    .use {{ color: var(--muted); }}
    @media (max-width: 860px) {{
      main {{ padding-top: 20px; }}
      header {{ min-height: 42vh; }}
      .facts, .analysis-grid, .reference-grid {{ grid-template-columns: 1fr; }}
      .reference-card {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="kicker">Design Inspiration Research · generated {esc(now)}</p>
      <h1>{esc(title)}</h1>
      <p class="subtitle">{esc(subtitle)}</p>
    </header>
    {body}
  </main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a design inspiration HTML report from JSON.")
    parser.add_argument("input", type=Path, help="Path to research JSON.")
    parser.add_argument("output", type=Path, help="Path to write the HTML report.")
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Input JSON root must be an object.")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(data), encoding="utf-8")
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
