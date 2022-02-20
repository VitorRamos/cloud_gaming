import socket
import threading
from collections import namedtuple
from ctypes import wintypes, windll, CFUNCTYPE, POINTER, c_int, c_void_p, byref
import ctypes
import win32con
import atexit
import time

sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.bind(("localhost",2020))
sock_server.listen(5)


def keyboard(cnn):
    KeyEvents = namedtuple("KeyEvents", (['event_type', 'key_code',
                                             'scan_code', 'alt_pressed',
                                             'time']))
                                                
    class KBDLLHOOKSTRUCT(ctypes.Structure):
        _fields_= [
            ("vkCode", wintypes.DWORD),
            ("scanCode", wintypes.DWORD),
            ("flags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_long)),
        ]

    # The listener listens to events and adds them to handlers
    event_types = {
        win32con.WM_KEYDOWN: 'key down',  # WM_KeyDown for normal keys
        win32con.WM_KEYUP: 'key up',  # WM_KeyUp for normal keys
        win32con.WM_SYSKEYDOWN: 'key down',  # WM_SYSKEYDOWN, used for Alt key.
        win32con.WM_SYSKEYUP: 'key up',  # WM_SYSKEYUP, used for Alt key.
    }

    def low_level_handler(nCode, wParam, lParam):
        """
        Processes a low level Windows keyboard event.
        """
        event = KeyEvents(event_types[wParam], lParam[0], lParam[1],
                            lParam[2] == 32, lParam[3])
        x = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT))
        cnn.send(b"key")
        print(x.contents.vkCode, x.contents.flags, x.contents.dwExtraInfo)
        return windll.user32.CallNextHookEx(hook_id, nCode, wParam, lParam)

    # Our low level handler signature.
    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    # Convert the Python handler into C pointer.
    pointer = CMPFUNC(low_level_handler)
    # Added 4-18-15 for move to ctypes:
    windll.kernel32.GetModuleHandleW.restype = wintypes.HMODULE
    windll.kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
    # Hook both key up and key down events for common keys (non-system).
    windll.user32.SetWindowsHookExA.argtypes = [wintypes.INT, 
                    CMPFUNC,  wintypes.HINSTANCE, wintypes.DWORD]

    hook_id = windll.user32.SetWindowsHookExA(win32con.WH_KEYBOARD_LL, pointer,
                            windll.kernel32.GetModuleHandleW(None), 0)

    # Register to remove the hook when the interpreter exits.
    atexit.register(windll.user32.UnhookWindowsHookEx, hook_id)
    while True:
        msg = windll.user32.GetMessageW(None, 0, 0,0)
        windll.user32.TranslateMessage(byref(msg))
        windll.user32.DispatchMessageW(byref(msg))

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