# Design Inspiration Research

A Codex skill that turns a loose design brief into a sourced inspiration research pack for designers.

It is built for moments like:

- "I want to make a Mid-Autumn Festival poster."
- "I need an abstract leopard logo for an event management system."
- "Help me gather references for a Father's Day campaign visual."

The skill analyzes the brief, generates categorized search keywords, searches visual reference sites, links usable references, deconstructs the visual language, and outputs practical directions plus AI image prompts.

## What It Does

- Analyzes the design need, audience, tone, symbols, and visual risks.
- Generates search keywords across every standard reference category.
- Searches across design, typography, photography, UI, and palette sources.
- Organizes references by type instead of dumping links.
- Deconstructs references into composition, typography, color, texture, motif, and mood.
- Provides 3-5 directions a designer can start from immediately.
- Writes AI image prompts matched to the artifact type.

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
- `index.html`: simple project introduction page.

## License

MIT License. You can use, copy, modify, and share this skill as long as the license notice is preserved.

