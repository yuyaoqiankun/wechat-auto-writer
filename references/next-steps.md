# Current Development Status

> Historical status file. Last refreshed: 2026-03-19.

## Done

- pluggable LLM provider for article writing
- theme-driven WeChat HTML formatting
- unified WeChat capability layer
- draft publishing wrapper
- local image path → WeChat URL replacement in formatter
- body image planning and Markdown placeholder insertion
- image fallback router with candidate ordering
- image prompt strategy switch (`full` / `lite`)
- image style control (`--image-style`, preset support)
- `dashscope_image` provider support aligned to official multimodal-generation API

## In progress

- stronger image compression policy tuning for broader WeChat edge cases
- docs consistency cleanup across historical reference files

## Recommended next milestones

1. add benchmark-article style extraction helper
2. add second-pass quality review before publishing
3. add sample fixtures / regression tests
4. refine theme styles and mapping
