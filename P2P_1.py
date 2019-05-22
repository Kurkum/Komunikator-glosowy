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





# stan nasłuchujący i odbierający
def first(flagi):
    thread_2 = threading.Thread(target=second, args=(flagi,))
    thread_2.start()

    serv = server()

    while 1:
        conn, addr = serv.accept()  # [4]
        while 1:
            message = conn.recv(1024)  # [5]
            if message:
                newMessage = str(message)  # musi być nowa zmienna
                if len(newMessage) > 3:
                    newMessage = newMessage[2:len(newMessage) - 1]
                newMessage = 'Hi, I am a server, I received: ' + newMessage
                newMessage = newMessage.encode('utf-8')
                conn.send(newMessage)
            else:
                break
        if flagi[0] == 1:
            conn.close()
        break



# stan interfejsu np. wysyłający
def second(flagi):
    proto = socket.getprotobyname('tcp')  # [1]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto)  # [2]
    try:
        s.connect(("127.0.0.1", 2222))  # [3]
        message = 'aaa'
        message = message.encode('utf-8')
        s.send(message)  # [4]

        resp = str(s.recv(1024))  # [5]
        if len(resp) > 3:
            resp = resp[2:len(resp) - 1]
        print(resp)
    except socket.error:
        pass
    finally:
        s.close()
    flagi[0] = 1



# stan czekający na wyłączenie itp.
flagi = []
flagi.append(0)


thread_1 = threading.Thread(target=first, args=(flagi,))
thread_1.start()


while(flagi[0] == 0):
    print("Ciagle czekam...")
    time.sleep(1)

