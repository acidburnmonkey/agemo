# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey


import json
import os
import sys

import PyQt6.QtWidgets as qt
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

import xdgthumbails
from constants import ASSETS_DIR, GLOBAL_VERSION
from settings import SettingsWindow


# Top bar
class TopBar(qt.QWidget):
    # emit signal on dir change
    directoryChanged = pyqtSignal(str)

    def __init__(self, shared_data=None, parent=None):
        super().__init__(parent)

        self.shared_data = shared_data

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
        self.settings_window = SettingsWindow(self.shared_data)
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
                print("First time run:", not bool(self.prev_wallpapers_dir))
                xdgthumbails.call_xdg(self.shared_data.data["wallpapers_dir"])
                xdgthumbails.ligma(self.shared_data.data["wallpapers_dir"])

            # emit signal to gallery
            self.directoryChanged.emit(wallpapers_dir)

            ## Debug
            print("Total images on wallpaper dir:", total)
            print("wallpapers_dir:", wallpapers_dir)
            print(
                "shared_data['wallpapers_dir'] :",
                self.shared_data.data["wallpapers_dir"],
            )

    # About window : dwindow
    def show_about(self):
        dwindow = qt.QDialog(self)
        dwindow.setWindowTitle("About")
        abox = qt.QVBoxLayout(dwindow)

        # image
        project_icon_label = qt.QLabel(dwindow)
        pixmap = QPixmap(str(ASSETS_DIR / "agemo.png"))
        project_icon_label.setPixmap(pixmap)
        project_icon_label.setFixedSize(50, 50)
        project_icon_label.setScaledContents(True)  # scale image to label size
        abox.addWidget(
            project_icon_label,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop,
        )

        # link
        description = qt.QLabel("https://github.com/acidburnmonkey/agemo", dwindow)
        version = qt.QLabel(GLOBAL_VERSION, dwindow)
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        abox.addWidget(description)
        abox.addWidget(version)

        # ok
        dismiss_button = qt.QPushButton("OK", dwindow)
        dismiss_button.clicked.connect(dwindow.close)
        dismiss_button.setFixedSize(50, 20)
        abox.addWidget(dismiss_button, alignment=Qt.AlignmentFlag.AlignCenter)

        dwindow.setLayout(abox)
        dwindow.adjustSize()  # calculate size
        dwindow.setFixedSize(dwindow.size())  # set fixed
        dwindow.exec()

    def exit(self):
        sys.exit()
