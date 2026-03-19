#!/usr/bin/env python3
import argparse
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Tuple
import requests

STYLE_PROMPTS = {
    "干货": "专业、信息密度高、实用、结构清晰。开头快速给收益，正文多用方法、步骤、案例。",
    "情感": "温暖、有共情力、有故事感。允许适度抒情，但不要空泛。",
    "资讯": "简洁、客观、信息优先。优先清楚传达事实、变化、结论。",
    "活泼": "轻松、接地气、节奏明快。允许口语化，但不要油腻。",
}


class BaseProvider:
    def generate(self, prompt: str, *, model: str = "", temperature: float = 0.7, max_tokens: int = 1200) -> Tuple[str, Dict[str, Any]]:
        raise NotImplementedError


class MockProvider(BaseProvider):
    def generate(self, prompt: str, *, model: str = "", temperature: float = 0.7, max_tokens: int = 1200):
        content = "# 示例标题\n\n这是 mock provider 生成的占位文章。\n\n## 开头\n快速说明读者收益。\n\n## 主体一\n给出方法和步骤。\n\n## 主体二\n补充案例和提醒。\n\n## 结尾\n总结并给出自然 CTA。\n"
        return content, {"provider": "mock", "model": model or "mock"}


class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, base_url: str, api_key: str, timeout: int = 180, retries: int = 2, fallback_base_urls=None, fallback_models=None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.fallback_base_urls = [u.rstrip('/') for u in (fallback_base_urls or []) if str(u).strip()]
        self.fallback_models = [str(m).strip() for m in (fallback_models or []) if str(m).strip()]

    @staticmethod
    def _uniq(items):
        out = []
        seen = set()
        for item in items:
            if not item or item in seen:
                continue
            seen.add(item)
            out.append(item)
        return out

    def generate(self, prompt: str, *, model: str = "", temperature: float = 0.7, max_tokens: int = 1200):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        base_urls = self._uniq([self.base_url] + self.fallback_base_urls)
        model_candidates = self._uniq([model] + self.fallback_models)
        if not model_candidates:
            raise ValueError('No model candidate available for OpenAI-compatible provider')

        errors = []

        for base_url in base_urls:
            url = base_url.rstrip('/') + '/chat/completions'
            for model_name in model_candidates:
                payload = {
                    "model": model_name,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "system", "content": "你是微信公众号写作助手。输出纯 Markdown 正文，不要解释，不要加多余前言。"},
                        {"role": "user", "content": prompt},
                    ],
                }

                last_err = None
                for attempt in range(self.retries + 1):
                    try:
                        r = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                        r.raise_for_status()
                        data = r.json()
                        content = data["choices"][0]["message"]["content"]
                        return content, {
                            "provider": "openai_compatible",
                            "model": model_name,
                            "id": data.get("id", ""),
                            "attempt": attempt + 1,
                            "base_url": base_url,
                            "fallback_used": (base_url != self.base_url) or (model_name != model),
                        }
                    except Exception as e:
                        last_err = e
                        if attempt < self.retries:
                            time.sleep(2 * (attempt + 1))
                errors.append(f'base_url={base_url}, model={model_name}, error={type(last_err).__name__}: {last_err}')

        raise RuntimeError('All LLM fallback candidates failed: ' + ' | '.join(errors))


class FallbackTextRouter(BaseProvider):
    def __init__(self, candidates):
        self.candidates = candidates

    def generate(self, prompt: str, *, model: str = "", temperature: float = 0.7, max_tokens: int = 1200):
        errors = []
        for idx, cand in enumerate(self.candidates, start=1):
            if cand.get('enabled', True) is False:
                continue
            provider = (cand.get('provider') or 'openai_compatible').strip()
            try:
                if provider == 'mock':
                    content, meta = MockProvider().generate(prompt, model=model, temperature=temperature, max_tokens=max_tokens)
                    return content, {**meta, 'router_candidate_index': idx, 'router_candidate_provider': provider, 'router_fallback_used': idx > 1}

                if provider == 'openai_compatible':
                    base_url = (cand.get('base_url') or '').strip()
                    api_key = (cand.get('api_key') or '').strip()
                    model_name = (cand.get('model') or model or '').strip()
                    if not base_url or not api_key or not model_name:
                        raise ValueError('missing base_url/api_key/model')
                    p = OpenAICompatibleProvider(
                        base_url,
                        api_key,
                        timeout=int(cand.get('timeout', 180) or 180),
                        retries=int(cand.get('retries', 2) or 2),
                        fallback_base_urls=cand.get('fallback_base_urls') or [],
                        fallback_models=cand.get('fallback_models') or [],
                    )
                    content, meta = p.generate(prompt, model=model_name, temperature=temperature, max_tokens=max_tokens)
                    return content, {
                        **meta,
                        'router_candidate_index': idx,
                        'router_candidate_provider': provider,
                        'router_fallback_used': idx > 1,
                    }

                raise ValueError(f'unsupported provider {provider}')
            except Exception as e:
                errors.append(f'candidate#{idx} provider={provider} error={type(e).__name__}: {e}')

        raise RuntimeError('All cross-provider LLM candidates failed: ' + ' | '.join(errors))


