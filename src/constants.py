from pathlib import Path
from __init__ import __version__

# check if the path is my dev env or normal .local
def get_root():
    dev_mode = (Path(__file__).parent.parent / '.git').exists()

    if dev_mode:
        print("Running DEV")
        return str(Path(__file__).parent)
    else:
        root_dir = str(Path.home() / '.local/share/agemo/src/')
        return root_dir



ROOT_DIR = get_root()
ASSETS_DIR = Path((ROOT_DIR)).parent / "assets"
GLOBAL_VERSION = __version__
