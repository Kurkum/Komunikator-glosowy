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

        self.modulation_scale = tk.Scale(self, orient="horizontal", background="#b2bec3", from_=-5, to=5)
        self.modulation_scale.pack()

        modulation_button = tk.Button(self, text="Ustaw", background="#b2bec3", command=self.set_modulation_value)
        modulation_button.pack()

        self.modulation_label = tk.Label(self, text="", background="#b2bec3")
        self.modulation_label.pack()

        self.bind("<<ShowFrame>>", self.on_show)

    def on_show(self, event):
        pass

    def set_modulation_value(self):
        self.controller.shared_data["modulation_value"] = self.modulation_scale.get()
        self.modulation_label.configure(text="Wartosc modulacji: {}".format(self.modulation_scale.get()))