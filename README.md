# WeChat Article Writer（Open Edition）

面向微信公众号运营者的自动化工作流：从选题到草稿，一条命令跑完。

---

## ✨ 功能特性

- 主题输入 → 自动生成文章草稿（Markdown 优先）
- 自动提取公众号草稿所需标题与摘要
- 自动生成封面图 + 正文配图（支持候选 fallback）
- 基于主题模板渲染公众号 HTML
- 可选上传图片素材并替换链接
- 自动推送草稿并执行回读校验

---

## 🧭 适用人群

- 想提升发文效率的公众号运营者
- 需要脚本化内容生产流程的开发者
- 希望把“写稿→配图→排版→草稿”标准化的团队

---

## 🚀 快速开始

### 1）准备配置文件

```bash
cp config.example.json config.json
```

### 2）在 `config.json` 填写你的信息

至少填写：

- `llm_candidates`
- `image_candidates`
- `appid`
- `appsecret`

### 3）运行完整链路（含推送草稿）

```bash
python scripts/run_workflow.py "春季养生" \
  --style 干货 \
  --theme shuimo/default \
  --publish-draft
```

成功后会返回：

- 文章 markdown/html 路径
- 封面图与正文图路径
- 草稿 `media_id`
- 回读校验结果

---

## ⚙️ 运行说明

- 建议 Python 3.10+
- 常见依赖：`requests`、`PyYAML`、`Pillow`
- 详细参数与流程见文档区

---

## 🧩 推荐配置模式

本项目采用候选列表 fallback 机制：

- `llm_candidates`：文本模型候选
- `image_candidates`：图片模型候选

推荐图片候选顺序：

1. `openai_compatible_images`（主）
2. `dashscope_image`（备）

> `dashscope_image` 必须使用 `.../api/v1`，不要使用 `.../compatible-mode/v1`。

---

## 🛠 常见问题速查

- **502 Bad Gateway**：上游接口不稳定，重试或等待 fallback 接管
- **404 Not Found**：大概率是图片 `base_url` / 路径配置错误
- **429 Rate Limit**：触发限流，降低请求频率后重试
- **草稿推送失败**：检查 `appid/appsecret` 和公众号 API 白名单

---

## 📚 文档导航

- 中文文档入口：`docs/zh/README.md`
- 英文文档入口：`docs/en/README.md`
- 中文 5 分钟上手：`docs/zh/quickstart.md`
- 运行手册：`references/runbook.md`
- 配置说明：`references/configuration.md`
- Provider 说明：`references/model-providers.md`

---

## 🔐 安全声明

- 不要提交 `config.json`
- 不要提交真实密钥或生产产物
- 如密钥疑似泄露，请立即轮换
- 对外发布前请执行 `RELEASE_CHECKLIST.md`

---

## 🧾 许可证

Copyright © 2026 煜耀乾坤  
GitHub: https://github.com/yuyaoqiankun

本项目采用 MIT License，详见 `LICENSE`。