def _normalize_llm_candidates(cfg: Dict[str, Any]) -> list:
    raw = cfg.get('llm_candidates') or []
    normalized = []

    if isinstance(raw, list) and raw:
        for item in raw:
            if not isinstance(item, dict):
                continue
            provider = str(item.get('provider', 'openai_compatible')).strip()
            normalized.append({
                'enabled': item.get('enabled', True),
                'provider': provider,
                'base_url': item.get('base_url', ''),
                'api_key': item.get('api_key', ''),
                'model': item.get('model', ''),
                'timeout': item.get('timeout', 180),
                'retries': item.get('retries', 2),
                'fallback_base_urls': item.get('fallback_base_urls', []),
                'fallback_models': item.get('fallback_models', []),
            })
        return normalized

    # Backward-compatible single-provider config
    normalized.append({
        'provider': cfg.get('llm_provider') or 'openai_compatible',
        'base_url': cfg.get('llm_base_url') or cfg.get('deepseek_base_url') or 'https://api.deepseek.com/v1',
        'api_key': cfg.get('llm_api_key') or cfg.get('deepseek_api_key') or '',
        'model': cfg.get('llm_model') or cfg.get('deepseek_model') or '',
        'timeout': cfg.get('llm_timeout', 180),
        'retries': cfg.get('llm_retries', 2),
        'fallback_base_urls': cfg.get('llm_fallback_base_urls') or cfg.get('fallback_llm_base_urls') or [],
        'fallback_models': cfg.get('llm_fallback_models') or cfg.get('fallback_llm_models') or [],
    })
    return normalized


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def make_provider(cfg: Dict[str, Any], override_provider: str = "") -> BaseProvider:
    # Cross-provider candidate router has highest priority when not overriding provider.
    if not override_provider:
        candidates = _normalize_llm_candidates(cfg)
        if candidates:
            return FallbackTextRouter(candidates)

    provider = override_provider or cfg.get("llm_provider") or "mock"
    if provider == "mock":
        return MockProvider()
    if provider == "openai_compatible":
        base_url = cfg.get("llm_base_url") or cfg.get("deepseek_base_url") or "https://api.deepseek.com/v1"
        api_key = cfg.get("llm_api_key") or cfg.get("deepseek_api_key")
        if not api_key:
            raise ValueError("Missing llm_api_key / deepseek_api_key")
        return OpenAICompatibleProvider(
            base_url,
            api_key,
            fallback_base_urls=cfg.get("llm_fallback_base_urls") or cfg.get("fallback_llm_base_urls") or [],
            fallback_models=cfg.get("llm_fallback_models") or cfg.get("fallback_llm_models") or [],
        )
    raise ValueError(f"Unsupported llm provider: {provider}")


def build_prompt(topic: str, style: str, keywords: str, length: int, title_hint: str, benchmark_summary: str, audience: str) -> str:
    style_rule = STYLE_PROMPTS.get(style, STYLE_PROMPTS["干货"])
    target_length = min(max(length, 600), 1200)
    return f"""
请写一篇适合微信公众号发布的 Markdown 文章。

主题：{topic}
风格：{style}
风格要求：{style_rule}
关键词：{keywords or '无'}
目标字数：约{target_length}字
标题提示：{title_hint or '无'}
目标受众：{audience or '泛公众号读者'}
对标文章风格摘要：{benchmark_summary or '无，按常规优质公众号文章写作'}

硬性要求：
1. 输出纯 Markdown。
2. 包含一个一级标题和 3-4 个二级标题。
3. 开头 2 段内说清文章价值。
4. 每段不要太长，适合公众号阅读。
5. 结尾自然，不要硬广。
6. 不要编造明显可核查但无依据的数据。
7. 不要照抄对标文章原句。
8. 先给稳定可发的首稿，不追求过长。
""".strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("topic")
    parser.add_argument("--style", default="干货")
    parser.add_argument("--keywords", default="")
    parser.add_argument("--length", type=int, default=1000)
    parser.add_argument("--title-hint", default="")
    parser.add_argument("--benchmark-summary", default="")
    parser.add_argument("--audience", default="")
    parser.add_argument("--provider", default="")
    parser.add_argument("--model", default="")
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument("--config", default=os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    parser.add_argument("--output-dir", default="./output")
    args = parser.parse_args()

    cfg = load_config(args.config)
    provider = make_provider(cfg, args.provider)
    model = args.model or cfg.get("llm_model") or cfg.get("deepseek_model") or ""
    prompt = build_prompt(args.topic, args.style, args.keywords, args.length, args.title_hint, args.benchmark_summary, args.audience)
    content, meta = provider.generate(prompt, model=model, temperature=args.temperature, max_tokens=args.max_tokens)

    os.makedirs(args.output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(args.output_dir, f"article-{ts}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

    print(json.dumps({
        "ok": True,
        "path": path,
        "topic": args.topic,
        "style": args.style,
        "provider": meta.get("provider", ""),
        "model": meta.get("model", model),
        "meta": meta,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
