# Open-source Release Preparation

## Do not publish the current working directory as-is

The current runtime workspace includes sensitive and environment-specific files, such as:

- real `config.json`
- `output/` artifacts
- `output/debug/` files
- token cache
- real draft results
- local environment traces

The correct approach is to prepare a **sanitized release package**.

## Keep in the public repository

- `SKILL.md`
- `scripts/`
- `themes/`
- `references/` (after review)
- `docs/zh/`
- `docs/en/`
- `README.md`
- `README.zh-CN.md`
- `config.example.json`
- `.gitignore`
- `LICENSE`

## Do not publish

- `config.json`
- `output/`
- `output/debug/`
- `wechat_token_cache.json`
- real API keys, tokens, app IDs, app secrets
- real article outputs
- real media IDs and draft payloads
- local host-specific traces

## Recommended additions

- `.gitignore`
- `config.example.json`
- `LICENSE`
- repository-level README files

## About copying / reuse

You cannot fully prevent copying once code is public. What you can do is:

- keep a clear copyright statement
- keep the git history intact
- explain upstream sources and your own reconstruction work
- build author authority through continued iteration and documentation quality
