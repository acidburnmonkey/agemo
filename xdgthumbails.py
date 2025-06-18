import os
import json
import hashlib
from PIL import Image
import urllib.parse
from datetime import datetime


def is_image(path: str) -> bool:
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def calculate_md5(path: str) -> str:
    # build the file:// URI exactly as freedesktop does, then MD5 it
    abs_path = os.path.abspath(path)
    uri = urllib.parse.urljoin("file:", urllib.parse.quote(abs_path))
    h = hashlib.md5(uri.encode("utf-8")).hexdigest()
    return f"{h}.png"


def search(target: str) -> str:
    # look in ~/.cache/thumbnails/{normal,large,x-large,xx-large}
    cache_root = os.path.expanduser("~/.cache/thumbnails")
    for size in ("normal", "large", "x-large", "xx-large"):
        folder = os.path.join(cache_root, size)
        candidate = os.path.join(folder, target)
        if os.path.isfile(candidate):
            return candidate
    return ""  # not found


def ligma(wallpapersDir: str):
    entries = []
    for fn in os.listdir(wallpapersDir):
        full = os.path.join(wallpapersDir, fn)

        # skip non‑image files
        if not is_image(full):
            continue

        thumb_name = calculate_md5(full)
        thumb_path = search(thumb_name)

        mtime = os.path.getmtime(full)
        mod_date = datetime.fromtimestamp(mtime).isoformat()

        entries.append(
            {"image": full, "thumbnail": thumb_path, "date": mod_date, "name": fn}
        )

    # write out cache.json next to script
    with open("xdgcache.json", "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    ligma("./src/smallb/")
