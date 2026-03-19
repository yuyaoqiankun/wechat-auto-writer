# WeChat Article Writer（中文版）

面向 **小白用户** 的微信公众号草稿自动化流程：

1. 写文章
2. 自动配图（封面 + 正文图）
3. 自动排版成公众号可用 HTML
4. 自动推送到公众号草稿箱

---

## 0）你需要准备什么

在开始前，只需要准备这三类信息：

- 文本模型（用于写稿）
- 图片模型（用于生图）
- 微信公众号 `appid` / `appsecret`（用于推草稿）

如果暂时没有图片模型，也可以先只跑到写稿与排版阶段（不加 `--publish-draft`）。

---

## 1）先复制配置模板

在 skill 目录下执行：

```bash
cp config.example.json config.json
```

然后打开 `config.json`，按下面说明填写。

---

## 2）按字段填写 config.json（重点）

最常用字段：

- `llm_candidates`：写稿模型候选（按顺序 fallback）
- `image_candidates`：生图模型候选（按顺序 fallback）
- `appid` / `appsecret`：公众号凭证

### 推荐新手配置（可直接照抄结构）

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
  "image_style": "轻插画",
  "appid": "wx123...",
  "appsecret": "xxxx"
}
```

### DashScope 特别注意

`dashscope_image` 必须使用：

- `base_url: https://dashscope.aliyuncs.com/api/v1`（中国区）
- 或 `https://dashscope-intl.aliyuncs.com/api/v1`（新加坡区）

不要填 `.../compatible-mode/v1`（会导致 404）。

---

## 快速开始

```bash
python scripts/run_workflow.py "春季养生" \
  --style 干货 \
  --theme shuimo/default \
  --publish-draft
```

如果你是第一次上手，先看：

- `docs/zh/quickstart.md`（5 分钟极简上手）

---

## 4）常见问题（小白版）

### 问题 A：图片 502 / 404 / 429

- 502：上游网关异常，稍后重试或走 fallback 候选
- 404：通常是接口路径/base_url 错（尤其 DashScope）
- 429：限流，降低并发，拉长重试间隔

### 问题 B：草稿推送失败

- 先检查 `appid` / `appsecret`
- 再检查公众号 API 权限和白名单

### 问题 C：只想先看稿子，不推草稿

去掉 `--publish-draft` 即可。

---

## 5）文档导航

- `docs/zh/configuration.md`：完整配置说明
- `docs/zh/usage.md`：命令行参数说明
- `references/runbook.md`：运行手册与排障
- `references/model-providers.md`：provider 能力与约束

---

## 6）当前能力边界

- 当前默认正文图数量：1 张
- 发布目标：草稿箱（不是直接群发）

