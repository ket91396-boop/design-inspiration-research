---
name: design-inspiration-research
description: Turn a design brief into a sourced inspiration research pack for designers, with an optional single-file HTML report only when requested. Use when the user asks for inspiration, references, moodboards, keywords, visual directions, poster/logo/cover/typography/packaging/UI reference research, HTML research reports, or AI image prompts for a design task such as a festival poster, brand logo, title lettering, wallpaper, texture, landing page, app UI, or campaign key visual.
---

# Design Inspiration Research

Use this skill as a design research assistant and visual design director. Convert one fuzzy design need into a compact, actionable research pack: brief analysis, category-specific search keywords, live visual references with links, aesthetic analysis, 3-5 directions, and AI image prompts matched to the requested artifact type. Default output is the normal chat research pack. When the user explicitly asks for HTML, a report file, or a shareable deliverable, generate the structured JSON file plus a single-file HTML report with `scripts/build_report.py` and keep the chat response to a concise file handoff.

Use a lightweight mode when the user asks for quick inspiration, a first pass, or a few directions without a file deliverable. In lightweight mode, keep the same source-quality rules but reduce the deliverable to a brief, keyword matrix, 8-12 references, 3 directions, prompts, and copyright notes.

Never run screenshot capture, image localization, JSON report preparation, or HTML rendering for ordinary chat research. These file/report steps are only for explicit requests such as "生成 HTML", "做成报告", "给我一个可分享文件", "输出文件", or "HTML 里要有图".

## Core Model

Keep the skill split into three layers:

1. **Facts layer**: collect the brief, search plan, candidate references, source URLs, image availability, and source metadata. This layer should be evidence-like and concise.
2. **Judgment layer**: classify references by design usefulness, source quality, borrowable parts, and copyright risk. This is where the agent acts as design director.
3. **Delivery layer**: produce the chat pack or, when requested, audited JSON plus an HTML report.

Do not let image extraction convenience drive the research. A high-quality Behance / Dribbble / Fonts In Use / Mobbin / Unsplash / Pexels page with no extractable image is still better than a low-quality template-market thumbnail.

## Language Rule

Match the user's language for all human-facing analysis and report text. If the user writes in Chinese, the HTML report must be Chinese-first:

- Section titles, field labels, reference explanations, directions, deconstruction, copyright notes, and next-step prompts should be Chinese.
- Keep original source titles and source names for traceability, but make Chinese the primary reading layer. Add `title_zh` for each reference; render/show it as the main card title, with the original `title` as secondary source text when different.
- `borrow`, `avoid`, and `borrowable_parts` must be written in Chinese for Chinese requests.
- Do not leave renderer labels such as "Visual References", "Borrow", "Avoid", "Source", "Tier", or "Risk" in English for Chinese report output.

## Bundled References

Load only the reference file needed for the task:

- `references/artifact-patterns.md`: read when deciding how to analyze logos, posters, typography, packaging, UI, textures, wallpapers, or illustration.
- `references/source-and-image-strategy.md`: read before live research or HTML report generation; contains source routing, image extraction policy, and site-specific expectations.
- `references/quality-rubric.md`: read when selecting final references or assigning `quality_tier`, `source_quality`, and `copyright_risk`.
- `scripts/generate_search_links.py`: run when browsing/image search is unavailable or the user wants manual search links.
- `scripts/prepare_report_images.ps1` and `scripts/build_report.ps1`: prefer on Windows when `python` is unavailable or resolves to the Microsoft Store placeholder. They create visual-complete HTML reports using Chrome/Edge screenshots and a PowerShell HTML renderer.

## Core Workflow

Always follow this sequence unless the user explicitly asks for a narrower output:

1. Analyze the design need.
2. Build a short research plan: artifact priorities, category priorities, route-to-site choices, and target reference counts.
3. List search keywords for every standard category.
4. Search every standard category immediately and collect a candidate pool with page links.
5. Select final references from the candidate pool using source quality, design relevance, borrowability, and copyright risk.
6. Deconstruct the selected references aesthetically.
7. Summarize 3-5 directions the designer can start today.
8. Write AI image prompts matched to the artifact type.
9. If and only if the user explicitly asks for HTML, a report file, an output file, or a shareable deliverable, build a JSON research file, prepare/audit images, audit research quality, and render it to HTML with `scripts/build_report.py`; in chat, link the generated report instead of repeating the full research pack.

