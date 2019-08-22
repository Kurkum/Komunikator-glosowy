import threading
import time
import socket
import wave
import pyaudio
import sys


def interrupt():
    proto = socket.getprotobyname('tcp')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)
    try:
        s.connect(("127.0.0.1", 2222))
    except socket.error:
        pass
    finally:
        s.close()


# SERWER --- odpowiedzialny za nasłuchiwanie
def serwer(flags):
    interface = threading.Thread(target=client, args=(flags,))
    interface.start()

    proto = socket.getprotobyname('tcp')
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)

    serv.bind(("localhost", 2222))
    serv.listen(1)

    while 1:  # po zakończeniu wymiany z tym klientem będzie czekał na następnego (chyba, że dostanie polecenie "exit"
        # print("alfa")
        conn, addr = serv.accept()  # on tu CZEKA i nic nie widzi!
        # print("beta")
        while 1:  # po w
            message = conn.recv(1024)  # [5]  ON W TYM MIEJSCU CZEKA! JAK GO ZAKOŃCZYĆ NORMALNIE????

            # print("ceta")
            if message:
                new_message = str(message)  # musi być nowa zmienna
                if len(str(message)) > 3:
                    new_message = str(message)[2:len(str(message)) - 1]
                new_message = 'Hi, I am a first thread and I received: ' + new_message
                new_message = new_message.encode('utf-8')
                conn.send(new_message)
            else:
                break
        # gdy klient zamknie połączenie to przechodzi dalej i sprawdza flagę:
        # jeśli nikt się nie połączy - jak zamknąć? Mogę się sam z nim połączyć i w ten sposób zamknąć
        if flags[0] != 0:
            conn.close()
            break


# KLIENT --- np. wysyłanie wiadomości
def client(flags):

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
e = threading.Event()

listener = threading.Thread(target=serwer, args=(flags,))
listener.start()


while flags[0] == 0:
    e.wait(1)

e.wait(.5)
if listener.is_alive():  # DO SERWERA:
    print("I will interrupt you!")
    interrupt()


# serwer zamyka się po dostaniu wiadomości od maina, ale jakieś errory <--- to będzie mój serwer.interrupt!!!


'''
PROPOZYCJE:
    zamiast zmieniać flagę wyłączenia programu, wykonać z jakiegokolwiek wątku funkcję ZAKOŃCZ, która pozamykałaby wszystko i zmieniła flagę na 1


'''

