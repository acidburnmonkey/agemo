# pyright: reportOptionalMemberAccess=none
#
#  https://github.com/acidburnmonkey


import json
import os
import sys

import PyQt6.QtWidgets as qt
from PyQt6.QtCore import QProcess, QProcessEnvironment, QSize, Qt
from PyQt6.QtGui import QIcon

from constants import ASSETS_DIR, ROOT_DIR


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

        self.scaleFactor = os.environ.get("QT_SCALE_FACTOR")
        if self.scaleFactor:
            self.label.setText(f"""You already have scaling set on environment :
                               $QT_SCALE_FACTOR: {self.scaleFactor}
                               """)

    # UI
    def initUI(self):
        script_path = os.path.join(ROOT_DIR, "style.qss")
        with open(script_path, "r") as f:
            qss = f.read()

        self.setStyleSheet(qss)
        self.setFixedSize(400, 300)  # w,h

        self.settingsLayout = qt.QGridLayout(self)
        self.settingsLayout.setContentsMargins(2, 2, 2, 2)
        self.settingsLayout.setVerticalSpacing(50)

        # settings

        # exit
        icon = QIcon(str(ASSETS_DIR / "close.svg"))
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
