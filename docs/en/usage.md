# Usage

## One-command workflow

```bash
python scripts/run_workflow.py "Spring Wellness" \
  --style practical \
  --theme shuimo/default \
  --publish-draft
```

## Common flags

- `--style`
- `--theme`
- `--publish-draft`
- `--max-body-images` (current default: 1)
- `--provider`
- `--model`
- `--output-dir`
- `--flat-output`
- `--image-prompt-strategy` (`full` / `lite`)
- `--image-prompt-lite-chars` (first-paragraph truncation length, `lite` only)
- `--image-style` (image visual style override, higher priority than config)
- `--image-style-preset` (`pro-1` / `pro-2` / `pro-3`, non-narrative content-focused presets)

## Prompt strategy switching

### Default (semantic coverage first)

```bash
python scripts/run_workflow.py "Spring Wellness" \
  --style practical \
  --theme shuimo/default \
  --image-prompt-strategy full
```

- `full`: uses title + content snippet for better semantic alignment.

### Lite (token-saving first)

```bash
python scripts/run_workflow.py "Spring Wellness" \
  --style practical \
  --theme shuimo/default \
  --image-prompt-strategy lite \
  --image-prompt-lite-chars 220
```

- `lite`: only reads title + truncated first paragraph, generates 1 cover + 1 body prompt.
- `--image-prompt-lite-chars`: controls first-paragraph truncation length (recommended 180~320).

## Step-by-step execution

```bash
python scripts/write_article.py ...
python scripts/generate_image.py ...
python scripts/add_article_images.py ...
python scripts/compress_image.py ...
python scripts/format_article.py --theme shuimo/default --upload-images ...
python scripts/publish_draft.py ...
```

## Recommended operator practice

- Prefer `run_workflow.py` for normal use
- Use individual scripts mainly for troubleshooting or partial retries
- Treat single-article workflow as the primary scenario
