# Workflow Orchestrator

Use `scripts/run_workflow.py` to execute the main pipeline in one command.

## What it does

1. write article
2. plan body images
3. generate cover + body images
4. compress images
5. format Markdown to themed WeChat HTML
6. optionally upload draft

## Example

```bash
python scripts/run_workflow.py "春季减肥变美" \
  --style 干货 \
  --theme macaron/blue \
  --provider mock
```

## Optional flags

- `--upload-images` → upload local Markdown images during HTML conversion
- `--publish-draft` → push final article to WeChat draft box
- `--max-body-images 1` (current default)
- `--benchmark-summary "..."`
- `--provider openai_compatible`
- `--model deepseek-chat`
- `--flat-output` → keep old flat output layout (default is per-run archive folders)

## Theme system

The skill now uses the full structured theme schema migrated from the reference project.
Available built-in themes:

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
- `wenyan/default`
- `wenyan/lapis`
- `wenyan/maize`
- `wenyan/mint`
- `wenyan/orange_heart`
- `wenyan/pie`
- `wenyan/purple`
- `wenyan/rainbow`
- `shuimo/default`

## Output organization

By default, each workflow run now creates a two-level archive structure under `output/`, for example:

```bash
output/2026-03-17/104233-测试归档整理/
```

Inside each run folder you will find:
- `article.md`
- `article.html`
- `cover.png`
- `cover.jpg`
- `generated-body-images/`
- `body-image-plan.json`
- `metadata.json`
- `publish-result.json`

A lightweight `output/index.jsonl` file is also appended on each run so you can quickly inspect past runs without opening every folder.

## Notes

- The orchestrator currently assumes `generate_image.py` can produce the planned image paths.
- In early development, image providers may be mock implementations.
- Publishing requires valid `appid` and `appsecret`.
