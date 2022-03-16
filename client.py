import socket
import threading
import time
from Xlib import X, display, XK
from Xlib.ext import xinput
import numpy as np
from PIL import Image

key_mapping = {}
for name in dir(XK):
    if name[:3] == "XK_":
        key_mapping[getattr(XK, name)] = name[3:]


disp = display.Display()
screen = disp.screen()
window = screen.root.create_window(
    100,
    100,
    1024,
    768,
    0,
    screen.root_depth,
    X.InputOutput,
    X.CopyFromParent,
    background_pixel=screen.white_pixel,
    override_redirect=0,
    event_mask=X.ExposureMask,# | X.StructureNotifyMask | X.ConfigureNotify,
    colormap=X.CopyFromParent,
)
window.change_attributes(backing_store=X.Always)
window.map()
window.xinput_select_events([(xinput.AllDevices, 
                                xinput.KeyPressMask | 
                                xinput.KeyReleaseMask |
                                xinput.MotionMask |
                                xinput.ButtonPressMask |
                                xinput.ButtonReleaseMask),])
screen.default_colormap.alloc_named_color('white')
gc = window.create_gc()

prev_ev = b""
prev_ev_mouse = b""

mutex = threading.Lock()


def input_events(kbd_sock, mouse_sock):
    global prev_ev, prev_ev_mouse
    while 1:
        mutex.acquire()
        data = disp.next_event()
        mutex.release()
        if data.type == 35:
            if data.evtype == X.KeyPress:
                keysym = disp.keycode_to_keysym(data.data.detail, 0)
                try:
                    symb = key_mapping[keysym].lower()
                    ev = f"{symb} {2}".encode()+b"\r"
                    if prev_ev != ev:
                        print(prev_ev)
                        kbd_sock.send(ev)
                        prev_ev = ev
                except socket.error as e:
                    print("A",e)
                    return
                except Exception as e:
                    print("A",e)
                    continue


            if data.evtype == X.KeyRelease:
                keysym = disp.keycode_to_keysym(data.data.detail, 0)
                try:
                    symb = key_mapping[keysym].lower()
                    ev = f"{symb} {1}".encode()+b"\r" 
                    if prev_ev != ev:
                        print(prev_ev)
                        kbd_sock.send(ev)
                        prev_ev = ev
                except socket.error as e:
                    print("A",e)
                    return
                except Exception as e:
                    print("A",e)
                    continue
            
            if data.evtype == X.ButtonPress:
                try:
                    aux = data.data
                    dx =  int(65535*aux.event_x/1024)
                    dy =  int(65535*aux.event_y/768)
                    ev = f"{aux.detail} {dx} {dy} 2".encode()+b"\r"
                    if prev_ev_mouse != ev:
                        print(aux.detail, aux.event_x, aux.event_y, 2)
                        mouse_sock.send(ev)
                        prev_ev_mouse = ev
                except socket.error as e:
                    print("A",e)
                    return
                except Exception as e:
                    print("A",e)
                    continue

            if data.evtype == X.ButtonRelease:
                try:
                    aux = data.data
                    dx =  int(65535*aux.event_x/1024)
                    dy =  int(65535*aux.event_y/768)
                    ev = f"{aux.detail} {dx} {dy} 1".encode()+b"\r"
                    if prev_ev_mouse != ev:
                        print(aux.detail, aux.event_x, aux.event_y, 2)
                        mouse_sock.send(ev)
                        prev_ev_mouse = ev
                except socket.error as e:
                    print("A",e)
                    return
                except Exception as e:
                    print("A",e)
                    continue

import hashlib
import PIL
import tempfile

def screen_stream(cnn):
    ti = time.time()
    fps = 0
    while 1:
        header = cnn.recv(5)
        magic = header[0]
        if magic != 170:
            print("Magic error")
            continue
        block_sz = int.from_bytes(header[1:], "big")
        data = b""
        while len(data) < block_sz:
            data += cnn.recv(block_sz-len(data))
        checksum = cnn.recv(16)
        if checksum != hashlib.md5(data).digest():
            print("Checksum error")
            continue
        # print(magic, block_sz, data)
        with tempfile.NamedTemporaryFile(suffix=".jpeg") as tmpfile:
            tmpfile.write(data)
            tmpfile.seek(0)
            data = Image.open(tmpfile)
            data.getdata()

        window.put_pil_image(gc, 0, 0, data)
        # mutex.acquire()
        disp.flush()
        # mutex.release()

        fps += 1
        if time.time()-ti > 1:
            print(f"FPS {fps}")
            fps = 0
            ti = time.time()


addr = ("192.168.122.153", 2020)
addr = ("201.9.172.250", 50505)

thread_input = None
thread_screen = None

import os
pid = os.fork()

if pid == 0:
    while 1:
        display_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        display_sock.connect(addr)
        display_sock.send(b"screen")
        try:
            screen_stream(display_sock)
        except:
            print("Screen died")
            break

while 1:
    if thread_input is None or not thread_input.is_alive():
        kbd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        kbd_sock.connect(addr)
        kbd_sock.send(b"input_events")
        mouse_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mouse_sock.connect(addr)
        mouse_sock.send(b"mouse")
        thread_input = threading.Thread(target=input_events, args=(kbd_sock,mouse_sock))
        thread_input.start()
        
    # if thread_screen is None or not thread_screen.is_alive():
    #     display_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     display_sock.connect(addr)
    #     display_sock.send(b"screen")
    #     thread_screen = threading.Thread(target=screen_stream, args=(display_sock,))
    #     thread_screen.start()