If the user says not to browse, skip step 3 and make that limitation explicit.

### Lightweight Mode

Use lightweight mode when the user says "快速", "先简单找", "不要报告", "先给几个方向", "quick inspiration", or the brief is exploratory and no file deliverable is requested.

- Keep the standard categories and source-quality rules.
- Search fewer but better sources: aim for 8-12 total references.
- Output compact reference cards with title, source link, source quality, quality tier, copyright risk, what to borrow, and what not to copy.
- Do not generate JSON, HTML, screenshots, image localization, remote preview extraction, or image audits.
- If the user later asks for HTML/report, convert the selected references into the structured JSON workflow.

### No-Browsing Fallback

If browsing or image search is unavailable, do not pretend to have found images. Generate a searchable link matrix instead:

```bash
python3 scripts/generate_search_links.py "brief text" --output design-inspiration-search-links.md
```

Then give the user the file/link matrix plus a short manual workflow: open the links, collect promising source URLs, and send them back for deconstruction.

## Step 1: Analyze The Need

Extract and state:

- Artifact type: logo, poster, cover, title lettering, packaging, texture, wallpaper, photography, UI, landing page, or mixed system.
- Use context: social post, brand campaign, event, ecommerce, packaging, offline material, app/web UI, deck, etc.
- Audience and tone: young, premium, friendly, official, cultural, experimental, playful, commercial, etc.
- Core symbols: product, holiday, region, material, emotion, character, action, motif.
- Visual risks: cliche templates, copyright risk, wrong audience tone, over-complexity, unreadable type.

Make reasonable assumptions when missing details. Do not stop for clarification unless the brief is impossible to route.

## Step 2: Keywords By Category

Always include every standard category, even when the user names one artifact type. The user wants a broad scan because unexpected references often come from adjacent categories. Each category must have Chinese keywords, English keywords, and site-limited keywords.

You may mark categories as `primary`, `secondary`, or `wildcard`, but do not omit any category:

- `primary`: directly matches the artifact type or brief. These categories should get visibly deeper search coverage.
- `secondary`: adjacent and likely useful.
- `wildcard`: less obvious, but searched to uncover unexpected inspiration.

### Site Routing

Do not search every site evenly. Route by reference type:

| Reference type | Prefer these sites | Best for |
| --- | --- | --- |
| Logo / identity | Dribbble, Behance, Pinterest | logos, marks, wordmarks, brand systems, symbol concepts |
| Poster / key visual | Behance, Pinterest, Dribbble | poster series, campaign KV, festival visuals, title hierarchy |
| Illustration | Dribbble, Behance, Pinterest | illustration styles, characters, symbols, pattern systems |
| Typography / lettering | Fonts In Use, Typewolf, Behance, Pinterest | type pairing, title lettering, real font usage, poster typography |
| Texture / material | Unsplash, Pexels, Pinterest, Behance | real material photos, paper, plants, food, light, print texture |
| Wallpaper / scenery | Unsplash, Pexels, Pinterest | nature, photography, abstract backgrounds, atmospheric images |
| Layout / composition | Behance, Pinterest, Awwwards, Land-book | poster layouts, web composition, hierarchy, visual systems |
| Color / palette inspiration | Pinterest, Behance, Dribbble, Coolors, Adobe Color | palettes, seasonal color systems, contrast, gradients, accent ratios |
| Web / product UI | Mobbin, Land-book, Awwwards | SaaS pages, mobile UI, landing pages, product interaction visuals |

### Source Quality Rule

The site routing table is a quality constraint, not a loose suggestion. For primary and secondary references, search the preferred design/reference sites first and keep them as the main evidence even when their images are harder to extract.

- Do not use template/material marketplaces such as Nipic / 昵图网, Tusij / 图司机, Qianku / 千库, 588ku / 千图, Pngtree, Canva templates, or BrandCrowd as main references just because their thumbnails are easy to download.
- These template/material sites may be used only as low-priority supplements, anti-pattern examples, or when the user explicitly asks for Chinese template-market references.
- If Behance, Dribbble, Pinterest, Awwwards, Land-book, Mobbin, Fonts In Use, Typewolf, Unsplash, or Pexels do not expose stable image URLs via static HTML, leave that reference's `image` empty. Do not screenshot it and do not replace it with an unrelated easier-to-scrape source.
- In HTML reports, source quality outranks image-extraction convenience. A report that passes image audit but is mostly template-market references is not acceptable.

