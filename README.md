# WeChat Article Writer (Open Edition)

Beginner-friendly automation pipeline to write a WeChat article, generate images, format HTML, and publish to Official Account **draft box**.

---

## ✨ Features

- Topic → full article draft (Markdown-first)
- Auto title + digest extraction for WeChat draft
- Cover image + body image generation (with fallback routing)
- Theme-based WeChat HTML rendering
- Optional material upload + image URL replacement
- Draft publish + readback validation

---

## 🧭 Who is this for?

- WeChat OA operators who want to speed up article production
- Developers who need a scriptable draft workflow
- Teams that want reproducible content pipelines (instead of manual editor clicks)

---

## 🚀 Quick Start

### 1) Prepare config

```bash
cp config.example.json config.json
```

Fill your own credentials in `config.json`:

- `llm_candidates`
- `image_candidates`
- `appid`
- `appsecret`

### 2) Run full pipeline

```bash
python scripts/run_workflow.py "Spring Wellness" \
  --style practical \
  --theme shuimo/default \
  --publish-draft
```

On success, you will get:

- article markdown/html paths
- cover/body image paths
- draft `media_id`
- readback validation result

---

## ⚙️ Runtime Notes

- Python 3.10+ recommended
- Typical dependencies: `requests`, `PyYAML`, `Pillow`
- For complete docs and examples, see the docs section below

---

## 🧩 Common Config Pattern

Use candidate-based fallback:

- `llm_candidates`: text generation providers
- `image_candidates`: image generation providers

Recommended image fallback order:

1. `openai_compatible_images` (primary)
2. `dashscope_image` (fallback)

> For `dashscope_image`, use `.../api/v1` base URL (not `.../compatible-mode/v1`).

---

## 🛠 Troubleshooting (Quick)

- **502 Bad Gateway**: upstream instability, retry or rely on fallback candidate
- **404 Not Found**: usually wrong image `base_url`/path
- **429 Rate Limit**: reduce pressure, retry later
- **Draft publish failed**: verify `appid/appsecret` and WeChat API whitelist

---

## 📚 Documentation

- English docs: `docs/en/README.md`
- Chinese docs: `docs/zh/README.md`
- Beginner quickstart (ZH): `docs/zh/quickstart.md`
- Runbook: `references/runbook.md`
- Config reference: `references/configuration.md`
- Provider reference: `references/model-providers.md`

---

## 🔐 Security Notice

- Never commit `config.json`
- Never commit real keys or production outputs
- If a key was exposed, rotate immediately
- Run `RELEASE_CHECKLIST.md` before public push

---

## 🧾 License

Copyright © 2026 煜耀乾坤  
GitHub: https://github.com/yuyaoqiankun

Released under the MIT License. See `LICENSE`.
