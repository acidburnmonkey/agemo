import os
import json
import hashlib
from PIL import Image
import urllib.parse
from datetime import datetime

CACHE_FILE = "xdgcache.json"
THUMB_ROOT = os.path.expanduser("~/.cache/thumbnails")
SIZES = ("normal", "large", "x-large", "xx-large")


def is_image(path: str) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def calculate_md5(path: str) -> str:
    abs_path = os.path.abspath(path)
    uri = urllib.parse.urljoin("file:", urllib.parse.quote(abs_path))
    return hashlib.md5(uri.encode("utf-8")).hexdigest() + ".png"


def find_thumbnail(name: str) -> str:
    for size in SIZES:
        candidate = os.path.join(THUMB_ROOT, size, name)
        if os.path.isfile(candidate):
            return candidate
    return ""


def ligma(wallpapers_dir: str, cache_file: str = CACHE_FILE):
    #  load existing cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = []
    else:
        existing = []

    old_map = {e["image"]: e for e in existing}

    new_entries = []
    changed = False

    #  scan directory
    for fn in os.listdir(wallpapers_dir):
        full = os.path.join(wallpapers_dir, fn)
        if not is_image(full):
            continue

        mtime = os.path.getmtime(full)
        mod_date = datetime.fromtimestamp(mtime).isoformat()
        old = old_map.get(full)

        if old and old.get("date") == mod_date:
            # unchanged
            new_entries.append(old)
        else:
            # new or modified
            thumb_name = calculate_md5(full)
            thumb_path = find_thumbnail(thumb_name)
            new_entries.append({
                "image": full,
                "thumbnail": thumb_path,
                "date": mod_date,
                "name": fn
            })
            changed = True

    # add more options latter , defaulting to date
    # new_entries.sort(key=lambda e: e["name"].lower())
    new_entries.sort(key=lambda e: e["date"])
    new_entries.reverse()

    #if nothing changed return
    if not changed and len(new_entries) == len(existing):
        print("Cache already up to date.")
        return


    # write updated cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(new_entries, f, indent=4, ensure_ascii=False)
    print(f"Cache updated: {len(new_entries)} entries.")


if __name__ == "__main__":
    ligma("/path/to/images")
