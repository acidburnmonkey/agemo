import sys
import PyQt6.QtWidgets as qt
from PyQt6.QtCore import Qt


# bottom bar
class BottomBar(qt.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


        # with open('BottomBar.qss','r') as f:
        #     self.css = f.read()


        # buttons
        self.apply = qt.QPushButton("Apply")
        self.apply2 = qt.QPushButton("Apply2")

        # Layout and  frame
        self.bframe = qt.QFrame(self)
        self.b_layout = qt.QHBoxLayout(self.bframe)
        self.b_layout.addWidget(self.apply)
        self.b_layout.addWidget(self.apply2)

        #mainLayout
        self.main_layout = qt.QHBoxLayout(self)
        self.main_layout.addWidget(self.bframe)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        #Styling
        self.initUi()


    def initUi(self):

        self.b_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.b_layout.setSpacing(4)

        # self.b_layout.setContentsMargins()
        self.bframe.setStyleSheet('QFrame{border:1px solid blue; border-radius: 10px;}')
        # self.bframe.setStyleSheet(self.css)

        self.apply.setFixedSize(100,20) #W , H





# Main Window
class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        self.bottom_bar = BottomBar(self)
        self.testLabel = qt.QLabel('TEST')

        self.initUi()

    def initUi(self):
        central_widget = qt.QWidget()  # these 2 are needed for MainWindow
        self.setCentralWidget(central_widget)

        v_box = qt.QVBoxLayout()

        # (left, top, right, bottom)
        v_box.setContentsMargins(0,0,0,0)


        #test
        v_box.addWidget(self.testLabel)

        self.testLabel.setStyleSheet('color:black; background-color:#6ea5ff; border: solid black;')

        v_box.addStretch() # Pushes to bottom
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
