# Theme System

Theme files live under:

```bash
themes/<category>/<name>.yaml
```

The skill now uses the full structured theme schema migrated from the reference project.

## Theme schema

Each theme YAML includes:

- `name`
- `description`
- `keywords`
- `colors`
- `styles`

`styles` is dict-based, not a raw CSS-string blob.

## Built-in themes

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

## Usage

Pass `--theme <category>/<name>` to `run_workflow.py` or `format_article.py`.

Examples:

```bash
--theme macaron/blue
--theme wenyan/purple
--theme shuimo/default
```

## Practical guidance

- **Macaron**: growth, education, lifestyle, mainstream content, friendly knowledge posts
- **Wenyan**: humanities, essays, literary expression, cultural topics, slower reading
- **Shuimo**: calm Chinese-style branding, restrained visual identity, seasonal养生 or东方气质 topics

## Validation status

The 21-theme set has already been imported into the skill and real draft publishing has been validated on representative themes.
