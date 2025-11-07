import os
import subprocess
import json
import shutil
import hashlib
from PIL import Image
import urllib.parse
from datetime import datetime

CACHE_FILE = "xdgcache.json"
THUMB_ROOT = os.path.expanduser("~/.cache/thumbnails")
SIZES = ("normal", "large", "x-large", "xx-large")


class NoThubnailerError(Exception):
    def __init__(self):
        print("No thubnailer detected on system (call_xdg) failed ")


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
            new_entries.append({"image": full, "thumbnail": thumb_path, "date": mod_date, "name": fn})
            changed = True


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

    try:
        tumbainer = get_thumbnailer()
        if tumbainer is None:
            raise NoThubnailerError
    except NoThubnailerError:
        exit(1)


    cache_dir = os.path.expanduser("~/.cache/thumbnails/large/")
    os.makedirs(cache_dir, exist_ok=True)

    for fn in os.listdir(img_dir):
        if not fn.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            continue

        img_path = os.path.abspath(os.path.join(img_dir, fn))

        uri = "file://" + urllib.parse.quote(img_path)
        name = hashlib.md5(uri.encode("utf-8")).hexdigest() + ".png"
        out = os.path.join(cache_dir, name)

        # only thumbnail if missing
        if not os.path.exists(out):
            if tumbainer == "gdk-pixbuf-thumbnailer":
                subprocess.run(
                    ["gdk-pixbuf-thumbnailer", "--size", str(size), img_path, out],
                    check=False,
                )

            #  glycin-thumbnailer -i file://$(pwd)/1.png -o /tmp/new.png -s 256
            elif tumbainer == "glycin-thumbnailer":
                subprocess.run( ["glycin-thumbnailer",'-i',"file://"+img_path ,'-o',out, '-s',str(size)], check=False,)



def get_thumbnailer():
    if shutil.which('gdk-pixbuf-thumbnailer'):
        return 'gdk-pixbuf-thumbnailer'

    elif shutil.which('glycin-thumbnailer'):
        return 'glycin-thumbnailer'

    else:
        return False




if __name__ == "__main__":
    # ligma("/path/to/images")
    call_xdg("./images/")
