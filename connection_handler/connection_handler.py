import socket
import asyncore

from random import randint
from threading import Thread
from threading import Event
from tkinter import messagebox

# Default parameters - IP address of current machine, along with random port from <20000, 21000>
HOST = socket.gethostbyname(socket.gethostname())
PORT = randint(20000, 21000)


class ConnectionHandler(object):
    def __init__(self, host=HOST, port=PORT):
        """
        Initializes ConnectionHandler object. Opens up two initial sockets - listener and connector.
        Default listener port is the one given by the init parameters, the connector is set to one number higher than
        the former.
        :param host:
        :param port:
        """
        self.host = host

        self.listener_port = port
        self.connector_port = port+1

        self.initial_listener_socket = self.open_listening_socket(self.host, self.listener_port)
        self.initial_connector_socket = self.open_connecting_socket(self.host, self.connector_port)

        self.event_to_kill = Event()

        self.initial_listener_thread = Thread(target=self.begin_listening, args=(self.event_to_kill, "lol"))
        self.initial_listener_thread.start()

    @staticmethod
    def open_listening_socket(host, port):
        """
        Returns socket that will begin listening by default.
        :param host:
        :param port:
        :return: socket
        """
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listening_socket.bind((host, port))
        print('Listener socket open at {}:{}'.format(host, port))
        return listening_socket

    @staticmethod
    def open_connecting_socket(host, port):
        connecting_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connecting_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connecting_socket.bind((host, port))
        return connecting_socket

    def begin_listening(self, stop_event, test):
        while not stop_event.is_set():
            self.initial_listener_socket.listen(1)
            incoming_conn, incoming_addr = self.initial_listener_socket.accept()
            print('Connected by', incoming_addr)
            incoming_ip, incoming_port = incoming_addr
            result = messagebox.askyesno('Info', 'Prosba o polaczenie przez {} - czy chcesz zaakceptowac?'.format(incoming_addr))
            print(result)
            if result:
                print('Trying to connect to {}:{}'.format(incoming_ip, incoming_port-1))
                self.initial_connector_socket.connect((incoming_ip, incoming_port-1))
                data = incoming_conn.recv(1024)
                data = data.decode('utf-8')
                print(data)
            else:
                self.initial_listener_socket.close()

    def begin_connect(self, ip, port):
        self.event_to_kill.set()
        try:
            self.initial_connector_socket.connect((ip, port))
            self.incoming_listener_socket = self.open_listening_socket(self.host, self.listener_port)
            self.incoming_listener_socket.listen(1)
            incoming_conn, incoming_addr = self.incoming_listener_socket.accept()
            print('Connected by', incoming_addr)

        except ConnectionRefusedError as connection_refused_error:
            messagebox.showerror('Klient odmowil polaczenia')

    def start_connection(self):
        try:
            self.initial_connector_socket.send(bytes('test', 'utf-8'))
        except Exception as error:
            print('Nie mozna wyslac wiadomosci')