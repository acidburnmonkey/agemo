from pathlib import Path


# check if the path is my dev env or normal .local
dev_mode = (Path(__file__).parent.parent / ".git").exists()


def get_root():
    if dev_mode:
        return Path(__file__).parent
    else:
        root_dir = Path.home() / ".local/share/agemo/src/"
        return root_dir


if dev_mode:
    print("Running DEV")


__version__  = "2.4.1"
# returning strings for old os module
ROOT_DIR = get_root()
ASSETS_DIR = Path((ROOT_DIR)).parent / "assets"
GLOBAL_VERSION = __version__
CACHE_FILE = Path(get_root() / "xdgcache.json")
