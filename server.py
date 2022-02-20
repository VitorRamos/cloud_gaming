import socket
import threading
import keyboard as kbd
import time


sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.bind(("0.0.0.0",2020))
sock_server.listen(5)

last_key = ''
last_state = ''
def keyboard(cnn):
    def keycallback(event):
        global last_key, last_state
        if event.name == last_key and event.event_type == last_state:
            return
        key = event.name
        state = event.event_type

        last_key = key
        last_state = state
        cnn.send(event.to_json().encode())
    kbd.hook(keycallback)
    kbd.wait()

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