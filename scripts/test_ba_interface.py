#!/usr/bin/env python3
"""Interface Test: Verify Blue Archive asset download and backend API."""
import json
import os
import sys

import pytest
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'static', 'assets', 'ba', 'students')


class TestSchaleDBAPI:
    """Interface Test: 验证 SchaleDB API 和图片 CDN 可用性"""

    def test_students_api_returns_dict(self):
        """SchaleDB students.json 返回有效 JSON"""
        res = requests.get('https://schaledb.com/data/cn/students.json', timeout=30)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_image_cdn_icon_returns_200(self):
        """CDN icon 图片可访问"""
        res = requests.get('https://schaledb.com/images/student/icon/10005.webp', timeout=30)
        assert res.status_code == 200
        assert len(res.content) > 100

    def test_image_cdn_portrait_returns_200(self):
        """CDN portrait 图片可访问"""
        res = requests.get('https://schaledb.com/images/student/portrait/10005.webp', timeout=30)
        assert res.status_code == 200
        assert len(res.content) > 1000

    def test_image_cdn_collection_returns_200(self):
        """CDN collection 图片可访问"""
        res = requests.get('https://schaledb.com/images/student/collection/10005.webp', timeout=30)
        assert res.status_code == 200
        assert len(res.content) > 100


class TestDownloadScript:
    """Interface Test: 验证下载脚本行为"""

    def test_index_json_generated(self):
        """脚本执行后生成 index.json"""
        index_path = os.path.join(ASSETS_DIR, 'index.json')
        assert os.path.exists(index_path), 'index.json 未生成'
        with open(index_path) as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert '10005' in data or '10010' in data

    def test_downloaded_icon_files_exist(self):
        """icon 目录包含下载的图片"""
        icon_dir = os.path.join(ASSETS_DIR, 'icon')
        assert os.path.exists(icon_dir)
        files = [f for f in os.listdir(icon_dir) if f.endswith('.webp')]
        assert len(files) > 0

    def test_downloaded_portrait_files_exist(self):
        """portrait 目录包含下载的图片"""
        portrait_dir = os.path.join(ASSETS_DIR, 'portrait')
        assert os.path.exists(portrait_dir)
        files = [f for f in os.listdir(portrait_dir) if f.endswith('.webp')]
        assert len(files) > 0

    def test_index_mapping_correct(self):
        """index.json 的 path 映射对应实际文件"""
        index_path = os.path.join(ASSETS_DIR, 'index.json')
        with open(index_path) as f:
            data = json.load(f)
        for char_id, info in data.items():
            icon_path = os.path.join(ASSETS_DIR, info['icon'].lstrip('/').replace('assets/ba/students/', ''))
            assert os.path.exists(icon_path), f'icon 文件不存在: {icon_path}'
            portrait_path = os.path.join(ASSETS_DIR, info['portrait'].lstrip('/').replace('assets/ba/students/', ''))
            assert os.path.exists(portrait_path), f'portrait 文件不存在: {portrait_path}'


if __name__ == '__main__':
    sys.exit(pytest.main([__file__, '-v']))
