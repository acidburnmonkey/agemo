import os
import subprocess
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


# generate missig thumbnails
def generate_with_cli(src, size, dst):
    subprocess.run( ["gdk-pixbuf-thumbnailer", "--size", str(size), src, dst], check=False)



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
            new_entries.append(
                {"image": full, "thumbnail": thumb_path, "date": mod_date, "name": fn}
            )
            changed = True

    # generate missing thumbnails
    # for entry in new_entries:
    #     if not entry["thumbnail"]:
    #         thumb_name = calculate_md5(entry["image"])
    #         dst = os.path.join(THUMB_ROOT, "normal", thumb_name)
    #         os.makedirs(os.path.dirname(dst), exist_ok=True)

    #         generate_with_cli(entry["image"], 128, dst)
    #         if os.path.exists(dst):
    #             entry["thumbnail"] = dst

    # new_entries.sort(key=lambda e: e["name"].lower())
    new_entries.sort(key=lambda e: e["date"])
    new_entries.reverse()

    # if nothing changed return
    if not changed and len(new_entries) == len(existing):
        print("Cache already up to date.")
        return

    # write updated cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(new_entries, f, indent=4, ensure_ascii=False)
    print(f"Cache updated: {len(new_entries)} entries.")


# force populate thubnails
def call_xdg(img_dir: str, size: int = 256):
    cache_dir = os.path.expanduser("~/.cache/thumbnails/large/")
    os.makedirs(cache_dir, exist_ok=True)

    for fn in os.listdir(img_dir):
        if not fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        img_path = os.path.join(img_dir, fn)

        uri = "file://" + urllib.parse.quote(img_path)
        name = hashlib.md5(uri.encode("utf-8")).hexdigest() + ".png"
        out = os.path.join(cache_dir, name)

        # only thumbnail if missing
        if not os.path.exists(out):
            subprocess.run(
                ["gdk-pixbuf-thumbnailer", "--size", str(size), img_path, out],
                check=False,
            )


if __name__ == "__main__":
    ligma("/path/to/images")
    call_xdg("/path/to/images")
