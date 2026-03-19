# 使用说明

## 一键工作流

```bash
python scripts/run_workflow.py "春季养生" \
  --style 干货 \
  --theme shuimo/default \
  --publish-draft
```

## 常用参数

- `--style`：文章风格，如 `干货` / `情感` / `资讯`
- `--theme`：排版主题
- `--publish-draft`：推送到草稿箱
- `--max-body-images`：正文图片数量上限（当前默认 1）
- `--provider`：模型 provider，可用于 mock 测试
- `--model`：指定模型名
- `--output-dir`：输出目录
- `--flat-output`：使用旧的平铺输出结构
- `--image-prompt-strategy`：提示词策略（`full` / `lite`）
- `--image-prompt-lite-chars`：轻量策略首段截断长度（仅 `lite` 生效）
- `--image-style`：图片视觉风格（如 `轻插画` / `电影感` / `极简`），优先级高于配置文件
- `--image-style-preset`：风格预设（`pro-1` / `pro-2` / `pro-3`），用于非叙事、信息表达型视觉

## 提示词策略切换

### 默认（全量语义优先）

```bash
python scripts/run_workflow.py "春季养生" \
  --style 干货 \
  --theme shuimo/default \
  --image-prompt-strategy full
```

- `full`：读取标题 + 正文截断，语义覆盖更完整。

### 轻量（省 token 优先）

```bash
python scripts/run_workflow.py "春季养生" \
  --style 干货 \
  --theme shuimo/default \
  --image-prompt-strategy lite \
  --image-prompt-lite-chars 220
```

- `lite`：只读标题 + 首段截断，封面图/正文图各 1 张，适合低成本快速出图。
- `--image-prompt-lite-chars`：控制首段最大截断字符数（建议 180~320）。

## 单独执行脚本（按顺序）

```bash
python scripts/write_article.py ...
python scripts/generate_image.py ...
python scripts/add_article_images.py ...
python scripts/compress_image.py ...
python scripts/format_article.py --theme shuimo/default --upload-images ...
python scripts/publish_draft.py ...
```

## 适合的工作方式

- 正常使用优先走 `run_workflow.py`
- 只有在排障或局部重试时，再拆脚本逐步执行
- 单篇任务当前优先，不把批量任务当主使用场景
