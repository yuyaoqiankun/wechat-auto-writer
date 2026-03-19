# Writing System

## What this skill is now

This skill is no longer just a draft uploader. It is a complete公众号文章生产流水线 with five layers:

1. **Content generation layer**
   - `scripts/write_article.py`
   - `scripts/wechat_metadata.py`
2. **Theme / layout layer**
   - `themes/<category>/<name>.yaml`
   - `scripts/format_article.py`
3. **HTML rendering layer**
   - Markdown → WeChat-compatible HTML
4. **Image generation and replacement layer**
   - `scripts/generate_image.py`
   - `scripts/add_article_images.py`
   - local image → WeChat material URL replacement
5. **Draft publishing layer**
   - `scripts/publish_draft.py`
   - `scripts/wechat_capability.py`

## Source of truth

- **Markdown is the source of truth** for article content.
- HTML is a generated artifact.
- The draft box is the publishing target, not the source of truth.

## Workflow logic

The typical workflow is:

1. Generate Markdown article
2. Extract metadata (publish title + digest)
3. Plan body image placement
4. Generate one cover image and one body image by default
5. Compress images
6. Convert Markdown into themed WeChat HTML
7. Upload body images to WeChat and replace local paths
8. Upload cover and create draft
9. Read draft back for validation

## Current defaults

- Default body image count: **1**
- Default output structure: `output/YYYY-MM-DD/HHMMSS-topic-slug/`
- Theme system: structured schema imported from the reference project
- Publishing target: **draft box only**

## Design decisions

### Why Markdown first

Markdown keeps the article editable, portable, and easy to inspect. It also makes batch and manual correction easier than editing only inside the WeChat editor.

### Why one body image by default

This is an intentional simplification. The current priority is image usability and visual consistency, not image quantity.

### Why structured themes

Themes now use a structured schema (`colors`, `styles`, dict-style values) because that is more maintainable and closer to a real公众号排版系统 than raw CSS-string themes.

## What this system does well now

- Stable Markdown → HTML conversion
- Stable WeChat draft upload
- Stable body image replacement with WeChat URLs
- Theme-driven rendering with 21 built-in themes
- Per-run archival output folders

## What is intentionally not optimized yet

- smart image-count decisions
- batch self-healing
- fully automatic article/benchmark style extraction UI
- multi-account publishing orchestration

Those can be added later if they become frequent needs.
