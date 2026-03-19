#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from typing import Dict, Any, Tuple

from write_article import load_config, make_provider

TITLE_MAX_BYTES = 96


def utf8_len(text: str) -> int:
    return len(text.encode('utf-8'))


def normalize_title(title: str) -> str:
    replacements = {
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '—': '-',
        '–': '-',
        '，': ',',
        '：': ':',
        '；': ';',
        '（': '(',
        '）': ')',
    }
    for old, new in replacements.items():
        title = title.replace(old, new)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def trim_title(title: str, max_bytes: int = TITLE_MAX_BYTES) -> str:
    if utf8_len(title) <= max_bytes:
        return title
    buf = []
    current = 0
    for ch in title:
        size = len(ch.encode('utf-8'))
        if current + size > max_bytes:
            break
        buf.append(ch)
        current += size
    return ''.join(buf).rstrip(' ，,：:；;、')


def extract_markdown_title_and_body(markdown_text: str) -> Tuple[str, str]:
    lines = markdown_text.splitlines()
    title = ''
    body_lines = []
    for line in lines:
        if not title and line.startswith('# '):
            title = line[2:].strip()
            continue
        body_lines.append(line)
    return title or '未命名文章', '\n'.join(body_lines).strip()


def fallback_digest(body: str, max_chars: int = 72) -> str:
    text = re.sub(r'[#>*`_\-]+', ' ', body)
    text = re.sub(r'!\[.*?\]\(.*?\)', ' ', text)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:max_chars].rstrip('，。；;、,. ') if text else ''


def build_metadata_prompt(markdown_title: str, body: str) -> str:
    body_preview = body[:1800]
    return f"""
你在为微信公众号草稿箱生成元数据。

原始标题：{markdown_title}
文章正文节选：
{body_preview}

请只输出 JSON，对象包含两个字段：
- short_title: 适合公众号草稿箱和发布使用的标题。优先保证表达完整、自然、有吸引力，不要为了变短而牺牲信息量；只有在明显过长时才适度收敛。
- digest: 40 到 80 字摘要，概括读者收益和内容重点，不要空话，不要营销腔

要求：
1. short_title 不要使用夸张标题党。
2. short_title 优先保留主题、利益点和场景感。
3. short_title 不是越短越好，不要机械压缩。
4. digest 必须是完整自然的中文句子。
5. 不要输出 markdown，不要输出解释。
""".strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('markdown_file')
    parser.add_argument('--provider', default='')
    parser.add_argument('--model', default='')
    parser.add_argument('--config', default=os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    args = parser.parse_args()

    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    markdown_title, body = extract_markdown_title_and_body(markdown_text)
    cfg = load_config(args.config)
    provider = make_provider(cfg, args.provider)
    model = args.model or cfg.get('llm_model') or cfg.get('deepseek_model') or ''

    prompt = build_metadata_prompt(markdown_title, body)
    short_title = trim_title(normalize_title(markdown_title))
    digest = fallback_digest(body)
    meta_raw: Dict[str, Any] = {}

    try:
        content, meta = provider.generate(prompt, model=model, temperature=0.3, max_tokens=220)
        meta_raw = meta
        parsed = json.loads(content.strip())
        candidate_title = normalize_title(str(parsed.get('short_title', '')).strip())
        candidate_digest = str(parsed.get('digest', '')).strip()
        if candidate_title:
            short_title = trim_title(candidate_title)
        if candidate_digest:
            digest = candidate_digest[:120].strip()
    except Exception as e:
        print(f'[WARN] extract_article_metadata failed: {type(e).__name__}: {e}', file=sys.stderr)

    print(json.dumps({
        'ok': True,
        'markdown_title': markdown_title,
        'short_title': short_title,
        'digest': digest,
        'short_title_utf8_bytes': utf8_len(short_title),
        'provider_meta': meta_raw,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
