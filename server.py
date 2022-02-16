import socket
import threading
import time

sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.bind(("localhost",2020))
sock_server.listen(5)

def keyboard(cnn):
    while 1:
        cnn.send(b"key")
        time.sleep(1)

def mouse(cnn):
    while 1:
        cnn.send(b"mouse")
        time.sleep(1)

while 1:
    cnn, addr = sock_server.accept()
    sock_type = cnn.recv(1024)

    if sock_type == b"keyboard":
        threading.Thread(target=keyboard, args=(cnn,)).start()
    elif sock_type == b"mouse":
        threading.Thread(target=mouse, args=(cnn,)).start()