### Keyword Categories

Use all of these category labels every time:

- `Logo / 标志`: symbols, marks, wordmarks, badges, negative space, identity systems.
- `Poster / 海报`: key visuals, campaign posters, title hierarchy, festival posters.
- `Typography / 标题字`: Chinese lettering, font pairing, headline forms, real typography usage.
- `Texture / 纹理材质`: paper, plants, food, fabric, water, grain, print, handmade textures.
- `Wallpaper / 背景壁纸`: photographic backgrounds, abstract backgrounds, scenery, atmosphere.
- `Layout / 版式构图`: grid, hierarchy, whitespace, poster systems, movement, landing page layouts.
- `Color / 配色灵感`: palettes, seasonal color systems, contrast relationships, gradients, accent ratios.
- `Illustration / 插画图形`: subject illustration, symbols, pattern language, characters, scenes.
- `Web / 产品界面`: SaaS, apps, websites, landing pages, dashboards, mobile screens.

## Step 3: Search And Link Images

Browse immediately for every standard category. Prefer primary visual sources and reputable image pages. Prioritize the category's preferred sites.

Use these reference-count targets:

- `primary`: find 5-6 strong references.
- `secondary`: find 2-3 useful references.
- `wildcard`: find at least 1 useful reference.

When the user explicitly names an artifact type, that matching category must be `primary`. For example, if the user asks for a poster, `Poster / 海报` should receive deeper coverage than the other categories.

For each reference include:

- Linked title.
- Image direct link when stable and available; otherwise the project/image page link.
- Source site.
- Quality tier: `green`, `yellow`, or `red`.
- Source quality: `primary`, `secondary`, or `supplement`.
- Copyright risk: `low`, `medium`, or `high`.
- Borrowable parts: composition, typography, color, motif, material, UI pattern, photographic treatment, etc.
- What to borrow: composition, typography, color, motif, material, UI pattern, etc.
- What not to copy: exact artwork, trademark-like mark, proprietary layout, licensed photo, cliche element.

If a site does not expose stable direct image links, page links are acceptable. Explain why the page is still useful.

### Reference Quality Tiers

Use quality tiers as a design decision list, not a moral judgment on the source:

- 🟢 `green`: safe to borrow abstract design logic such as composition, color relationships, material treatment, spacing, hierarchy, or interaction pattern.
- 🟡 `yellow`: useful but needs transformation. Examples: strong art direction, recognizable commercial campaign, distinctive custom lettering, branded photography, or a reference whose source is relevant but image extraction is weak.
- 🔴 `red`: anti-pattern or high-risk reference. Examples: template-market work, obvious IP, trademark-like logos, copied mascot styles, generic stock layouts, or overused festival tropes. Include only when it helps explain what to avoid.

Primary and secondary final references should mostly be green/yellow. Red references should be rare and framed as warnings.

## Step 4: Aesthetic Deconstruction

Do not say only "looks good." Translate references into designer-operable language:

- Composition: centered, diagonal, radial, grid, whitespace, full-bleed, close crop, movement.
- Type: sans, serif, handwritten, condensed, decorative, cut strokes, custom lettering.
- Color: primary/secondary palette, contrast, value, how to avoid cliche colors.
- Color inspiration: dominant/accent ratio, seasonal color alternatives, contrast mood, gradient logic.
- Motifs: symbols, geometry, illustration language, repeated patterns.
- Texture: paper, grain, plant, food, water, light, print, photography texture.
- Mood: premium, warm, festive, cultural, modern, experimental, cute, commercial.
- Application: what can inspire the logo, title, background, layout, main visual, UI, or system.

## Step 5: Actionable Directions

Output 3-5 directions. Each direction must include:

- Direction name.
- Best use case.
- Visual keywords.
- Reference basis: which reference patterns inspired it.
- Composition advice.
- Type or lettering advice.
- Color advice.
- Graphic/texture advice.
- Today's execution steps, ideally 1-5 concrete steps.

## Step 6: AI Image Prompts By Artifact Type

First identify the artifact type. Prompt behavior must match it.

### Posters / Covers / Key Visuals

Give two prompts for each direction:

