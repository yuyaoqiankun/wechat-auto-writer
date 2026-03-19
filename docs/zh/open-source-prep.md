# 开源发布前整理建议

## 建议不要直接公开当前运行目录

当前 skill 工作目录中混有：

- 真实 `config.json`
- `output/` 产物
- `output/debug/` 调试文件
- token cache
- 真实草稿测试结果
- 本地运行环境痕迹

正确做法应是：

> 基于当前 skill，整理一个 **脱敏后的开源发布版**。

## 建议保留到开源仓库的内容

- `SKILL.md`
- `scripts/`
- `themes/`
- `references/`（筛选后）
- `docs/zh/`
- `docs/en/`
- `README.md`
- `README.zh-CN.md`
- `config.example.json`
- `.gitignore`
- `LICENSE`

## 不建议公开提交的内容

- `config.json`
- `output/`
- `output/debug/`
- `wechat_token_cache.json`
- 任何真实 API key / token / appid / appsecret
- 真实文章产物
- 真实 media_id、draft payload、回读结果
- 本机路径和环境痕迹

## 建议新增的文件

- `.gitignore`
- `config.example.json`
- `LICENSE`
- `README.md`
- `README.zh-CN.md`

## 建议做一次脱敏审计

发布前至少全文检查：

- `sk-`
- `appid`
- `appsecret`
- 真实 endpoint
- token cache
- media_id
- 本机路径

## 许可建议

如果希望更容易传播与使用，可考虑：

- MIT
- Apache-2.0

## 关于“防抄袭”

开源代码无法从技术上彻底防止别人复制。更现实的做法是：

- 保留清晰版权声明
- 保留 git 历史
- 说明上游来源与当前重构成果
- 用持续迭代和文档质量建立项目主导权
