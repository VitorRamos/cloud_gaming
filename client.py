import socket
import threading

def keyboard(cnn):
    while 1:
        data = cnn.recv(1024)
        print(data)


def mouse(cnn):
    while 1:
        data = cnn.recv(1024)
        print(data)


sock_mouse = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_mouse.connect(("localhost",2020))
sock_mouse.send(b"mouse")
threading.Thread(target=mouse, args=(sock_mouse,)).start()
sock_keyboard = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_keyboard.connect(("localhost",2020))
sock_keyboard.send(b"keyboard")
threading.Thread(target=keyboard, args=(sock_keyboard,)).start()