- `带版式参考的完整画面提示词`: Include poster design, typographic layout, title hierarchy, subtitle/date/brand information zones, and placeholder headline blocks if reliable text rendering is uncertain.
- `无文字底图提示词`: Generate a clean background or visual base with intentional blank space for the designer to set real type later.

### Logos / Marks

Prompt for a logo, not a scene:

- Use `simple vector logo`, `symbol mark`, `wordmark`, `badge`, `flat color`, `scalable icon`.
- Avoid mockups, realistic scenes, detailed backgrounds, mascots unless requested.

### Title Lettering / Typography

Prompt for lettering style references:

- Use `custom lettering`, `typography design`, `bold headline characters`, `type specimen`.
- For Chinese text, treat AI output as form exploration; recommend manual correction or real type-setting for final characters.

### Textures / Wallpapers / Scenery / Photography

Prompt for non-layout assets:

- Use `no text`, `no poster layout`, `no typography`, `clean background`, `seamless texture`, `wallpaper`, or `photography`.
- Do not ask for title hierarchy or information blocks.

Always include a negative prompt to remove gibberish text, low quality, watermarks, wrong artifact type, cheap templates, and copyrighted characters.

## Optional Step 7: HTML Report

Create an HTML report only when the user explicitly asks for HTML, a report file, polished deliverable, shareable file, or visual research pack as a file. In that case, the HTML report is the primary deliverable: the chat reply should briefly summarize and link the generated HTML/JSON instead of duplicating the full report content.

### Runtime Decision

Choose the fastest reliable path automatically. Do not ask the user to choose an implementation tool.

