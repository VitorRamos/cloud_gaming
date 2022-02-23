import socket
import threading
import keyboard as kbd
import json

addr = ("localhost", 2020)

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(addr)
server_sock.listen(5)

def keyboard(cnn):
    while 1:
        data = cnn.recv(1024)
        print(data)


def mouse(cnn):
    while 1:
        data = cnn.recv(1024)
        print(data)

while 1:
    cnn, addr = server_sock.accept()
    data = cnn.recv(1024)
    if data == b"keyboard":
        threading.Thread(target=keyboard, args=(cnn,)).start()
    if data == b"mouse":
        threading.Thread(target=mouse, args=(cnn,)).start()