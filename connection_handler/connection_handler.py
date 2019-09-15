import threading
import socket
import pyaudio
import tkinter as tk
import numpy as np
import wave
import struct

from random import randint


class ConnectionHandler(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.flags = [0, 0, 0]
        self.thread_stopper = {
            "listener": False,
            "clienter": False
        }
        self.listener = threading.Thread(target=self.listener_action, args=())
        self.listener.start()
        self.clienter = threading.Thread(target=self.client_action, args=())
        self.clienter.start()

    def imherre(self):
        print("im here")
        print(self.thread_stopper)

    def add_source_and_target_to_conversation(self, source, target):
        actual_conversation = self.controller.get_current_conversation()
        actual_conversation["source"] = source
        actual_conversation["target"] = target

    def modulate_voice(self, data):
        swidth = 2
        data = np.array(wave.struct.unpack("%dh" % (len(data) / swidth), data)) * 2

        data = np.fft.rfft(data)
        # MANipulation

        # This does the shifting
        data2 = [0] * len(data)
        if self.modulation >= 0:
            data2[self.modulation:len(data)] = data[0:(len(data) - self.modulation)]
            data2[0:self.modulation] = data[(len(data) - self.modulation):len(data)]
        else:
            data2[0:(len(data) + self.modulation)] = data[-self.modulation:len(data)]
            data2[(len(data) + self.modulation):len(data)] = data[0:-self.modulation]

        data = np.array(data2)

        data = np.fft.irfft(data)

        dataout = np.array(data * 0.5, dtype='int16')  # undo the *2 that was done at reading
        chunkout = struct.pack("%dh" % (len(dataout)), *list(dataout))  # convert back to 16-bit data
        return chunkout

    def listener_action(self):
        proto = socket.getprotobyname('tcp')
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)
        self.listen_port = randint(20000, 21000)
        print("Slucham na porcie {}".format(self.listen_port))
        self.serv.bind((self.get_local_ip(), self.listen_port))
        self.serv.listen(1)
        try:
            while 1:
                self.modulation = self.controller.shared_data["modulation_value"]
                conn, addr = self.serv.accept()
                message = self.utfToString(str(conn.recv(1024)))
                tk.messagebox.showinfo("Informacja", "listenAction: Nowa rozmowa typu: {}".format(str(message)))
                if message == "EXIT":  # komunikat pobudzający, nie oczekuje odpowiedzi
                    conn.close()
                    break
                elif message == "ROZMOWA":
                    if self.isBusy():  # jest zajęty
                        print("listenAction [ Sory, jestem zajęty ]")
                        new_message = "NIE ZGODA".encode('utf-8')
                        conn.send(new_message)
                        pass
                    else:
                        self.iAmBusy()
                        if tk.messagebox.askokcancel("Nowe polaczenie", "Czy chcesz oderac nadchodzace polaczenie?"):
                            new_message = "ZGODA".encode('utf-8')
                            conn.send(new_message)
                            self.controller.shared_data["who_called"] = "you"
                            self.controller.show_frame("ConversationFrame")
                            self.add_source_and_target_to_conversation(str(self.get_local_ip()), addr[0])
                            self.conversation_listener(conn)
                        else:
                            new_message = "NIE ZGODA".encode('utf-8')
                            conn.send(new_message)
                if self.thread_stopper["listener"]:
                    print(self.thread_stopper["listener"])
                    self.serv.close()
                    break
        except OSError:
            print("Closed listener socket")

    def conversation_listener(self, conn):
        while 1:
            self.controller.shared_data["cycle_ender"] = "new_cycle"
            message = self.utfToString(str(conn.recv(1024)))
            if message == "KONIEC":
                print("Przeciwnik zażądał zakończenia rozmowy")
                break
            elif message == "NIE KONIEC":
                # ustawienia dla odbierania i wysyłania
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 44100
                RECORD_SECONDS = 10
                WIDTH = 2

                # Odbieranie dźwięku
                p = pyaudio.PyAudio()
                stream = p.open(format=p.get_format_from_width(WIDTH),
                                channels=CHANNELS,
                                rate=RATE,
                                output=True,
                                frames_per_buffer=CHUNK)


                print("Odbieranie dźwięku")
                frames = []
                while 1:
                    data = conn.recv(1024)
                    print(str(data))
                    if str(data)[len(str(data)) - 2] == "K" and str(data)[len(str(data)) - 3] == "K" and str(data)[
                        len(str(data)) - 4] == "K":
                        print("Znaleziono K")
                        break
                    frames.append(data)

                print("Odtworzenie")
                for x in range(len(frames)):
                    stream.write(frames[x])

                print("Zamknięcie strumieni dźwiękowych")
                stream.stop_stream()
                stream.close()
                p.terminate()

                # Koniec / nagraj
                if not tk.messagebox.askokcancel("Akcja", "Co chcesz zrobic? Kontynuuj rozmowe, badz odrzuc"):
                    # Komunikat do drugiej strony
                    message = "KONIEC".encode('utf-8')
                    conn.send(message)
                    break

                else:
                    self.controller.shared_data["cycle_ender"] = "new_cycle"

                    p = pyaudio.PyAudio()
                    stream = p.open(format=FORMAT,
                                    channels=CHANNELS,
                                    rate=RATE,
                                    input=True,
                                    frames_per_buffer=CHUNK)


                    # Nagrywanie
                    print("Nagrywanie: ")
                    frames = []

                    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                        data = stream.read(CHUNK)
                        data = self.modulate_voice(data)
                        frames.append(data)
                    print("KONIEC NAGRYWANIA")

                    # Wysyłanie komunikatu
                    message = "NIE KONIEC".encode('utf-8')
                    conn.send(message)

                    # Wysyłanie dźwięku
                    print("Wysyłanie dźwięku: ")
                    for i in range(len(frames)):
                        conn.send(frames[i])

                    conn.send("KKK".encode('utf-8'))

                    # Zamknięcie strumieni dźwiękowych
                    stream.stop_stream()
                    stream.close()
                    p.terminate()

                    print("Zakończenie wysyłania. Czekam na odpowiedź wroga")
            else:
                print("Wadliwy komunikat: listenAction [ KONIEC / NIE KONIEC ]")
            if self.thread_stopper["listener"]:
                print(self.thread_stopper["listener"])
                conn.close()
                break

    def client_action(self):
        while 1:
            self.modulation = self.controller.shared_data["modulation_value"]
            proto = socket.getprotobyname('tcp')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)
            if self.isFree() and self.controller.shared_data["host_ip"] != "":
                self.iAmBusy()
                adres = self.controller.shared_data["host_ip"]
                port = self.controller.shared_data["host_port"]
                print("Łączę z adresem: " + str(adres))
                try:
                    s.connect((adres, int(port)))

                    # Żądanie rozmowy
                    message = "ROZMOWA".encode('utf-8')
                    s.send(message)
                    while not self.controller.shared_data["waiting_frame"]["not_accepted_flag"]:
                        resp = self.utfToString(str(s.recv(1024)))
                        if resp != "":
                            print("A oto odpowiedź: " + resp)
                            break
                    if resp != "ZGODA":
                        print("Ta osoba X nie ma teraz czasu na rozmowę!")
                        self.controller.shared_data["waiting_frame"]["not_accepted_flag"] = True
                        pass  # finally zamknie sockety i ustawi iAmFree
                    else:  # czyli koniecznie resp == "ZGODA"
                        self.controller.shared_data["waiting_frame"]["stop_timer_flag"] = True
                        print("ZGODA na rozmowę!")
                        self.controller.shared_data["who_called"] = "me"
                        self.controller.show_frame("ConversationFrame")
                        self.add_source_and_target_to_conversation(str(self.get_local_ip()), adres)
                        self.conversation_clienter(s)
                except socket.error:
                    self.controller.shared_data["waiting_frame"]["not_accepted_flag"] = True
                    print("Ta osoba nie ma teraz czasu na rozmowę!")
                finally:
                    self.iAmFree()
                    self.controller.shared_data["host_ip"] = ""

            if self.thread_stopper["clienter"]:
                break

    def conversation_clienter(self, conn):
        while 1:
            print("Co chcesz zrobić: Nagraj wiadomość / Zakończ? [N/Z]")
            if not tk.messagebox.askokcancel("Akcja", "Czy chcesz nagrac odpowiedz czy zakonczyc konwersacje?"):
                # Komunikat do drugiej strony
                message = "KONIEC".encode('utf-8')
                conn.send(message)
                break

            else:
                self.controller.shared_data["cycle_ender"] = "new_cycle"

                # Ustawienia dla wysyłania i odbierania
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 44100
                RECORD_SECONDS = 10
                WIDTH = 2

                # Nagrywanie
                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT,
                                channels=CHANNELS,
                                rate=RATE,
                                input=True,
                                frames_per_buffer=CHUNK)

                print("Nagrywanie: ")
                frames = []

                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    data = self.modulate_voice(data)
                    frames.append(data)
                print("KONIEC NAGRYWANIA")

                # Wysyłanie komunikatu
                message = "NIE KONIEC".encode('utf-8')
                conn.send(message)

                # Wysyłanie dźwięku
                print("Wysyłanie dźwięku: ")
                for i in range(len(frames)):
                    conn.send(frames[i])
                conn.send("KKK".encode('utf-8'))

                # Zamknięcie strumieni dźwiękowych
                stream.stop_stream()
                stream.close()
                p.terminate()

                print("Zakończenie wysyłania. Czekam na odpowiedź wroga")
                self.controller.shared_data["cycle_ender"] = "new_cycle"

                # Czekam na komunikat
                resp = self.utfToString(str(conn.recv(1024)))
                if resp == "KONIEC":
                    print("Wróg zażądał zakończenia rozmowy")
                    break

                elif resp == "NIE KONIEC":

                    # Odbieranie dźwięku
                    p = pyaudio.PyAudio()
                    stream = p.open(format=p.get_format_from_width(WIDTH),
                                    channels=CHANNELS,
                                    rate=RATE,
                                    output=True,
                                    frames_per_buffer=CHUNK)

                    print("Odbieranie dźwięku")
                    frames = []
                    while 1:
                        data = conn.recv(1024)
                        print(str(data))
                        if str(data)[len(str(data)) - 2] == "K" and str(data)[len(str(data)) - 3] == "K" and str(data)[
                            len(str(data)) - 4] == "K":
                            print("Znaleziono K")
                            break
                        frames.append(data)

                    print("Odtworzenie")
                    for x in range(len(frames)):
                        stream.write(frames[x])

                    print("Zamknięcie strumieni dźwiękowych")
                    stream.stop_stream()
                    stream.close()
                    p.terminate()

                else:
                    print("Wadliwy komunikat: clientAction [ KONIEC / NIE KONIEC ]")
                    print(str(resp))
            if self.thread_stopper["clienter"]:
                break

    def get_local_ip(self):
        ip_address_list = socket.gethostbyname_ex(socket.gethostname())[2]

        local = "not_found"

        for address in ip_address_list:
            if address[0] == '1' and address[1] == '9' and address[2] == '2':
                local = address

        return local

    def iAmBusy(self):
        self.flags[1] = 1

    def iAmFree(self):
        self.flags[1] = 0

    def isBusy(self):
        if self.flags[1] == 0:
            return False
        return True

    def isFree(self):
        if self.flags[1] == 0:
            return True
        return False

    def exit_listener(self):
        done = False
        while not done:
            test_socket_protocol = socket.getprotobyname('tcp')  # [1]
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, test_socket_protocol)  # [2]
            try:
                test_socket.connect((self.get_local_ip(), self.listen_port))  # [3]
                message = "EXIT"
                message = message.encode('utf-8')
                test_socket.send(message)  # [4]
                done = True
            except socket.error:
                print("CheckTheFlag: Złe IP!")
                pass
            finally:
                test_socket.close()

    def utfToString(self, word):
        if len(word) > 3:
            word = word[2:len(word) - 1]
        return word

