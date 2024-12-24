import re
import json
import subprocess


def hypr_reader():
    
    with open('hyprpaper.conf', 'r') as file:
        config = file.read()

    # Regular expressions to capture relevant patterns
    # preload_pattern = re.compile(r'preload\s*=\s*(.+)')
    # wallpaper_pattern = re.compile(r'wallpaper\s*=\s*([^,]+),(.+)')
    splash_pattern = re.compile(r'splash\s*=\s*(\w+)')
    ipc_pattern = re.compile(r'#?\s*ipc\s*=\s*(\w+)')

    # # Extract preloads
    # preloads = preload_pattern.findall(config)

    # # Extract wallpapers
    # wallpapers = wallpaper_pattern.search(config)

    # Extract splash status
    splash_status = splash_pattern.search(config)
    splash = splash_status.group(0) if splash_status else None

    # Extract ipc status
    ipc_status = ipc_pattern.search(config)
    ipc = ipc_status.group(0) if ipc_status else None

    # print("Preloads:")
    # print(preloads)
    # print("\nWallpapers:")
    # print(wallpapers.group(0))
    # print("\nSplash:", splash)
    # print("IPC:", ipc)

    return(splash, ipc)

# This is gonna get arguments from gui just hrd code it atm
def hypr_write():

    img_path = '$HOME/photos/'
    imgages = ['wallhaven-jx77pq.jpg','han-flores-dark-star-final-x-final-rs.jpg']
    monitors = get_mornitors()
    preload = []

    # Preload + wipe file
    with open('test.conf', 'w+') as f:
        for image in imgages:
            preload.append(f"preload= {img_path}{image}")

        #elements to write must be str
        f.writelines('\n'.join(preload))
           

    # Appends 
    with open('test.conf', 'a') as f:
        
        for monitor in monitors:
            f.write('\n')
            f.write(f'wallpaper = {monitor},{img_path}{imgages[0]}')
        
        f.write('\n\n\n')
        spash, ipc = hypr_reader()
        f.write(str(spash))
        f.write('\n')
        f.write(str(ipc))



# This loads all monitor info into Json
def get_mornitors():
 
    hypr_ctl = subprocess.run(['hyprctl','monitors','-j'], stdout=subprocess.PIPE, text=True)

    data = json.loads(hypr_ctl.stdout)
    
    # returns list of monitor names 
    monitors = [m.get('name') for m in data] 

    return monitors
    


if __name__=='__main__':
    hypr_write()
