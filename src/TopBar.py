# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey


import json
import os
import sys
from typing import override

import PyQt6.QtWidgets as qt
import requests
from PyQt6.QtCore import QSize, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

import xdgthumbails
from constants import ASSETS_DIR, GLOBAL_VERSION, get_logger
from settings import SettingsWindow
from SharedData import SharedData

logg = get_logger(__name__)


# returns string as tuple
def version_to_tuple(version: str) -> tuple[int, ...]:
    return tuple(map(int, version.strip("v").split(".")))


class UpdateChecker(QThread):
    finished = pyqtSignal(str)

    @override
    def run(self):
        try:
            res = requests.get(
                "https://api.github.com/repos/acidburnmonkey/agemo/tags", timeout=5
            )
            if res.ok:
                data = res.json()[0].get("name")
                self.finished.emit(data)
            else:
                self.finished.emit("N/A")
        except Exception as e:
            logg.info(f"Exception in thread: {e}")
            self.finished.emit("Error")


# Top bar
class TopBar(qt.QWidget):
    # emit signal on dir change
    directoryChanged = pyqtSignal(str)
    checkOnline = pyqtSignal(str)

    def __init__(
        self, shared_data: SharedData | None = None, parent: qt.QWidget | None = None
    ):
        super().__init__(parent)

        self.shared_data: SharedData | None = shared_data
        self.upstream_version: str | None = None

        # Buttons
        self.close_button = qt.QPushButton()
        self.close_button.clicked.connect(self.exit)

        self.settings = qt.QPushButton("Settings")
        self.settings.clicked.connect(self.open_settings)

        self.sources = qt.QPushButton("Sources")
        self.sources.clicked.connect(self.get_wallpapers)

        self.about = qt.QPushButton("About")
        self.about.clicked.connect(self.show_about)

        self.close_button.setObjectName("close_button")
        self.settings.setObjectName("settings")
        self.sources.setObjectName("sources")
        self.about.setObjectName("about")

        self.initUI()

    def initUI(self):
        self.tlayout = qt.QHBoxLayout(self)

        self.tlayout.setContentsMargins(0, 0, 0, 0)
        # settings
        self.tlayout.addWidget(self.settings)
        self.tlayout.addWidget(self.sources)
        self.tlayout.addWidget(self.about)

        # exit
        icon = QIcon(str(ASSETS_DIR / "close.svg"))
        self.close_button.setIcon(icon)
        self.close_button.setIconSize(QSize(25, 25))
        self.close_button.setFixedSize(self.close_button.iconSize())

        self.tlayout.addWidget(
            self.close_button,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
        )

    ## open SettingsWindow
    def open_settings(self):
        self.settings_window: SettingsWindow = SettingsWindow(self.shared_data)
        self.settings_window.show()

    # wallpapers dir
    def get_wallpapers(self):
        wallpapers_dir = qt.QFileDialog.getExistingDirectory(
            self,
            "Select the wallpapers directory ",
            "",
            qt.QFileDialog.Option.ShowDirsOnly,
        )

        self.prev_wallpapers_dir = self.shared_data.data["wallpapers_dir"]

        # on select
        if wallpapers_dir:
            self.shared_data.data["wallpapers_dir"] = wallpapers_dir
            total = len(os.listdir(wallpapers_dir))

            with open(
                os.path.join(self.shared_data.script_path, "agemo.json"), "w"
            ) as f:
                json.dump(self.shared_data.data, f, indent=4)

            # emit signal to gallery
            self.directoryChanged.emit(wallpapers_dir)

            # fisrst time run here
            if (not bool(self.prev_wallpapers_dir)) and wallpapers_dir:
                logg.info(f"First time run: {not bool(self.prev_wallpapers_dir)}")
                xdgthumbails.call_xdg(self.shared_data.data["wallpapers_dir"])
                xdgthumbails.ligma(self.shared_data.data["wallpapers_dir"])

            # emit signal to gallery
            self.directoryChanged.emit(wallpapers_dir)

            ## Debug
            logg.debug(f"Total images on wallpaper dir: {total}")
            logg.debug(f"wallpapers_dir: {wallpapers_dir}")
            logg.debug(
                f"shared_data['wallpapers_dir'] : {self.shared_data.data['wallpapers_dir']}"
            )

    # About window : dwindow
    def show_about(self):
        self.check_updates()
        self.dwindow: qt.QDialog = qt.QDialog(self)
        self.dwindow.setWindowTitle("About")
        abox = qt.QVBoxLayout(self.dwindow)

        # image
        project_icon_label = qt.QLabel(self.dwindow)
        pixmap = QPixmap(str(ASSETS_DIR / "agemo.png"))
        project_icon_label.setPixmap(pixmap)
        project_icon_label.setFixedSize(50, 50)
        project_icon_label.setScaledContents(True)  # scale image to label size
        abox.addWidget(
            project_icon_label,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop,
        )

        # link
        description = qt.QLabel("https://github.com/acidburnmonkey/agemo", self.dwindow)
        self.version_label: qt.QLabel = qt.QLabel(GLOBAL_VERSION, self.dwindow)
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        abox.addWidget(description)
        abox.addWidget(self.version_label)

        # ok
        dismiss_button = qt.QPushButton("OK", self.dwindow)
        dismiss_button.clicked.connect(self.dwindow.close)
        dismiss_button.setFixedSize(50, 20)
        abox.addWidget(dismiss_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.dwindow.setLayout(abox)
        self.dwindow.adjustSize()  # calculate size
        self.dwindow.setMinimumSize(self.dwindow.size())
        self.dwindow.exec()

    def exit(self):
        sys.exit()

    def check_updates(self):
        self.update_worker: UpdateChecker = UpdateChecker()
        self.update_worker.finished.connect(self.update_version_display)
        self.update_worker.start()
        logg.info("Checking for Updates")

    def update_version_display(self, version: str):
        self.upstream_version = version
        logg.info(f"self.upstream_version:  {self.upstream_version}")

        if version_to_tuple(self.upstream_version) > version_to_tuple(GLOBAL_VERSION):
            self.version_label.setStyleSheet("color: green;")
            self.version_label.setText(
                f"There is a new version!: {self.upstream_version} \n Current: {GLOBAL_VERSION} "
            )
            self.dwindow.adjustSize()

        self.dwindow.setFixedSize(self.dwindow.size())  # set fix size at the end