# import socket
# import asyncore
#
# from random import randint
# from threading import Thread
# from threading import Event
# from tkinter import messagebox
#
# # Default parameters - IP address of current machine, along with random port from <20000, 21000>
# HOST = socket.gethostbyname(socket.gethostname())
# PORT = randint(20000, 21000)
#
#
# class ConnectionHandler(object):
#     def __init__(self, host=HOST, port=PORT):
#         """
#         Initializes ConnectionHandler object. Opens up two initial sockets - listener and connector.
#         Default listener port is the one given by the init parameters, the connector is set to one number higher than
#         the former.
#         :param host:
#         :param port:
#         """
#         self.host = host
#
#         self.listener_port = port
#         self.connector_port = port+1
#
#         self.initial_listener_socket = self.open_listening_socket(self.host, self.listener_port)
#         self.initial_connector_socket = self.open_connecting_socket(self.host, self.connector_port)
#
#         self.event_to_kill = Event()
#
#         self.initial_listener_thread = Thread(target=self.begin_listening, args=(self.event_to_kill, "lol"))
#         self.initial_listener_thread.start()
#
#     @staticmethod
#     def open_listening_socket(host, port):
#         """
#         Returns socket that will begin listening by default.
#         :param host:
#         :param port:
#         :return: socket
#         """
#         listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         listening_socket.bind((host, port))
#         print('Listener socket open at {}:{}'.format(host, port))
#         return listening_socket
#
#     @staticmethod
#     def open_connecting_socket(host, port):
#         connecting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         connecting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         connecting_socket.bind((host, port))
#         return connecting_socket
#
#     def begin_listening(self, stop_event, test):
#         while not stop_event.is_set():
#             self.initial_listener_socket.listen(1)
#             incoming_conn, incoming_addr = self.initial_listener_socket.accept()
#             print('Connected by', incoming_addr)
#             incoming_ip, incoming_port = incoming_addr
#             result = messagebox.askyesno('Info', 'Prosba o polaczenie przez {} - czy chcesz zaakceptowac?'.format(incoming_addr))
#             print(result)
#             if result:
#                 print('Trying to connect to {}:{}'.format(incoming_ip, incoming_port-1))
#                 self.initial_connector_socket.connect((incoming_ip, incoming_port-1))
#                 data = incoming_conn.recv(1024)
#                 data = data.decode('utf-8')
#                 print(data)
#             else:
#                 self.initial_listener_socket.close()
#
#     def begin_connect(self, ip, port):
#         self.event_to_kill.set()
#         try:
#             self.initial_connector_socket.connect((ip, port))
#             self.incoming_listener_socket = self.open_listening_socket(self.host, self.listener_port)
#             self.incoming_listener_socket.listen(1)
#             incoming_conn, incoming_addr = self.incoming_listener_socket.accept()
#             print('Connected by', incoming_addr)
#
#         except ConnectionRefusedError as connection_refused_error:
#             messagebox.showerror('Klient odmowil polaczenia')
#
#     def start_connection(self):
#         try:
#             self.initial_connector_socket.send(bytes('test', 'utf-8'))
#         except Exception as error:
#             print('Nie mozna wyslac wiadomosci')