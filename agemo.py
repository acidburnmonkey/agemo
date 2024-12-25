import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

class Main_Frame(ctk.CTk):
    def __init__(self):
        super().__init__()

        #General settings
        # self.attributes('-type', 'window')
        # self.geometry('1000x1400')
        self.columnconfigure(0, weight=1)

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

        self.attributes('-type', 'dialog')
        # self.minsize('300x400')
        self.geometry('600x800')
        self.columnconfigure(4,weight=1)

        self.exit  = ctk.CTkButton(self,text='x',fg_color='black',command=self.destroy)
        self.exit.grid(row=0,column=4 ,sticky='ne')
        
        self.dpi_label = ctk.CTkLabel(self,text='Default Dpi')
        self.dpi_label.grid(row=1,column=1 ,padx=10, pady=10)

        
        # DPI Scale
        self.dpi_scale = ctk.CTkSlider(self, from_=0, to=3, number_of_steps=6, state='disabled', command=self.set_dpi)
        self.dpi_scale.grid(row=2,column=1 ,padx=5, pady=5)


        #switch
        self.swtich_var = ctk.IntVar(value=0)
        self.dpi_enabler = ctk.CTkSwitch(self, variable=self.swtich_var,onvalue=1, offvalue=0 ,command=self.dpi_switch,text='Enable DPI')
        self.dpi_enabler.grid(row=2,column=3 ,padx=10, pady=10)

        self.splash_label = ctk.CTkLabel(self,text='Splash')
        self.splash_label.grid(row=3,column=1 ,padx=5, pady=5)



        # Apply Button
        self.apply_button = ctk.CTkButton(self, text='Apply', command=self.apply)
        self.apply_button.grid(row=8,column=3 ,padx=10, pady=10)
        


    
    # Enables or Disables dpi scaling
    def dpi_switch(self):
        if self.swtich_var.get() == 0:
            self.dpi_scale.configure(state='disabled')
            self.dpi_label.configure(text='Default Dpi')
        elif self.swtich_var.get() == 1:
            self.dpi_scale.configure(state='normal')
               

        print(self.swtich_var,self.dpi_scale._state)

        
    def set_dpi(self,value):
        self.dpi_label.configure(text=f'Dpi:{value}')
        

    def apply(self):
        value = self.dpi_scale.get()
        #print(self.dpi_scale._state)
        
        #Allows to set Dpi
        if self.swtich_var.get() == 1:
            self.wscaling =  ctk.set_widget_scaling(value)  # widget dimensions and text size
            self.scaling = ctk.set_window_scaling(value)
        
    


if __name__ == '__main__':
    app = Main_Frame()
    app.mainloop()
