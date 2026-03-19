#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from typing import List, Dict, Any

from archive_utils import make_run_dir

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCRIPTS_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(BASE_DIR, 'config.json')
DEFAULT_PYTHON = '/root/.agent-reach/venv/bin/python'
PYTHON_BIN = DEFAULT_PYTHON if os.path.exists(DEFAULT_PYTHON) else sys.executable

IMAGE_STYLE_PRESETS = {
    'pro-1': '编辑感概念插画，细节丰富，信息表达清晰，分层构图，专业高级，非叙事',
    'pro-2': '商业杂志视觉风，高级配色与材质细节，克制光影，主体明确，非叙事',
    'pro-3': '科技视觉风，空间层次与结构感强，精致光影，丰富但不花哨，非信息图',
}


def run_py(script: str, args: List[str]) -> Dict[str, Any]:
    cmd = [PYTHON_BIN, os.path.join(SCRIPTS_DIR, script)] + args
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f'{script} failed\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}')
    last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else '{}'
    return json.loads(last)


def maybe_compress(path: str, width: int, height: int, max_kb: int) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {'output_path': path, 'compressed': False, 'reason': 'missing_file'}
    try:
        result = run_py('compress_image.py', [path, '--width', str(width), '--height', str(height), '--max-kb', str(max_kb)])
        result['compressed'] = True
        return result
    except Exception as e:
        return {'output_path': path, 'compressed': False, 'reason': str(e)}


def extract_markdown_title(markdown_path: str, fallback: str) -> str:
    with open(markdown_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('# '):
                return re.sub(r'\s+', ' ', line[2:].strip()) or fallback
    return fallback


def rewrite_markdown_image_paths(markdown_path: str, replacements: Dict[str, str]) -> None:
    if not replacements:
        return
    with open(markdown_path, 'r', encoding='utf-8') as f:
        text = f.read()
    updated = text
    for old_path, new_path in replacements.items():
        updated = updated.replace(old_path, new_path)
    if updated != text:
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(updated)


def move_if_exists(src: str, dst: str) -> str:
    if not src or not os.path.exists(src):
        return src
    if os.path.abspath(src) == os.path.abspath(dst):
        return src
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst):
        os.remove(dst)
    shutil.move(src, dst)
    return dst


