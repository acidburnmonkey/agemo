# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey

import json
import os

import PyQt6.QtWidgets as qt
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap

from constants import ROOT_DIR


## Gallery
class Gallery(qt.QWidget):
    def __init__(self, shared_data):
        super().__init__()
        self.shared_data = shared_data
        self.selected_label = None

        # Create the scroll area and its inner widget
        self.scroll_area = qt.QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.scroll_widget = qt.QWidget()
        # grid_layout parent should be scroll_widget
        self.grid_layout = qt.QGridLayout(self.scroll_widget)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(5)
        self.grid_layout.setVerticalSpacing(5)

        self.scroll_widget.setLayout(self.grid_layout)
        self.scroll_widget.setObjectName("galleryGridWidget")
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setSizePolicy(
            qt.QSizePolicy.Policy.MinimumExpanding,
            qt.QSizePolicy.Policy.MinimumExpanding,
        )

        main_layout = qt.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)
        if self.shared_data.data["wallpapers_dir"]:
            self.load_gallery()

    def load_gallery(self):
        try:
            # object {"image": "thumbnail": "date": "name": }
            with open(os.path.join(ROOT_DIR, "xdgcache.json"), "r+") as f:
                thumbnails = json.load(f)

        except FileNotFoundError:
            thumbnails = []
            with open(os.path.join(ROOT_DIR, "xdgcache.json"), "w") as f:
                f.write("[]")

        for i, item in enumerate(thumbnails):
            # print(i,item['thumbnail'])

            # each square
            imageLabel = ClickableLabel()
            imageLabel.setPixmap(QPixmap(item["thumbnail"]))
            imageLabel.setProperty("image", item["image"])
            imageLabel.setFixedSize(180, 100)
            imageLabel.setScaledContents(True)

            imageLabel.clicked.connect(self.getClick)

            # shadow effect
            shadow = qt.QGraphicsDropShadowEffect(self.scroll_widget)
            shadow.setBlurRadius(12)
            shadow.setOffset(3, 3)
            shadow.setColor(QColor(0, 0, 0, 150))
            imageLabel.setGraphicsEffect(shadow)

            # 5 columns
            row, col = divmod(i, 10)
            imageLabel.setProperty("coordinates", (row, col))
            self.grid_layout.addWidget(imageLabel, row, col)

    def getClick(self):
        lbl = self.sender()

        # clear the old border
        if self.selected_label and self.selected_label is not lbl:
            self.selected_label.setStyleSheet("")

        #  set red border on the newly clicked label
        lbl.setStyleSheet("border: 2px solid red; border-radius: 4px;")

        # remember
        self.selected_label = lbl
        self.shared_data.selectedImage = lbl.property("image")
        print("label:", lbl.property("image"))
        # print("coordinates :", lbl.property("coordinates"))


# subclass for Gallery
class ClickableLabel(qt.QLabel):
    """This just makes the labels Clickable , ignore lps sperging"""

    clicked = pyqtSignal()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)