1. For ordinary chat research: do not run scripts.
2. Keep the Python scripts. They are good for token-free mechanical work when a real Python runtime is available, especially source-image extraction, audits, and deterministic report rendering.
3. For HTML on Windows when `python` is missing or is the Microsoft Store placeholder: use the PowerShell screenshot path. It is the most convenient path for visual-complete reports:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\prepare_report_images.ps1 research.raw.json research.json -AssetsDir report-assets -ImageMode screenshot
powershell -ExecutionPolicy Bypass -File scripts\build_report.ps1 research.json design-inspiration-report.html
```

4. For HTML when Python is available and source-image fidelity matters more than visual completeness: use the Python extraction path below.
5. Avoid installing Playwright browsers during a user task. If Playwright's bundled Chromium is missing but Chrome/Edge exists, prefer Chrome/Edge screenshot fallback instead of asking the user to run `npx playwright install`.

Default preference: use Python when it is already available and works; otherwise use the PowerShell fallback without mentioning the tool choice unless there is a failure. The user experience should be "I asked for HTML and got HTML", not "I had to choose Python vs PowerShell".

1. Complete Steps 1-6 first.
2. Save the research pack as a raw JSON file using the fields below.
3. Prepare local report images from each reference's own page. Choose the image strategy before running the script:

- Use `--image-mode extract` by default when source fidelity matters most. This tries same-page metadata/images and leaves missing images empty.
- Use `--image-mode hybrid` when the user wants an HTML report with fewer empty cards. This tries source images first, keeps a remote preview candidate, then screenshots only missing cards.
- Use `--image-mode screenshot` when the user cares more about fast visual preview coverage than original image extraction. This captures each reference page as a local screenshot thumbnail and is the closest practical way to make every reachable reference card visual.

```bash
python3 scripts/prepare_report_images.py /path/to/research.raw.json /path/to/research.json --assets-dir /path/to/report-assets --image-mode extract --timeout 8 --max-candidates 4
```

For visual-complete HTML reports:

```bash
python3 scripts/prepare_report_images.py /path/to/research.raw.json /path/to/research.json --assets-dir /path/to/report-assets --image-mode screenshot --screenshot-timeout 18
```

4. Audit the prepared JSON before rendering. Missing images are allowed because source quality outranks thumbnail availability:

```bash
python3 scripts/audit_report_images.py /path/to/research.json --min-ratio 0 --fail-on-duplicates
```

5. Audit research quality before rendering:

```bash
python3 scripts/audit_research_quality.py /path/to/research.json
```

6. Render the HTML only after audits pass:

```bash
python3 scripts/build_report.py /path/to/research.json /path/to/design-inspiration-report.html
```

Use the current skill directory as the working directory, or call scripts by absolute path. The scripts use only Python standard library modules.

### JSON Fields For The Renderer

Keep the JSON concise but structured:

- `title`: report title.
- `subtitle`: one-line report context.
- `brief`: object with `artifact_type`, `use_context`, `audience_tone`, `core_symbols`, and `visual_risks`.
- `assumptions`: optional list of assumptions.
- `keywords`: list of objects with `category`, `priority`, `zh`, `en`, and `site`.
- `references`: list of objects with `category`, `title`, optional `title_zh`, `url`, `image`, `source`, `source_quality`, `quality_tier`, `copyright_risk`, `borrowable_parts`, `borrow`, and `avoid`. For Chinese reports, `title_zh`, `borrowable_parts`, `borrow`, and `avoid` should be Chinese-first while `title` preserves the original source title.
- `deconstruction`: object with `composition`, `type`, `color`, `motifs`, `texture`, `mood`, and `application`.
- `directions`: list of objects with `name`, `best_use_case`, `visual_keywords`, `reference_basis`, `composition_advice`, `type_advice`, `color_advice`, `graphic_texture_advice`, and `execution_steps`.
- `prompts`: list of objects with `direction`, `artifact_type`, `prompt`, and `negative_prompt`.
- `copyright_notes`: list of usage and copyright cautions.
- `next_prompt`: optional next-step prompt for continuing the design work.

For HTML reports, image quality is part of the deliverable, but source relevance comes first:

- Prefer references whose own page exposes a usable thumbnail or stable direct image URL.
- `image` must be from the same reference page, from metadata on that page, or a local file downloaded from that page by `prepare_report_images.py`.
- If localizing a candidate fails, `prepare_report_images.py` may keep `_preview_image`; `build_report.py` can display it as a labeled remote preview. Treat it as a preview only, not a downloaded asset.
- If a preferred high-quality reference does not expose a usable image, leave `image` empty and keep the reference if its design value is strong.
- Do not claim screenshot thumbnails are original images. Label them as page previews when discussing the report.
- Use screenshots when the user explicitly values visual completeness in HTML, such as "HTML 里都要有图", "不要 no link", "快速预览", or "截图兜底".
- Do not use unrelated websites, generic search-result thumbnails, or random replacement images to fill missing cards.
- Do not reuse the same image across multiple references unless the duplicate is intentional and explained.
- If `audit_report_images.py --fail-on-duplicates` fails, fix the duplicate image assignments before rendering HTML.
- When `prepare_report_images.py` cannot localize an image, it writes `_image_status` and `_image_error`. Keep those fields. `build_report.py` will show a useful no-image card with an "open original page" link instead of a dead blank card.

### Image Extraction Reality Check

Behance, Dribbble, Unsplash, and Pexels often change markup, lazy-load images, proxy assets, or block simple static fetching. The default policy is:

1. Keep the high-quality reference page URL.
2. For source-fidelity reports, try same-page `og:image`, `twitter:image`, `<img>`, and direct image candidates via `prepare_report_images.py --image-mode extract`.
3. If a candidate cannot be downloaded locally, keep `_preview_image` so the HTML can try a remote preview without blocking the report.
4. For visual-complete reports, use `--image-mode screenshot` to capture a page preview for each reachable source page. This avoids empty cards, but the thumbnail is a screenshot of the source page, not the source artwork file.
5. If neither extraction, remote preview, nor screenshot works because the page is blocked, private, or unreachable, keep the source link and show the no-image card with the failure reason.
6. Do not replace missing cards with unrelated thumbnails.

Prefer improving the reference set over forcing image extraction. If an HTML report has too many no-image cards, replace some references with high-quality sources that expose metadata images, such as Unsplash/Pexels photo pages or Behance/Dribbble pages with stable preview metadata. Keep at least a few high-value no-image references when their design value is stronger than easier thumbnails.

## Default Output Structure

Use this structure by default:

```markdown
## 第一步：需求分析

## 第二步：各品类搜索关键词

## 第三步：联网搜图与图片链接

## 第四步：参考图审美拆解

## 第五步：3-5 个今天能上手的设计方向

## 第六步：AI 生图提示词

## 版权与避坑提醒

## 下一步提示词
```

For file deliverables, create the JSON and HTML in the user's requested output folder. If no folder is specified, use the current workspace's `outputs/` directory when available.

Keep the result useful rather than exhaustive. The goal is to reduce the designer's browser-tab chaos and help them begin work immediately.
