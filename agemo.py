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
        self.rowconfigure(0,weight=1)

        self.exit  = ctk.CTkButton(self,text='x',fg_color='black',command=self.destroy).pack(anchor='e')
        
        self.dpi_label = ctk.CTkLabel(self,text='Default')
        self.dpi_label.pack(padx=10, pady=10)
        self.dpi_scale = ctk.CTkSlider(self,from_=1, to=3, number_of_steps=6,command=self.set_dpi)
        self.dpi_scale.pack(padx=10,pady=10)
        
        self.testo = ctk.CTkButton(self,text='Apply',command=self.apply).pack()

    def set_dpi(self,value):
        self.dpi_label.configure(text=value)
        print(value)

    def apply(self):
        pass

        # self.wscaling =  ctk.set_widget_scaling(1)  # widget dimensions and text size
        # self.scaling = ctk.set_window_scaling(1)
    


if __name__ == '__main__':
    app = Main_Frame()
    app.mainloop()
