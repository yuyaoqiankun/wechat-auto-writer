#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple

import requests
from PIL import Image, ImageDraw

from write_article import load_config, make_provider as make_text_provider

NEGATIVE_WORDS = '文字，水印，logo，低清，模糊，畸形手指，多余肢体，杂乱背景，过度锐化'
DEFAULT_PROMPT_STRATEGY = 'full'


class MockImageProvider:
    def render(self, prompt: str, output_path: str, **kwargs):
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        width = int(kwargs.get('width', 1024))
        height = int(kwargs.get('height', 576))
        bg = kwargs.get('background', '#F6E7DA')
        fg = kwargs.get('foreground', '#7A4B37')
        img = Image.new('RGB', (width, height), bg)
        draw = ImageDraw.Draw(img)
        title = (prompt[:90] + '...') if len(prompt) > 90 else prompt
        draw.rounded_rectangle((40, 40, width - 40, height - 40), radius=24, outline=fg, width=4)
        draw.text((70, 80), 'Mock WeChat Image', fill=fg)
        draw.text((70, 150), title, fill=fg)
        img.save(output_path, format='PNG')
        return {'provider': 'mock-image', 'output_path': output_path, 'prompt': prompt, 'width': width, 'height': height}


class OpenAICompatibleImagesProvider:
    def __init__(self, base_url: str, api_key: str, model: str, fallback_base_urls=None, fallback_models=None, retries: int = 1):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.fallback_base_urls = [u.rstrip('/') for u in (fallback_base_urls or []) if str(u).strip()]
        self.fallback_models = [str(m).strip() for m in (fallback_models or []) if str(m).strip()]
        self.retries = retries

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

    def render(self, prompt: str, output_path: str, **kwargs):
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        size = kwargs.get('size', '1024x1024')
        base_urls = self._uniq([self.base_url] + self.fallback_base_urls)
        models = self._uniq([self.model] + self.fallback_models)
        errors = []

        for base_url in base_urls:
            url = base_url.rstrip('/') + '/images/generations'
            for model_name in models:
                payload = {
                    'model': model_name,
                    'prompt': prompt,
                    'size': size,
                }
                last_err = None
                for attempt in range(self.retries + 1):
                    try:
                        r = requests.post(url, headers=headers, json=payload, timeout=300)
                        r.raise_for_status()
                        data = r.json()
                        item = (data.get('data') or [{}])[0]
                        if item.get('b64_json'):
                            with open(output_path, 'wb') as f:
                                f.write(base64.b64decode(item['b64_json']))
                        elif item.get('url'):
                            img = requests.get(item['url'], timeout=300)
                            img.raise_for_status()
                            with open(output_path, 'wb') as f:
                                f.write(img.content)
                        else:
                            raise RuntimeError(f'No image payload returned: {data}')
                        return {
                            'provider': 'openai_compatible_images',
                            'output_path': output_path,
                            'prompt': prompt,
                            'response_meta': {
                                'created': data.get('created'),
                                'base_url': base_url,
                                'model': model_name,
                                'attempt': attempt + 1,
                                'fallback_used': (base_url != self.base_url) or (model_name != self.model),
                            }
                        }
                    except Exception as e:
                        last_err = e
                errors.append(f'base_url={base_url}, model={model_name}, error={type(last_err).__name__}: {last_err}')

        raise RuntimeError('All image fallback candidates failed: ' + ' | '.join(errors))


