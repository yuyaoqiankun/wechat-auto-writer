# Runbook

## Full workflow

```bash
cd skills/wechat-article-writer
/root/.agent-reach/venv/bin/python scripts/run_workflow.py "主题" \
  --style 干货 \
  --theme shuimo/default \
  --provider openai_compatible \
  --upload-images \
  --publish-draft
```

## Notes

- Use `/root/.agent-reach/venv/bin/python` because Pillow and related deps are available there.
- If image upload fails with `40164`, re-check the公众号 IP whitelist.

## DashScope fallback config (recommended)

If your primary image endpoint is unstable, keep DashScope as candidate #2:

```json
{
  "image_candidates": [
    {
      "enabled": true,
      "provider": "openai_compatible_images",
      "base_url": "https://primary-image.example.com/v1",
      "api_key": "sk-primary",
      "model": "grok-imagine-1.0",
      "retries": 1
    },
    {
      "enabled": true,
      "provider": "dashscope_image",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "api_key": "sk-dashscope",
      "model": "qwen-image-2.0-pro",
      "retries": 1
    }
  ]
}
```

DashScope note:
- `dashscope_image` must use `.../api/v1` base URL.
- Do not use `.../compatible-mode/v1` for this provider.

## Common image errors

- `502 Bad Gateway` (primary image provider): keep fallback enabled and retry.
- `404 Not Found` (DashScope): check whether base URL is mistakenly set to `compatible-mode`.
- `429 RateQuota`: reduce request pressure and retry later.

## Prompt strategy switch (full vs lite)

### Full strategy (default)

```bash
/root/.agent-reach/venv/bin/python scripts/run_workflow.py "主题" \
  --style 干货 \
  --image-style 轻插画 \
  --theme shuimo/default \
  --image-prompt-strategy full
```

- Uses title + content snippet for prompt generation.
- Better semantic coverage for long or complex articles.

### Lite strategy (token-saving)

```bash
/root/.agent-reach/venv/bin/python scripts/run_workflow.py "主题" \
  --style 干货 \
  --image-style 极简 \
  --theme shuimo/default \
  --image-prompt-strategy lite \
  --image-prompt-lite-chars 220
```

- Uses title + truncated first paragraph only.
- Generates one cover prompt + one body prompt.
- Useful for fast drafts and token-sensitive workflows.

## Style presets (non-narrative, content-focused)

You can quickly pick one of the built-in presets:

- `pro-1`: 编辑感概念插画，细节丰富，信息表达清晰，分层构图，专业高级，非叙事
- `pro-2`: 商业杂志视觉风，高级配色与材质细节，克制光影，主体明确，非叙事
- `pro-3`: 科技视觉风，空间层次与结构感强，精致光影，丰富但不花哨，非信息图

Example:

```bash
/root/.agent-reach/venv/bin/python scripts/run_workflow.py "主题" \
  --style 干货 \
  --image-style-preset pro-1 \
  --image-prompt-strategy full
```

## Run without publish/upload

```bash
/root/.agent-reach/venv/bin/python scripts/run_workflow.py "主题" \
  --style 干货 \
  --theme shuimo/default \
  --provider openai_compatible
```

This runs real article + image generation + compression + HTML formatting, but does not upload images or publish draft.
