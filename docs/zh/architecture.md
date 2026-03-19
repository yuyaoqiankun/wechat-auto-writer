# 系统架构与写作系统说明

## 这条 skill 现在是什么

这条 skill 已经不是单一脚本，而是一条完整的公众号文章生产流水线，分为五层：

1. **内容生成层**
   - `scripts/write_article.py`
   - `scripts/wechat_metadata.py`
2. **主题 / 排版层**
   - `themes/<category>/<name>.yaml`
   - `scripts/format_article.py`
3. **HTML 渲染层**
   - Markdown → 公众号兼容 HTML
4. **图片生成与替换层**
   - `scripts/generate_image.py`
   - `scripts/add_article_images.py`
   - 本地图片上传到微信素材库并替换 URL
5. **草稿发布层**
   - `scripts/publish_draft.py`
   - `scripts/wechat_capability.py`

## Source of truth

- **Markdown 是文章内容源文件**
- HTML 是生成产物
- 草稿箱是发布目标，不是内容源

## 工作流逻辑

典型流程：

1. 生成 Markdown 初稿
2. 提炼发布标题与摘要
3. 规划正文配图位置
4. 生成 1 张封面图 + 1 张正文主图（默认）
5. 压缩图片
6. 选择主题并渲染 HTML
7. 上传正文图并替换成微信素材 URL
8. 上传封面并创建草稿
9. 回读草稿并做验收

## 当前默认策略

- 正文默认图片数量：**1 张**
- 默认输出目录结构：`output/YYYY-MM-DD/HHMMSS-topic-slug/`
- 当前发布目标：**公众号草稿箱**
- 当前主题系统：结构化主题 schema，已导入 21 个主题

## 为什么这样设计

### 为什么 Markdown 优先

Markdown 易编辑、易对比、易归档，适合后续继续修改，不把内容锁死在微信后台里。

### 为什么正文图默认只保留 1 张

当前优先级是“图可用、风格稳定、不要乱码文字图”，而不是追求图片数量。

### 为什么主题系统改成结构化 schema

结构化主题更适合长期维护，也更接近成熟公众号排版系统，不再依赖粗糙的 CSS 字符串主题。

## 当前做得好的部分

- Markdown → HTML 转换稳定
- 草稿上传稳定
- 正文图片替换成微信素材 URL 稳定
- 21 个主题可用
- 单次任务输出按日期/单篇归档

## 当前有意不做复杂化的部分

- 智能配图数量判断
- 批量任务自愈
- 多账号发布编排
- 自动化 benchmark UI

这些后续按真实需要再做，不在当前收尾范围内。
