#!/bin/python3

# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey

import json
import os
import sys

import PyQt6.QtWidgets as qt
import helper
import xdgthumbails
from BottomBar import BottomBar
from constants import ROOT_DIR
from SharedData import SharedData
from splashWindow import SplashScreen
from TopBar import TopBar
from Gallery import Gallery

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
        self.gallery = Gallery(self.shared_data)

        self.top_bar.directoryChanged.connect(self.reloadGallery)

        self.initUi()

    def initUi(self):
        central_widget = qt.QWidget()  # these 2 are needed for MainWindow
        self.setCentralWidget(central_widget)

        v_box = qt.QVBoxLayout()
        # (left, top, right, bottom)
        v_box.setContentsMargins(0, 0, 0, 0)
        v_box.setSpacing(0)

        v_box.addWidget(self.top_bar)
        v_box.addWidget(self.gallery, 1)

        # v_box.addStretch()  # Pushes to bottom
        # bottom-bar
        v_box.addWidget(self.bottom_bar)

        central_widget.setLayout(v_box)

    def reloadGallery(self, newDir):
        print("new dir emitted:", newDir)
        # take the old gallery out of the layout
        layout = self.centralWidget().layout()
        layout.removeWidget(self.gallery)

        xdgthumbails.call_xdg(newDir)
        xdgthumbails.ligma(newDir)

        self.gallery.deleteLater()
        self.gallery = Gallery(self.shared_data)
        layout.insertWidget(1, self.gallery, stretch=1)


def load_index():
    print("Loading index...")
    shared_data = SharedData()

    try:
        if shared_data.data["wallpapers_dir"]:
            xdgthumbails.call_xdg(shared_data.data["wallpapers_dir"])
            xdgthumbails.ligma(shared_data.data["wallpapers_dir"])
        print("Loading complete!")

    except FileNotFoundError as e:
        print(e, " >> select a new source dir wallpapers_dir <<")


def main():
    # app init
    app = qt.QApplication(sys.argv)
    app.setDesktopFileName("Agemo")
    window = MainWindow()
    window.setWindowTitle("Agemo")

    SharedData.load_settings()

    # check for preset DPI
    with open(os.path.join(ROOT_DIR, "agemo.json"), "r") as f:
        data = json.load(f)
        # print('data[dpi]:',data['dpi'])

    if data["dpi"]:
        os.environ["QT_SCALE_FACTOR"] = str(data["dpi"])

    script_path = os.path.join(ROOT_DIR, "style.qss")
    with open(script_path, "r") as f:
        qss = f.read()

    # splash screen
    splash = SplashScreen()
    splash.setStyleSheet(qss)

    splash.show()
    qt.QApplication.processEvents()

    indexing_thread = helper.WorkerThread(load_index)

    def main_window():
        splash.finish(window)  # close splash
        window.setStyleSheet(qss)
        window.show()

    indexing_thread.finished.connect(main_window)
    indexing_thread.start()

    app.exec()


if __name__ == "__main__":
    sys.exit(main())
