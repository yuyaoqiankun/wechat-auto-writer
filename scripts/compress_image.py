#!/usr/bin/env python3
import argparse
import json
import os
from PIL import Image, ImageOps


def compress_iteratively(img: Image.Image, output_path: str, quality_start: int, max_kb: int):
    quality = quality_start
    while quality >= 25:
        img.save(output_path, format='JPEG', quality=quality, optimize=True)
        size_kb = os.path.getsize(output_path) / 1024
        if size_kb <= max_kb:
            return quality, round(size_kb, 2)
        quality -= 5
    size_kb = os.path.getsize(output_path) / 1024
    return quality + 5, round(size_kb, 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('--output-path', default='')
    parser.add_argument('--width', type=int, default=900)
    parser.add_argument('--height', type=int, default=500)
    parser.add_argument('--quality', type=int, default=85)
    parser.add_argument('--max-kb', type=int, default=300)
    args = parser.parse_args()

    root, _ = os.path.splitext(args.input_path)
    output = args.output_path or root + '.jpg'
    img = Image.open(args.input_path).convert('RGB')
    img = ImageOps.fit(img, (args.width, args.height))
    used_quality, final_kb = compress_iteratively(img, output, args.quality, args.max_kb)

    print(json.dumps({
        'ok': True,
        'output_path': output,
        'width': args.width,
        'height': args.height,
        'quality': used_quality,
        'final_kb': final_kb,
        'max_kb': args.max_kb,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
