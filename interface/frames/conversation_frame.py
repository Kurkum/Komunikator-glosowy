import tkinter as tk
import time

from tkinter import messagebox

# really temporary stuff
# until sockets come lol
whoami = "caller"


class ConversationFrame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Controller from parent element (can turn frames)
        self.controller = controller
        self["bg"] = '#b2bec3'

        # Dictionary that holds flags
        self.flags = {
            "pause_counter": 0
        }

        # Bind ShowFrame event to on_show function
        self.bind("<<ShowFrame>>", self.on_show)

        self.title = tk.Label(self, background="#b2bec3", text="Trwa rozmowa...")
        self.title.pack()

        # Receiver label
        self.receiver_label = tk.Label(self, background="#b2bec3", text="")

        # Is modulation active
        self.modulation_label = tk.Label(self, background="#b2bec3", text="")
        self.modulation_label.pack()

        # Return button
        # return_button = tk.Button(self, text="Zakończ połączenie i wróć do strony głównej", command=self.return_to_main_frame)
        # return_button.pack(side="bottom")

        # End conversation button

        # self.pause_information_label = tk.Label(self, text="", background='#b2bec3')
        # self.pause_information_label.pack(side="bottom")

        # Timer that holds conversation time
        self.conversation_timer = tk.Label(self, background="#b2bec3", text="")
        self.conversation_timer_info = [0, 0, 0]

        # Timer that holds pause time
        self.pause_timer = tk.Label(self, background="#b2bec3", text="")

        # Label that states who has a right to talk right now
        self.who_talks_label = tk.Label(self, background="#b2bec3", text="")

        # Ask for pause
        # pause_button = tk.Button(self, text="Poproś o więcej czasu", command=lambda: self.ask_for_pause())
        # pause_button.pack(side="bottom")

        self.modulation_scale = tk.Scale(self, orient="horizontal", background="#b2bec3", from_=-5, to=5)
        self.modulation_scale.set(self.controller.shared_data["modulation_value"])

        modulation_button = tk.Button(self, text="Ustaw", background="#b2bec3", command=self.set_modulation_value)

        self.modulation_label = tk.Label(self, text="Wartosc modulacji: {}".format(self.modulation_scale.get()), background="#b2bec3")

        self.modulation_label.pack(side="bottom")
        modulation_button.pack(side="bottom")
        self.modulation_scale.pack(side="bottom")

    def set_modulation_value(self):
        self.controller.shared_data["modulation_value"] = self.modulation_scale.get()
        self.modulation_label.configure(text="Wartosc modulacji: {}".format(self.modulation_scale.get()))

    def new_conversation(self):
        return self.controller.conversationHistory.newConversation()

    def set_caller(self):
        self.who_talks_label.pack()
        if self.controller.shared_data["who_called"] == "me":
            self.who_talks_label.configure(text="Nadawca (ja)")
        else:
            self.who_talks_label.configure(text="Nadawca")
        self.controller["bg"] = '#00b894'
        # self.flags["who_talks_flag"] = not self.flags["who_talks_flag"]
        self.flags["who_talks_flag"] = "caller"

    def set_receiver(self):
        self.who_talks_label.pack()
        if self.controller.shared_data["who_called"] == "you":
            self.who_talks_label.configure(text="Odbierający (ja)")
        else:
            self.who_talks_label.configure(text="Odbierający")
        self.controller["bg"] = '#e17055'
        # self.flags["who_talks_flag"] = not self.flags["who_talks_flag"]
        self.flags["who_talks_flag"] = "receiver"

    # Part responsible for conversation timer
    pattern = '{0:02d}:{1:02d}:{2:02d}'

    # Decide whether it's time for me or recipient to talk
    def conversation_timer_after_cycle(self):
        if self.conversation_timer_info[2] == 0 or self.conversation_timer_info[2] == 30:
            return True
        else:
            return False

    def update_messages_sent(self):
        if self.conversation["messages-sent"] is None:
            self.conversation["messages-sent"] = 0
            self.conversation["messages-sent"] = self.conversation["messages-sent"] + 1
        else:
            self.conversation["messages-sent"] = self.conversation["messages-sent"] + 1

    def update_messages_sent_by_source(self):
        if self.conversation["messages-sent-by-source"] is None:
            self.conversation["messages-sent-by-source"] = 0
            self.conversation["messages-sent-by-source"] = self.conversation["messages-sent-by-source"] + 1
        else:
            self.conversation["messages-sent-by-source"] = self.conversation["messages-sent-by-source"] + 1

    def update_messages_sent_by_target(self):
        if self.conversation["messages-sent-by-target"] is None:
            self.conversation["messages-sent-by-target"] = 0
            self.conversation["messages-sent-by-target"] = self.conversation["messages-sent-by-target"] + 1
        else:
            self.conversation["messages-sent-by-target"] = self.conversation["messages-sent-by-target"] + 1

    # Handle conversation timer
    def update_conversation_timer(self, is_ended=False):
        if not is_ended:
            # If it's not stopped
            if self.flags["conversation_timer_running_flag"]:
                # Decide whose time it is to talk
                if self.controller.new_cycle():
                    self.controller.shared_data["cycle_ender"] = "cycle_ended"


                    if self.flags["who_talks_flag"] == "receiver":

                        # if self.conversation["messages-sent"] is None:
                        #     self.conversation["messages-sent"] = 0
                        #     self.conversation["messages-sent"] = self.conversation["messages-sent"] + 1
                        # else:
                        #     self.conversation["messages-sent"] = self.conversation["messages-sent"] + 1

                        self.set_caller()
                    else:

                        # if self.conversation["messages-sent"] is None:
                        #     self.conversation["messages-sent"] = 0
                        #     self.conversation["messages-sent"] = self.conversation["messages-sent"] + 1
                        # else:
                        #     self.conversation["messages-sent"] = self.conversation["messages-sent"] + 1

                        self.set_receiver()

                # Increment conversation timer data
                self.conversation_timer_info[2] += 1

                # If 60 seconds passed, zero the value and increment minutes
                if self.conversation_timer_info[2] >= 60:
                    self.conversation_timer_info[2] = 0
                    self.conversation_timer_info[1] += 1

                # If 60 minutes passed, zero the value and increment hours
                if self.conversation_timer_info[1] >= 60:
                    self.conversation_timer_info[0] += 1
                    self.conversation_timer_info[1] = 0

                # Format time_string in regards to pattern
                time_string = self.pattern.format(self.conversation_timer_info[0],
                                                  self.conversation_timer_info[1],
                                                  self.conversation_timer_info[2])
                return time_string
        else:
            time_string = self.pattern.format(self.conversation_timer_info[0],
                                              self.conversation_timer_info[1],
                                              self.conversation_timer_info[2])
            return time_string

    # Handle conversation timer
    def set_conversation_timer(self):
        if self.flags["conversation_timer_working_flag"]:
            # Update timer with formatted pattern timer value
            self.conversation_timer.configure(text=self.update_conversation_timer())
            # Set new value after 1000 ms
            self.after(1000, self.set_conversation_timer)
        else:
            return

    # To stop conversation timer
    def stop_conversation_timer(self):
        self.flags["conversation_timer_running_flag"] = False

    # To start conversation timer
    def start_conversation_timer(self):
        self.flags["conversation_timer_running_flag"] = True

    def kill_conversation_timer(self):
        self.flags["conversation_timer_working_flag"] = False
        self.conversation_timer.pack_forget()

    def kill_pause_timer(self):
        self.flags["pause_timer_flag"] = False
        number = 30
        self.pause_timer.configure(text="Czas do konca pauzy: {}".format(number))
        self.pause_timer.pack_forget()

    # Handle pause timer
    def update_pause_timer(self, number):
        # If timer still has > seconds left decrement the number and continue counting
        if number != -1:
            self.pause_timer.configure(text="Czas do konca pauzy: {}".format(number))
            self.pause_timer.after(1000, self.update_pause_timer, number-1)
        else:
            # Restart pause timer
            # self.flags["pause_timer_flag"] = False
            # number = 30
            # self.pause_timer.configure(text="Czas do konca pauzy: {}".format(number))
            # self.pause_timer.pack_forget()

            self.kill_pause_timer()

            # After pause time start counting conversation timer again
            self.start_conversation_timer()
            if self.flags["who_talks_flag"] == "receiver":
                self.controller["bg"] = '#e17055'
            else:
                self.controller["bg"] = '#00b894'
            return

    def return_to_main_frame(self):
        #if tk.messagebox.askokcancel("Zakończ", "Czy na pewno chcesz zakończyć połączenie?"):

        # TODO: chamsko zamknij sockety
        tk.messagebox.showinfo("Tajniacy - zakończ", "Połączenie zakończone.")
        self.receiver_label.pack_forget()
        self.kill_conversation_timer()
        self.kill_pause_timer()
        self.conversation["duration"] = self.update_conversation_timer(True)
        self.conversation["status"] = "ended"
        self.controller.conversationHistory.addConversation(self.conversation)
        self.conversation_timer_info = [0, 0, 0]
        self.controller.return_to_main_frame()
        self.pack_forget()

    def on_show(self, event):
        self.flags["pause_timer_flag"] = False
        self.flags["conversation_timer_running_flag"] = True
        self.flags["conversation_timer_working_flag"] = True
        if self.controller.shared_data["modulation_value"] != 0:
            self.modulation_label.configure(text="Modulacja jest aktywna - wartosc: {}".format(self.controller.shared_data["modulation_value"]))
        else:
            self.modulation_label.configure(text="Modulacja nie jest aktywna")

        # who_talks_flag oznacza osobe ktora aktualnie ma prawo do rozmowy - na poczatku rozmowy Callerowi
        # (tu jest wpisane receiver ale potem jest warunek i przechodzi na callera takze spoko)
        #

        self.flags["who_talks_flag"] = "receiver"
        # self.receiver_label.configure(text=self.controller.shared_data["host_ip"])
        # self.receiver_label.pack(side="top")
        self.conversation = self.new_conversation()
        self.conversation["status"] = "in progress"
        self.conversation_timer.pack()
        self.set_conversation_timer()

    def get_current_conversation(self):
        return self.conversation