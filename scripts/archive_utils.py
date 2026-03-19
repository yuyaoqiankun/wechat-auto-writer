#!/usr/bin/env python3
import os
import re
from datetime import datetime


def slugify_topic(topic: str, max_len: int = 24) -> str:
    text = topic.strip().lower()
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'[^\w\-\u4e00-\u9fff]+', '-', text)
    text = re.sub(r'-{2,}', '-', text).strip('-_')
    if not text:
        text = 'untitled'
    return text[:max_len].rstrip('-_') or 'untitled'


def make_run_dir(base_output_dir: str, topic: str) -> str:
    now = datetime.now()
    day_dir = now.strftime('%Y-%m-%d')
    time_part = now.strftime('%H%M%S')
    slug = slugify_topic(topic)
    folder = f'{time_part}-{slug}'
    return os.path.join(base_output_dir, day_dir, folder)
