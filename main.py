import sys
import PyQt6.QtWidgets as qt
from PyQt6.QtCore import Qt


# bottom bar
class BottomBar(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # buttons
        self.apply = qt.QPushButton("Apply")
        self.apply2 = qt.QPushButton("Apply2")

        # Layout
        self.b_layout = qt.QHBoxLayout(self)

        self.b_layout.addWidget(self.apply)
        self.b_layout.addWidget(self.apply2)

        #Styling
        self.initUi()


    def initUi(self):
        # "ClassName"
        self.setObjectName("bottomBar")
        self.setStyleSheet('background: #181825 ; color: white')

        self.b_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.b_layout.setSpacing(4)

        # (left, top, right, bottom)
        # self.b_layout.setContentsMargins()
        self.apply.setGeometry(0,0,200,200)

        # self.apply.









# Main Window
class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        self.bottom_bar = BottomBar(self)

        self.initUi()

    def initUi(self):
        central_widget = qt.QWidget()  # these 2 are needed for MainWindow
        self.setCentralWidget(central_widget)

        v_box = qt.QVBoxLayout()

        v_box.addStretch() #  verify

        v_box.addWidget(self.bottom_bar)

        central_widget.setLayout(v_box)


def main():
    app = qt.QApplication(sys.argv)
    app.setDesktopFileName("Agemo")
    window = MainWindow()

    window.setWindowTitle("Agemo")

    window.show()
    app.exec()


if __name__ == "__main__":
    sys.exit(main())
