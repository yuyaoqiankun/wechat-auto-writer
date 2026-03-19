# 主题系统说明

主题文件位于：

```bash
themes/<category>/<name>.yaml
```

当前 skill 使用的是从参考项目迁入的**结构化主题 schema**。

## 主题结构

每个主题 YAML 主要包含：

- `name`
- `description`
- `keywords`
- `colors`
- `styles`

其中 `styles` 是 dict-style 结构，不再是粗糙的原始 CSS 字符串。

## 当前内置主题

### Macaron
- `macaron/blue`
- `macaron/coral`
- `macaron/cream`
- `macaron/lavender`
- `macaron/lemon`
- `macaron/lilac`
- `macaron/mint`
- `macaron/peach`
- `macaron/pink`
- `macaron/rose`
- `macaron/sage`
- `macaron/sky`

### Wenyan
- `wenyan/default`
- `wenyan/lapis`
- `wenyan/maize`
- `wenyan/mint`
- `wenyan/orange_heart`
- `wenyan/pie`
- `wenyan/purple`
- `wenyan/rainbow`

### Shuimo
- `shuimo/default`

## 使用方式

```bash
--theme macaron/blue
--theme wenyan/purple
--theme shuimo/default
```

## 实际使用建议

- **Macaron**：成长、教育、生活方式、知识型大众内容
- **Wenyan**：人文、散文、文化、偏文气内容
- **Shuimo**：中式气质、克制沉静、养生/节气/东方审美内容

## 当前状态

21 个主题已经导入当前 skill，并已做过代表性主题的真实草稿发布验证。
