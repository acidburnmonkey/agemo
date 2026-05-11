from __future__ import annotations

# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey
import json
import os
from typing import cast, override

import PyQt6.QtWidgets as qt
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QMouseEvent, QPixmap, QResizeEvent

from constants import ROOT_DIR, get_logger
from SharedData import SharedData

logg = get_logger(__name__)


## Gallery
class Gallery(qt.QWidget):
    def __init__(self, shared_data: SharedData):
        super().__init__()
        self.shared_data: SharedData = shared_data
        self.selected_label: ClickableLabel | None = None

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
        self.labels: list[ClickableLabel] = []
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

        for item in thumbnails:
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

            self.labels.append(imageLabel)

        self.reflow()

    # calculates rows and columns to display
    def reflow(self):
        columns = max(1, self.width() // 180)
        for i, lbl in enumerate(self.labels):
            row, col = divmod(i, columns)
            self.grid_layout.addWidget(lbl, row, col)

    @override
    def resizeEvent(self, event: QResizeEvent):  # pyright: ignore
        self.reflow()
        super().resizeEvent(event)

    def getClick(self):
        lbl = cast(ClickableLabel, self.sender())

        # clear the old border
        if self.selected_label and self.selected_label is not lbl:
            self.selected_label.setStyleSheet("")

        #  set red border on the newly clicked label
        lbl.setStyleSheet("border: 2px solid red; border-radius: 4px;")

        # remember
        self.selected_label = lbl
        self.shared_data.selectedImage = lbl.property("image")
        logg.info(f"label: {lbl.property('image')}")
        logg.debug(f"coordinates : {lbl.property('coordinates')}")


# subclass for Gallery
class ClickableLabel(qt.QLabel):
    """This just makes the labels Clickable , ignore lps sperging"""

    clicked = pyqtSignal()

    @override
    def mouseReleaseEvent(self, event: QMouseEvent):  # pyright: ignore
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)
