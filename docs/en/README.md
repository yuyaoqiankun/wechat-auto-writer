# WeChat Article Writer

A **beginner-friendly** WeChat Official Account draft workflow:

1. write article
2. generate images (cover + body)
3. format to WeChat HTML
4. push to draft box

---

## 0) What you need before starting

Prepare only these inputs:

- one text model (for writing)
- one image model (for image generation)
- WeChat `appid` / `appsecret` (for draft publishing)

If image provider is not ready yet, you can still run writing + formatting first.

---

## 1) Copy config template

In skill directory:

```bash
cp config.example.json config.json
```

Then edit `config.json`.

---

## 2) Fill config.json (important)

Most important fields:

- `llm_candidates`: writing model candidates (ordered fallback)
- `image_candidates`: image model candidates (ordered fallback)
- `appid` / `appsecret`: WeChat credentials

### Starter config example

```json
{
  "llm_candidates": [
    {
      "enabled": true,
      "provider": "openai_compatible",
      "base_url": "https://your-llm-endpoint/v1",
      "api_key": "sk-xxx",
      "model": "gpt-5.4",
      "retries": 2,
      "timeout": 180
    }
  ],
  "image_candidates": [
    {
      "enabled": true,
      "provider": "openai_compatible_images",
      "base_url": "https://your-image-endpoint/v1",
      "api_key": "sk-xxx",
      "model": "grok-imagine-1.0",
      "retries": 1
    },
    {
      "enabled": true,
      "provider": "dashscope_image",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "api_key": "sk-xxx",
      "model": "qwen-image-2.0-pro",
      "retries": 1
    }
  ],
  "image_prompt_strategy": "full",
  "image_prompt_lite_content_chars": 240,
  "image_style": "light illustration",
  "appid": "wx123...",
  "appsecret": "xxxx"
}
```

### DashScope note

For `dashscope_image`, use:

- `https://dashscope.aliyuncs.com/api/v1` (China)
- or `https://dashscope-intl.aliyuncs.com/api/v1` (Singapore)

Do **not** use `.../compatible-mode/v1` for this provider.

---

## 3) Run full pipeline (including draft publish)

```bash
/root/.agent-reach/venv/bin/python scripts/run_workflow.py "Spring Wellness" \
  --style practical \
  --theme shuimo/default \
  --publish-draft
```

On success, output includes:

- article path
- cover/body image paths
- draft `media_id`
- readback validation

---

## 4) Common issues (quick checks)

### A) Image API errors: 502 / 404 / 429

- 502: upstream gateway issue, retry or rely on fallback candidate
- 404: usually wrong `base_url`/path (very common with DashScope)
- 429: rate limit, reduce request pressure and retry later

### B) Draft publish failed

- verify `appid` / `appsecret`
- verify WeChat API permissions / whitelist

### C) I only want article output first

Run without `--publish-draft`.

---

## 5) Where to read more

- `docs/en/configuration.md`
- `docs/en/usage.md`
- `references/runbook.md`
- `references/model-providers.md`

---

## 6) Current boundaries

- default body image count: 1
- publish target: draft box only
