# Configuration

Main config file:

```bash
config.json
```

## Core keys

### LLM (new mode only)

- `llm_candidates` (required)
  - ordered candidate list for cross-provider fallback
  - each item supports:
    - `enabled` (bool)
    - `provider` (`openai_compatible` | `mock`)
    - `base_url`
    - `api_key`
    - `model`
    - `retries`
    - `timeout`

### Image generation (new mode only)

- `image_candidates` (required)
  - ordered candidate list for cross-provider fallback
  - each item supports:
    - `enabled` (bool)
    - `provider` (`openai_compatible_images` | `dashscope_image` | `mock`)
    - `base_url`
    - `api_key`
    - `model`
    - `retries`

- `image_prompt_strategy` (`full` | `lite`)
- `image_prompt_lite_content_chars` (used in `lite` strategy)
- `image_style` (default visual style, overridable by `--image-style`)

### WeChat Official Account

- `appid`
- `appsecret`

### Optional article defaults

- `author`
- `digest`
- `content_source_url`
- `thumb_crop`
- `default_output_dir`

## Blank fallback examples

```json
{
  "llm_candidates": [
    {
      "enabled": true,
      "provider": "openai_compatible",
      "base_url": "https://primary-llm.example.com/v1",
      "api_key": "sk-primary",
      "model": "gpt-5.4",
      "retries": 2,
      "timeout": 180
    },
    {
      "enabled": false,
      "provider": "openai_compatible",
      "base_url": "",
      "api_key": "",
      "model": "",
      "retries": 2,
      "timeout": 180
    }
  ],
  "image_candidates": [
    {
      "enabled": true,
      "provider": "openai_compatible_images",
      "base_url": "https://primary-image.example.com/v1",
      "api_key": "sk-primary-image",
      "model": "grok-imagine-1.0",
      "retries": 1
    },
    {
      "enabled": false,
      "provider": "openai_compatible_images",
      "base_url": "",
      "api_key": "",
      "model": "",
      "retries": 1
    }
  ]
}
```

## Provider notes

### `openai_compatible_images`

- Expects OpenAI Images-compatible endpoint behavior (e.g. `/images/generations`).

### `dashscope_image`

- Uses DashScope official multimodal generation API.
- `base_url` should be region root API URL:
  - China: `https://dashscope.aliyuncs.com/api/v1`
  - Singapore: `https://dashscope-intl.aliyuncs.com/api/v1`
- Do not use `.../compatible-mode/v1` for this provider.

## Notes

- Candidates are tried in order.
- Disabled candidates are skipped.
- If all candidates fail, the step fails with full error chain.
- `--provider mock` still works as explicit local test override.
