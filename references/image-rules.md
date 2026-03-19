# Image Rules

## Current standard (V1)

This project now uses **LLM-driven visual planning** plus deterministic guardrails.

### Defaults

- Cover images: enabled
- Body images: **1 by default**
- Visual tone: **light illustration** (clean, modern, premium)

## Prompt generation policy

Prompting is no longer a plain direct template feed.

The pipeline now supports two strategies:

- `full` (default): title + content snippet analysis for stronger semantic coverage
- `lite`: title + first-paragraph truncation only for token savings

Both strategies output:

- 1 cover prompt
- 1 body illustration prompt

Image model renders from those prompts.
If LLM prompt stage fails, fallback to template prompts.

## Visual strategy card (required structure)

- target_reader
- core_emotions
- visual_narrative
- keywords
- banned_elements

## Cover image requirements

- Horizontal cover logic aligned with WeChat usage
- Composition with safe whitespace (avoid crowded center)
- No visible text or watermark
- Clear subject and visual hierarchy
- High-definition detail and clean edges

### Size handling

- Prefer generating larger horizontal canvas first (e.g., 1.8:1 family)
- Normalize/compress to publish target (900x500 in current pipeline)

## Body image requirements (V1)

- Exactly 1 body image by default
- Must align with core paragraph topic
- Same visual family as cover, but scene variation allowed
- Should support reading rhythm (not overly flashy)

## Unified negative words (current)

```text
文字，水印，logo，低清，模糊，畸形手指，多余肢体，杂乱背景，过度锐化
```

## Not in V1 yet

- Dynamic image count (1~3) by article structure
- Multiple style presets (editorial/cinematic/etc.)
- Content-type adaptive visual direction routing
