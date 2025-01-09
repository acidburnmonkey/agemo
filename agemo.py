#!/bin/python3

#
#  https://github.com/acidburnmonkey
#


import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from PIL import Image
import json
import subprocess
import time
import os
import threading

import thumnailer


class SharedData:
    def __init__(self):
      
        self.script_path = os.path.join(os.path.dirname(__file__))
        self.data = self.load_settings()
        self.check_monitors()
        self.thumbnails_data = self.load_thubnailer_data()


    def load_settings(self):
        try:
            with open(os.path.join(self.script_path,'agemo.json'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Malformed JSON in.")
            return {}

    def check_monitors(self):
        try:
            hypr_ctl = subprocess.run(['hyprctl','monitors','-j'], stdout=subprocess.PIPE, text=True)
            hold = json.loads(hypr_ctl.stdout)
            
            # returns list of monitor names 
            monitors = [m.get('name') for m in hold] 
            self.data['monitors'] = monitors
 
            # Auto populate Monitors
            with open(os.path.join(self.script_path,'agemo.json'),'w') as f:
                json.dump(self.data,f, indent=4)

        except Exception as e:
            print(e)

    def load_thubnailer_data(self):
        try:
            with open(os.path.join(self.script_path,'thumbnail_cache.json'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Malformed JSON in.")
            return {}


# APP Main Logic
class Main_Frame(ctk.CTk):
    def __init__(self):
        super().__init__()

        #General settings
        self.attributes('-type', 'window')
        self.title("Agemo")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # intantiate Json files
        self.file_data = SharedData()
        self.file_data.check_monitors()
        
        if self.file_data.data.get('dpi'):
            self.wscaling =  ctk.set_widget_scaling(self.file_data.data['dpi'])  # widget dimensions and text size
            self.scaling = ctk.set_window_scaling(self.file_data.data['dpi'])
         
        
        # thumnailer.ligma()
        
        #thumbnailer disabled on first time setup
        if self.file_data.data.get('wallpapers_dir'):
             thumnailer.ligma(self.file_data.data['wallpapers_dir'])



        ## Widgets
        #top menu bar
        self.top_bar =Top_bar(self, self.file_data)
        self.top_bar.grid(column=0 , row=0, sticky='we')
        
        self.gallery_frame = Gallery(self,self.file_data , None)
        self.gallery_frame.grid(column=0 , row=1, sticky='wens')
        

        self.bottom_bar = Bottom_Bar(self, self.gallery_frame,self.file_data)
        self.bottom_bar.grid(column=0 , row=2, sticky='we')
        
        # Link Bottom_Bar back to Gallery (janky circular link but works)
        self.gallery_frame.bottom_button = self.bottom_bar

    
class Gallery(ctk.CTkScrollableFrame):
    def __init__(self, parent, shared_data, load_button):
        super().__init__(parent, width=3200, height=2600)
        

        self.json = shared_data
        self.image_paths = list(self.json.thumbnails_data.keys())
        self.current_batch_index = 0  
        self.batch_size = 40  
        self.labels = []  # Store references to labels for the images
        self.current_image_index = ctk.IntVar(value=-1) 
        self.bottom_button = load_button

        self.columnconfigure((0, 1, 2, 3), weight=1, uniform="batch") 
        self.rowconfigure((0, 1, 2, 3), weight=1, uniform="batch")  

        # Load the first batch
        self.load_batch(self.current_batch_index)

        # Scroll Wheel
        self.bind_all("<Button-4>", lambda e: self._parent_canvas.yview("scroll", -1, "units"))
        self.bind_all("<Button-5>", lambda e: self._parent_canvas.yview("scroll", 1, "units"))

    
    def load_batch(self, batch_index):
        """
        Load a specific batch of images.
        """
        start_index = batch_index * self.batch_size
        end_index = min(start_index + self.batch_size, len(self.image_paths))

        print(f"Loading batch {batch_index}: Images {start_index} to {end_index - 1}")  # Debugging line
        for index in range(start_index, end_index):
            try:
                image_path = self.image_paths[index]
                image = Image.open(image_path)
                photo = ctk.CTkImage(light_image=image, dark_image=image, size=(600, 600))

                label = ctk.CTkLabel(self, image=photo, text=f"Image {index}")
                label.grid(
                    row=index // 4 % self.batch_size, column=index % 4, padx=5, pady=5, sticky="wens"
                )
                label.image_path = image_path  # Attach the image path to the label
                self.labels.append(label)

                # Bind click event to the label
                label.bind("<Button-1>", lambda event, idx=index: self.image_clicked(idx))

            except Exception as e:
                print(f"Error loading image {index}: {e}")  # Debugging line


    def load_next_batch(self):
        """
        Load the next batch of images.
        """
        self.current_batch_index += 1
        if self.current_batch_index * self.batch_size < len(self.image_paths):
            self.load_batch(self.current_batch_index)
        else :
            self.bottom_button.load_more_button.configure(text="No More Images", state="disabled")


    def image_clicked(self, index):
        
        # Update the currently clicked image index
        self.current_image_index.set(index)
        clicked_label = self.labels[index]
        
        if hasattr(self, 'overlay_image') and self.overlay_image.winfo_exists():
            self.overlay_image.destroy()

        # Create a button and place it over the clicked image
        image = Image.open('assets/salomon.png')
        photo = ctk.CTkImage(light_image=image, dark_image=image, size=(300, 300))
        
        self.overlay_image = ctk.CTkLabel(self, text='', image=photo)
        grid_info = clicked_label.grid_info()
        self.overlay_image.grid(row=grid_info["row"], column=grid_info["column"], padx=grid_info["padx"], pady=grid_info["pady"])




#bottom_bar
class Bottom_Bar(ctk.CTkFrame):
    def __init__(self, parent, gallery_instance, shared_data):
        super().__init__(parent)
        
        # Json
        self.file_data = shared_data
        self.gallery = gallery_instance
        

        # Widgets
        ctk.CTkButton(self, text="Apply", command=self.apply_button).pack(side='left', padx=30)
        

        self.mw_var = ctk.StringVar()
        self.mw_var.set('Monitors')

        monitor_widget = ctk.CTkOptionMenu(self, values=[v for v in self.file_data.data['monitors']] ,command=self.select_monitor , variable=self.mw_var) 
        monitor_widget.pack(side='left', padx=30)

        self.load_more_button = ctk.CTkButton(self, text="Load More", command=self.gallery.load_next_batch)
        self.load_more_button.pack(side='left', padx=50)
        

    # Debugging
    def select_monitor(self,monitor):
        print(f"Selected monitor: {monitor}")  

    def apply_button(self):
        from HyprParser import HyprParser
        
        # Check if an image has been clicked
        current_index = self.gallery.current_image_index.get()

        if current_index != -1:
            # Retrieve the image last clicked as key
            clicked_image = self.gallery.labels[current_index].image_path
            real_path = self.file_data.thumbnails_data.get(clicked_image)[0]
            
            # Debug
            print(real_path)
            
            if (self.mw_var.get() !='Monitors'):

                HyprParser.hypr_write(real_path,self.mw_var.get())
                subprocess.call(['kill','hyprpaper'])
                time.sleep(1)
                subprocess.Popen(['hyprpaper'])

                #debug
                #print(real_path, '        ', self.mw_var.get())
        
        


#### top bar
class Top_bar(ctk.CTkFrame):
    def __init__(self,parent,shared_data):
        super().__init__(parent)
        
        self.file_data = shared_data
        self.flag = threading.Event()
        self.total = None

        self.settings = ctk.CTkButton(self, text= "settings",command=self.call_settings).pack(side='left',padx=10)
        self.sources = ctk.CTkButton(self, text= "Srources",command=self.getdir).pack(side='left',padx=10)
        self.about = ctk.CTkButton(self, text= "About",command=self.aboutf).pack(side='left',padx=10)
        self.ex = ctk.CTkButton(self, text= 'X', fg_color='black' ,command=self.kill).pack(anchor='e')
        
        self.settings_window = None
    
    # calls Settings_Window
    def call_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = Settings_Window(self)
        else:
            self.settings_window.focus()

    #quit app
    def kill(self):
        app.quit()
    
    def first_time_run(self):
       #inner f
       def progressBar(iteration, total, label, prefix='', suffix='', decimals=1, length=100, fill='█'):
            """
            @params:
                iteration   - Required  : current iteration (Int)
                total       - Required  : total iterations (Int)
                label       - Required  : CTkLabel widget to update (CTkLabel)
            """
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + '-' * (length - filledLength)
            label_text = f'{prefix} |{bar}| {percent}% {suffix}'
            label.configure(text=label_text)
            if iteration == total:
                label.configure(text=f"{prefix} |{'█' * length}| 100% {suffix}")

       popup = ctk.CTkToplevel(self)
       popup.focus()
       popup.attributes('-type', 'dialog')
       popup.geometry('500x400')
       
       popup_label = ctk.CTkLabel(popup,text='Indexing and creating thumbnails')
       popup_label.pack()

       popup_loading = ctk.CTkLabel(popup,text='█')
       popup_loading.pack(pady=20, padx= 20 ,anchor='w')
    
       #inner f 
       while not self.flag.is_set():
            current = len(os.listdir(os.path.join(os.path.dirname(__file__), 'thumbnails/') ))
            progressBar(current,self.total,popup_loading)
            print(current)
            

    #About Popup
    def aboutf(self):
        message = '''
        Agemo 
        https://github.com/acidburnmonkey/agemo
        '''
        CTkMessagebox(self,title="About",wraplength=9000000 ,icon='assets/agemo.png',message=message)
     
    def getdir(self):
        
        self.wallpapers_dir=  ctk.filedialog.askdirectory()
        self.file_data.data['wallpapers_dir'] = self.wallpapers_dir
        print(self.wallpapers_dir)
        print (self.file_data.data['wallpapers_dir'])

        self.total = len(self.wallpapers_dir)
        print('Total images on wallpaper dir:', self.total)

        # Write path of wallpapers_dir
        with open(os.path.join(self.file_data.script_path,'agemo.json'),'w') as f:
            json.dump(self.file_data.data,f, indent=4)

        # start indexing
        if self.file_data.data.get('wallpapers_dir'):
            thumnailer.ligma(self.file_data.data['wallpapers_dir'])

        # fisrst time run here
        elif self.file_data.data.get('wallpapers_dir') == '':
            print('First time run')
            
            t1 = threading.Thread(target=self.first_time_run)
            t1.start()
            thumnailer.ligma(self.file_data.data['wallpapers_dir'])
            self.flag.set()
            t1.join()



# settings window pop up 
class Settings_Window(ctk.CTkToplevel):
    def __init__(self,parent):
        super().__init__(parent)
        
        self.file_data = SharedData()

        self.attributes('-type', 'dialog')
        self.columnconfigure((6,1),weight=1)
        
        #exit button
        self.exit  = ctk.CTkButton(self,text='x',fg_color='black',command=self.destroy)
        self.exit.grid(row=0,column=6,sticky='ne')
        
        self.dpi_label = ctk.CTkLabel(self,text='Default Dpi')
        self.dpi_label.grid(row=1,column=1 ,padx=10, pady=10)
        # DPI Scale
        self.dpi_scale = ctk.CTkSlider(self, from_=0, to=3, number_of_steps=6, state='disabled', command=self.set_dpi)
        self.dpi_scale.grid(row=2,column=1 ,padx=5, pady=5)

        #switch
        self.swtich_var = ctk.IntVar(value=0)
        self.dpi_enabler = ctk.CTkSwitch(self, variable=self.swtich_var,onvalue=1, offvalue=0 ,command=self.dpi_switch,text='Enable DPI')
        self.dpi_enabler.grid(row=2,column=2 ,padx=10, pady=10)
        

        #Splash
        self.splash_label = ctk.CTkLabel(self,text='Splash')
        self.splash_label.grid(row=3,column=1 ,padx=5, pady=5)
        self.splash_options = ctk.CTkOptionMenu(self,values=['disabled','enabled'])
        self.splash_options.grid(row=3,column=2 ,padx=5, pady=10)
        
        #IPc
        self.ipc_label = ctk.CTkLabel(self,text='Ipc')
        self.ipc_label.grid(row=3,column=3 ,padx=5, pady=5)
        self.ipc_options = ctk.CTkOptionMenu(self,values=['enabled','disabled'])
        self.ipc_options.grid(row=3,column=4 ,padx=10, pady=10)


        # Apply Button
        self.apply_button = ctk.CTkButton(self, text='Apply', command=self.apply)
        self.apply_button.grid(row=8,column=2 ,padx=10, pady=10)
        
        # Reading from json
        if self.file_data.data['dpi']:
            self.swtich_var.set(1)
            self.dpi_scale._state = 'normal'

        if self.file_data.data['ipc'] == False:
            self.ipc_options.set('disabled')

        if self.file_data.data['splash']:
            self.splash_options.set('enabled')

    
    # Enables or Disables dpi scaling
    def dpi_switch(self):
        if self.swtich_var.get() == 0:
            self.dpi_scale.configure(state='disabled')
            self.dpi_label.configure(text='Default Dpi')
        elif self.swtich_var.get() == 1:
            self.dpi_scale.configure(state='normal')
               
        self.columnconfigure(4,weight=1)

        
    def set_dpi(self,value):
        self.dpi_label.configure(text=f'Dpi:{value}')
        

    def apply(self):
        value = self.dpi_scale.get()
        #print(self.dpi_scale._state)
        
        #Allows to set Dpi
        if self.swtich_var.get() == 1:
            self.wscaling =  ctk.set_widget_scaling(value)  # widget dimensions and text size
            self.scaling = ctk.set_window_scaling(value)
            self.file_data.data['dpi'] = value

        elif self.swtich_var.get() == 0:
            self.file_data.data['dpi'] = None
        
        # IPC
        if self.ipc_options.get() == 'enabled':
            self.file_data.data['ipc'] = True 
        else:
            self.file_data.data['ipc'] = False 

        #Splash
        if self.splash_options.get() == 'enabled':
            self.file_data.data['splash'] = True 
        else:
            self.file_data.data['splash'] = False 
        
        # write to config file
        with open(os.path.join(self.file_data.script_path,'agemo.json'), 'w') as f:
            json.dump(self.file_data.data,f, indent=4)



class loading_bar():
    def __init__(self):
        pass
        



if __name__ == '__main__':
    app = Main_Frame()
    app.mainloop()