class DashScopeImageProvider:
    """Minimal DashScope Qwen-Image provider (multimodal-generation API)."""

    def __init__(self, api_key: str, model: str, retries: int = 1, endpoint: str = ''):
        self.api_key = api_key
        self.model = model
        self.retries = retries
        self.endpoint = endpoint or 'https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'

    def render(self, prompt: str, output_path: str, **kwargs):
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

        size = kwargs.get('size', '1024x1024')
        if isinstance(size, str) and 'x' in size:
            w, h = size.lower().split('x', 1)
            size_str = f'{int(w)}*{int(h)}'
        elif isinstance(size, str) and '*' in size:
            size_str = size
        else:
            size_str = '1024*1024'

        payload = {
            'model': self.model,
            'input': {
                'messages': [
                    {
                        'role': 'user',
                        'content': [{'text': prompt}],
                    }
                ]
            },
            'parameters': {
                'size': size_str,
                'n': 1,
                'prompt_extend': True,
                'watermark': False,
            },
        }

        last_err = None
        for attempt in range(self.retries + 1):
            try:
                r = requests.post(self.endpoint, headers=headers, json=payload, timeout=300)
                r.raise_for_status()
                data = r.json()
                output = data.get('output', {}) if isinstance(data, dict) else {}

                img_url = ''
                # Official sync response format:
                # output.choices[0].message.content[0].image
                choices = output.get('choices') or []
                if choices and isinstance(choices[0], dict):
                    message = choices[0].get('message') or {}
                    content = message.get('content') or []
                    if content and isinstance(content[0], dict):
                        img_url = content[0].get('image', '')

                # Compatibility fallback for other envelope formats.
                if not img_url:
                    results = output.get('results') or []
                    if results and isinstance(results[0], dict):
                        img_url = results[0].get('url', '')

                if not img_url:
                    raise RuntimeError(f'No image url in DashScope response: {data}')

                img = requests.get(img_url, timeout=300)
                img.raise_for_status()
                with open(output_path, 'wb') as f:
                    f.write(img.content)

                return {
                    'provider': 'dashscope_image',
                    'output_path': output_path,
                    'prompt': prompt,
                    'response_meta': {
                        'base_url': 'dashscope',
                        'model': self.model,
                        'attempt': attempt + 1,
                        'request_id': data.get('request_id', ''),
                        'fallback_used': False,
                    },
                }
            except Exception as e:
                last_err = e

        raise RuntimeError(f'DashScope image generation failed: {type(last_err).__name__}: {last_err}')


class FallbackImageRouter:
    def __init__(self, candidates):
        self.candidates = candidates

    def render(self, prompt: str, output_path: str, **kwargs):
        errors = []
        for idx, cand in enumerate(self.candidates, start=1):
            if cand.get('enabled', True) is False:
                continue
            provider = (cand.get('provider') or 'openai_compatible_images').strip()
            try:
                if provider == 'mock':
                    result = MockImageProvider().render(prompt, output_path, **kwargs)
                    result['response_meta'] = {
                        'router_candidate_index': idx,
                        'router_candidate_provider': provider,
                        'router_fallback_used': idx > 1,
                    }
                    return result

                if provider == 'openai_compatible_images':
                    base_url = str(cand.get('base_url', '')).strip()
                    api_key = str(cand.get('api_key', '')).strip()
                    model = str(cand.get('model', '')).strip()
                    if not base_url or not api_key or not model:
                        raise ValueError('missing base_url/api_key/model')
                    p = OpenAICompatibleImagesProvider(
                        base_url,
                        api_key,
                        model,
                        fallback_base_urls=cand.get('fallback_base_urls') or [],
                        fallback_models=cand.get('fallback_models') or [],
                        retries=int(cand.get('retries', 1) or 1),
                    )
                    result = p.render(prompt, output_path, **kwargs)
                    rm = result.get('response_meta', {})
                    result['response_meta'] = {
                        **rm,
                        'router_candidate_index': idx,
                        'router_candidate_provider': provider,
                        'router_fallback_used': idx > 1,
                    }
                    return result

                if provider == 'dashscope_image':
                    api_key = str(cand.get('api_key', '')).strip()
                    model = str(cand.get('model', '')).strip()
                    endpoint = str(cand.get('endpoint', '')).strip()
                    base_url = str(cand.get('base_url', '')).strip()
                    if not endpoint and base_url:
                        endpoint = base_url.rstrip('/') + '/services/aigc/multimodal-generation/generation'
                    if not api_key or not model:
                        raise ValueError('missing api_key/model')
                    p = DashScopeImageProvider(
                        api_key=api_key,
                        model=model,
                        retries=int(cand.get('retries', 1) or 1),
                        endpoint=endpoint,
                    )
                    result = p.render(prompt, output_path, **kwargs)
                    rm = result.get('response_meta', {})
                    result['response_meta'] = {
                        **rm,
                        'router_candidate_index': idx,
                        'router_candidate_provider': provider,
                        'router_fallback_used': idx > 1,
                    }
                    return result

                raise ValueError(f'unsupported provider {provider}')
            except Exception as e:
                errors.append(f'candidate#{idx} provider={provider} error={type(e).__name__}: {e}')

        raise RuntimeError('All cross-provider image candidates failed: ' + ' | '.join(errors))


