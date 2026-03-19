# Image Pipeline

## V1 pipeline (current)

The image workflow now supports **switchable prompt strategies**:

- `full` strategy: title + content snippet analysis (semantic coverage first)
- `lite` strategy: title + truncated first paragraph only (token-saving first)

Both strategies still keep:

1. Ask LLM to generate a visual strategy + image prompts
2. Feed prompts into the image model
3. Compress and normalize output sizes
4. Upload body images to WeChat (when enabled)

## Cover image flow

- Input: article title + full content summary context
- LLM output: `cover_prompt` with composition, color, lighting, style, quality, ratio, negatives
- Image generation target: horizontal cover (generate large first, normalize to 900x500 downstream)
- WeChat publish uses uploaded cover `thumb_media_id`

## Body image flow (V1)

- V1 keeps body-image count fixed at **1**
- `add_article_images.py` still inserts markdown placeholder and plan metadata
- `generate_image.py` asks LLM for one body prompt
  - `full`: based on title + content snippet + section context
  - `lite`: based on title + first-paragraph truncation (fast mode)
- Final body image path is rewritten into markdown/html flow as before

## Prompt source + fallback

`generate_image.py` returns:

- `prompt_source = "llm" | "template"`
- `prompt_strategy = "full" | "lite"`
- `prompt_llm_meta` for model response/debug context
- `visual_strategy_card` for explainability

If LLM prompt generation fails or JSON parse fails, code falls back to template prompts so pipeline remains available.

## Markdown → WeChat HTML image handling

`format_article.py --upload-images` will:

- detect local markdown image paths
- upload with `material/add_news_image`
- replace local paths with WeChat CDN URLs

## Execution sequence

1. `write_article.py`
2. `add_article_images.py`
3. `generate_image.py` (LLM strategy + prompt generation)
4. `compress_image.py`
5. `format_article.py --upload-images` (optional)
6. `publish_draft.py` (optional)
7. `run_workflow.py`
