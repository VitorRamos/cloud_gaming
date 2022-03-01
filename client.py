import socket
import threading
import keyboard as kbd
import time
from Xlib import X, display, XK
from Xlib.ext import record
from Xlib.protocol import rq


key_mapping = {}
for name in dir(XK):
    if name[:3] == "XK_":
        key_mapping[getattr(XK, name)] = name[3:]

def input_events(cnn):
    record_dpy = display.Display()
    local_dpy = display.Display()
    
    def keycallback(event):
        data = event.data
        while len(data):
            event, data = rq.EventField(None).parse_binary_value(data, record_dpy.display, None, None)

            if event.type == X.KeyPress:
                keysym = local_dpy.keycode_to_keysym(event.detail, 0)
                try:
                        symb = key_mapping[keysym].lower()
                except:
                    return
                cnn.send(f"{symb} {2}".encode()+b"\r")

            if event.type == X.KeyRelease:
                keysym = local_dpy.keycode_to_keysym(event.detail, 0)
                try:
                        symb = key_mapping[keysym].lower()
                except:
                    return
                cnn.send(f"{symb} {1}".encode()+b"\r")

    ctx = record_dpy.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyReleaseMask, X.PointerMotionMask),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }])
        
    record_dpy.record_enable_context(ctx, keycallback)
    record_dpy.record_free_context(ctx)


addr = ("localhost", 2020)
kbd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
kbd_sock.connect(addr)
kbd_sock.send(b"input_events")
threading.Thread(target=input_events, args=(kbd_sock,)).start()