def _normalize_image_candidates(cfg: Dict[str, Any]) -> list:
    raw = cfg.get('image_candidates') or []
    normalized = []

    if isinstance(raw, list) and raw:
        for item in raw:
            if not isinstance(item, dict):
                continue
            provider = str(item.get('provider', 'openai_compatible_images')).strip()
            normalized.append({
                'enabled': item.get('enabled', True),
                'provider': provider,
                'base_url': item.get('base_url', ''),
                'api_key': item.get('api_key', ''),
                'model': item.get('model', ''),
                'retries': item.get('retries', 1),
                'fallback_base_urls': item.get('fallback_base_urls', []),
                'fallback_models': item.get('fallback_models', []),
            })
        return normalized

    normalized.append({
        'provider': cfg.get('image_provider') or 'openai_compatible_images',
        'base_url': cfg.get('image_base_url') or '',
        'api_key': cfg.get('image_api_key') or '',
        'model': cfg.get('image_model') or '',
        'retries': cfg.get('image_request_retries', 1),
        'fallback_base_urls': cfg.get('image_fallback_base_urls') or cfg.get('fallback_image_base_urls') or [],
        'fallback_models': cfg.get('image_fallback_models') or cfg.get('fallback_image_models') or [],
    })
    return normalized


def make_image_provider(cfg: Dict[str, Any], override: str = ''):
    # Cross-provider candidate router has highest priority when not overriding provider.
    if not override:
        candidates = _normalize_image_candidates(cfg)
        if candidates:
            return FallbackImageRouter(candidates)

    provider = override or cfg.get('image_provider') or 'mock'
    if provider == 'mock':
        return MockImageProvider()
    if provider == 'openai_compatible_images':
        return OpenAICompatibleImagesProvider(
            cfg['image_base_url'],
            cfg['image_api_key'],
            cfg['image_model'],
            fallback_base_urls=cfg.get('image_fallback_base_urls') or cfg.get('fallback_image_base_urls') or [],
            fallback_models=cfg.get('image_fallback_models') or cfg.get('fallback_image_models') or [],
            retries=int(cfg.get('image_request_retries', 1) or 1),
        )
    raise ValueError(f'Unsupported image provider: {provider}')


def _extract_json_object(text: str) -> Dict[str, Any]:
    text = text.strip()
    if text.startswith('{') and text.endswith('}'):
        return json.loads(text)
    m = re.search(r'\{[\s\S]*\}', text)
    if not m:
        raise ValueError('No JSON object found in LLM response')
    return json.loads(m.group(0))


def _extract_first_paragraph(content: str) -> str:
    lines = content.splitlines()
    buf: List[str] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            if buf:
                break
            continue
        if line.startswith('#'):
            continue
        if line.startswith('!['):
            continue
        buf.append(line)
    if not buf:
        return ''
    return re.sub(r'\s+', ' ', ' '.join(buf)).strip()


def _build_visual_prompt_full(title: str, content: str, style: str) -> str:
    content_preview = content[:3500]
    return f"""
你是资深公众号视觉总监 + AIGC提示词工程师。
任务：根据“文章标题+正文”输出可直接用于文生图模型的提示词方案（封面图1条 + 正文插图1条）。
目标：漂亮、吸引眼球、信息表达准确、风格统一、可用于公众号排版。

【输入】
- 标题：{title}
- 正文：{content_preview}
- 视觉风格偏好：{style or '轻插画'}

【全局硬约束】
1) 视觉风格优先遵循“视觉风格偏好”，同时保持现代、干净、留白、质感高级
2) 画面中禁止出现：文字、水印、logo、品牌名、二维码
3) 禁止低质量问题：低清、模糊、畸形手指、多余肢体、脏乱背景、过度锐化
4) 封面与正文图要同一视觉家族，但正文图场景需有变化
5) 输出必须严格按 JSON，不要额外解释

【输出 JSON 结构】
{{
  "visual_strategy_card": {{
    "target_reader": "1句话",
    "core_emotions": ["希望"],
    "visual_narrative": "1句话",
    "style_anchor": "与视觉风格偏好一致的风格锚",
    "keywords": ["关键词1", "关键词2"],
    "banned_elements": ["禁用元素1", "禁用元素2"]
  }},
  "cover_prompt": {{
    "positive": "封面正向提示词（需包含：主体、构图、色彩、光线、风格词、画质词）",
    "negative": "{NEGATIVE_WORDS}",
    "ratio": "1.8:1（900x500，建议先生成1800x1000）"
  }},
  "body_prompt": {{
    "paragraph_topic": "最核心段落主题",
    "positive": "正文图正向提示词（需包含：主体、构图、色彩、光线、风格词、画质词）",
    "negative": "{NEGATIVE_WORDS}",
    "ratio": "16:9"
  }}
}}
""".strip()


