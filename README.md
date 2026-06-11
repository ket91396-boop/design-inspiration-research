# Design Inspiration Research

A Codex skill that turns a loose design brief into a sourced, audited inspiration research pack for designers.

It is built for moments like:

- "I want to make a Mid-Autumn Festival poster."
- "I need an abstract leopard logo for an event management system."
- "Help me gather references for a Father's Day campaign visual."
- "I need a QL lettermark logo with a big-tech feel."

The skill analyzes the brief, creates a research plan, searches quality visual sources, selects references with design judgment, deconstructs the visual language, and outputs practical directions plus AI image prompts. When an HTML deliverable is requested, it renders a single-file report from audited JSON.

## What It Does

- Analyzes the design need, audience, tone, symbols, and visual risks.
- Builds a short research plan before browsing.
- Generates search keywords across every standard reference category.
- Searches across design, typography, photography, UI, layout, and palette sources.
- Selects references by source quality, design relevance, borrowable parts, and copyright risk.
- Deconstructs references into composition, typography, color, texture, motif, mood, and application.
- Provides 3-5 directions a designer can start from immediately.
- Writes AI image prompts matched to the artifact type.
- Generates optional HTML reports from structured JSON.
- Supports Chinese-first report output while preserving original source titles for traceability.

## Workflow Model

The skill is organized into three layers:

1. **Facts layer**: brief, research plan, candidate references, source URLs, image availability, and source metadata.
2. **Judgment layer**: source quality, reference quality tier, copyright risk, borrowable parts, and design directions.
3. **Delivery layer**: chat research pack or audited JSON plus an HTML report.

This keeps browsing evidence separate from design judgment, and keeps final reports easier to verify.

## Reference Categories

The skill scans all standard categories every time:

- Logo / identity
- Poster / key visual
- Typography / lettering
- Texture / material
- Wallpaper / scenery
- Layout / composition
- Color / palette inspiration
- Illustration
- Web / product UI

## Reference Quality

References can include:

- `source_quality`: `primary`, `secondary`, or `supplement`
- `quality_tier`: `green`, `yellow`, or `red`
- `copyright_risk`: `low`, `medium`, or `high`
- `borrowable_parts`: concrete design attributes worth studying

Use the tiers as design guidance:

- `green`: safe to borrow abstract logic such as composition, palette, spacing, type rhythm, material, or interaction pattern.
- `yellow`: useful but needs transformation, such as distinctive commercial campaigns or recognizable custom lettering.
- `red`: anti-pattern or high-risk reference, such as template-market work, obvious IP, or trademark-like marks.

## HTML Reports

When the user explicitly asks for HTML or a shareable report, use the bundled scripts:

```bash
python3 scripts/prepare_report_images.py research.raw.json research.json --assets-dir report-assets
python3 scripts/audit_report_images.py research.json --min-ratio 0 --fail-on-duplicates
python3 scripts/audit_research_quality.py research.json
python3 scripts/build_report.py research.json design-inspiration-report.html
```

Image extraction is intentionally conservative. The skill tries same-page `og:image`, `twitter:image`, `<img>`, and direct image candidates. If a high-quality reference page does not expose a usable image, the report keeps the page link and leaves the image empty instead of using unrelated thumbnails or screenshots.

For Chinese prompts, reports are Chinese-first: section labels, reference explanations, borrow/avoid notes, directions, and prompts should be in Chinese. Original source titles are preserved as secondary traceability text.

## Installation

Clone or copy this repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/ket91396-boop/design-inspiration-research.git ~/.codex/skills/design-inspiration-research
```

Then start a new Codex conversation and invoke it like:

```text
Use $design-inspiration-research to help me create a Father's Day poster.
```

## Files

- `SKILL.md`: required Codex skill entrypoint.
- `agents/openai.yaml`: optional Codex UI metadata.
- `references/`: artifact patterns, source/image strategy, and quality rubric.
- `scripts/prepare_report_images.py`: localizes same-page reference images for reports.
- `scripts/audit_report_images.py`: checks image reachability and duplicate assets.
- `scripts/audit_research_quality.py`: checks source quality, required fields, and research structure.
- `scripts/build_report.py`: renders the structured JSON into a single HTML report.
- `index.html`: simple project introduction page.

## License

MIT License. You can use, copy, modify, and share this skill as long as the license notice is preserved.
