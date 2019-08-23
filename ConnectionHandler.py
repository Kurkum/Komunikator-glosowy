import socket
from threading import Thread


class ConnectionHandler(object):
    def __init__(self, host, port):
        self.host = host
        self.port_listen = port
        self.port_connect = port+1
        self.sock_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_listen.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_connect.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock_listen.bind((self.host, self.port_listen))
        self.sock_connect.bind((self.host, self.port_connect))
        listen_thread = Thread(target=self.listen)
        listen_thread.start()

    def listen(self):
        print('Listening at {}'.format(self.port_listen))
        self.sock_listen.listen(1)
        conn, addr = self.sock_listen.accept()
        print('Connected by', addr)

    def connect(self, ip, port):
        self.sock_connect.connect((ip, port))

# if __name__ == "__main__":
#     while True:
#         port_num = input("Port? ")
#         try:
#             port_num = int(port_num)
#             break
#         except ValueError:
#             pass
#
#     ConnectionHandler('',port_num).listen()