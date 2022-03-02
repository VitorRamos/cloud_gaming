import socket
import threading
import win32api, win32con, win32gui, win32ui
import vkcodes
import numpy as np

addr = ("0.0.0.0", 2020)

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


def get_screenshot():
    w = 1024 # set this
    h = 768 # set this
    hwnd = None
    # get the window image data
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj = win32ui.CreateDCFromHandle(wDC)
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
    cDC.SelectObject(dataBitMap)

    cDC.BitBlt((0, 0), (w, h), dcObj, (0, 0), win32con.SRCCOPY)
    # convert the raw data into a format opencv can read
    signedIntsArray = dataBitMap.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (h, w, 4)

    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())
    # free resources
    return img

def screen(cnn):
    while 1:
        img = get_screenshot()
        data = img.tobytes()
        sz = len(data)
        cnn.send(sz.to_bytes(4,"big")+data)
        
while 1:
    cnn, addr = server_sock.accept()
    data = cnn.recv(1024)
    print(data)
    if data == b"input_events":
        threading.Thread(target=input_events, args=(cnn,)).start()
    if data == b"screen":
        threading.Thread(target=screen, args=(cnn,)).start()