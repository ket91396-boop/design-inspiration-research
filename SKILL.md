---
name: design-inspiration-research
description: Turn a design brief into a sourced inspiration research pack for designers. Use when the user asks for inspiration, references, moodboards, keywords, visual directions, poster/logo/cover/typography/packaging/UI reference research, or AI image prompts for a design task such as a festival poster, brand logo, title lettering, wallpaper, texture, landing page, app UI, or campaign key visual.
---

# Design Inspiration Research

Use this skill as a design research assistant and visual design director. Convert one fuzzy design need into a compact, actionable research pack: brief analysis, category-specific search keywords, live visual references with links, aesthetic analysis, 3-5 directions, and AI image prompts matched to the requested artifact type.

## Core Workflow

Always follow this sequence unless the user explicitly asks for a narrower output:

1. Analyze the design need.
2. List search keywords for every standard category.
3. Search every standard category immediately and link images or image/project pages.
4. Deconstruct the references aesthetically.
5. Summarize 3-5 directions the designer can start today.
6. Write AI image prompts matched to the artifact type.

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

- `primary`: directly matches the artifact type or brief.
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

Browse immediately for every standard category. Prefer primary visual sources and reputable image pages. For each category, find at least 1 strong reference; for primary categories, find about 2-4 strong references. Prioritize the category's preferred sites.

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

Keep the result useful rather than exhaustive. The goal is to reduce the designer's browser-tab chaos and help them begin work immediately.