def _build_visual_prompt_lite(title: str, content: str, max_chars: int, style: str) -> Tuple[str, str]:
    first_paragraph = _extract_first_paragraph(content)
    first_paragraph = first_paragraph[:max(max_chars, 80)]
    return (
        f"""
你是资深公众号视觉总监 + AIGC提示词工程师。
任务：在 token 成本优先场景，基于“标题 + 首段摘要”快速生成提示词（封面图1条 + 正文图1条）。
目标：快速、稳定、可用，不追求复杂分镜。

【输入】
- 标题：{title}
- 首段摘要（截断）：{first_paragraph or '无'}
- 视觉风格偏好：{style or '轻插画'}

【轻量策略硬约束】
1) 只使用标题与首段摘要推断主要信息，不读取全文细节
2) 视觉风格优先遵循“视觉风格偏好”，同时保持现代、干净、留白、质感高级
3) 封面图与正文图各输出 1 条提示词
4) 画面中禁止出现：文字、水印、logo、品牌名、二维码
5) 输出必须严格按 JSON，不要额外解释

【输出 JSON 结构】
{{
  "visual_strategy_card": {{
    "strategy": "lite",
    "core_subject": "1句话",
    "core_emotions": ["希望"],
    "style_anchor": "与视觉风格偏好一致的风格锚",
    "keywords": ["关键词1", "关键词2"],
    "banned_elements": ["禁用元素1", "禁用元素2"]
  }},
  "cover_prompt": {{
    "positive": "封面正向提示词（需包含：主体、构图、色彩、光线、风格词、画质词）",
    "negative": "{NEGATIVE_WORDS}",
    "ratio": "1.8:1（900x500，建议先生成1800x1000）"
  }},
  "body_prompt": {{
    "paragraph_topic": "正文图主题（由标题+首段归纳）",
    "positive": "正文图正向提示词（需包含：主体、构图、色彩、光线、风格词、画质词）",
    "negative": "{NEGATIVE_WORDS}",
    "ratio": "16:9"
  }}
}}
""".strip(),
        first_paragraph,
    )


def _build_fallback_cover(topic: str, title: str, style: str) -> str:
    return (
        f'轻插画风格微信公众号封面图，主题:{topic}，标题意图:{title}，整体气质:{style}，'
        '构图简洁，主体明确，前中后景分层，留白充足，低饱和配色，柔和光线，高清细节，无文字无水印无logo'
    )


def _build_fallback_body(topic: str, section_title: str, section_hint: str, style: str) -> str:
    snippet = re.sub(r'\s+', ' ', section_hint or '').strip()[:120]
    return (
        f'轻插画风格公众号正文插图，主题:{topic}，段落主题:{section_title}，内容要点:{snippet}，整体气质:{style}，'
        '画面干净，留白合理，主体突出，构图稳定，色彩克制，柔和光线，高清细节，无文字无水印无logo'
    )


