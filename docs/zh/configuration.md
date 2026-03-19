# 配置说明

主配置文件：

```bash
config.json
```

## 核心配置（仅新模式）

### 文本生成（LLM）

- `llm_candidates`（必填）
  - 跨供应商候选列表，按顺序 fallback
  - 每项支持：
    - `enabled`（是否启用）
    - `provider`（`openai_compatible` 或 `mock`）
    - `base_url`
    - `api_key`
    - `model`
    - `retries`
    - `timeout`

### 图片生成

- `image_candidates`（必填）
  - 跨供应商候选列表，按顺序 fallback
  - 每项支持：
    - `enabled`
    - `provider`（`openai_compatible_images` 或 `dashscope_image` 或 `mock`）
    - `base_url`
    - `api_key`
    - `model`
    - `retries`

- `image_prompt_strategy`（`full` | `lite`）
- `image_prompt_lite_content_chars`（`lite` 策略下首段截断长度）
- `image_style`（默认图片视觉风格，可被 `--image-style` 覆盖）

### 微信公众号

- `appid`
- `appsecret`

### 可选文章默认值

- `author`
- `digest`
- `content_source_url`
- `thumb_crop`
- `default_output_dir`

## 空白 fallback 示例

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

## Provider 说明

### `openai_compatible_images`

- 走 OpenAI Images 兼容协议（如 `/images/generations`）。

### `dashscope_image`

- 走 DashScope 官方 multimodal-generation 协议。
- `base_url` 要填区域 API 根地址：
  - 中国区：`https://dashscope.aliyuncs.com/api/v1`
  - 新加坡：`https://dashscope-intl.aliyuncs.com/api/v1`
- 不要给 `dashscope_image` 填 `.../compatible-mode/v1`。

## 说明

- 候选按顺序尝试。
- `enabled=false` 的候选会被跳过。
- 所有候选失败时，会返回完整失败链路。
- `--provider mock` 仍可用于显式本地测试覆盖。
