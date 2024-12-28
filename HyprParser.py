import re
from pathlib import Path
from CTkMessagebox import CTkMessagebox



class HyprParser:

    @classmethod
    def hypr_reader(cls):

        config_file = str( Path.home()) + '/.config/hypr/hyprpaper.conf' 
        
        with open(config_file, 'r') as file:
            config = file.read()

        # Regular expressions to capture relevant patterns
        splash_pattern = re.compile(r'splash\s*=\s*(\w+)')
        ipc_pattern = re.compile(r'#?\s*ipc\s*=\s*(\w+)')
        monitor_pattern = re.compile(r'^wallpaper\s*=\s*([^,]+),', re.MULTILINE)

        # Extract splash status
        splash_status = splash_pattern.search(config)
        splash = splash_status.group(1) if splash_status else None

        # Extract ipc status
        ipc_status = ipc_pattern.search(config)
        ipc = ipc_status.group(1) if ipc_status else None

        # Extract monitors
        monitor_stats = monitor_pattern.findall(config)  # findall returns all matches as a list
        monitors = monitor_stats if monitor_stats else []

        # Return extracted values
        return splash, ipc, monitors


    @classmethod
    def hypr_write(cls,image_path, target_monitor):

        config_file = str( Path.home()) + '/.config/hypr/hyprpaper.conf' 

        try:
            with open(config_file, 'r') as file:
                lines = file.readlines()

            preload_pattern = re.compile(r'^preload\s*=\s*(.+)$')
            wallpaper_pattern = re.compile(r'^wallpaper\s*=\s*([^,]+),(.*)$')

            # Extract preload and wallpaper data
            preloads = set()  
            wallpapers = {}
            other_lines = []

            for line in lines:
                if preload_match := preload_pattern.match(line):
                    preload_path = preload_match.group(1).strip()
                    preloads.add(preload_path)
                elif wallpaper_match := wallpaper_pattern.match(line):
                    monitor = wallpaper_match.group(1).strip()
                    wallpaper_path = wallpaper_match.group(2).strip()
                    wallpapers[monitor] = wallpaper_path
                else:
                    other_lines.append(line.strip())

            wallpapers[target_monitor] = image_path

            # Synchronize preload with wallpapers
            preloads = {path for path in preloads if path in wallpapers.values()}  # Keep only valid paths
            preloads.add(image_path)  # Ensure the new wallpaper is preloaded

            # Write the updated configuration back to the file
            with open('hyprpaper.conf', 'w') as file:
                # Write updated preload entries
                for preload_path in sorted(preloads):  
                    file.write(f"preload= {preload_path}\n")

                # Write updated wallpaper entries
                for monitor, wallpaper_path in wallpapers.items():
                    file.write(f"wallpaper = {monitor},{wallpaper_path}\n")

                # Write other configuration lines
                for line in other_lines:
                    file.write(f"{line}\n")

            return True

        except  FileNotFoundError:
            CTkMessagebox(title="Error", icon="warning", message="hyprpaper.conf file not found")
            return False

