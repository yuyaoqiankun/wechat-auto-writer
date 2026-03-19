# Write Provider Stability

## Current strategy

- keep first draft short and stable
- default length near 1000 chars/words-scale target
- 3-4 sections only
- default `max_tokens` reduced to 900
- default temperature reduced to 0.6
- retry 2 times with short backoff

## Why

The current upstream gateway can answer tiny requests reliably but may time out on heavier generation requests. A shorter first draft is more reliable, and later expansion/refinement can be added as a separate step.

## Next possible improvements

- two-pass generation: outline -> full draft
- expand section by section instead of one giant request
- adaptive retry with smaller token budget after timeout
