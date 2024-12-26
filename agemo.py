import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
import json
import subprocess

class SharedData:
    def __init__(self):
        self.data = self.load_settings()
        self.check_monitors()

    def load_settings(self):
        try:
            with open('agemo.json', 'r') as f:
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

        except Exception as e:
            print(e)



class Main_Frame(ctk.CTk):
    def __init__(self):
        super().__init__()

        #General settings
        # self.attributes('-type', 'window')
        self.columnconfigure(0, weight=1)
    
        # hdpi settings
        self.file_data = SharedData()
        
        if self.file_data.data['dpi']:
            self.wscaling =  ctk.set_widget_scaling(self.file_data.data['dpi'])  # widget dimensions and text size
            self.scaling = ctk.set_window_scaling(self.file_data.data['dpi'])


        ## Widgets
        #top menu bar
        self.top_bar =Top_bar(self).grid(column=0 , row=0, sticky='we')


class Top_bar(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent)
        
        self.settings = ctk.CTkButton(self, text= "settings",command=self.call_settings).pack(side='left',padx=10)
        self.sources = ctk.CTkButton(self, text= "Srources").pack(side='left',padx=10)
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
    

    #About Popup
    def aboutf(self):
        message = '''
        Agemo 
        https://github.com/acidburnmonkey/agemo
        '''
        CTkMessagebox(self,title="About",wraplength=9000000 ,icon='assets/agemo.png',message=message)



#This is the settings window pop up 
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
        with open('agemo.json','w') as f:
            json.dump(self.file_data.data,f, indent=4)

            
    


if __name__ == '__main__':
    app = Main_Frame()
    app.mainloop()
