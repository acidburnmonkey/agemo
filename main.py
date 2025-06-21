#!/bin/python3


# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey
#

import sys
import os
import json
import subprocess
import time
import PyQt6.QtWidgets as qt
from PyQt6.QtCore import Qt, QSize, QProcess, QProcessEnvironment, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QColor
import xdgthumbails
from SharedData import SharedData
from HyprParser import HyprParser


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
        if self.shared_data.data['wallpapers_dir']:
            self.load_gallery()

    def load_gallery(self):
        # object {"image": "thumbnail": "date": "name": }
        with open(os.path.join(os.path.dirname(__file__), "xdgcache.json"), "r") as f:
            thumbnails = json.load(f)

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
            row, col = divmod(i, 5)
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
        self.shared_data.selectedImage = lbl.property('image')
        print("label:", lbl.property("image"))
        # print("coordinates :", lbl.property("coordinates"))


class ClickableLabel(qt.QLabel):
    """This just makes the labels Clickable , ignore lps sperging"""

    clicked = pyqtSignal()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


# bottom bar
class BottomBar(qt.QWidget):
    def __init__(self, shared_data, parent=None):
        super().__init__(parent)

        self.monitors = shared_data.data["monitors"]
        self.shared_data = shared_data

        # buttons
        self.applyButton = qt.QPushButton("Apply")
        self.applyButton.clicked.connect(self.apply)
        self.monitors_select = qt.QComboBox()
        self.monitors_select.addItems(self.monitors)
        self.current_monitor = self.monitors[0]

        # events
        self.monitors_select.currentTextChanged.connect(self.select_monitor)

        # Layout and  frame
        self.bframe = qt.QFrame(self)
        self.b_layout = qt.QHBoxLayout(self.bframe)
        self.b_layout.addWidget(self.applyButton)
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

        self.bframe.setStyleSheet(
            "QFrame{border:1px solid #cad3f5; border-radius: 10px;}"
        )

        self.applyButton.setFixedSize(80, 20)  # W , H
        self.monitors_select.setFixedSize(100, 20)  # W , H
        self.monitors_select.setObjectName("monitors_select")

    def select_monitor(self, selected):
        self.current_monitor = selected
        print("selected > self.current_monitor:", self.current_monitor)


    def apply(self):

        if self.shared_data.selectedImage:
            print("applying to :", self.current_monitor)
            print('Image selected : ', self.shared_data.selectedImage)

            HyprParser.hypr_write(self.shared_data.selectedImage,self.current_monitor)
            subprocess.call(['kill','hyprpaper'])
            time.sleep(1)
            subprocess.Popen(['hyprpaper'])




# Top bar
class TopBar(qt.QWidget):
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
        icon = QIcon(os.path.join(self.shared_data.script_path, "assets/close.svg"))
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
                xdgthumbails.ligma(self.shared_data.data["wallpapers_dir"])

            elif wallpapers_dir:
                xdgthumbails.ligma(self.shared_data.data["wallpapers_dir"])

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


