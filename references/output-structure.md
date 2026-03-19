# Output Structure

## Default layout

Each run writes into:

```bash
output/YYYY-MM-DD/HHMMSS-topic-slug/
```

Example:

```bash
output/2026-03-17/184502-春季养生/
```

## Files inside a run folder

Typical files:

- `article.md` — source Markdown
- `article.html` — themed WeChat HTML
- `cover.png` — original generated cover
- `cover.jpg` — compressed cover for upload
- `body-image-plan.json` — body image planning result
- `metadata.json` — publish title, digest, provider/model metadata
- `publish-result.json` — draft publishing result and validation output
- `generated-body-images/` — local body image artifacts

## Debug files

Some lower-level debug files are still written to:

```bash
output/debug/
```

These are helper artifacts for draft payload/readback inspection.

## Global index

The orchestrator also appends a summary line into:

```bash
output/index.jsonl
```

This is useful for quickly scanning past runs without opening every folder.

## Recommended operator practice

- Use the per-run folder as the unit of inspection.
- Treat `article.md` as the editable source.
- Treat `publish-result.json` as the first place to inspect failures.
- Keep `output/debug/` for troubleshooting, but do not rely on it as the primary archive.
