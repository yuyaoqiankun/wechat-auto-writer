#!/usr/bin/env python3
import argparse
import json
import os
import re
from html import escape
from typing import Dict, List, Optional

import yaml

from wechat_capability import wechat_manage_capability


def load_theme(theme_ref: str, base_dir: str) -> Dict:
    if '/' not in theme_ref:
        raise ValueError('theme must be category/name, e.g. macaron/blue')
    category, name = theme_ref.split('/', 1)
    path = os.path.join(base_dir, 'themes', category, f'{name}.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        theme_data = yaml.safe_load(f)
    return {
        'id': theme_ref,
        'name': theme_data.get('name', theme_ref),
        'description': theme_data.get('description', ''),
        'keywords': theme_data.get('keywords', []),
        'colors': theme_data.get('colors', {}),
        'styles': theme_data.get('styles', {}),
    }


def style_to_str(style_dict: Optional[Dict]) -> str:
    if not style_dict:
        return ''
    return '; '.join([f"{k.replace('_', '-')}: {v}" for k, v in style_dict.items() if v])


def esc(text: str) -> str:
    return escape(text, quote=False)


def render_inline(text: str, theme: Dict) -> str:
    text = esc(text)
    strong_style = style_to_str(theme['styles'].get('strong', {}))
    code_inline_style = style_to_str(theme['styles'].get('code_inline', {}))
    link_style = style_to_str(theme['styles'].get('link', {}))
    body_color = theme.get('colors', {}).get('text', '#333333')

    text = re.sub(r'\[(.*?)\]\((.+?)\)', lambda m: f'<a href="{m.group(2)}" style="{link_style}">{m.group(1)}</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', lambda m: f'<strong style="{strong_style}">{m.group(1)}</strong>', text)
    text = re.sub(r'__(.+?)__', lambda m: f'<strong style="{strong_style}">{m.group(1)}</strong>', text)
    text = re.sub(r'`([^`]+)`', lambda m: f'<code style="{code_inline_style}">{m.group(1)}</code>', text)
    text = re.sub(r'\*(.+?)\*', lambda m: f'<em style="font-style: italic; color: {body_color};">{m.group(1)}</em>', text)
    text = re.sub(r'_(.+?)_', lambda m: f'<em style="font-style: italic; color: {body_color};">{m.group(1)}</em>', text)
    return text


def load_config(config_path: Optional[str]) -> Dict:
    if not config_path:
        return {}
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def resolve_local_image(src: str, markdown_file: str) -> Optional[str]:
    if re.match(r'^https?://', src):
        return None
    if os.path.isabs(src):
        return src if os.path.exists(src) else None
    candidate = os.path.normpath(os.path.join(os.path.dirname(markdown_file), src))
    return candidate if os.path.exists(candidate) else None


def upload_news_image_if_needed(src: str, markdown_file: str, cfg: Dict, upload_images: bool, image_map: Dict[str, str]):
    if not upload_images:
        return src
    local_path = resolve_local_image(src, markdown_file)
    if not local_path:
        return src
    if local_path in image_map:
        return image_map[local_path]
    if not cfg.get('appid') or not cfg.get('appsecret'):
        raise ValueError('Missing appid/appsecret for image upload')
    result = wechat_manage_capability(cfg['appid'], cfg['appsecret'], 'material', 'add_news_image', file_path=local_path)
    url = result['url']
    image_map[local_path] = url
    return url


def render_table(block_lines: List[str], theme: Dict) -> str:
    styles = theme['styles']
    table_style = style_to_str(styles.get('table', {}))
    th_style = style_to_str(styles.get('table_th', {}))
    td_style = style_to_str(styles.get('table_td', {}))

    rows = []
    for row in block_lines:
        cells = [c.strip() for c in row.split('|')]
        if cells and cells[0] == '':
            cells.pop(0)
        if cells and cells[-1] == '':
            cells.pop()
        rows.append(cells)

    headers = rows[0] if rows else []
    content_rows = rows[2:] if len(rows) > 2 else []
    if not headers:
        return ''

    html = [f'<section style="margin: 16px 0; width: 100%; overflow-x: auto; box-sizing: border-box;"><table style="{table_style}">']
    html.append('<thead><tr>')
    for header in headers:
        html.append(f'<th style="{th_style}">{esc(header)}</th>')
    html.append('</tr></thead>')
    if content_rows:
        html.append('<tbody>')
        for row in content_rows:
            html.append('<tr>')
            for cell in row:
                html.append(f'<td style="{td_style}">{render_inline(cell, theme)}</td>')
            html.append('</tr>')
        html.append('</tbody>')
    html.append('</table></section>')
    return ''.join(html)


def md_to_wechat_html(text: str, theme: Dict, markdown_file: str, cfg: Dict, upload_images: bool = False):
    styles = theme['styles']
    body_style = style_to_str(styles.get('body', {}))
    h1_style = style_to_str(styles.get('h1', {}))
    h3_style = style_to_str(styles.get('h3', {}))
    blockquote_style = style_to_str(styles.get('blockquote', {}))
    list_style = style_to_str(styles.get('list', {}))
    image_style = style_to_str(styles.get('image', {}))
    separator_style = style_to_str(styles.get('separator', {}))
    code_block_style = style_to_str(styles.get('code_block', {}))

    primary_color = theme.get('colors', {}).get('primary', '#2563eb')
    h2_cfg = styles.get('h2', {})
    h2_text_align = h2_cfg.get('text_align', 'left')
    h2_font_size = h2_cfg.get('font_size', '18px')
    h2_container_style = f'margin: 32px 0 16px 0; text-align: {h2_text_align}; line-height: 1.5;'
    h2_inner_style = f'display: inline-block; background-color: {primary_color}; color: #ffffff; padding: 6px 16px; border-radius: 12px; font-size: {h2_font_size}; font-weight: bold; letter-spacing: 1px;'

    html = [f'<section style="{body_style}">']
    image_map: Dict[str, str] = {}
    lines = text.splitlines()
    i = 0
    in_code_block = False
    code_lines: List[str] = []

    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip('\n')
        stripped = line.strip()

        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lines = []
            else:
                code_html = esc('\n'.join(code_lines))
                html.append(f'<section style="margin: 16px 0; max-width: 100%; box-sizing: border-box;"><pre style="{code_block_style}; overflow-x: auto; font-family: Courier New, monospace; box-sizing: border-box;"><code style="display: block; white-space: pre; font-size: 13px; line-height: 1.6;">{code_html}</code></pre></section>')
                in_code_block = False
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if re.match(r'^\|.*\|$', stripped) and i + 1 < len(lines) and re.match(r'^\|?\s*[-: ]+(\|\s*[-: ]+)+\|?$', lines[i + 1].strip()):
            table_lines = [stripped]
            i += 1
            table_lines.append(lines[i].strip())
            i += 1
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i].strip())
                i += 1
            html.append(render_table(table_lines, theme))
            continue

        if stripped in {'---', '***', '___'}:
            html.append(f'<section style="{separator_style}"></section>')
            i += 1
            continue

        if line.startswith('# '):
            html.append(f'<h1 style="{h1_style}">{render_inline(line[2:].strip(), theme)}</h1>')
            i += 1
            continue
        if line.startswith('## '):
            html.append(f'<h2 style="{h2_container_style}"><span style="{h2_inner_style}">{render_inline(line[3:].strip(), theme)}</span></h2>')
            i += 1
            continue
        if line.startswith('### '):
            html.append(f'<h3 style="{h3_style}">{render_inline(line[4:].strip(), theme)}</h3>')
            i += 1
            continue
        if line.startswith('#### '):
            html.append(f'<h4 style="{h3_style}">{render_inline(line[5:].strip(), theme)}</h4>')
            i += 1
            continue

        if line.startswith('> '):
            quote_lines = []
            while i < len(lines) and lines[i].startswith('> '):
                quote_lines.append(render_inline(lines[i][2:].strip(), theme))
                i += 1
            html.append(f'<blockquote style="{blockquote_style}">{"<br>".join(quote_lines)}</blockquote>')
            continue

        if re.match(r'^!\[(.*?)\]\((.+)\)$', stripped):
            alt, src = re.findall(r'^!\[(.*?)\]\((.+)\)$', stripped)[0]
            final_src = upload_news_image_if_needed(src, markdown_file, cfg, upload_images, image_map)
            html.append(f'<p style="text-align: center; margin: 20px 0; padding: 0 16px;"><img src="{final_src}" alt="{esc(alt)}" style="max-width: 100%; height: auto; display: block; margin: 0 auto; {image_style}" referrerpolicy="no-referrer" /></p>')
            i += 1
            continue

        if re.match(r'^[\s]*[-\*] ', line):
            items = []
            while i < len(lines) and re.match(r'^[\s]*[-\*] ', lines[i]):
                items.append(re.sub(r'^[\s]*[-\*] ', '', lines[i]).strip())
                i += 1
            html.append(f'<ul style="{list_style}; list-style-type: disc; padding-left: 24px;">' + ''.join([f'<li style="margin: 4px 0;">{render_inline(item, theme)}</li>' for item in items]) + '</ul>')
            continue

        if re.match(r'^[\s]*\d+\. ', line):
            items = []
            while i < len(lines) and re.match(r'^[\s]*\d+\. ', lines[i]):
                items.append(re.sub(r'^[\s]*\d+\. ', '', lines[i]).strip())
                i += 1
            html.append(f'<ol style="{list_style}; list-style-type: decimal; padding-left: 24px;">' + ''.join([f'<li style="margin: 4px 0;">{render_inline(item, theme)}</li>' for item in items]) + '</ol>')
            continue

        paragraph_lines = []
        while i < len(lines):
            probe = lines[i].strip()
            if not probe:
                i += 1
                break
            if probe.startswith(('```', '# ', '## ', '### ', '#### ', '> ', '![', '- ', '* ')):
                break
            if re.match(r'^\d+\. ', probe):
                break
            if probe in {'---', '***', '___'}:
                break
            if re.match(r'^\|.*\|$', probe):
                break
            paragraph_lines.append(lines[i].strip())
            i += 1
        if paragraph_lines:
            html.append(f'<p style="{body_style}; margin: 0; padding: 0;">{render_inline("".join(paragraph_lines), theme)}</p>')

    html.append('</section>')
    return ''.join(html), image_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('markdown_file')
    parser.add_argument('--output-file', default='')
    parser.add_argument('--theme', default='macaron/blue')
    parser.add_argument('--base-dir', default=os.path.join(os.path.dirname(__file__), '..'))
    parser.add_argument('--config', default=os.path.join(os.path.dirname(__file__), '..', 'config.json'))
    parser.add_argument('--upload-images', action='store_true')
    args = parser.parse_args()

    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        text = f.read()
    theme = load_theme(args.theme, args.base_dir)
    cfg = load_config(args.config)
    html, image_map = md_to_wechat_html(text, theme, args.markdown_file, cfg, upload_images=args.upload_images)
    output = args.output_file or os.path.splitext(args.markdown_file)[0] + '.html'
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html)
    print(json.dumps({'ok': True, 'html_file': output, 'theme': args.theme, 'theme_label': theme.get('name', ''), 'uploaded_images': image_map}, ensure_ascii=False))


if __name__ == '__main__':
    main()
