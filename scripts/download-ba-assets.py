#!/usr/bin/env python3
"""Download Blue Archive student assets from SchaleDB CDN."""
import argparse
import json
import os
import sys

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'static', 'assets', 'ba', 'students')

# 默认角色分配：Light / Dark / 通用
DEFAULT_CHARACTERS = {
    '10010': {'theme': 'light', 'name': '白子', 'dev_name': 'Shiroko'},
    '10005': {'theme': 'dark', 'name': '星野', 'dev_name': 'Hoshino'},
    '10015': {'theme': 'common', 'name': '爱丽丝', 'dev_name': 'Aris'},
    '10059': {'theme': 'common', 'name': '未花', 'dev_name': 'Mika'},
}

IMAGE_TYPES = ['icon', 'portrait', 'collection']
CDN_BASE = 'https://schaledb.com/images/student'
API_URL = 'https://schaledb.com/data/cn/students.json'


def download_file(url: str, dest: str) -> bool:
    """Download a single file. Return True if success."""
    if os.path.exists(dest):
        return True
    try:
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, 'wb') as f:
            f.write(res.content)
        return True
    except Exception as e:
        print(f'  [ERROR] Failed to download {url}: {e}', file=sys.stderr)
        return False


def fetch_student_data() -> dict:
    """Fetch student list from SchaleDB API."""
    res = requests.get(API_URL, timeout=30)
    res.raise_for_status()
    return res.json()


def main():
    parser = argparse.ArgumentParser(description='Download BA student assets')
    parser.add_argument('--characters', type=str, default='10005,10010,10015,10059',
                        help='Comma-separated student IDs')
    parser.add_argument('--all', action='store_true',
                        help='Download all students (WARNING: very large)')
    args = parser.parse_args()

    os.makedirs(ASSETS_DIR, exist_ok=True)
    for t in IMAGE_TYPES:
        os.makedirs(os.path.join(ASSETS_DIR, t), exist_ok=True)

    student_data = fetch_student_data()

    if args.all:
        char_ids = list(student_data.keys())
    else:
        char_ids = [c.strip() for c in args.characters.split(',')]

    index = {}
    for char_id in char_ids:
        info = student_data.get(char_id, {})
        name = info.get('Name', '')
        dev_name = info.get('DevName', '')
        path_name = info.get('PathName', '')

        print(f'Downloading {char_id}: {name} ({dev_name})')
        success = True
        for img_type in IMAGE_TYPES:
            url = f'{CDN_BASE}/{img_type}/{char_id}.webp'
            dest = os.path.join(ASSETS_DIR, img_type, f'{char_id}.webp')
            if not download_file(url, dest):
                success = False

        if success:
            index[char_id] = {
                'name': name,
                'devName': dev_name,
                'pathName': path_name,
                'icon': f'/assets/ba/students/icon/{char_id}.webp',
                'portrait': f'/assets/ba/students/portrait/{char_id}.webp',
                'collection': f'/assets/ba/students/collection/{char_id}.webp',
            }

    index_path = os.path.join(ASSETS_DIR, 'index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    print(f'Index written: {index_path} ({len(index)} characters)')


if __name__ == '__main__':
    main()