class SettingsWindow(qt.QWidget):
    """Settings Window"""

    def __init__(self, shared_data, parent=None):
        super().__init__(parent)

        self.shared_data = shared_data

        # Widgets
        self.close_button = qt.QPushButton()
        self.close_button.clicked.connect(self.close)
        self.close_button.setObjectName("close_button")

        # switch
        self.checkBox = qt.QCheckBox()
        self.checkBox.stateChanged.connect(self.checkorNot)
        self.checkBox.setObjectName("checkBox")

        # Sllider
        self.slider = qt.QSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.slide)
        self.slider.setRange(0, 4)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(qt.QSlider.TickPosition.TicksAbove)
        self.slider.setObjectName("slider")

        # labels
        self.label = qt.QLabel("Scale Factor")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("displaySettings")
        self.dpiLabel = qt.QLabel()
        self.dpiLabel.setObjectName("dpiLabel")

        # apply
        self.buttonScale = qt.QPushButton("Apply")
        self.buttonScale.setObjectName("settingsApply")
        self.buttonScale.clicked.connect(self.scaleNow)

        self.initUI()

        try:
            self.scaleFactor = os.environ["QT_SCALE_FACTOR"]
        except Exception as e:
            print(self.scaleFactor, e)

        if self.scaleFactor:
            self.label.setText(f"""You already have scaling set on environment :
                                  $QT_SCALE_FACTOR: {self.scaleFactor}
                               """)

    # UI
    def initUI(self):
        script_path = os.path.join(os.path.dirname(__file__), "style.qss")
        with open(script_path, "r") as f:
            qss = f.read()

        self.setStyleSheet(qss)
        self.setFixedSize(400, 300)  # w,h

        self.settingsLayout = qt.QGridLayout(self)
        self.settingsLayout.setContentsMargins(2, 2, 2, 2)
        self.settingsLayout.setVerticalSpacing(50)

        # settings

        # exit
        icon = QIcon(os.path.join(self.shared_data.script_path, "assets/close.svg"))
        self.close_button.setIcon(icon)
        self.close_button.setIconSize(QSize(25, 25))
        self.close_button.setFixedSize(self.close_button.iconSize())

        # row=0, column=0, rowspan=1, colspan=3
        # Corrected: Add widgets to layout (not layout itself)
        self.settingsLayout.addWidget(
            self.close_button,
            0,
            1,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )
        self.settingsLayout.addWidget(self.label, 0, 0)
        self.settingsLayout.addWidget(self.checkBox, 1, 0, 1, 1)
        self.settingsLayout.addWidget(self.dpiLabel, 1, 1, 1, 1)
        self.settingsLayout.addWidget(
            self.slider, 2, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        self.settingsLayout.addWidget(
            self.buttonScale,
            3,
            0,
            1,
            2,
            alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
        )

        # checkbox
        if self.shared_data.data["dpi"]:
            self.checkBox.setChecked(True)
            self.dpiLabel.setText("Disable Dpi Scaling")
        elif not self.shared_data.data["dpi"]:
            self.dpiLabel.setText("Set DPI")
            self.checkBox.setChecked(False)

        if self.checkBox.isChecked():
            self.slider.setEnabled(True)
        else:
            self.slider.setEnabled(False)

        ##END UI
        self.setLayout(self.settingsLayout)

    # Apply Settings
    def scaleNow(self):
        if self.shared_data.data["dpi"] and self.checkBox.isChecked():
            # write to config file
            with open(
                os.path.join(self.shared_data.script_path, "agemo.json"), "w"
            ) as f:
                json.dump(self.shared_data.data, f, indent=4)

            # build a QProcessEnvironment
            env = QProcessEnvironment.systemEnvironment()
            env.insert("QT_SCALE_FACTOR", self.shared_data.data["dpi"])

            # make a QProcess instance
            proc = QProcess(self)
            proc.setProcessEnvironment(env)
            proc.setProgram(sys.executable)
            proc.setArguments(sys.argv)
            proc.setWorkingDirectory(os.getcwd())

            # restart UI
            ok = proc.startDetached()
            if not ok:
                print("⚠️ child spawn failed")
                return

            # kill current UI
            qt.QApplication.quit()

        elif not self.checkBox.isChecked():
            self.shared_data.data["dpi"] = None
            with open(
                os.path.join(self.shared_data.script_path, "agemo.json"), "w"
            ) as f:
                json.dump(self.shared_data.data, f, indent=4)

    def slide(self, i):
        val = 1.0 + i * 0.5
        self.label.setText(f"Dpi :{val * 100}%")
        self.shared_data.data["dpi"] = str(val)  # it takes a string
        print("self.uiScaling:", self.shared_data.data["dpi"])

    def checkorNot(self, state):
        if state == 0:
            self.slider.setDisabled(True)
            self.dpiLabel.setText("Scale UI")
            self.shared_data.data["dpi"] = None
        else:
            self.dpiLabel.setText("Disable UI Scaling")
            self.slider.setEnabled(True)


# END OF SettingsWindow


# Main Window
class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        # shared data
        self.shared_data = SharedData()

        print(
            "shared_data['wallpapers_dir'] :", self.shared_data.data["wallpapers_dir"]
        )

        xdgthumbails.ligma(self.shared_data.data["wallpapers_dir"])

        self.bottom_bar = BottomBar(self.shared_data, self)
        self.top_bar = TopBar(self.shared_data, self)
        self.gallery = Gallery(self.shared_data)

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


def main():
    # check for preset DPI
    with open(os.path.join(os.path.dirname(__file__), "agemo.json"), "r") as f:
        data = json.load(f)
        # print('data[dpi]:',data['dpi'])

    if data["dpi"]:
        os.environ["QT_SCALE_FACTOR"] = str(data["dpi"])

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
