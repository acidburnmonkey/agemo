from pathlib import Path
import sys
from __init__ import __version__


# check if the path is my dev env or normal .local
dev_mode = (Path(__file__).parent.parent / '.git').exists()


def get_root():
    if dev_mode:
        print("Running DEV")
        return Path(__file__).parent
    else:
        root_dir = Path.home() / '.local/share/agemo/src/'
        return root_dir


def get_asset_path():
    """Get the correct assets path whether running from source or installed."""

    if dev_mode:
        return Path((ROOT_DIR)).parent / "assets"

    # if installed pipx
    if sys.prefix != sys.base_prefix:  # We're in a venv
        installed_assets = Path(sys.prefix) / "share" / "agemo" / "assets"
        if installed_assets.exists():
            return installed_assets


# returning strings for old os module
ROOT_DIR = str(get_root())

ASSETS_DIR = str(get_asset_path())

GLOBAL_VERSION = __version__
CACHE_FILE = str(Path(get_root() / "xdgcache.json"))  # fix this for pipx
