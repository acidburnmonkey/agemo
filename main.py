import sys
import PyQt6.QtWidgets as qt


class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        pass


def main():
    app = qt.QApplication(sys.argv)
    window = MainWindow()

    window.show()
    app.exec()


if __name__ == "__main__":
    sys.exit(main())
