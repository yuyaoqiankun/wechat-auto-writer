# Output Structure

## Default layout

Each run writes into:

```bash
output/YYYY-MM-DD/HHMMSS-topic-slug/
```

Example:

```bash
output/2026-03-17/184502-spring-wellness/
```

## Typical files inside a run folder

- `article.md`
- `article.html`
- `cover.png`
- `cover.jpg`
- `body-image-plan.json`
- `metadata.json`
- `publish-result.json`
- `generated-body-images/`

## Debug files

Lower-level draft debug files may still be written to:

```bash
output/debug/
```

## Global index

The orchestrator also appends a line to:

```bash
output/index.jsonl
```

This is useful for quickly scanning past runs.
