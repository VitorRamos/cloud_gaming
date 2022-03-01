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
    # override_redirect=1,
    event_mask=X.ExposureMask | X.StructureNotifyMask | X.ConfigureNotify,
    colormap=X.CopyFromParent,
)
window.change_attributes(backing_store=X.Always)
window.map()
window.xinput_select_events([(xinput.AllDevices, 
                                xinput.KeyPressMask | 
                                xinput.KeyReleaseMask |
                                xinput.MotionMask |
                                xinput.ButtonPressMask),])
screen.default_colormap.alloc_named_color('white')
gc = window.create_gc()

prev_ev = b""

def input_events(cnn):
    global prev_ev
    while 1:
        data = disp.next_event()
        if data.type == 35:
            if data.evtype == X.KeyPress:
                keysym = disp.keycode_to_keysym(data.data.detail, 0)
                try:
                    symb = key_mapping[keysym].lower()
                    ev = f"{symb} {2}".encode()+b"\r"
                    if prev_ev != ev:
                        print(prev_ev)
                        cnn.send(ev)
                        prev_ev = ev
                except socket.error as e:
                    print(e)
                    return
                except Exception as e:
                    print(e)
                    continue


            if data.evtype == X.KeyRelease:
                keysym = disp.keycode_to_keysym(data.data.detail, 0)
                try:
                    symb = key_mapping[keysym].lower()
                    ev = f"{symb} {1}".encode()+b"\r" 
                    if prev_ev != ev:
                        print(prev_ev)
                        cnn.send(ev)
                        prev_ev = ev
                except socket.error as e:
                    print(e)
                    return
                except Exception as e:
                    print(e)
                    continue
                    

def screen_stream(cnn):
    ti = time.time()
    fps = 0
    while 1:
        block_sz = cnn.recv(4)
        block_sz = int.from_bytes(block_sz, "big")
        data = b""
        while len(data) < block_sz:
            data += cnn.recv(block_sz-len(data))
        img = np.frombuffer(data, dtype='uint8')
        img.shape = (768, 1024, 4)
        img = img[:,:,-2::-1] # RGB to BGR
        
        data = Image.fromarray(img,'RGB')
        window.put_pil_image(gc, 0, 0, data)
        disp.flush()

        fps += 1
        if time.time()-ti > 1:
            print(f"FPS {fps}")
            fps = 0
            ti = time.time()


addr = ("192.168.122.153", 2020)

thread_input = None
thread_screen = None

while 1:
    if thread_input is None or not thread_input.is_alive():
        kbd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        kbd_sock.connect(addr)
        kbd_sock.send(b"input_events")
        thread_input = threading.Thread(target=input_events, args=(kbd_sock,))
        thread_input.start()
        
    if thread_screen is None or not thread_screen.is_alive():
        display_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        display_sock.connect(addr)
        display_sock.send(b"screen")
        thread_screen = threading.Thread(target=screen_stream, args=(display_sock,))
        thread_screen.start()