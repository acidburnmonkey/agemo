import os
import subprocess
import json
from constants import ROOT_DIR

class SharedData:
    """
    This class load in memory data that the application uses
    @ self.data => default_settings {dict}
    @ self.thumbnails_data => json
    @ self.script_path => gets the directory of this program
    @self.selectedImage -> shared at runtime

    """

    def __init__(self):

        self.script_path = ROOT_DIR
        self.selectedImage = None
        self.data = self.load_settings()
        self.check_monitors()
        # self.thumbnails_data = self.load_xdgcache()

    @classmethod
    def load_settings(cls):
        default_settings = {
            "monitors": [],
            "splash": False,
            "ipc": True,
            "dpi": None,
            "wallpapers_dir": None,
        }

        try:
            with open(os.path.join(ROOT_DIR, "agemo.json"), "r") as f:
                file_data = json.load(f)
                return {**default_settings, **file_data}

        except FileNotFoundError:
            print("Error: Configuration file not found. Creating agemo.json")

            with open(os.path.join(ROOT_DIR, "agemo.json"),'w') as f:
                json.dump(default_settings, f, indent=4)
                return default_settings

        except json.JSONDecodeError:
            print("Error: Malformed JSON in.")
            return {}

    def check_monitors(self):
        try:
            hypr_ctl = subprocess.run(["hyprctl", "monitors", "-j"], stdout=subprocess.PIPE, text=True)
            hold = json.loads(hypr_ctl.stdout)

            # returns list of monitor names
            monitors = [m.get("name") for m in hold]
            self.data["monitors"] = monitors

            # Auto populate Monitors
            with open(os.path.join(self.script_path, "agemo.json"), "w") as f:
                json.dump(self.data, f, indent=4)

        except Exception as e:
            print(e)

    # unused check if needed or mk @classmethod
    def load_xdgcache(self):
        try:
            with open(os.path.join(self.script_path, "xdgcache.json"), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: Configuration file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error: Malformed JSON in.")
            return {}
