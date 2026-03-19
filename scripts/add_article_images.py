#!/usr/bin/env python3
import argparse
import json
import os
import re
from typing import List, Dict


def extract_sections(md: str) -> List[Dict[str, str]]:
    sections = []
    current = None
    for line in md.splitlines():
        if line.startswith('## '):
            if current:
                sections.append(current)
            current = {'title': line[3:].strip(), 'content': ''}
        elif current is not None:
            current['content'] += line + '\n'
    if current:
        sections.append(current)
    return sections


def build_image_prompt(topic: str, title: str, style: str, section_title: str, section_content: str) -> str:
    snippet = re.sub(r'\s+', ' ', section_content).strip()[:120]
    return f'微信公众号正文插图，主题:{topic}，文章标题:{title}，整体风格:{style}，小节:{section_title}，内容摘要:{snippet}'


def insert_placeholders(md: str, sections: List[Dict[str, str]], prompts: List[Dict[str, str]]) -> str:
    out = md
    for item in prompts:
        marker = f"## {item['section_title']}"
        replacement = marker + f"\n\n![{item['section_title']}]({item['markdown_image_path']})\n"
        out = out.replace(marker, replacement, 1)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('markdown_file')
    parser.add_argument('--topic', default='')
    parser.add_argument('--title', default='')
    parser.add_argument('--style', default='干货')
    parser.add_argument('--max-images', type=int, default=1)
    parser.add_argument('--output-file', default='')
    args = parser.parse_args()

    with open(args.markdown_file, 'r', encoding='utf-8') as f:
        md = f.read()

    sections = extract_sections(md)
    picked = sections[:max(args.max_images, 0)]
    prompts = []
    base_dir = os.path.dirname(args.markdown_file)
    images_dir = os.path.join(base_dir, 'generated-body-images')
    os.makedirs(images_dir, exist_ok=True)

    for idx, sec in enumerate(picked, start=1):
        image_path = os.path.join(images_dir, f'body-{idx:02d}.png')
        markdown_image_path = os.path.relpath(image_path, start=base_dir)
        prompts.append({
            'section_title': sec['title'],
            'prompt': build_image_prompt(args.topic, args.title, args.style, sec['title'], sec['content']),
            'image_path': image_path,
            'markdown_image_path': markdown_image_path,
        })

    updated = insert_placeholders(md, sections, prompts)
    output = args.output_file or args.markdown_file
    with open(output, 'w', encoding='utf-8') as f:
        f.write(updated)

    print(json.dumps({'ok': True, 'markdown_file': output, 'planned_images': prompts}, ensure_ascii=False))


if __name__ == '__main__':
    main()
