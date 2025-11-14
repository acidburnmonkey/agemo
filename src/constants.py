from pathlib import Path
from __init__ import __version__

# check if the path is my dev env or normal .local
def get_root():
    dev_mode = (Path(__file__).parent.parent / '.git').exists()

    if dev_mode:
        print("Running DEV")
        return Path(__file__).parent
    else:
        root_dir = Path.home() / '.local/share/agemo/src/'
        return root_dir


#returning strings for old os module

ROOT_DIR = str(get_root())
ASSETS_DIR = Path((ROOT_DIR)).parent / "assets"
GLOBAL_VERSION = __version__

CACHE_FILE = str(Path(get_root() / "xdgcache.json"))

