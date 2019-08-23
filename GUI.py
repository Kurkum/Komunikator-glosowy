import tkinter
import socket
import ast
import random
from threading import Thread

from ConversationHistory import ConversationHistory
from ConnectionHandler import ConnectionHandler
from tkinter import messagebox


class GUI(tkinter.Tk):

    def __init__(self):
        tkinter.Tk.__init__(self)

        main_window = tkinter.Frame(self, width=555, height=555)
        main_window.pack_propagate(0)
        main_window.pack()

        self.conversationHistory = ConversationHistory()
        self.connectionHandler = ConnectionHandler('169.254.199.114', random.randint(20000, 20100))

        self.shared_data = {
            "host": ""
        }

        self.frames = {}

        for F in (IPSearchFrame, ConversationFrame, ConversationHistoryFrame):
            page_name = F.__name__
            frame = F(parent=main_window, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("IPSearchFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()


class IPSearchFrame(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller

        ip_search_message = tkinter.Message(self, justify="left", pady=20,
                                            text="Witaj w aplikacji Tajniacy. \n\n"
                                                 "Za jej pomoca mozesz polaczyc sie z wybranym adresem IP i "
                                                 "przeprowadzic tajna konwersacje.\n\nW celu przeprowadzenia rozmowy "
                                                 "wybierz adres IP, a nastepnie wybierz przycisk \"Podejmij "
                                                 "probe kontaktu\".")
        ip_search_message.pack()

        ip_search_entry = tkinter.Entry(self, bd=10, text="Wpisz adres IP")
        ip_search_button = tkinter.Button(self, text="Podejmij probe kontaktu",
                                          command=lambda: self.ip_search_callback(ip_search_entry))
        ip_search_entry.pack()
        ip_search_button.pack()

        conversation_history_button = tkinter.Button(self, text="Pokaz historie polaczen",
                                                     command=lambda: self.controller.show_frame("ConversationHistoryFrame"))
        conversation_history_button.pack()


    def ip_search_callback(self, field):
        ip_search_entry_get = field.get()
        ip, port = ip_search_entry_get.split(":")
        print(ip, port)
        try:
            self.controller.connectionHandler.connect(ip, int(port))
            print('Klient odnaleziony')
            self.controller.shared_data["host"] = ip_search_entry_get
            self.controller.show_frame("ConversationFrame")
        except Exception as ip_search_exception:
            messagebox.showinfo('Blad', 'Nie znaleziono podanego klienta')
            return 0


class ConversationFrame(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)
        self.controller = controller

        self.bind("<<ShowFrame>>", self.on_show)
        button = tkinter.Button(self, text="Wroc do poprzedniej strony", command=lambda: controller.show_frame("IPSearchFrame"))
        button.pack(side="bottom")

    def on_show(self, event):
        try:
            self.receiver_label.pack_forget()
            self.receiver_label = tkinter.Label(self, text=self.controller.shared_data["host"])
            self.receiver_label.pack(side="top")
        except AttributeError:
            self.receiver_label = tkinter.Label(self, text=self.controller.shared_data["host"])
            self.receiver_label.pack(side="top")


class ConversationHistoryFrame(tkinter.Frame):

    def __init__(self, parent, controller):
        tkinter.Frame.__init__(self, parent)

        self.controller = controller

        button = tkinter.Button(self, text="Wroc do poprzedniej strony", command=lambda: controller.show_frame("IPSearchFrame"))
        button.pack(side=tkinter.BOTTOM)

        self.scrollbar = tkinter.Scrollbar(self)
        self.scrollbar.pack(side=tkinter.RIGHT, fill="y")

        self.mylist = tkinter.Listbox(self, yscrollcommand=self.scrollbar.set)
        self.mylist.bind("<<ListboxSelect>>", self.on_select)
        self.conversation_history = self.controller.conversationHistory.readConversationHistoryFromFile()
        self.conversation_history = ast.literal_eval(self.conversation_history)

        for conversation in self.conversation_history:
            self.mylist.insert(tkinter.END, "Rozmowa o ID: " + str(conversation["id"]))
            self.mylist.pack(side="left", fill=tkinter.BOTH)
            self.scrollbar.config(command=self.mylist.yview)

    def on_select(self, event):
        try:
            self.conversation_label_frame.pack_forget()
            selected = event.widget
            index = int(selected.curselection()[0])
            value = selected.get(index)
            self.conversation_label_frame = tkinter.LabelFrame(self,
                                                               text=f"Konwersacja {self.conversation_history[index].get('id')}")
            self.conversation_label_frame.pack(fill="both", expand="yes")

            on_show_message = tkinter.Message(self.conversation_label_frame,
                                              text=self.controller.conversationHistory.prettifyConversation(
                                                  self.conversation_history[index]))
            on_show_message.pack()
        except AttributeError:
            selected = event.widget
            index = int(selected.curselection()[0])
            value = selected.get(index)
            self.conversation_label_frame = tkinter.LabelFrame(self, text=f"Konwersacja {self.conversation_history[index].get('id')}")
            self.conversation_label_frame.pack(fill="both", expand="yes")

            on_show_message = tkinter.Message(self.conversation_label_frame,
                                              text=self.controller.conversationHistory.prettifyConversation(self.conversation_history[index]))
            on_show_message.pack()


interface = GUI()
interface.geometry("300x300")
interface.title("Tajniacy")
interface.resizable(1,1)
interface.mainloop()
print(socket.gethostbyname(socket.gethostname()))