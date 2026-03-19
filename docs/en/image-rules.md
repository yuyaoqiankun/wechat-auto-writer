# Image Rules

## Current minimum standard

The current image system follows a simplified but more stable rule set.

### Cover image

Requirements:

- horizontal cover logic (targeted toward 900:500 after compression)
- simple and premium
- clean visual hierarchy
- clear subject
- no text
- no watermark
- suitable for new-media distribution
- high-definition texture

### Body image

Requirements:

- one main body image by default
- vertical or square-friendly composition logic
- lightweight
- atmospheric but not flashy
- should not interrupt reading
- should stay visually consistent with the article

## Fixed prompt structure

```text
【Subject / Visual Content】 + 【Scene / Mood】 + 【Style】 + 【Color】 + 【Composition / Quality】 + 【Negative Words】
```

## Unified negative words

```text
模糊，低清，水印，文字，杂乱，扭曲，瑕疵，低俗，过度渲染
```

## Why this rule exists

The earlier image prompts behaved too much like article-summary prompts and often produced images with garbled pseudo-text or overly text-heavy compositions.

The current goal is to prioritize:

- no text in images
- visual cleanliness
- consistency
- usable output for new-media publishing
