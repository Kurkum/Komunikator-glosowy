import tkinter as tk
import re


class SettingsFrame(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self["bg"] = '#b2bec3'

        self.controller = controller
        return_button = tk.Button(self, text="Wróć do poprzedniej strony", command=self.controller.return_to_main_frame)
        return_button.pack(side="bottom")

        self.controller.modulation_var = tk.IntVar()

        modulation_check = tk.Checkbutton(self, text="Modulacja", variable=self.controller.modulation_var, \
                                          background='#b2bec3')
        modulation_check.pack()


        self.bind("<<ShowFrame>>", self.on_show)

    def on_show(self, event):
        pass