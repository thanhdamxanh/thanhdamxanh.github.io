#!/usr/bin/env python3

import sys
import re
import requests
from pathlib import Path
from urllib.parse import urlparse

# ------------------ Input ------------------

if len(sys.argv) != 2:
    print("Usage: python3 fetch_images.py file.md")
    sys.exit(1)

md_path = Path(sys.argv[1]).expanduser().resolve()

if not md_path.exists():
    print(f"File not found: {md_path}")
    sys.exit(1)

text = md_path.read_text(encoding="utf-8")

# ------------------ Paths ------------------

base_name = md_path.stem
assets_dir = md_path.parent / "assets" / base_name
assets_dir.mkdir(parents=True, exist_ok=True)

# ------------------ Regex ------------------

md_img = re.compile(r'!\[[^\]]*\]\((https?://[^)]+)\)')
html_img = re.compile(r'<img[^>]+src=["\'](https?://[^"\']+)["\']')

urls = list(dict.fromkeys(md_img.findall(text) + html_img.findall(text)))

if not urls:
    print("Không tìm thấy ảnh.")
    sys.exit(0)

# ------------------ Helpers ------------------

def ext_from_content_type(ct: str) -> str:
    if not ct:
        return ".img"
    if "jpeg" in ct:
        return ".jpg"
    if "png" in ct:
        return ".png"
    if "webp" in ct:
        return ".webp"
    if "gif" in ct:
        return ".gif"
    return ".img"

def filename_from_url(url: str) -> str | None:
    name = Path(urlparse(url).path).name
    if "." in name:
        return name
    return None

# ------------------ Download ------------------

counter = 1

for url in urls:
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"⚠ Không tải được {url}: {e}")
        continue

    filename = filename_from_url(url)

    if not filename:
        ext = ext_from_content_type(r.headers.get("Content-Type", ""))
        filename = f"{base_name}-{counter}{ext}"
        counter += 1

    local_path = assets_dir / filename
    local_ref = f"assets/{base_name}/{filename}"

    if not local_path.exists():
        print(f"↓ {url}")
        local_path.write_bytes(r.content)

    text = text.replace(url, local_ref)

# ------------------ Write back ------------------

md_path.write_text(text, encoding="utf-8")

print(f"✔ Ảnh đã lưu tại {assets_dir}")
print("✔ Đã cập nhật đường dẫn trong Markdown")
