#!/usr/bin/env python3
"""
Scrape Tomy Pokemon toys from tomydatabase.weebly.com

- Collects toy name + image URL from each generation page
- Downloads images to ./images
- Writes tomydatabase.weebly.com.json with one entry per toy:
  {
    "name": "...",
    "generation": "...",
    "image_url": "...",
    "image_path": "images/....jpg",
    "id": "stable hash"
  }
"""

import hashlib
import json
import re
import time
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE = "https://tomydatabase.weebly.com/"
PAGES = [
    ("Kanto", BASE),  # root is Kanto
    ("Johto", urljoin(BASE, "johto.html")),
    ("Hoenn", urljoin(BASE, "hoenn.html")),
    ("Sinnoh", urljoin(BASE, "sinnoh.html")),
    ("Unova", urljoin(BASE, "unova.html")),
    ("Kalos", urljoin(BASE, "kalos.html")),
    ("Alola", urljoin(BASE, "alola.html")),
]

OUT_DIR = Path("images")
OUT_DIR.mkdir(parents=True, exist_ok=True)
JSON_PATH = Path("tomydatabase.weebly.com.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ToyScraper/1.0; +https://example.com)"
}

IMG_RE = re.compile(r"/uploads/.*\.(?:jpg|jpeg|png|gif)$", re.IGNORECASE)

def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\-]+", "-", text)
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "item"

def file_ext_from_url(url: str) -> str:
    path = urlparse(url).path
    m = re.search(r"\.(jpe?g|png|gif)$", path, re.IGNORECASE)
    return "." + (m.group(1).lower() if m else "jpg")

def stable_id(name: str, image_url: str) -> str:
    return hashlib.sha256((name + "|" + image_url).encode("utf-8")).hexdigest()[:16]

def fetch(url: str) -> requests.Response:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r

def parse_generation(gen_name: str, url: str) -> List[Dict]:
    print(f"[+] Parsing {gen_name}: {url}")
    resp = fetch(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    items = []
    # Site structure: <a href=".../uploads/.../something.jpg">Toy Name</a>
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = (a.get_text() or "").strip()
        if not text:
            continue
        if not IMG_RE.search(href):
            continue

        img_url = urljoin(url, href)
        name = text
        sid = stable_id(name, img_url)

        # build a deterministic filename
        fname = f"{slugify(name)}-{sid}{file_ext_from_url(img_url)}"
        items.append({
            "id": sid,
            "name": name,
            "generation": gen_name,
            "image_url": img_url,
            "image_filename": fname,  # filename only
        })
    return items

def download_image(img_url: str, dest_path: Path, max_retries: int = 3):
    for attempt in range(1, max_retries + 1):
        try:
            with requests.get(img_url, headers=HEADERS, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            return
        except Exception as e:
            if attempt == max_retries:
                print(f"[!] Failed to download {img_url}: {e}")
                return
            wait = 1.5 * attempt
            print(f"[~] Retry {attempt}/{max_retries} after {wait:.1f}s: {img_url}")
            time.sleep(wait)

def main():
    all_items: List[Dict] = []
    for gen_name, url in PAGES:
        try:
            items = parse_generation(gen_name, url)
            all_items.extend(items)
            # be polite; the site is small
            time.sleep(0.8)
        except Exception as e:
            print(f"[!] Error parsing {gen_name}: {e}")

    # Deduplicate by (name, image_url)
    seen = set()
    deduped = []
    for it in all_items:
        key = (it["name"], it["image_url"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(it)

    print(f"[+] Found {len(deduped)} toys. Downloading images…")

    # Download images and finalize entries
    final = []
    for it in deduped:
        dest = OUT_DIR / it["image_filename"]
        if not dest.exists():
            download_image(it["image_url"], dest)
            time.sleep(0.25)  # small throttle
        entry = {
            "id": it["id"],
            "name": it["name"],
            "generation": it["generation"],
            "image_url": it["image_url"],
            "image_path": str(dest.as_posix()),
        }
        final.append(entry)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"[+] Done. JSON: {JSON_PATH}  Images dir: {OUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
