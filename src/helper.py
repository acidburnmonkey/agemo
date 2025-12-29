from PyQt6.QtCore import QThread, pyqtSignal


class WorkerThread(QThread):
    """Thread to run func() without blocking the GUI"""

    finished = pyqtSignal()

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.func()
        self.finished.emit()
