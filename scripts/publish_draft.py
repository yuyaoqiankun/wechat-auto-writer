#!/usr/bin/env python3
import argparse
import ast
import json
import os
import re
from datetime import datetime
from html import unescape
from typing import Dict, Any
from wechat_capability import wechat_manage_capability


WECHAT_TITLE_MAX_BYTES = 96
WECHAT_TITLE_LIMIT_ERRCODES = {45028}


def extract_title_from_html(html: str) -> str:
    m = re.search(r'<h1[^>]*>(.*?)</h1>', html, flags=re.I | re.S)
    if not m:
        return '未命名文章'
    title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    title = unescape(title)
    return title or '未命名文章'


def contains_replacement_char(text: str) -> bool:
    return '�' in text


def maybe_decode_unicode_escapes(text: str) -> str:
    if '\\u' not in text:
        return text
    try:
        return text.encode('utf-8').decode('unicode_escape')
    except Exception:
        return text


def utf8_len(text: str) -> int:
    return len(text.encode('utf-8'))


def normalize_title_for_wechat(title: str) -> str:
    title = unescape(title)
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


def trim_title_to_wechat_limit(title: str, max_bytes: int = WECHAT_TITLE_MAX_BYTES) -> str:
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
    return ''.join(buf).rstrip(' ，,：:；;、') or '未命名文章'


def extract_draft_article(draft_get_response: Dict[str, Any]) -> Dict[str, Any]:
    news_item = draft_get_response.get('news_item') or []
    if isinstance(news_item, list) and news_item:
        return news_item[0]
    item = draft_get_response.get('item') or []
    if isinstance(item, list) and item:
        return item[0]
    return {}


def extract_wechat_error_fields(exc: Exception) -> Dict[str, Any]:
    if not isinstance(exc, RuntimeError):
        return {}
    text = str(exc).strip()
    try:
        data = ast.literal_eval(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def is_title_limit_error(exc: Exception) -> bool:
    fields = extract_wechat_error_fields(exc)
    errcode = fields.get('errcode')
    if isinstance(errcode, int) and errcode in WECHAT_TITLE_LIMIT_ERRCODES:
        return True

    err_str = str(exc).lower()
    fallback_markers = [
        'title size out of limit',
        'title out of limit',
        '标题',
        '超限',
        '过长',
    ]
    return any(marker in err_str for marker in fallback_markers)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('html_file')
    parser.add_argument('cover_image')
    parser.add_argument('--title', default='')
    parser.add_argument('--config', default=os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    parser.add_argument('--author', default='')
    parser.add_argument('--digest', default='')
    parser.add_argument('--content-source-url', default='')
    parser.add_argument('--need-open-comment', type=int, default=0)
    parser.add_argument('--only-fans-can-comment', type=int, default=0)
    parser.add_argument('--debug-dir', default=os.path.join(os.path.dirname(__file__), '..', 'output', 'debug'))
    parser.add_argument('--no-debug', action='store_true')
    args = parser.parse_args()

    with open(args.config, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    with open(args.html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    raw_title = args.title or extract_title_from_html(html)
    normalized_title = normalize_title_for_wechat(raw_title)
    title = trim_title_to_wechat_limit(normalized_title)
    author = args.author or cfg.get('author', '')
    digest = args.digest or cfg.get('digest', '')
    content_source_url = args.content_source_url or cfg.get('content_source_url', '')

    run_id = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    os.makedirs(args.debug_dir, exist_ok=True)
    debug_payload_path = os.path.join(args.debug_dir, f'draft-upload-payload-{run_id}.json')

    thumb = wechat_manage_capability(cfg['appid'], cfg['appsecret'], 'material', 'add_image', file_path=args.cover_image)
    base_article = {
        'content': html,
        'thumb_media_id': thumb['media_id'],
    }
    if author:
        base_article['author'] = author
    if digest:
        base_article['digest'] = digest
    if content_source_url:
        base_article['content_source_url'] = content_source_url
    if args.need_open_comment:
        base_article['need_open_comment'] = args.need_open_comment
    if args.only_fans_can_comment:
        base_article['only_fans_can_comment'] = args.only_fans_can_comment

    attempted_titles = []
    title_candidates = []
    seen = set()
    for candidate in [normalized_title, trim_title_to_wechat_limit(normalized_title, 72), trim_title_to_wechat_limit(normalized_title, 60), trim_title_to_wechat_limit(normalized_title, 48), trim_title_to_wechat_limit(normalized_title, 36)]:
        candidate = candidate.strip()
        if candidate and candidate not in seen:
            title_candidates.append(candidate)
            seen.add(candidate)

    result = None
    article = None
    media_id = None
    last_err = None
    for candidate_title in title_candidates:
        attempted_titles.append({'title': candidate_title, 'utf8_bytes': utf8_len(candidate_title)})
        article = {**base_article, 'title': candidate_title}
        if not args.no_debug:
            with open(debug_payload_path, 'w', encoding='utf-8') as f:
                json.dump({'article': article, 'html_file': args.html_file, 'cover_image': args.cover_image, 'attempted_titles': attempted_titles}, f, ensure_ascii=False, indent=2)
        try:
            result = wechat_manage_capability(cfg['appid'], cfg['appsecret'], 'draft', 'add', articles=[article])
            title = candidate_title
            media_id = result.get('media_id', '')
            break
        except Exception as e:
            last_err = e
            if not is_title_limit_error(e):
                raise
    if result is None:
        raise last_err if last_err else RuntimeError('draft add failed')
    if not media_id:
        raise RuntimeError('draft add succeeded but media_id is missing')

    readback = {}
    readback_article = {}
    validation = {'title_match': None, 'content_has_replacement_char': None, 'title_has_replacement_char': None}
    readback = wechat_manage_capability(cfg['appid'], cfg['appsecret'], 'draft', 'get', media_id=media_id)
    readback_article = extract_draft_article(readback)
    readback_title = maybe_decode_unicode_escapes(str(readback_article.get('title', '')))
    readback_content = maybe_decode_unicode_escapes(str(readback_article.get('content', '')))
    validation = {
        'title_match': readback_title == title,
        'content_has_replacement_char': contains_replacement_char(readback_content),
        'title_has_replacement_char': contains_replacement_char(readback_title),
    }
    debug_readback_path = os.path.join(args.debug_dir, f'draft-readback-{run_id}.json')
    if not args.no_debug:
        with open(debug_readback_path, 'w', encoding='utf-8') as f:
            json.dump(readback, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        'ok': True,
        'title': title,
        'raw_title': raw_title,
        'normalized_title': normalized_title,
        'digest': digest,
        'title_utf8_bytes': utf8_len(title),
        'raw_title_utf8_bytes': utf8_len(raw_title),
        'normalized_title_utf8_bytes': utf8_len(normalized_title),
        'thumb_media_id': thumb['media_id'],
        'draft_result': result,
        'media_id': media_id,
        'readback_validation': validation,
        'readback_title': readback_article.get('title', ''),
        'debug_payload_path': '' if args.no_debug else debug_payload_path,
        'debug_readback_path': '' if args.no_debug else debug_readback_path,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