def _parse_llm_prompts(data: Dict[str, Any], fallback_cover: str, fallback_body: str) -> Tuple[str, str, Dict[str, Any]]:
    strategy = data.get('visual_strategy_card', {}) if isinstance(data, dict) else {}

    cover_prompt = fallback_cover
    cover = data.get('cover_prompt', {}) if isinstance(data, dict) else {}
    if isinstance(cover, dict):
        positive = str(cover.get('positive', '')).strip()
        negative = str(cover.get('negative', '')).strip() or NEGATIVE_WORDS
        ratio = str(cover.get('ratio', '')).strip() or '1.8:1（900x500，建议先生成1800x1000）'
        if positive:
            cover_prompt = f'{positive}。比例建议:{ratio}。负向词:{negative}'

    body_prompt = fallback_body
    body = data.get('body_prompt', {}) if isinstance(data, dict) else {}
    if isinstance(body, dict):
        positive = str(body.get('positive', '')).strip()
        negative = str(body.get('negative', '')).strip() or NEGATIVE_WORDS
        ratio = str(body.get('ratio', '')).strip() or '16:9'
        if positive:
            body_prompt = f'{positive}。比例建议:{ratio}。负向词:{negative}'

    return cover_prompt, body_prompt, strategy if isinstance(strategy, dict) else {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--topic', default='')
    parser.add_argument('--title', default='')
    parser.add_argument('--style', default='轻插画')
    parser.add_argument('--output-dir', default='./output')
    parser.add_argument('--body-plan', default='')
    parser.add_argument('--markdown-file', default='')
    parser.add_argument('--provider', default='')
    parser.add_argument('--prompt-strategy', default='')
    parser.add_argument('--lite-content-chars', type=int, default=0)
    parser.add_argument('--config', default=os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    args = parser.parse_args()

    cfg = load_config(args.config)
    image_provider = make_image_provider(cfg, args.provider)
    os.makedirs(args.output_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')

    plan = {'planned_images': []}
    if args.body_plan:
        with open(args.body_plan, 'r', encoding='utf-8') as f:
            plan = json.load(f)

    body_item = (plan.get('planned_images') or [{}])[0]
    fallback_cover = _build_fallback_cover(args.topic, args.title, args.style)
    fallback_body = _build_fallback_body(args.topic, body_item.get('section_title', ''), body_item.get('section_hint', ''), args.style)

    cover_prompt = fallback_cover
    body_prompt = fallback_body
    prompt_source = 'template'
    prompt_strategy = (args.prompt_strategy or cfg.get('image_prompt_strategy') or DEFAULT_PROMPT_STRATEGY).strip().lower()
    if prompt_strategy not in ('full', 'lite'):
        prompt_strategy = DEFAULT_PROMPT_STRATEGY

    lite_chars = args.lite_content_chars or int(cfg.get('image_prompt_lite_content_chars', 240) or 240)
    if lite_chars < 80:
        lite_chars = 80

    visual_strategy_card: Dict[str, Any] = {}
    prompt_llm_meta: Dict[str, Any] = {}

    content = ''
    if args.markdown_file and os.path.exists(args.markdown_file):
        with open(args.markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()

    try:
        text_provider = make_text_provider(cfg, cfg.get('llm_provider', ''))
        model = cfg.get('llm_model') or cfg.get('deepseek_model') or ''

        prompt_request = _build_visual_prompt_full(args.title or args.topic, content, args.style)
        lite_first_paragraph = ''
        if prompt_strategy == 'lite':
            prompt_request, lite_first_paragraph = _build_visual_prompt_lite(args.title or args.topic, content, lite_chars, args.style)

        response_text, prompt_llm_meta = text_provider.generate(prompt_request, model=model, temperature=0.6, max_tokens=1200)
        parsed = _extract_json_object(response_text)
        cover_prompt, body_prompt, visual_strategy_card = _parse_llm_prompts(parsed, fallback_cover, fallback_body)

        if prompt_strategy == 'lite':
            visual_strategy_card = {
                **(visual_strategy_card or {}),
                'strategy': 'lite',
                'first_paragraph_chars': len(lite_first_paragraph),
            }

        prompt_llm_meta = {
            **(prompt_llm_meta or {}),
            'prompt_strategy': prompt_strategy,
            'lite_content_chars': lite_chars if prompt_strategy == 'lite' else 0,
        }
        prompt_source = 'llm'
    except Exception as e:
        prompt_llm_meta = {
            'error': f'{type(e).__name__}: {e}',
            'prompt_strategy': prompt_strategy,
            'lite_content_chars': lite_chars if prompt_strategy == 'lite' else 0,
        }

    cover_path = os.path.join(args.output_dir, f'cover-{ts}.png')
    cover_meta = image_provider.render(cover_prompt, cover_path, width=1800, height=1000, size='1792x1024')

    body_results: List[Dict[str, Any]] = []
    planned_images = plan.get('planned_images', [])[:1]
    for item in planned_images:
        result = image_provider.render(body_prompt, item['image_path'], width=1280, height=720, size='1280x720')
        body_results.append({
            'section_title': item.get('section_title', ''),
            'paragraph_topic': item.get('section_title', ''),
            'prompt_source': prompt_source,
            **result,
        })

    print(json.dumps({
        'ok': True,
        'cover': {**cover_meta, 'prompt_source': prompt_source},
        'body_images': body_results,
        'visual_strategy_card': visual_strategy_card,
        'prompt_source': prompt_source,
        'prompt_strategy': prompt_strategy,
        'prompt_llm_meta': prompt_llm_meta,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
