# Architecture and Writing System

## What this skill is now

This skill is no longer just a draft uploader. It is a full公众号文章 production pipeline with five layers:

1. **Content generation layer**
2. **Theme / layout layer**
3. **HTML rendering layer**
4. **Image generation and replacement layer**
5. **Draft publishing layer**

## Source of truth

- Markdown is the source of truth
- HTML is a generated artifact
- The draft box is the publishing target, not the source of truth

## Workflow

1. Generate Markdown article
2. Extract publish title and digest
3. Plan body image placement
4. Generate one cover image and one body image by default
5. Compress images
6. Render themed WeChat HTML
7. Upload body images and replace local paths with WeChat URLs
8. Upload cover and create draft
9. Read draft back for validation

## Current defaults

- Default body image count: **1**
- Default output structure: `output/YYYY-MM-DD/HHMMSS-topic-slug/`
- Publishing target: **draft box only**
- Theme system: structured schema with 21 imported themes

## Design decisions

### Why Markdown first
Markdown is editable, portable, and easier to inspect than treating the WeChat editor as the primary source.

### Why one body image by default
The current priority is image usability and consistency, not image quantity.

### Why structured themes
Structured themes are easier to maintain and much closer to a real公众号 layout system than raw CSS-string themes.
