
 #Add parent directory to sys.path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pytest
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from agemo import BottomBar, Gallery, TopBar, SettingsWindow, ClickableLabel, MainWindow
from SharedData import SharedData

app = QApplication([])

@pytest.fixture
def shared_data(tmp_path):
    sd = SharedData()
    sd.data = {
        "dpi": None,
        "wallpapers_dir": str(tmp_path),
        "monitors": ["HDMI-A-1"]
    }
    sd.script_path = str(tmp_path)
    return sd


def test_bottombar_monitor_selection(shared_data):
    bar = BottomBar(shared_data)
    assert bar.current_monitor == "HDMI-A-1"
    bar.select_monitor("HDMI-A-1")
    assert bar.current_monitor == "HDMI-A-1"


@patch("subprocess.call")
@patch("subprocess.Popen")
@patch("HyprParser.HyprParser.hypr_write")
def test_apply_runs_command(mock_write, mock_popen, mock_call, shared_data):
    bar = BottomBar(shared_data)
    shared_data.selectedImage = "/fake/image.jpg"
    bar.apply()
    mock_write.assert_called_once()
    mock_call.assert_called_with(["kill", "hyprpaper"])
    mock_popen.assert_called_with(["hyprpaper"])


def test_settings_toggle_and_slide(shared_data):
    win = SettingsWindow(shared_data)
    win.checkBox.setChecked(True)
    assert win.slider.isEnabled()
    win.slider.setValue(2)
    assert shared_data.data["dpi"] == "2.0"
    win.checkBox.setChecked(False)
    assert not win.slider.isEnabled()


@patch("agemo.os.path.dirname")
def test_gallery_load_and_click(mock_dirname, tmp_path, shared_data):
    mock_dirname.return_value = str(tmp_path)
    shared_data.data["wallpapers_dir"] = str(tmp_path)

    json_path = tmp_path / "xdgcache.json"
    thumbs = [{"image": "img1.jpg", "thumbnail": "img1.jpg", "date": "today", "name": "img"}]
    with open(json_path, "w") as f:
        json.dump(thumbs, f)

    gallery = Gallery(shared_data)
    assert gallery.grid_layout.count() == 1


@patch("agemo.os.path.dirname")
def test_gallery_creates_empty_cache_if_missing(mock_dirname, tmp_path, shared_data):
    mock_dirname.return_value = str(tmp_path)
    shared_data.data["wallpapers_dir"] = str(tmp_path)

    cache_file = tmp_path / "xdgcache.json"
    if cache_file.exists():
        os.remove(cache_file)

    gallery = Gallery(shared_data)
    assert cache_file.exists()
    assert cache_file.read_text() == "[]"


def test_mainwindow_bootstrap(monkeypatch):
    monkeypatch.setenv("QT_SCALE_FACTOR", "1.5")
    window = MainWindow()
    assert isinstance(window.gallery, Gallery)
    assert isinstance(window.bottom_bar, BottomBar)
    assert isinstance(window.top_bar, TopBar)
