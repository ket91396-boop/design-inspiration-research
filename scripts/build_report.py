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
    return ", ".join(values) if values else '<span class="muted">Not specified</span>'


def section(title: str, body: str, extra_class: str = "") -> str:
    class_attr = f' class="section {extra_class}"' if extra_class else ' class="section"'
    return f"<section{class_attr}><h2>{esc(title)}</h2>{body}</section>"


def render_brief(data: dict[str, Any]) -> str:
    brief = data.get("brief") or {}
    if not isinstance(brief, dict):
        brief = {"summary": brief}

    fields = [
        ("Artifact type", brief.get("artifact_type")),
        ("Use context", brief.get("use_context")),
        ("Audience / tone", brief.get("audience_tone")),
        ("Core symbols", comma_list(brief.get("core_symbols"))),
        ("Visual risks", comma_list(brief.get("visual_risks"))),
    ]
    cards = []
    for label, value in fields:
        if value is None:
            value = '<span class="muted">Not specified</span>'
        cards.append(f'<div class="fact"><span>{esc(label)}</span><strong>{value}</strong></div>')

    assumptions = data.get("assumptions")
    if assumptions:
        cards.append(f'<div class="fact wide"><span>Assumptions</span>{text_list(assumptions)}</div>')
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
        return '<p class="muted">No keyword categories provided.</p>'
    return (
        '<div class="table-wrap"><table><thead><tr>'
        "<th>Category</th><th>Chinese keywords</th><th>English keywords</th><th>Site-limited searches</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def render_references(data: dict[str, Any]) -> str:
    cards = []
    for item in as_list(data.get("references")):
        if not isinstance(item, dict):
            continue
        title = esc(item.get("title", "Untitled reference"))
        url = esc(item.get("url", ""))
        image = esc(item.get("image", ""))
        source = esc(item.get("source", "Reference"))
        image_html = (
            f'<a class="thumb" href="{url or image}" target="_blank" rel="noreferrer">'
            f'<img src="{image}" alt="{title}" loading="lazy"></a>'
            if image
            else '<div class="thumb placeholder">No image link</div>'
        )
        link_html = f'<a href="{url}" target="_blank" rel="noreferrer">{title}</a>' if url else title
        cards.append(
            '<article class="reference-card">'
            f"{image_html}"
            '<div class="reference-body">'
            f"<p class=\"source\">{source} · {esc(item.get('category', 'General'))}</p>"
            f"<h3>{link_html}</h3>"
            f"<p><b>Borrow:</b> {esc(item.get('borrow', 'Not specified'))}</p>"
            f"<p><b>Avoid:</b> {esc(item.get('avoid', 'Not specified'))}</p>"
            "</div></article>"
        )
    if not cards:
        return '<p class="muted">No references provided.</p>'
    return '<div class="reference-grid">' + "".join(cards) + "</div>"


def render_deconstruction(data: dict[str, Any]) -> str:
    deconstruction = data.get("deconstruction") or {}
    if not isinstance(deconstruction, dict):
        return f"<p>{esc(deconstruction)}</p>"

    order = ["composition", "type", "color", "motifs", "texture", "mood", "application"]
    labels = {
        "composition": "Composition",
        "type": "Type",
        "color": "Color",
        "motifs": "Motifs",
        "texture": "Texture",
        "mood": "Mood",
        "application": "Application",
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
    return '<div class="analysis-grid">' + "".join(blocks) + "</div>" if blocks else '<p class="muted">No deconstruction provided.</p>'


def render_directions(data: dict[str, Any]) -> str:
    cards = []
    for index, item in enumerate(as_list(data.get("directions")), start=1):
        if not isinstance(item, dict):
            continue
        cards.append(
            '<article class="direction-card">'
            f'<span class="count">{index:02d}</span>'
            f"<h3>{esc(item.get('name', f'Direction {index}'))}</h3>"
            f"<p class=\"use\"><b>Best use:</b> {esc(item.get('best_use_case', 'Not specified'))}</p>"
            f"<p><b>Visual keywords:</b> {comma_list(item.get('visual_keywords'))}</p>"
            f"<p><b>Reference basis:</b> {esc(item.get('reference_basis', 'Not specified'))}</p>"
            f"<p><b>Composition:</b> {esc(item.get('composition_advice', 'Not specified'))}</p>"
            f"<p><b>Type:</b> {esc(item.get('type_advice', 'Not specified'))}</p>"
            f"<p><b>Color:</b> {esc(item.get('color_advice', 'Not specified'))}</p>"
            f"<p><b>Graphic / texture:</b> {esc(item.get('graphic_texture_advice', 'Not specified'))}</p>"
            f"<div><b>Execution steps:</b>{text_list(item.get('execution_steps'))}</div>"
            "</article>"
        )
    return '<div class="direction-list">' + "".join(cards) + "</div>" if cards else '<p class="muted">No directions provided.</p>'


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
            f"{f'<p><b>Negative:</b> {negative}</p>' if negative else ''}"
            "</article>"
        )
    return '<div class="prompt-list">' + "".join(cards) + "</div>" if cards else '<p class="muted">No prompts provided.</p>'


def render_notes(data: dict[str, Any]) -> str:
    parts = []
    if data.get("copyright_notes"):
        parts.append("<h3>Copyright and usage notes</h3>" + text_list(data.get("copyright_notes")))
    if data.get("next_prompt"):
        parts.append(f"<h3>Next prompt</h3><pre>{esc(data.get('next_prompt'))}</pre>")
    return "".join(parts) if parts else '<p class="muted">No notes provided.</p>'


def build_html(data: dict[str, Any]) -> str:
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    title = data.get("title") or "Design Inspiration Research"
    subtitle = data.get("subtitle") or "Sourced references, visual analysis, directions, and image prompts."

    body = "\n".join(
        [
            section("Brief", render_brief(data)),
            section("Search Keywords", render_keywords(data)),
            section("Visual References", render_references(data)),
            section("Aesthetic Deconstruction", render_deconstruction(data)),
            section("Actionable Directions", render_directions(data)),
            section("AI Image Prompts", render_prompts(data)),
            section("Notes", render_notes(data)),
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
    .thumb.placeholder {{ display: grid; place-items: center; color: var(--muted); font-weight: 800; }}
    .reference-body, .analysis-block, .direction-card, .prompt-card {{ padding: 16px; }}
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
