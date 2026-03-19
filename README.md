# WeChat Article Writer (Open Edition)

Beginner-friendly workflow to generate a WeChat article and push it to Official Account **draft box**.

## What this project does

- Write article draft from topic
- Generate cover/body images
- Convert Markdown to WeChat-compatible HTML
- Upload assets and publish to draft box
- Validate draft readback

## Quick start

1. Copy config template:

```bash
cp config.example.json config.json
```

2. Fill your own credentials in `config.json`:

- `llm_candidates`
- `image_candidates`
- `appid`
- `appsecret`

3. Run full pipeline:

```bash
python scripts/run_workflow.py "Spring Wellness" --style practical --theme shuimo/default --publish-draft
```

## Security notice (important)

- Never commit `config.json`.
- Never commit real keys or production outputs.
- If any key was ever exposed, rotate it immediately.
- Use `RELEASE_CHECKLIST.md` before public push.

## Docs

- Chinese docs: `docs/zh/README.md`
- English docs: `docs/en/README.md`
- Beginner quickstart (ZH): `docs/zh/quickstart.md`

## License

This project is released under the MIT License (see `LICENSE`).
