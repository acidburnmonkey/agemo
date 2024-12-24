import customtkinter as ctk



class Main_Frame(ctk.CTk):
    def __init__(self):
        super().__init__()

        #General settings
        self.attributes('-type', 'dialog')
        self.geometry('1900x1900')
        self.columnconfigure(0, weight=1)
        
        ## Widgets
        #top menu bar
        self.top_bar =Top_bar(self).grid(column=0 , row=0, sticky='we')
        


class Top_bar(ctk.CTkFrame):
    def __init__(self,parent):
        super().__init__(parent)

        self.settings = ctk.CTkButton(self, text= "settings").pack(side='left',padx=10)
        self.sources = ctk.CTkButton(self, text= "Srources").pack(side='left',padx=10)
        self.about = ctk.CTkButton(self, text= "About").pack(side='left',padx=10)
        self.ex = ctk.CTkButton(self, text= 'X',command=self.kill).pack(anchor='e')
    
    #quit app
    def kill(self):
        app.quit()
        







if __name__ == '__main__':
    app = Main_Frame()
    app.mainloop()
