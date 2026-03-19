# Model Providers

This skill uses **candidate-based fallback** for both text and image generation.

## 1) LLM providers (`write_article.py`)

Current supported values in `llm_candidates[*].provider`:

- `openai_compatible`
- `mock`

Each candidate item:

```json
{
  "enabled": true,
  "provider": "openai_compatible",
  "base_url": "https://api.example.com/v1",
  "api_key": "sk-xxx",
  "model": "gpt-5.4",
  "retries": 2,
  "timeout": 180
}
```

## 2) Image providers (`generate_image.py`)

Current supported values in `image_candidates[*].provider`:

- `openai_compatible_images`
- `dashscope_image`
- `mock`

Each candidate item:

```json
{
  "enabled": true,
  "provider": "dashscope_image",
  "base_url": "https://dashscope.aliyuncs.com/api/v1",
  "api_key": "sk-xxx",
  "model": "qwen-image-2.0-pro",
  "retries": 1
}
```

## DashScope-specific notes

- `dashscope_image` uses the official multimodal endpoint path:
  - `/services/aigc/multimodal-generation/generation`
- `base_url` should be region API root (for example):
  - China: `https://dashscope.aliyuncs.com/api/v1`
  - Singapore: `https://dashscope-intl.aliyuncs.com/api/v1`
- Do **not** use `.../compatible-mode/v1` for `dashscope_image`.

## Fallback behavior

- Candidates are tried in order.
- `enabled: false` candidates are skipped.
- If all candidates fail, the step returns the full chained error.
