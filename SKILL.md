---
name: design-inspiration-research
description: Turn a design brief into a sourced inspiration research pack for designers, with an optional single-file HTML report only when requested. Use when the user asks for inspiration, references, moodboards, keywords, visual directions, poster/logo/cover/typography/packaging/UI reference research, HTML research reports, or AI image prompts for a design task such as a festival poster, brand logo, title lettering, wallpaper, texture, landing page, app UI, or campaign key visual.
---

# Design Inspiration Research

Use this skill as a design research assistant and visual design director. Convert one fuzzy design need into a compact, actionable research pack: brief analysis, category-specific search keywords, live visual references with links, aesthetic analysis, 3-5 directions, and AI image prompts matched to the requested artifact type. Default output is the normal chat research pack. When the user explicitly asks for HTML, a report file, or a shareable deliverable, generate the structured JSON file plus a single-file HTML report with `scripts/build_report.py` and keep the chat response to a concise file handoff.

## Core Workflow

Always follow this sequence unless the user explicitly asks for a narrower output:

1. Analyze the design need.
2. List search keywords for every standard category.
3. Search every standard category immediately and link images or image/project pages.
4. Deconstruct the references aesthetically.
5. Summarize 3-5 directions the designer can start today.
6. Write AI image prompts matched to the artifact type.
7. If the user explicitly asks for HTML, a report file, or a shareable deliverable, build a JSON research file and render it to HTML with `scripts/build_report.py`; in chat, link the generated report instead of repeating the full research pack.

If the user says not to browse, skip step 3 and make that limitation explicit.

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
- What to borrow: composition, typography, color, motif, material, UI pattern, etc.
- What not to copy: exact artwork, trademark-like mark, proprietary layout, licensed photo, cliche element.

If a site does not expose stable direct image links, page links are acceptable. Explain why the page is still useful.

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

1. Complete Steps 1-6 first.
2. Save the research pack as a raw JSON file using the fields below.
3. Prepare local report images from each reference's own page:

```bash
python3 scripts/prepare_report_images.py /path/to/research.raw.json /path/to/research.json --assets-dir /path/to/report-assets
```

4. Audit the prepared JSON before rendering:

```bash
python3 scripts/audit_report_images.py /path/to/research.json --min-ratio 0 --fail-on-duplicates
```

5. Render the HTML only after the image audit passes:

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
- `references`: list of objects with `category`, `title`, `url`, `image`, `source`, `borrow`, and `avoid`.
- `deconstruction`: object with `composition`, `type`, `color`, `motifs`, `texture`, `mood`, and `application`.
- `directions`: list of objects with `name`, `best_use_case`, `visual_keywords`, `reference_basis`, `composition_advice`, `type_advice`, `color_advice`, `graphic_texture_advice`, and `execution_steps`.
- `prompts`: list of objects with `direction`, `artifact_type`, `prompt`, and `negative_prompt`.
- `copyright_notes`: list of usage and copyright cautions.
- `next_prompt`: optional next-step prompt for continuing the design work.

For HTML reports, image quality is part of the deliverable, but source relevance comes first:

- Prefer references whose own page exposes a usable thumbnail or stable direct image URL.
- `image` must be from the same reference page, from metadata on that page, or a local file downloaded from that page by `prepare_report_images.py`.
- If a preferred high-quality reference does not expose a usable image, leave `image` empty and keep the reference if its design value is strong.
- Do not screenshot pages for missing images.
- Do not use unrelated websites, generic search-result thumbnails, or random replacement images to fill missing cards.
- Do not reuse the same image across multiple references unless the duplicate is intentional and explained.
- If `audit_report_images.py --fail-on-duplicates` fails, fix the duplicate image assignments before rendering HTML.

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
