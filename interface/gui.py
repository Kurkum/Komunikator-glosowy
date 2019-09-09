import tkinter as tk
import socket
import random

from interface.frames.ip_search_frame import IPSearchFrame
from interface.frames.waiting_frame import WaitingFrame
from interface.frames.conversation_frame import ConversationFrame
from interface.frames.conversation_history_frame import ConversationHistoryFrame
from interface.frames.settings_frame import SettingsFrame

from conversation_history.conversation_history import ConversationHistory
from connection_handler.connection_handler import ConnectionHandler


class GUI(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)

        self.main_window = tk.Frame(self, width=555, height=555)
        self.main_window.pack_propagate(0)
        self.main_window.pack()
        self["bg"] = '#b2bec3'

        self.conversationHistory = ConversationHistory()
        self.connectionHandler = ConnectionHandler('169.254.199.114', random.randint(20000, 20100))

        self.shared_data = {
            "host": ""
        }

        self.frame_objects_list = (
            IPSearchFrame,
            WaitingFrame,
            ConversationFrame,
            ConversationHistoryFrame,
            SettingsFrame
        )

        self.frame_objects_container = {}
        self.fill_frame_objects_container(self.frame_objects_list)

        self.show_frame("IPSearchFrame")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def fill_frame_objects_container(self, frame_objects):
        for FrameObject in frame_objects:
            frame_object_name = FrameObject.__name__
            frame_object = FrameObject(parent=self.main_window, controller=self)
            self.frame_objects_container[frame_object_name] = frame_object
            frame_object.grid(row=0, column=0, sticky="nsew")

    def return_to_main_frame(self):
        self["bg"] = '#b2bec3'
        self.frame_objects_container["IPSearchFrame"].event_generate("<<ShowFrame>>")
        self.frame_objects_container["IPSearchFrame"].tkraise()

    def show_frame(self, frame_object_name):
        frame_object = self.frame_objects_container[frame_object_name]
        frame_object.event_generate("<<ShowFrame>>")
        frame_object.tkraise()

    def on_closing(self):
        if tk.messagebox.askokcancel("Zakończ", "Czy na pewno chcesz wyjść z programu?"):
            self.conversationHistory.saveConversationHistoryToFile()
            self.destroy()


if __name__ == '__main__':
    interface = GUI()
    interface.geometry("400x400")
    interface.title("Tajniacy")
    interface.resizable(1,1)
    interface.mainloop()
    # print(socket.gethostbyname(socket.gethostname()))