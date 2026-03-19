# 迁移教程（服务器迁移）

这份教程用于把当前 `wechat-article-writer` skill 从一台服务器迁移到另一台服务器。

## 迁移目标

需要迁移的是：

- skill 代码目录
- 主题文件
- 文档
- 配置模板或真实配置（按你的安全策略决定）
- Python 运行环境依赖
- OpenClaw 运行环境中对该 skill 的调用方式

## 推荐迁移策略

### 方案 A：迁移生产版（仅内部自用）
适用于你自己的新服务器，保留真实配置。

### 方案 B：迁移开源发布版
适用于 GitHub / 对外共享，只迁移脱敏版本。

本教程优先写 **生产版迁移**。

---

## 一、源服务器上要准备什么

当前生产目录：

```bash
/root/.openclaw/workspace/skills/wechat-article-writer
```

建议先确认：

1. `config.json` 配置是否正确
2. `scripts/`、`themes/`、`references/`、`docs/` 是否完整
3. `output/` 是否需要迁移

### 关于 `output/`

- 如果只是迁移程序本身：**可以不迁移**
- 如果你还想保留历史草稿产物：可以一起带走

---

## 二、目标服务器需要具备的基础条件

至少保证：

1. 已安装 OpenClaw
2. 已有工作区目录：

```bash
/root/.openclaw/workspace
```

3. 已安装 Python 3
4. 能访问你使用的文本生成与图片生成 API
5. 目标服务器允许访问微信接口

---

## 三、迁移步骤

### 1）复制 skill 目录

在源服务器打包：

```bash
cd /root/.openclaw/workspace/skills
tar czf wechat-article-writer.tar.gz wechat-article-writer
```

传到目标服务器后解压：

```bash
cd /root/.openclaw/workspace/skills
tar xzf wechat-article-writer.tar.gz
```

---

### 2）检查配置文件

生产迁移时，重点检查：

```bash
/root/.openclaw/workspace/skills/wechat-article-writer/config.json
```

确认这些项：

- `llm_candidates`（至少一个 `enabled=true` 的候选）
- `image_candidates`（至少一个 `enabled=true` 的候选）
- `appid`
- `appsecret`

如果不想直接复制真实配置，也可以先复制 `config.example.json` 再手工填入。

---

### 3）安装 Python 依赖

当前 skill 依赖至少包括：

- `requests`
- `PyYAML`
- `Pillow`

如果目标机没有这些依赖，可以安装：

```bash
pip install requests pyyaml pillow
```

如果你使用的是 OpenClaw/Agent Reach 现有虚拟环境，也可以直接沿用同一 Python 环境。

---

### 4）检查脚本可运行性

在目标服务器上先做一轮最小检查：

```bash
cd /root/.openclaw/workspace/skills/wechat-article-writer/scripts
python3 run_workflow.py "迁移测试" --style 干货 --theme shuimo/default --provider mock --output-dir ../output
```

这个命令用于检查：

- 目录结构是否正常
- 主题系统是否正常
- 工作流脚本是否可调用

---

### 5）做真实接口测试

如果 mock 测试通过，再做一轮真实测试：

```bash
cd /root/.openclaw/workspace/skills/wechat-article-writer/scripts
python3 run_workflow.py "迁移后真实测试" --style 干货 --theme shuimo/default --output-dir ../output --publish-draft
```

重点确认：

- 写稿成功
- 生图成功
- 图片上传替换成功
- 草稿创建成功
- 回读校验正常

---

## 四、迁移后重点检查项

迁移完成后，建议重点检查：

1. `themes/` 是否完整（当前应为 21 个主题）
2. `docs/` 和 `references/` 是否完整
3. `output/` 是否能按新结构写入
4. `format_article.py` 是否能正确上传正文图
5. `publish_draft.py` 是否能正常回读草稿

---

## 五、如果是开源版迁移

如果你要迁移的是公开发布版目录，例如：

```bash
/root/.openclaw/workspace/skills/wechat-article-writer-open
```

那它默认不带：

- `config.json`
- `output/`
- token cache
- 真实草稿结果

此时要在目标机上额外做：

1. 复制或新建 `config.json`
2. 手工配置 API key / appid / appsecret
3. 首次运行前确认 `.gitignore` 和脱敏策略

---

## 六、迁移建议总结

### 最稳做法

- 先迁生产版目录
- 先跑 mock
- 再跑真实草稿测试
- 确认没问题后再正式使用

### 不建议做法

- 不校验就直接切生产
- 把开源版直接当生产版跑
- 忽略 `config.json` 和 Python 依赖差异

---

## 七、一句话版

**迁移 skill 的核心不是复制目录本身，而是同时确保：代码、主题、配置、依赖、微信接口权限、输出目录写入能力都一起正常。**
