#!/usr/bin/env python3
"""Download Blue Archive official Fan Kit assets when the official site is reachable.

The official precautions define Fan Kit materials as wallpapers, stamps, and icons.
This script intentionally records source URLs and refuses to silently generate an empty
index when the site layout or network changes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "static" / "assets" / "ba" / "fankit"
FANKIT_URL = "https://bluearchive.jp/fankit"
PRECAUTIONS_URL = "https://bluearchive.jp/fankit/Precautions"
USER_AGENT = "Mozilla/5.0 open-webui-ba-fankit-downloader/1.0"

TYPE_PATTERNS = {
    "wallpaper": re.compile(r"wallpaper|壁紙|sp_?wall|pc_?wall", re.I),
    "stamp": re.compile(r"stamp|スタンプ", re.I),
    "icon": re.compile(r"icon|アイコン", re.I),
}
ASSET_RE = re.compile(r"(?:src|href)=[\"']([^\"']+\.(?:png|jpe?g|webp|zip))(?:\?[^\"']*)?[\"']", re.I)


@dataclass
class FanKitAsset:
    type: str
    sourceUrl: str
    localPath: str
    filename: str


def infer_type(url: str, requested: str) -> str | None:
    if requested != "all":
        return requested
    for asset_type, pattern in TYPE_PATTERNS.items():
        if pattern.search(url):
            return asset_type
    return None


def fetch_html() -> str:
    res = requests.get(FANKIT_URL, timeout=30, headers={"User-Agent": USER_AGENT})
    res.raise_for_status()
    return res.text


def discover_assets(html: str, requested: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for match in ASSET_RE.finditer(html):
        source = urljoin(FANKIT_URL, match.group(1))
        asset_type = infer_type(source, requested)
        if not asset_type or source in seen:
            continue
        seen.add(source)
        found.append((asset_type, source))
    return found


def safe_filename(url: str) -> str:
    parsed = urlparse(url)
    name = os.path.basename(parsed.path) or "asset"
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name)


def download(asset_type: str, source: str, force: bool) -> FanKitAsset:
    target_dir = OUT_DIR / asset_type
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = safe_filename(source)
    dest = target_dir / filename
    if force or not dest.exists():
        res = requests.get(source, timeout=60, headers={"User-Agent": USER_AGENT})
        res.raise_for_status()
        dest.write_bytes(res.content)
    local = "/" + str(dest.relative_to(ROOT / "static")).replace(os.sep, "/")
    return FanKitAsset(asset_type, source, local, filename)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download official Blue Archive Fan Kit assets")
    parser.add_argument("--type", choices=["all", "wallpaper", "stamp", "icon"], default="all")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = fetch_html()
    assets = discover_assets(html, args.type)
    if not assets:
        raise RuntimeError(
            "No official Fan Kit asset URLs were discovered. The site layout may have changed "
            "or the network/proxy may be serving an incomplete page."
        )

    if args.dry_run:
        for asset_type, source in assets:
            print(f"{asset_type}\t{source}")
        return 0

    downloaded = [download(asset_type, source, args.force) for asset_type, source in assets]
    index = {
        "source": FANKIT_URL,
        "precautions": PRECAUTIONS_URL,
        "generated": True,
        "assets": [asdict(item) for item in downloaded],
    }
    (OUT_DIR / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Downloaded {len(downloaded)} Fan Kit assets into {OUT_DIR}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        raise SystemExit(1)
