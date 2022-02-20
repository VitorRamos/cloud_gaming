import socket
import threading
import keyboard as kbd
import json

def keyboard(cnn):
    while 1:
        data = cnn.recv(1024)
        ev1 = kbd.KeyboardEvent(**json.loads(data.decode()))
        kbd.play([ev1])
        print(data)


def mouse(cnn):
    while 1:
        data = cnn.recv(1024)
        print(data)

addr = ("localhost", 2020)
sock_mouse = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_mouse.connect(addr)
sock_mouse.send(b"mouse")
threading.Thread(target=mouse, args=(sock_mouse,)).start()
sock_keyboard = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_keyboard.connect(addr)
sock_keyboard.send(b"keyboard")
threading.Thread(target=keyboard, args=(sock_keyboard,)).start()