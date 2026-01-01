import re
from pathlib import Path
from string import Template

from SharedData import SharedData

# class HyprParser:

#     @classmethod
#     def hypr_write(cls, image_path, target_monitor):


class Wallpaper:
    def __init__(self, monitor="", path="", fit_mode="cover"):
        self.monitor = monitor
        self.path = path
        self.fit_mode = fit_mode

    def __repr__(self):
        return f"Wallpaper(monitor={self.monitor!r}, path={self.path!r}, fit_mode={self.fit_mode!r})"


class HyprpaperConfig:
    def __init__(self):
        self.globals = {}  # {"wallpaper1": "/path/to/img", ...}  (no leading $)
        self.wallpapers = []  # [Wallpaper(...), ...]

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
    def parse(cls, text=None):
        """
        Resolve a hyprpaper variable reference into its concrete value.

        Hyprpaper config can declare globals like:
            $wallpaper1 = /home/user/pic.jpg

        And then reference them inside wallpaper blocks:
            wallpaper {
                monitor = DP-1
                path = $wallpaper1
                fit_mode = cover
            }

        Creates wallpaper {} block
        stored together on a single Wallpaper object:
            wp.monitor -> "DP-1"
            wp.path    -> "$wallpaper1"

        This method only resolves the  value if it starts with '$':
            - If value == "$name" and `self.globals["name"]` exists, return that global value.
            - Otherwise return the original value unchanged.

        Args:
            value: A string that may be a variable reference like "$wallpaper1".

        Returns:
            The resolved string  ("/home/user/pic.jpg") if the variable exists,
            otherwise the original input string.
        """

        cfg = HyprpaperConfig()
        lines = []

        # just for passing raw text for writing
        if text:
            lines = text.splitlines()

        with open("./src/test.conf", "r") as f:
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

                wp = Wallpaper(
                    monitor=data.get("monitor", ""),
                    path=data.get("path", ""),
                    fit_mode=data.get("fit_mode", "cover"),
                )
                cfg.wallpapers.append(wp)
                continue

            i += 1

        return cfg


class HyprpaperWrite(SharedData):


    def __init__(self) :
        super().__init__()

        self.config_path = Path("./src/test.conf")

        self.template = Template("""

wallpaper {
    monitor = $var
    path =
    fit_mode = cover
}\n """)

        # monitors: ['DP-1', 'DP-2']
        self.fistRun()



    #writes file if not exist on initial run
    def fistRun(self):
        if not self.config_path.exists():
            with open(self.config_path, "w+") as f:
                for  m in self.monitors:
                    txt = self.template.substitute(var=m)
                    f.write(txt)


    def hypr_write(self, image_path, target_monitor):
        parser = HyprpaperParser.parse()



# reader does not open the file
def test_reader():
    print("Testing reader")
    print("reading from :", Path.cwd())

    reader_sample = r"""
$wallpaper1 = /home/mahalo/photos/wallhaven-e8x3yo.jpg
$wallpaper2 = /home/mahalo/photos/wallhaven-8ggqqj.jpg

wallpaper {
    monitor = DP-1
    path = $wallpaper1
    fit_mode = cover
}

wallpaper {
    monitor = DP-2
    path = $wallpaper2
    fit_mode = cover
}
"""

    # cfg = HyprpaperParser.parse(reader_sample)
    cfg = HyprpaperParser.parse()

    # globals.get(var1)
    # # wallpaper.monitor / wallpaper.path

    for wp in cfg.wallpapers:
        print(wp.monitor, wp.path, "->", cfg.resolve(wp.path))


if __name__ == "__main__":
    # test_reader()

    writer = HyprpaperWrite()
    print(writer.fistRun())

    # writer.hypr_write('','')
