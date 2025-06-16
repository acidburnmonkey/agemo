import sys
import os
import subprocess
import json
import PyQt6.QtWidgets as qt
from PyQt6.QtCore import Qt


class SharedData:
    '''
    This class load in memory data that the application uses
    @ self.data => default_settings {dict}
    @ self.thumbnails_data => json

    '''
    def __init__(self):

        self.script_path = os.path.join(os.path.dirname(__file__))
        self.data = self.load_settings()
        self.check_monitors()
        self.thumbnails_data = self.load_thubnailer_data()


    def load_settings(self):
        default_settings = {
            "monitors": [],
            "splash": False,
            "ipc": True,
            "dpi": None,
            "wallpapers_dir": None
        }

        try:
            with open(os.path.join(self.script_path,'agemo.json'), 'r') as f:
                file_data = json.load(f)
                return {**default_settings, **file_data}

        except FileNotFoundError:
            print("Error: Configuration file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Malformed JSON in.")
            return {}

    def check_monitors(self):
        try:
            hypr_ctl = subprocess.run(['hyprctl','monitors','-j'], stdout=subprocess.PIPE, text=True)
            hold = json.loads(hypr_ctl.stdout)

            # returns list of monitor names
            monitors = [m.get('name') for m in hold]
            self.data['monitors'] = monitors

            # Auto populate Monitors
            with open(os.path.join(self.script_path,'agemo.json'),'w') as f:
                json.dump(self.data,f, indent=4)

        except Exception as e:
            print(e)

    def load_thubnailer_data(self):
        try:
            with open(os.path.join(self.script_path,'thumbnail_cache.json'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: Configuration file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Malformed JSON in.")
            return {}



# bottom bar
class BottomBar(qt.QWidget):
    def __init__(self,shared_data=None,parent=None):
        super().__init__(parent)


        # with open('BottomBar.qss','r') as f:
        #     self.css = f.read()

        self.monitors = shared_data.data['monitors']
        print(self.monitors)

        # buttons
        self.apply = qt.QPushButton("Apply")
        self.monitors_select = qt.QComboBox()
        self.monitors_select.addItems(self.monitors)
        self.current_monitor = self.monitors[0]

        #events
        self.monitors_select.currentTextChanged.connect(self.select_monitor)


        # Layout and  frame
        self.bframe = qt.QFrame(self)
        self.b_layout = qt.QHBoxLayout(self.bframe)
        self.b_layout.addWidget(self.apply)
        self.b_layout.addWidget(self.monitors_select)

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

        self.apply.setFixedSize(80,20) #W , H
        self.monitors_select.setFixedSize(100,20) #W , H


    def select_monitor(self,l):
        self.current_monitor = l
        print('self.current_monitor:',self.current_monitor)



# Main Window
class MainWindow(qt.QMainWindow):
    def __init__(self):
        super().__init__()

        #shared data
        self.shared_data = SharedData()

        self.bottom_bar = BottomBar(self.shared_data,self)
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