def normalize_run_artifacts(run_output_dir: str, article_path: str, html_path: str, cover_png_path: str, cover_jpg_path: str) -> Dict[str, str]:
    normalized = {}

    article_md = os.path.join(run_output_dir, 'article.md')
    article_html = os.path.join(run_output_dir, 'article.html')
    cover_png = os.path.join(run_output_dir, 'cover.png')
    cover_jpg = os.path.join(run_output_dir, 'cover.jpg')

    normalized['article_md'] = move_if_exists(article_path, article_md)
    normalized['article_html'] = move_if_exists(html_path, article_html)
    normalized['cover_png'] = move_if_exists(cover_png_path, cover_png)
    normalized['cover_jpg'] = move_if_exists(cover_jpg_path, cover_jpg)
    return normalized


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('topic')
    parser.add_argument('--style', default='干货')
    parser.add_argument('--keywords', default='')
    parser.add_argument('--length', type=int, default=1500)
    parser.add_argument('--title-hint', default='')
    parser.add_argument('--benchmark-summary', default='')
    parser.add_argument('--audience', default='')
    parser.add_argument('--provider', default='')
    parser.add_argument('--model', default='')
    parser.add_argument('--theme', default='shuimo/default')
    parser.add_argument('--max-body-images', type=int, default=1)
    parser.add_argument('--image-style', default='')
    parser.add_argument('--image-style-preset', default='')
    parser.add_argument('--image-prompt-strategy', default='')
    parser.add_argument('--image-prompt-lite-chars', type=int, default=0)
    parser.add_argument('--output-dir', default=os.path.join(BASE_DIR, 'output'))
    parser.add_argument('--publish-draft', action='store_true')
    parser.add_argument('--upload-images', action='store_true')
    parser.add_argument('--flat-output', action='store_true')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    run_output_dir = args.output_dir if args.flat_output else make_run_dir(args.output_dir, args.topic)
    os.makedirs(run_output_dir, exist_ok=True)

    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # Keep mock override explicit; otherwise let scripts pick router/candidates from config.
    provider_override_text = 'mock' if args.provider == 'mock' else ''

    preset_style = IMAGE_STYLE_PRESETS.get((args.image_style_preset or '').strip().lower(), '')
    effective_image_style = args.image_style or preset_style or cfg.get('image_style') or args.style

    article = run_py('write_article.py', [
        args.topic,
        '--style', args.style,
        '--keywords', args.keywords,
        '--length', str(args.length),
        '--title-hint', args.title_hint,
        '--benchmark-summary', args.benchmark_summary,
        '--audience', args.audience,
        '--provider', provider_override_text,
        '--model', args.model,
        '--config', CONFIG_PATH,
        '--output-dir', run_output_dir,
    ])

    article_path = article['path']
    article_title = extract_markdown_title(article_path, args.title_hint or args.topic)

    metadata = run_py('wechat_metadata.py', [
        article_path,
        '--provider', provider_override_text,
        '--model', args.model,
        '--config', CONFIG_PATH,
    ])
    publish_title = metadata.get('short_title') or article_title
    publish_digest = metadata.get('digest', '')

    body_plan = run_py('add_article_images.py', [
        article_path,
        '--topic', args.topic,
        '--title', article_title,
        '--style', args.style,
        '--max-images', str(args.max_body_images),
    ])

    plan_path = os.path.join(run_output_dir, 'body-image-plan.json')
    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(body_plan, f, ensure_ascii=False, indent=2)

    image_args = [
        '--topic', args.topic,
        '--title', article_title,
        '--style', effective_image_style,
        '--output-dir', run_output_dir,
        '--body-plan', plan_path,
        '--markdown-file', article_path,
    ]
    if args.image_prompt_strategy:
        image_args += ['--prompt-strategy', args.image_prompt_strategy]
    if args.image_prompt_lite_chars > 0:
        image_args += ['--lite-content-chars', str(args.image_prompt_lite_chars)]
    if provider_override_text == 'mock':
        image_args += ['--provider', 'mock']
    image_result = run_py('generate_image.py', image_args)

    cover_path = image_result['cover']['output_path']
    compressed_cover = maybe_compress(cover_path, 900, 500, 300)

    body_outputs = []
    image_path_replacements: Dict[str, str] = {}
    for item in image_result.get('body_images', []):
        compressed = maybe_compress(item['output_path'], 900, 500, 400)
        final_body_path = compressed.get('output_path') if compressed.get('compressed') else item['output_path']
        image_path_replacements[item['output_path']] = final_body_path
        body_outputs.append({**item, 'compression': compressed, 'final_output_path': final_body_path})

    rewrite_markdown_image_paths(article_path, image_path_replacements)

    effective_upload_images = args.upload_images or args.publish_draft
    format_args = [
        article_path,
        '--theme', args.theme,
        '--config', CONFIG_PATH,
        '--output-file', os.path.join(run_output_dir, 'article.html'),
    ]
    if effective_upload_images:
        format_args.append('--upload-images')
    html_result = run_py('format_article.py', format_args)

    normalized_paths = normalize_run_artifacts(
        run_output_dir,
        article_path=article_path,
        html_path=html_result['html_file'],
        cover_png_path=image_result['cover']['output_path'],
        cover_jpg_path=compressed_cover['output_path'],
    )
    article_path = normalized_paths['article_md']
    html_result['html_file'] = normalized_paths['article_html']
    image_result['cover']['output_path'] = normalized_paths['cover_png']
    compressed_cover['output_path'] = normalized_paths['cover_jpg']

    draft_result = None
    if args.publish_draft:
        draft_result = run_py('publish_draft.py', [
            html_result['html_file'],
            compressed_cover['output_path'],
            '--title', publish_title,
            '--digest', publish_digest,
            '--config', CONFIG_PATH,
        ])

    summary = {
        'ok': True,
        'python_bin': PYTHON_BIN,
        'run_output_dir': run_output_dir,
        'article': {**article, 'title': article_title},
        'metadata': metadata,
        'body_plan_path': plan_path,
        'images': {
            'cover': image_result['cover'],
            'cover_compression': compressed_cover,
            'body_images': body_outputs,
            'image_style': effective_image_style,
            'image_style_preset': (args.image_style_preset or '').strip().lower(),
            'prompt_strategy': image_result.get('prompt_strategy', ''),
            'prompt_source': image_result.get('prompt_source', ''),
        },
        'html': {**html_result, 'upload_images_used': effective_upload_images},
        'draft': draft_result,
    }

    metadata_path = os.path.join(run_output_dir, 'metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump({
            'topic': args.topic,
            'article_title': article_title,
            'publish_title': publish_title,
            'digest': publish_digest,
            'style': args.style,
            'provider': args.provider,
            'model': args.model,
            'metadata': metadata,
        }, f, ensure_ascii=False, indent=2)

    publish_result_path = os.path.join(run_output_dir, 'publish-result.json')
    with open(publish_result_path, 'w', encoding='utf-8') as f:
        json.dump(draft_result or {'published': False}, f, ensure_ascii=False, indent=2)

    index_path = os.path.join(args.output_dir, 'index.jsonl')
    index_record = {
        'run_output_dir': run_output_dir,
        'topic': args.topic,
        'article_title': article_title,
        'publish_title': publish_title,
        'digest': publish_digest,
        'published': bool(draft_result),
        'draft_media_id': (draft_result or {}).get('media_id', '') if draft_result else '',
        'html_file': html_result.get('html_file', ''),
        'markdown_file': article_path,
        'metadata_file': metadata_path,
        'publish_result_file': publish_result_path,
    }
    with open(index_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(index_record, ensure_ascii=False) + '\n')

    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
