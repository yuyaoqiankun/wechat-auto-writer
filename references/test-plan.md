# Test Plan

## Smoke tests

- run `write_article.py` with `mock`
- run `add_article_images.py` on generated Markdown
- run `generate_image.py` with body plan JSON
- run `compress_image.py` on a real image fixture
- run `format_article.py` with and without `--upload-images`
- run `run_workflow.py` without publish

## Integration tests after credentials

- run `format_article.py --upload-images` with real local images
- run `publish_draft.py` against a real公众号草稿箱
- run `run_workflow.py --publish-draft`
