import os
import sys
import json
import hashlib
import urllib.parse
import subprocess
import pytest
from PIL import Image

# Ensure the parent directory (where SharedData.py lives) is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Now import the module under test
import xdgthumbails


def test_is_image_with_valid_image(tmp_path):
    img_path = tmp_path / "test.png"
    # create a small valid image
    img = Image.new("RGB", (10, 10), color="red")
    img.save(img_path)
    assert xdgthumbails.is_image(str(img_path)) is True


def test_is_image_with_invalid_file(tmp_path):
    txt_file = tmp_path / "not_image.txt"
    txt_file.write_text("this is not an image")
    assert xdgthumbails.is_image(str(txt_file)) is False


def test_calculate_md5(tmp_path):
    # create a dummy file
    file = tmp_path / "file.txt"
    file.write_text("content")
    abs_path = str(file.resolve())
    uri = urllib.parse.urljoin("file:", urllib.parse.quote(abs_path))
    expected = hashlib.md5(uri.encode("utf-8")).hexdigest() + ".png"
    assert xdgthumbails.calculate_md5(str(file)) == expected


def test_find_thumbnail(monkeypatch, tmp_path):
    # override THUMB_ROOT to point to tmp
    monkeypatch.setattr(xdgthumbails, 'THUMB_ROOT', str(tmp_path))
    # create size directories
    for size in xdgthumbails.SIZES:
        (tmp_path / size).mkdir(parents=True, exist_ok=True)
    # place a thumbnail in 'large'
    name = "thumb123.png"
    thumb_path = tmp_path / 'large' / name
    thumb_path.write_text('x')
    # should find under 'large'
    found = xdgthumbails.find_thumbnail(name)
    assert found == str(thumb_path)
    # non-existent
    assert xdgthumbails.find_thumbnail("nope.png") == ""


def test_generate_with_cli(monkeypatch):
    calls = []
    monkeypatch.setattr(subprocess, 'run', lambda args, check: calls.append((args, check)))
    xdgthumbails.generate_with_cli('src.png', 128, 'dst.png')
    assert calls == [(['gdk-pixbuf-thumbnailer', '--size', '128', 'src.png', 'dst.png'], False)]


def test_call_xdg(monkeypatch, tmp_path):
    # simulate HOME so expanduser uses tmp_path
    monkeypatch.setenv('HOME', str(tmp_path))
    # create images directory
    img_dir = tmp_path / 'images'
    img_dir.mkdir()
    # dummy image files
    img1 = img_dir / 'a.jpg'
    img1.write_bytes(b'fake')
    img2 = img_dir / 'b.png'
    img2.write_bytes(b'fake')
    # capture subprocess calls
    calls = []
    monkeypatch.setattr(subprocess, 'run', lambda args, check: calls.append((args, check)))
    # first run: no cache exists
    xdgthumbails.call_xdg(str(img_dir), size=64)
    assert len(calls) == 2
    for args, check in calls:
        assert args[0] == 'gdk-pixbuf-thumbnailer'
        assert args[1] == '--size'
        assert args[2] == '64'
        assert check is False
    # simulate existing thumbnail for img1 only
    calls.clear()
    uri1 = 'file://' + urllib.parse.quote(str(img1.resolve()))
    name1 = hashlib.md5(uri1.encode('utf-8')).hexdigest() + '.png'
    out1 = tmp_path / '.cache' / 'thumbnails' / 'large' / name1
    out1.parent.mkdir(parents=True, exist_ok=True)
    out1.write_bytes(b'')
