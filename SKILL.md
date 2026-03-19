---
name: wechat-article-writer
description: Generate, format, illustrate, and publish WeChat Official Account articles into the draft box using a multi-step workflow. Use when the user wants to read benchmark articles, imitate a target account style, write a public-account article around a given topic, generate cover/body images, choose a visual layout theme, convert Markdown to WeChat-compatible HTML, and push the result into a微信公众号草稿箱. Also use when the user asks for公众号写稿、公众号排版、公众号草稿箱发布、参考对标文章风格发文、自动配图、微信公众号内容自动化.
---

# WeChat Article Writer

Execute the workflow in fixed order. Do not skip steps unless the user explicitly asks for a partial run.

## Workflow

1. Read source material and benchmark articles.
2. Extract writing style, audience, structure, title habits, and CTA patterns.
3. Generate article draft in Markdown.
4. Generate a cover image and optional body images.
5. Compress and normalize images to WeChat-safe dimensions and size.
6. Choose a layout theme.
7. Convert Markdown to WeChat-compatible HTML.
8. Push article to WeChat Official Account draft box.
9. Return a concise report with title, theme, images used, and draft result.

## Required inputs

Collect or infer these inputs before running end-to-end:

- topic
- target style or benchmark source
- account positioning / audience if available
- whether cover image is required
- whether body images are required
- desired tone (e.g. 干货 / 情感 / 资讯 / 活泼)
- layout theme (e.g. `shuimo/default`, `wenyan/default`, `macaron/blue`)
- publish target: draft box only

If a required credential/config is missing, stop and report exactly what is missing.

## Strict execution rules

- Keep intermediate artifacts under this skill folder.
- Prefer deterministic script calls over freehand regeneration.
- Keep the final article editable; Markdown is the source of truth.
- Never publish directly; only push to 草稿箱 unless the user explicitly asks otherwise and the script supports it.
- Before draft upload, run the preflight checks from `references/wechat-publish-checklist.md`.
- If the user requests “参考对标文章”, first summarize benchmark style in 5-10 bullets before writing.
- If the user requests a visual style like “暖色风” or “水墨风”, map it to a concrete theme file instead of improvising CSS inline.

## LLM provider design

`write_article.py` must stay provider-pluggable.

- Prompt construction should remain provider-agnostic.
- Provider-specific HTTP logic should stay isolated in provider classes.
- Current supported modes:
  - `mock`
  - `openai_compatible`
- Prefer candidate-based config keys below:
  - `llm_candidates`
  - `image_candidates`

Read `references/model-providers.md` before extending provider support.

## WeChat-specific quality bar

Always enforce these constraints before upload:

- Title should be concise, concrete, and not excessively clickbait.
- Lead paragraph must explain value within 2-3 sentences.
- Paragraphs should stay short; avoid huge walls of text.
- Use `##` sections for body structure.
- Lists should remain readable after HTML conversion.
- Preserve image alt/caption intent where possible.
- Avoid raw Markdown constructs that convert poorly in WeChat editor.
- Ensure local images are uploaded to WeChat material library and remote links are not left dangling.
- Check cover ratio, body image width, and file size constraints.
- Check common compliance risks: exaggerated claims, medical/finance promises, copyright/source attribution, aggressive external diversion.

## Files

- `config.json`: secrets and app config
- `scripts/write_article.py`: draft generation with pluggable LLM providers
- `scripts/wechat_metadata.py`: publish title + digest extraction
- `scripts/generate_image.py`: cover/body image generation
- `scripts/add_article_images.py`: body image planning and placeholder insertion
- `scripts/compress_image.py`: image normalization/compression
- `scripts/format_article.py`: Markdown → themed WeChat HTML
- `scripts/wechat_capability.py`: unified WeChat API capability layer
- `scripts/publish_draft.py`: upload materials + create draft
- `scripts/run_workflow.py`: one-command orchestrator for the main pipeline
- `themes/`: YAML theme definitions
- `references/writing-system.md`: pipeline architecture and writing system explanation
- `references/themes.md`: built-in theme guide
- `references/image-rules.md`: current cover/body image rules
- `references/output-structure.md`: archival output structure and file meanings
- `references/configuration.md`: config key explanations
- `references/wechat-style-rules.md`: WeChat style and publishing details
- `references/wechat-publish-checklist.md`: final checks before draft upload
- `references/model-providers.md`: provider contract and config
- `references/image-pipeline.md`: cover/body image handling and upload flow
- `references/orchestrator.md`: one-command workflow usage
- `references/test-plan.md`: smoke/integration test checklist

## Suggested command sequence

Run scripts in this order, or use the orchestrator:

```bash
python scripts/write_article.py ...
python scripts/generate_image.py ...
python scripts/add_article_images.py ...
python scripts/compress_image.py ...
python scripts/format_article.py --theme macaron/blue --upload-images ...
python scripts/publish_draft.py ...

# or
python scripts/run_workflow.py "主题" --theme macaron/blue ...
```

## Config contract

Read `config.json` as JSON. Expected keys:

- `llm_candidates`
- `image_candidates`
- `appid`
- `appsecret`
- optional: `author`, `digest`, `content_source_url`, `thumb_crop`, `default_output_dir`

## Benchmark-article mode

When benchmark links or copied article text are provided:

1. Read them first.
2. Extract:
   - title pattern
   - opening pattern
   - section rhythm
   - sentence density
   - emotional temperature
   - ending CTA style
3. Use those findings to steer writing, but do not plagiarize.
4. Keep facts fresh and adapt examples to the requested topic.

## Theme selection

Theme selection is file-driven.

- Lifestyle / growth / mass friendly → `macaron/blue`, `macaron/cream`, `macaron/mint`
- Humanities / essay / literary → `wenyan/default`, `wenyan/lapis`, `wenyan/purple`
- Chinese-style / restrained / calm → `shuimo/default`

If no theme is specified in the workflow, use the current script default.

## Failure handling

If a step fails:

- report the exact failing step
- keep prior artifacts on disk
- propose the smallest retry step instead of restarting the whole workflow

## References

Read these when needed:

- `references/wechat-style-rules.md`
- `references/wechat-publish-checklist.md`
- `references/themes.md`
- `references/model-providers.md`
- `references/image-pipeline.md`
