# Current State

As of 2026-03-18, this skill has completed real end-to-end validation on the new V1 image prompting approach.

## V1 image prompting status

Implemented:

- LLM reads article title + content before image generation
- LLM outputs a visual strategy card + cover/body prompts
- Prompt source tracking (`llm` vs `template` fallback)
- Default body image count fixed to 1
- Default visual baseline anchored to light-illustration style

## Verified full flow (including draft publish)

1. `write_article.py`
2. `wechat_metadata.py`
3. `add_article_images.py` (1 body image plan)
4. `generate_image.py` (LLM strategy + prompt output)
5. `compress_image.py`
6. `format_article.py --upload-images`
7. `publish_draft.py`
8. `run_workflow.py --publish-draft`

## Validation notes

- Config (`llm_candidates` + `image_candidates`) is callable
- Intermittent 504 may occur on upstream gateway; rerun typically succeeds
- End-to-end run has succeeded with:
  - body image upload to WeChat
  - draft push success
  - draft readback validation success

## Production caveats

- WeChat API still requires server IP whitelist setup
- Keep `config.json` private; use `config.example.json` for public sharing
- Use debug artifacts for troubleshooting draft failures

## Next planned enhancements (post-V1)

- dynamic body-image count (max 3)
- richer style presets and routing
- stricter structured output validation + auto-repair on LLM JSON drift
