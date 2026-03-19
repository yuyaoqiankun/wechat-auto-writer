# 输出目录与文件说明

## 默认输出结构

每次运行默认输出到：

```bash
output/YYYY-MM-DD/HHMMSS-topic-slug/
```

示例：

```bash
output/2026-03-17/184502-春季养生/
```

## 单篇目录里的典型文件

- `article.md`：文章 Markdown 源文件
- `article.html`：主题渲染后的公众号 HTML
- `cover.png`：原始封面图
- `cover.jpg`：压缩后用于上传的封面图
- `body-image-plan.json`：正文图片规划结果
- `metadata.json`：发布标题、摘要、模型信息等
- `publish-result.json`：草稿发布结果与回读验收结果
- `generated-body-images/`：正文图片产物目录

## Debug 文件

当前底层调试文件还会写到：

```bash
output/debug/
```

用于查看 draft payload / readback。

## 全局索引

工作流还会往：

```bash
output/index.jsonl
```

追加每次运行的摘要，方便快速浏览历史运行记录。

## 推荐操作习惯

- 以单篇目录作为最小检查单位
- 把 `article.md` 当作真正可继续编辑的内容源
- 出错时优先看 `publish-result.json`
- `output/debug/` 用于排障，不建议当作正式归档主入口
