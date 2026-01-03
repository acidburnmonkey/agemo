import re
from pathlib import Path
from string import Template

from SharedData import SharedData

CONFIG_PATH = Path("~/.config/hypr/hyprpaper.conf").expanduser()

TEMPLATE = Template("""
wallpaper {
    monitor = $monitor
    path = $path
    fit_mode = $fit
}\n """)


class Wallpaper:
    def __init__(self, monitor="", path="", fit_mode="cover"):
        self.monitor = monitor
        self.path = path
        self.fit_mode = fit_mode

    def to_conf(self):
        return TEMPLATE.substitute(
            monitor=self.monitor,
            path=self.path,
            fit=self.fit_mode or "cover",
        )

    def __repr__(self):
        return f"Wallpaper(monitor={self.monitor!r}, path={self.path!r}, fit_mode={self.fit_mode!r})"

    def __str__(self):
        return self.to_conf()


class HyprpaperConfig:
    """
    Container for a parsed hyprpaper.conf.

    Holds:
      - self.globals: dict of `$var = value` assignments no leading '$' in keys
      - self.wallpapers: list of Wallpaper ( objects )

    Example:
        cfg.wallpapers[0].monitor
        cfg.wallpapers[0].to_conf()
        cfg.globals.get("wallpaper1")
    """

    def __init__(self):
        self.globals = {}
        self.wallpapers = []
        self.settings = {}

    def resolve(self, value):
        if isinstance(value, str) and value.startswith("$"):
            return self.globals.get(value[1:], value)
        return value


class HyprpaperParser:
    GLOBAL_RE = re.compile(r"^\s*\$(\w+)\s+=\s+(.+?)\s*$")
    BLOCK_START_RE = re.compile(r"^\s*wallpaper\s*\{\s*$")
    BLOCK_END_RE = re.compile(r"^\s*\}\s*$")
    KV_RE = re.compile(r"^\s*(\w+)\s+=\s+(.+?)\s*$")

    @classmethod
    def parse(cls):
        cfg = HyprpaperConfig()
        lines = []

        with open(CONFIG_PATH, "r") as f:
            lines = f.read().splitlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line or line.startswith("#"):
                i += 1
                continue

            m = cls.GLOBAL_RE.match(lines[i])
            if m:
                name = m.group(1)
                val = m.group(2).strip()
                cfg.globals[name] = val
                i += 1
                continue

            if cls.BLOCK_START_RE.match(lines[i]):
                i += 1
                data = {}
                while i < len(lines) and not cls.BLOCK_END_RE.match(lines[i]):
                    raw = lines[i].strip()
                    if raw and not raw.startswith("#"):
                        m2 = cls.KV_RE.match(lines[i])
                        if m2:
                            data[m2.group(1)] = m2.group(2).strip()
                    i += 1
                if i < len(lines) and cls.BLOCK_END_RE.match(lines[i]):
                    i += 1

                conf_block = Wallpaper(
                    monitor=data.get("monitor", ""),
                    path=data.get("path", ""),
                    fit_mode=data.get("fit_mode", "cover"),
                )
                cfg.wallpapers.append(conf_block)
                continue

            # settings splash
            m3 = cls.KV_RE.match(lines[i])
            if m3:
                cfg.settings[m3.group(1)] = m3.group(2).strip()
                i += 1
                continue

            i += 1

        return cfg


class HyprpaperWrite(SharedData):
    def __init__(self):
        super().__init__()
        self.config_path = Path(CONFIG_PATH)

        try:
            self.firstRun()
        except FileNotFoundError:
            Path.mkdir(CONFIG_PATH.parent, parents=True)
            self.firstRun()

    # writes file if not exist on initial run
    def firstRun(self):
        if not self.config_path.exists():
            self.monitors.sort()
            with open(self.config_path, "x") as f:
                for m in self.monitors:
                    try:
                        txt = TEMPLATE.substitute(monitor=m, path="", fit="cover")
                    except ValueError as e:
                        print(e.with_traceback)
                        return

                    f.write(txt)
                    f.write("\nsplash = true")

    def hypr_write(self, image_path, target_monitor):
        parser = HyprpaperParser.parse()
        create_new = True

        # splash serializer
        splash = parser.settings.get("splash")
        if splash == "true" or splash is None:
            splash = "\nsplash = true"
        else:
            splash = "\nsplash = false"

        for i, block in enumerate(parser.wallpapers):
            if block.monitor == target_monitor:
                parser.wallpapers[i].path = image_path
                create_new = False
                break

        out = "\n".join(block.to_conf() for block in parser.wallpapers)
        with open(CONFIG_PATH, "w") as f:
            f.write(out)

        # append to the top if monitor not in config
        if create_new:
            new_block = Wallpaper(image_path, target_monitor)

            with open(CONFIG_PATH, "r") as f:
                old = f.read()

            with open(CONFIG_PATH, "w") as f:
                f.write(new_block.to_conf() + "\n" + old)

        with open(CONFIG_PATH, "a") as f:
            f.write(splash)


def test_reader():
    print("Testing reader")
    print("reading from :", Path.cwd())

    cfg = HyprpaperParser.parse()

    # globals.get(var1)
    # # wallpaper.monitor / wallpaper.path
    print("Splash: ", cfg.settings.get("splash"))

    for wp in cfg.wallpapers:
        print(wp.monitor, wp.path, "->", cfg.resolve(wp.path))


if __name__ == "__main__":
    # test_reader()
    writer = HyprpaperWrite()
    writer.hypr_write("xxddd/xdhehe", "DP-2")
