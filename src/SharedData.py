import os
import subprocess
import json


class SharedData:
    """
    This class load in memory data that the application uses
    @ self.data => default_settings {dict}
    @ self.thumbnails_data => json
    @ self.script_path => gets the directory of this program
    @self.selectedImage -> shared at runtime

    """

    def __init__(self):
        # Dev check
        dev_mode = os.path.exists(os.path.dirname(os.path.join(os.path.dirname(__file__), '.git')))
        if dev_mode:
            self.script_path = os.path.dirname(__file__)
        else:
            self.script_path = os.path.join(os.path.expanduser("~"), '.local/share/agemo/')

        self.selectedImage = None
        self.data = self.load_settings()
        self.check_monitors()
        # self.thumbnails_data = self.load_xdgcache()

    def load_settings(self):
        default_settings = {
            "monitors": [],
            "splash": False,
            "ipc": True,
            "dpi": None,
            "wallpapers_dir": None,
        }

        try:
            with open(os.path.join(self.script_path, "agemo.json"), "r") as f:
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
