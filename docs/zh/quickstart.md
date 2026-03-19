# 5 分钟上手（小白版）

这份页只做一件事：让你 **最快跑通一条完整链路**（写稿 + 配图 + 排版 + 推草稿）。

## 1）复制配置模板

在 skill 目录执行：

```bash
cd /root/.openclaw/workspace/skills/wechat-article-writer
cp config.example.json config.json
```

## 2）把 `config.json` 最少填这几项

直接照这个结构改（只改带 `your-` 的值）：

```json
{
  "llm_candidates": [
    {
      "enabled": true,
      "provider": "openai_compatible",
      "base_url": "https://your-llm-endpoint/v1",
      "api_key": "sk-your-llm-key",
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
      "api_key": "sk-your-image-key",
      "model": "grok-imagine-1.0",
      "retries": 1
    },
    {
      "enabled": true,
      "provider": "dashscope_image",
      "base_url": "https://dashscope.aliyuncs.com/api/v1",
      "api_key": "sk-your-dashscope-key",
      "model": "qwen-image-2.0-pro",
      "retries": 1
    }
  ],
  "image_prompt_strategy": "full",
  "image_prompt_lite_content_chars": 240,
  "image_style": "轻插画",
  "appid": "wx你的公众号appid",
  "appsecret": "你的公众号appsecret"
}
```

> 注意：`dashscope_image` 必须用 `.../api/v1`，不要用 `.../compatible-mode/v1`。

## 3）一条命令直接跑全链路

```bash
/root/.agent-reach/venv/bin/python scripts/run_workflow.py "春季养生" \
  --style 干货 \
  --theme shuimo/default \
  --publish-draft
```

## 4）成功后你会看到什么

- 文章 markdown 路径
- 封面与正文图路径
- 草稿 `media_id`
- 读回校验结果（标题一致、内容无异常字符）

## 5）报错先看这个

- **502**：主图接口不稳，重试或让 fallback 接管
- **404**：大概率 `base_url` 填错（尤其 DashScope）
- **429**：限流，等几分钟再试
- **草稿失败**：先查 `appid/appsecret` 和公众号 API 白名单
