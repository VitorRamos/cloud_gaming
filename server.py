import socket
import threading
import win32api, win32con
import vkcodes
import json

addr = ("localhost", 2020)

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.bind(addr)
server_sock.listen(5)

def input_events(cnn):
    while 1:
        data = cnn.recv(1024)
        aux_ = data.split(b"\r")[:-1]
        while len(aux_):
            aux = aux_.pop()
            aux = aux.decode().split(" ")
            key = aux[0]
            state = aux[1]
            try:
                vk = vkcodes.VK_CODE[key]
                keyup = win32con.KEYEVENTF_KEYUP if state == "1" else 0
                win32api.keybd_event(vk, 0, keyup, 0)
            except:
                pass
            print(data)


while 1:
    cnn, addr = server_sock.accept()
    data = cnn.recv(1024)
    if data == b"input_events":
        threading.Thread(target=input_events, args=(cnn,)).start()