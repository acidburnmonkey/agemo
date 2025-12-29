from PyQt6.QtWidgets import QDialog, QLabel, QHBoxLayout
from PyQt6.QtCore import QTimer, Qt


class SplashScreen(QDialog):
    def __init__(self):
        super().__init__()

        self.setObjectName("splashWindow")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.message = QLabel("Generating thumbnails and Indexing")
        self.message.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Animate with QTimer
        self.dot_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dots)
        self.timer.start(500)

        layout.addWidget(self.message)
        self.setLayout(layout)

    # copying what builtin splash does
    def finish(self, main_window):
        self.close()
        main_window.show()

    def update_dots(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.message.setText(f"Generating thumbnails and Indexing{dots}   ")
