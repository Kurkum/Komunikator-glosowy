import threading
import time
import socket
import sys


def server():
    proto = socket.getprotobyname('tcp')  # [1]
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)

    serv.bind(("localhost", 2222))  # [2]
    serv.listen(1)  # [3]
    return serv


# listener --- odpowiedzialny za nasłuchiwanie
def first(flags):
    thread_2 = threading.Thread(target=second, args=(flags,))
    thread_2.start()

    serv = server()

    while 1:  # po zakończeniu wymiany z tym klientem będzie próbował nawiązać połączenie z kolejnym klientem
        conn, addr = serv.accept()  # [4]  # on tu chyba czeka tak?
        while 1:
            message = conn.recv(1024)  # [5]  ON W TYM MIEJSCU CZEKA! JAK GO ZAKOŃCZYĆ NORMALNIE????
            if message:
                new_message = str(message)  # musi być nowa zmienna
                if len(str(message)) > 3:
                    new_message = str(message)[2:len(str(message)) - 1]
                new_message = 'Hi, I am a first thread and I received: ' + new_message
                new_message = new_message.encode('utf-8')
                conn.send(new_message)
            else:
                break
        if flags[0] != 0:
            conn.close()
            break


# interfejs --- np. wysyłanie wiadomości
def second(flags):
    proto = socket.getprotobyname('tcp')  # [1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)  # [2]
    try:
        s.connect(("127.0.0.1", 2222))  # [3]
        while 1:
            message = str(input("Podaj wiadomosc (exit zamyka program): "))  # wczytywanie z konsoli
            if message == "exit":
                flags[0] = 1
                break
            message = message.encode('utf-8')

            s.send(message)  # [4]
            resp = str(s.recv(1024))  # [5]

            if len(resp) > 3:
                resp = resp[2:len(resp) - 1]  # usuwanie znaków dodanych przez .encode
            print(resp)
    except socket.error:
        pass
    finally:
        s.close()
    ######## zakończy już po jednym połączeniu
    flags[0] = 1
    ######## zakończy już po jednym połączeniu


# program główny --- sprawujący pieczę nad resztą. Być może w przyszłości zastąpi go listener.
flags = [0]  # flagi


listener = threading.Thread(target=first, args=(flags,))
listener.start()


e = threading.Event()
while flags[0] == 0:
    e.wait(1)

