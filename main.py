#!/bin/python3


# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey
#

import sys
import os
import subprocess
import json
import PyQt6.QtWidgets as qt
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
import xdgthumbails

class SharedData:
    """
    This class load in memory data that the application uses
    @ self.data => default_settings {dict}
    @ self.thumbnails_data => json
    @ self.script_path => gets the directory of this program
    """

    def __init__(self):
        self.script_path = os.path.join(os.path.dirname(__file__))
        self.data = self.load_settings()
        self.check_monitors()
        self.thumbnails_data = self.load_thubnailer_data()

    def load_settings(self):
        default_settings = {
            "monitors": [],
            "splash": False,
            "ipc": True,
            "dpi": None,
            "wallpapers_dir": None,
        }

        try:
            with open(os.path.join(self.script_path, "agemo.json"), "r") as f:
                file_data = json.load(f)
                return {**default_settings, **file_data}

        except FileNotFoundError:
            print("Error: Configuration file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Malformed JSON in.")
            return {}

    def check_monitors(self):
        try:
            hypr_ctl = subprocess.run(
                ["hyprctl", "monitors", "-j"], stdout=subprocess.PIPE, text=True
            )
            hold = json.loads(hypr_ctl.stdout)

            # returns list of monitor names
            monitors = [m.get("name") for m in hold]
            self.data["monitors"] = monitors

            # Auto populate Monitors
            with open(os.path.join(self.script_path, "agemo.json"), "w") as f:
                json.dump(self.data, f, indent=4)

        except Exception as e:
            print(e)

    def load_thubnailer_data(self):
        try:
            with open(os.path.join(self.script_path, "thumbnail_cache.json"), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: Configuration file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Malformed JSON in.")
            return {}


# bottom bar
class BottomBar(qt.QWidget):
    def __init__(self, shared_data=None, parent=None):
        super().__init__(parent)

        self.monitors = shared_data.data["monitors"]

        # buttons
        self.apply = qt.QPushButton("Apply")
        self.monitors_select = qt.QComboBox()
        self.monitors_select.addItems(self.monitors)
        self.current_monitor = self.monitors[0]

        # events
        self.monitors_select.currentTextChanged.connect(self.select_monitor)

        # Layout and  frame
        self.bframe = qt.QFrame(self)
        self.b_layout = qt.QHBoxLayout(self.bframe)
        self.b_layout.addWidget(self.apply)
        self.b_layout.addWidget(self.monitors_select)

        # mainLayout
        self.main_layout = qt.QHBoxLayout(self)
        self.main_layout.addWidget(self.bframe)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Styling
        self.initUi()

    def initUi(self):
        self.b_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.b_layout.setSpacing(4)

        self.bframe.setStyleSheet("QFrame{border:1px solid blue; border-radius: 10px;}")

        self.apply.setFixedSize(80, 20)  # W , H
        self.monitors_select.setFixedSize(100, 20)  # W , H
        self.monitors_select.setObjectName("monitors_select")

    def select_monitor(self, selected):
        self.current_monitor = selected
        print("self.current_monitor:", self.current_monitor)


# Top bar
class TopBar(qt.QWidget):
    def __init__(self, shared_data=None, parent=None):
        super().__init__(parent)

        self.shared_data = shared_data

        # Buttons
        self.close_button = qt.QPushButton()
        self.close_button.clicked.connect(self.exit)

        self.settings = qt.QPushButton("Settings")
        self.sources = qt.QPushButton("Sources")
        self.sources.clicked.connect(self.get_wallpapers)

        self.about = qt.QPushButton("About")
        self.about.clicked.connect(self.show_about)

        self.close_button.setObjectName("close_button")

        self.initUI()

    def initUI(self):
        self.tlayout = qt.QHBoxLayout(self)

        self.tlayout.setContentsMargins(0, 0, 0, 0)
        # settings
        self.tlayout.addWidget(self.settings)
        self.tlayout.addWidget(self.sources)
        self.tlayout.addWidget(self.about)

        # exit
        icon = QIcon(os.path.join(self.shared_data.script_path, "assets/close.svg"))
        self.close_button.setIcon(icon)
        self.close_button.setIconSize(QSize(25, 25))
        self.close_button.setFixedSize(self.close_button.iconSize())

        self.tlayout.addWidget(
            self.close_button,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
        )

    # wallpapers dir
    def get_wallpapers(self):

        wallpapers_dir = qt.QFileDialog.getExistingDirectory(
            self,
            "Select the wallpapers directory ",
            "",
            qt.QFileDialog.Option.ShowDirsOnly,
        )

        self.prev_wallpapers_dir = self.shared_data.data["wallpapers_dir"]

        if wallpapers_dir:
            self.shared_data.data["wallpapers_dir"] = wallpapers_dir

            total = len(os.listdir(wallpapers_dir))

            with open(
                os.path.join(self.shared_data.script_path, "agemo.json"), "w"
            ) as f:
                json.dump(self.shared_data.data, f, indent=4)

            # start indexing
            # fisrst time run here
            if (not bool(self.prev_wallpapers_dir)) and wallpapers_dir:
                # self.first_time_run(total) # Implement the loading bar other way
                print("First time run:", not bool(self.prev_wallpapers_dir))
                thumnailer.ligma(self.shared_data.data["wallpapers_dir"])

            elif wallpapers_dir:
                xdgthumbails.ligma(self.shared_data.data["wallpapers_dir"])

            ## Debug
            print("Total images on wallpaper dir:", total)
            print("wallpapers_dir:", wallpapers_dir)
            print( "shared_data['wallpapers_dir'] :", self.shared_data.data["wallpapers_dir"],)


    # About window : dwindow
    def show_about(self):
        dwindow = qt.QDialog(self)
        dwindow.setWindowTitle("About")
        abox = qt.QVBoxLayout(dwindow)

        # image
        project_icon_label = qt.QLabel(dwindow)
        pixmap = QPixmap(self.shared_data.script_path + "/assets/agemo.png")
        project_icon_label.setPixmap(pixmap)
        project_icon_label.setFixedSize(50, 50)
        project_icon_label.setScaledContents(True)  # scale image to label size
        abox.addWidget(
            project_icon_label,
            alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop,
        )

        # link
        description = qt.QLabel("https://github.com/acidburnmonkey/agemo", dwindow)
        version = qt.QLabel("version 2.0", dwindow)
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


# Main Window
class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        # shared data
        self.shared_data = SharedData()

        print(
            "shared_data['wallpapers_dir'] :", self.shared_data.data["wallpapers_dir"]
        )

        self.bottom_bar = BottomBar(self.shared_data, self)
        self.top_bar = TopBar(self.shared_data, self)
        self.testLabel = qt.QLabel("TEST")
        self.testLabel2 = qt.QLabel("TEST2")

        self.initUi()

    def initUi(self):
        central_widget = qt.QWidget()  # these 2 are needed for MainWindow
        self.setCentralWidget(central_widget)

        v_box = qt.QVBoxLayout()

        # (left, top, right, bottom)
        v_box.setContentsMargins(0, 0, 0, 0)

        # test
        v_box.addWidget(self.top_bar)
        v_box.addWidget(self.testLabel)
        v_box.addWidget(self.testLabel2)

        self.testLabel.setStyleSheet(
            "color:black; background-color:#6ea5ff; border: solid black;"
        )
        self.testLabel.setFixedSize(155,100)

        self.testLabel2.setPixmap(QPixmap('./src/120.jpg'))
        self.testLabel2.setFixedSize(155,100)
        self.testLabel2.setScaledContents(True)



        v_box.addStretch()  # Pushes to bottom
        #bottom-bar
        v_box.addWidget(self.bottom_bar)

        central_widget.setLayout(v_box)


def main():
    app = qt.QApplication(sys.argv)
    app.setDesktopFileName("Agemo")
    window = MainWindow()
    window.setWindowTitle("Agemo")

    script_path = os.path.join(os.path.dirname(__file__), "style.qss")
    with open(script_path, "r") as f:
        qss = f.read()

    window.setStyleSheet(qss)

    window.show()
    app.exec()


if __name__ == "__main__":
    sys.exit(main())
